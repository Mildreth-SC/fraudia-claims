#!/usr/bin/env Rscript

# ============================================================
# FraudIA - Data Cleaner & Fraud Detection Script
# Limpieza de datos + detección de fraude con 7 reglas RF
# ============================================================

library(dplyr)
library(readr)
library(ggplot2)
library(scales)

# ============================================================
# 1. FUNCIONES AUXILIARES
# ============================================================

detectar_columna <- function(nombres_cols, patrones) {
  # Busca columna que coincida con patrones (case-insensitive)
  nombres_lower <- tolower(nombres_cols)
  for (patron in patrones) {
    idx <- which(grepl(patron, nombres_lower, ignore.case = TRUE))
    if (length(idx) > 0) return(nombres_cols[idx[1]])
  }
  return(NULL)
}

mapear_columnas <- function(df) {
  # Mapea columnas del CSV entrante a estructura esperada
  cols <- names(df)

  mapeo <- list(
    id_siniestro = detectar_columna(cols, c("id", "siniestro", "claim", "codigo", "case")),
    monto_reclamado = detectar_columna(cols, c("amount", "monto", "valor", "suma", "reclamado")),
    dias_desde_inicio_poliza = detectar_columna(cols, c("days.*policy", "dias.*poliza", "policy_age", "dias_vigencia")),
    dias_entre_ocurrencia_reporte = detectar_columna(cols, c("days.*report", "dias.*reporte", "report_delay", "demora")),
    historial_siniestros_asegurado = detectar_columna(cols, c("history", "historial", "count.*claim", "siniestros_prev")),
    documentos_completos = detectar_columna(cols, c("document", "documents", "documentos", "complete")),
    id_proveedor = detectar_columna(cols, c("provider", "proveedor", "vendor", "id_prv", "supplier")),
    suma_asegurada = detectar_columna(cols, c("sum.*insured", "suma", "coverage", "asegurada")),
    cobertura = detectar_columna(cols, c("coverage", "cobertura", "type", "line", "ramo")),
    ciudad = detectar_columna(cols, c("city", "ciudad", "location", "ubication")),
    ramo = detectar_columna(cols, c("ramo", "line", "branch", "tipo_cobertura"))
  )

  return(mapeo)
}

limpiar_valores_faltantes <- function(df) {
  # Rellena valores faltantes de forma inteligente
  for (col in names(df)) {
    if (is.numeric(df[[col]])) {
      mediana <- median(df[[col]], na.rm = TRUE)
      if (is.na(mediana)) mediana <- 0
      df[[col]][is.na(df[[col]])] <- mediana
    } else if (is.logical(df[[col]])) {
      df[[col]][is.na(df[[col]])] <- TRUE
    } else if (is.character(df[[col]])) {
      df[[col]][is.na(df[[col]])] <- "No especificado"
    }
  }
  return(df)
}

procesar_tipos <- function(df) {
  # Convierte tipos de datos apropiadamente
  df <- df %>%
    mutate(
      across(contains("fecha") | contains("date"), as.character),
      across(contains("completo") | contains("documento"), as.logical),
      across(matches("^(monto|suma|dias)"), as.numeric),
      across(matches("^(id_|codigo)", ignore.case = TRUE), as.character)
    )
  return(df)
}

# ============================================================
# 2. REGLAS DE FRAUDE (RF-01 a RF-07)
# ============================================================

calcular_score_fraude <- function(df) {
  df <- df %>%
    mutate(
      score = 0,
      alertas = "",

      # RF-01: Borde de vigencia (primeros 10-30 días)
      score = if_else(dias_desde_inicio_poliza <= 10, score + 8, score),
      alertas = if_else(dias_desde_inicio_poliza <= 10,
                       paste(alertas, "RF-01a: Siniestro en primeros 10 días (+8 pts)", sep=" | "),
                       alertas),
      score = if_else(dias_desde_inicio_poliza > 10 & dias_desde_inicio_poliza <= 30, score + 4, score),
      alertas = if_else(dias_desde_inicio_poliza > 10 & dias_desde_inicio_poliza <= 30,
                       paste(alertas, "RF-01b: Siniestro en 11-30 días (+4 pts)", sep=" | "),
                       alertas),

      # RF-02: Reporte tardío
      score = if_else(dias_entre_ocurrencia_reporte > 7, score + 5, score),
      alertas = if_else(dias_entre_ocurrencia_reporte > 7,
                       paste(alertas, "RF-02a: Reporte tardío >7 días (+5 pts)", sep=" | "),
                       alertas),
      score = if_else(dias_entre_ocurrencia_reporte > 3 & dias_entre_ocurrencia_reporte <= 7, score + 3, score),
      alertas = if_else(dias_entre_ocurrencia_reporte > 3 & dias_entre_ocurrencia_reporte <= 7,
                       paste(alertas, "RF-02b: Reporte tardío 4-7 días (+3 pts)", sep=" | "),
                       alertas),

      # RF-03: Alta frecuencia de asegurado
      score = if_else(historial_siniestros_asegurado >= 3, score + 8, score),
      alertas = if_else(historial_siniestros_asegurado >= 3,
                       paste(alertas, "RF-03a: 3+ siniestros en 18 meses (+8 pts)", sep=" | "),
                       alertas),
      score = if_else(historial_siniestros_asegurado == 2, score + 4, score),
      alertas = if_else(historial_siniestros_asegurado == 2,
                       paste(alertas, "RF-03b: 2 siniestros recientes (+4 pts)", sep=" | "),
                       alertas),

      # RF-04: Documentos incompletos
      score = if_else(!documentos_completos, score + 4, score),
      alertas = if_else(!documentos_completos,
                       paste(alertas, "RF-04: Documentos incompletos (+4 pts)", sep=" | "),
                       alertas),

      # RF-05: Proveedor restrictivo
      score = if_else(id_proveedor %in% c("P001", "P002", "P007"), score + 10, score),
      alertas = if_else(id_proveedor %in% c("P001", "P002", "P007"),
                       paste(alertas, "RF-05: Proveedor restrictivo (+10 pts)", sep=" | "),
                       alertas),

      # RF-06: Monto cercano a suma asegurada
      score = if_else(suma_asegurada > 0 & (monto_reclamado / suma_asegurada) >= 0.95, score + 5, score),
      alertas = if_else(suma_asegurada > 0 & (monto_reclamado / suma_asegurada) >= 0.95,
                       paste(alertas, "RF-06: Monto ≥95% suma asegurada (+5 pts)", sep=" | "),
                       alertas),

      # RF-07: Demora en robo
      score = if_else(cobertura == "Robo" & dias_entre_ocurrencia_reporte > 2, score + 8, score),
      alertas = if_else(cobertura == "Robo" & dias_entre_ocurrencia_reporte > 2,
                       paste(alertas, "RF-07: Robo con >48h demora (+8 pts)", sep=" | "),
                       alertas),

      # Normalizar score (máx 100)
      score = pmin(score, 100),

      # Clasificación por nivel de riesgo
      nivel_riesgo = case_when(
        score >= 40 ~ "ROJO",
        score >= 20 ~ "AMARILLO",
        TRUE ~ "VERDE"
      ),

      # Limpiar alertas
      alertas = trimws(sub("^\\s*\\|\\s*", "", alertas))
    )

  return(df)
}

# ============================================================
# 6. GENERACIÓN DE GRÁFICOS
# ============================================================

generar_graficos <- function(df, output_dir) {
  # Crear carpeta de gráficos
  graficos_dir <- file.path(output_dir, "graficos")
  if (!dir.exists(graficos_dir)) {
    dir.create(graficos_dir, recursive = TRUE, showWarnings = FALSE)
  }

  # Definir paleta de colores para riesgo
  colores_riesgo <- c("ROJO" = "#dc2626", "AMARILLO" = "#eab308", "VERDE" = "#16a34a")

  # Gráfico 1: Distribución de riesgo (Donut chart profesional)
  p1 <- df %>%
    group_by(nivel_riesgo) %>%
    summarise(count = n(), .groups = "drop") %>%
    mutate(percentage = round(100 * count / sum(count), 1)) %>%
    ggplot(aes(x = 2, y = count, fill = factor(nivel_riesgo, levels = c("ROJO", "AMARILLO", "VERDE")))) +
    geom_bar(stat = "identity", width = 1, color = "white", linewidth = 2) +
    coord_polar(theta = "y", start = 0) +
    xlim(0.5, 2.5) +
    scale_fill_manual(values = colores_riesgo, name = "Nivel de Riesgo") +
    labs(title = "Distribución de Riesgo - FraudIA",
         subtitle = paste("Total casos:", nrow(df))) +
    theme_minimal() +
    theme(
      axis.text = element_blank(),
      axis.title = element_blank(),
      panel.grid = element_blank(),
      legend.position = "right",
      plot.title = element_text(size = 16, face = "bold", hjust = 0.5),
      plot.subtitle = element_text(size = 12, hjust = 0.5)
    ) +
    geom_text(aes(x = 1.3, label = paste0(percentage, "%")), position = position_stack(vjust = 0.5), size = 5, color = "white", fontface = "bold")

  ggsave(file.path(graficos_dir, "distribucion_riesgo.png"), p1, width = 10, height = 7, dpi = 100)

  # Gráfico 2: Distribución por Ramo Y Riesgo (barras apiladas, no agrupadas)
  p2 <- df %>%
    group_by(ramo, nivel_riesgo) %>%
    summarise(count = n(), .groups = "drop") %>%
    mutate(nivel_riesgo = factor(nivel_riesgo, levels = c("ROJO", "AMARILLO", "VERDE"))) %>%
    ggplot(aes(x = reorder(ramo, count, sum), y = count, fill = nivel_riesgo)) +
    geom_bar(stat = "identity", position = "stack", color = "white", linewidth = 0.5) +
    scale_fill_manual(values = colores_riesgo, name = "Nivel de Riesgo") +
    labs(title = "Distribución de Casos por Ramo y Riesgo",
         subtitle = "Barras apiladas: ROJO (crítico), AMARILLO (medio), VERDE (normal)",
         x = "Ramo",
         y = "Cantidad de Casos") +
    theme_minimal() +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1, size = 10),
      plot.title = element_text(size = 14, face = "bold"),
      plot.subtitle = element_text(size = 10, color = "gray50"),
      legend.position = "right"
    )

  ggsave(file.path(graficos_dir, "score_por_ramo.png"), p2, width = 12, height = 7, dpi = 100)

  # Gráfico 3: Top proveedores con desglose de riesgo (apilado)
  prov_data <- df %>%
    group_by(proveedor = coalesce(id_proveedor, "No especificado"), nivel_riesgo) %>%
    summarise(count = n(), .groups = "drop") %>%
    group_by(proveedor) %>%
    mutate(total = sum(count)) %>%
    ungroup() %>%
    arrange(desc(total)) %>%
    distinct(proveedor, .keep_all = FALSE) %>%
    slice(1:10)

  prov_top <- prov_data %>% pull(proveedor) %>% unique()

  p3 <- df %>%
    filter(id_proveedor %in% prov_top | (is.na(id_proveedor) & "No especificado" %in% prov_top)) %>%
    mutate(proveedor = coalesce(id_proveedor, "No especificado")) %>%
    group_by(proveedor, nivel_riesgo) %>%
    summarise(count = n(), .groups = "drop") %>%
    mutate(
      proveedor = factor(proveedor, levels = prov_top),
      nivel_riesgo = factor(nivel_riesgo, levels = c("ROJO", "AMARILLO", "VERDE"))
    ) %>%
    ggplot(aes(x = proveedor, y = count, fill = nivel_riesgo)) +
    geom_bar(stat = "identity", position = "stack", color = "white", linewidth = 0.5) +
    scale_fill_manual(values = colores_riesgo, name = "Nivel de Riesgo") +
    labs(title = "Top 10 Proveedores con Alertas",
         subtitle = "Desglose por ROJO, AMARILLO y VERDE",
         x = "Proveedor",
         y = "Cantidad de Alertas") +
    coord_flip() +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 14, face = "bold"),
      plot.subtitle = element_text(size = 10, color = "gray50"),
      legend.position = "right"
    )

  ggsave(file.path(graficos_dir, "top_proveedores.png"), p3, width = 12, height = 8, dpi = 100)

  # Gráfico 4: Alertas por ciudad con desglose de riesgo (apilado)
  ciudad_data <- df %>%
    group_by(ciudad = coalesce(ciudad, "No especificada")) %>%
    summarise(total = n(), .groups = "drop") %>%
    arrange(desc(total)) %>%
    head(10)

  ciudad_top <- ciudad_data %>% pull(ciudad)

  p4 <- df %>%
    filter(ciudad %in% ciudad_top | (is.na(ciudad) & "No especificada" %in% ciudad_top)) %>%
    mutate(ciudad = coalesce(ciudad, "No especificada")) %>%
    group_by(ciudad, nivel_riesgo) %>%
    summarise(count = n(), .groups = "drop") %>%
    mutate(
      ciudad = factor(ciudad, levels = ciudad_top),
      nivel_riesgo = factor(nivel_riesgo, levels = c("ROJO", "AMARILLO", "VERDE"))
    ) %>%
    ggplot(aes(x = ciudad, y = count, fill = nivel_riesgo)) +
    geom_bar(stat = "identity", position = "stack", color = "white", linewidth = 0.5) +
    scale_fill_manual(values = colores_riesgo, name = "Nivel de Riesgo") +
    labs(title = "Top 10 Ciudades por Casos de Riesgo",
         subtitle = "Barras apiladas: ROJO (crítico), AMARILLO (medio), VERDE (normal)",
         x = "Ciudad",
         y = "Cantidad de Casos") +
    theme_minimal() +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1),
      plot.title = element_text(size = 14, face = "bold"),
      plot.subtitle = element_text(size = 10, color = "gray50"),
      legend.position = "right"
    )

  ggsave(file.path(graficos_dir, "alertas_ciudad.png"), p4, width = 12, height = 7, dpi = 100)

  return(graficos_dir)
}

generar_reporte_limpieza <- function(df, mapeo) {
  reporte <- c(
    paste0(strrep("=", 60)),
    "REPORTE DE LIMPIEZA DE DATOS - FraudIA",
    paste0(strrep("=", 60)),
    "",
    "MAPEO DE COLUMNAS DETECTADAS:",
    paste0(strrep("-", 60)),
    paste("  • ID Siniestro:", mapeo$id_siniestro %||% "NO DETECTADA"),
    paste("  • Monto Reclamado:", mapeo$monto_reclamado %||% "NO DETECTADA"),
    paste("  • Días Vigencia:", mapeo$dias_desde_inicio_poliza %||% "NO DETECTADA"),
    paste("  • Reporte Tardío:", mapeo$dias_entre_ocurrencia_reporte %||% "NO DETECTADA"),
    paste("  • Historial Asegurado:", mapeo$historial_siniestros_asegurado %||% "NO DETECTADA"),
    paste("  • Documentos:", mapeo$documentos_completos %||% "NO DETECTADA"),
    paste("  • Proveedor:", mapeo$id_proveedor %||% "NO DETECTADA"),
    paste("  • Suma Asegurada:", mapeo$suma_asegurada %||% "NO DETECTADA"),
    paste("  • Cobertura:", mapeo$cobertura %||% "NO DETECTADA"),
    paste("  • Ciudad:", mapeo$ciudad %||% "NO DETECTADA"),
    paste("  • Ramo:", mapeo$ramo %||% "NO DETECTADA"),
    "",
    "RESUMEN DE LIMPIEZA:",
    paste0(strrep("-", 60)),
    paste("  • Registros procesados:", nrow(df)),
    paste("  • Valores faltantes detectados:", sum(is.na(df))),
    paste("  • Tipos de datos convertidos: Numérico, Booleano, Fecha, Texto"),
    "",
    "CALIDAD DE DATOS RESULTANTE:",
    paste0(strrep("-", 60)),
    paste("  • Score de completitud:", round(100 * (1 - sum(is.na(df)) / (nrow(df) * ncol(df))), 1), "%"),
    paste("  • Registros válidos para análisis:", nrow(df))
  )

  return(paste(reporte, collapse = "\n"))
}

generar_informe_alertas <- function(df) {
  total <- nrow(df)
  rojos <- sum(df$nivel_riesgo == "ROJO")
  amarillos <- sum(df$nivel_riesgo == "AMARILLO")
  verdes <- sum(df$nivel_riesgo == "VERDE")

  score_medio <- mean(df$score, na.rm = TRUE)
  score_mediano <- median(df$score, na.rm = TRUE)

  # Top 5 indicadores
  alertas_split <- strsplit(df$alertas, " \\| ")
  todas_alertas <- unlist(alertas_split)
  todas_alertas <- todas_alertas[todas_alertas != ""]
  indicadores <- table(todas_alertas) %>% sort(decreasing = TRUE) %>% head(5)

  # Distribución por ciudad (si existe)
  dist_ciudad <- df %>%
    group_by(ciudad = coalesce(ciudad, "No especificada")) %>%
    summarise(total = n(), rojos = sum(nivel_riesgo == "ROJO"), .groups = "drop") %>%
    arrange(desc(rojos)) %>%
    head(5)

  # Top 5 proveedores
  dist_prov <- df %>%
    group_by(proveedor = coalesce(id_proveedor, "No especificado")) %>%
    summarise(total = n(), rojos = sum(nivel_riesgo == "ROJO"), .groups = "drop") %>%
    arrange(desc(rojos)) %>%
    head(5)

  # Top 3 casos críticos
  top_casos <- df %>%
    arrange(desc(score)) %>%
    slice(1:3) %>%
    select(id_siniestro, score, nivel_riesgo, alertas)

  informe <- c(
    paste0(strrep("═", 60)),
    "INFORME EJECUTIVO - ANÁLISIS DE FRAUDE",
    "Sistema FraudIA - Detección de Posibles Fraudes en Seguros",
    paste0(strrep("═", 60)),
    "",
    "RESUMEN GENERAL",
    paste0(strrep("─", 60)),
    paste("Total de siniestros analizados:", total),
    paste("Score promedio de riesgo:", round(score_medio, 1), "(escala 0-100)"),
    paste("Score mediano:", round(score_mediano, 1)),
    "",
    "DISTRIBUCIÓN DE RIESGO",
    paste0(strrep("─", 60)),
    paste(sprintf("  🔴 ROJO (Crítico):     %3d casos (%5.1f%%) - Revisión especializada inmediata",
                  rojos, 100 * rojos / total)),
    paste(sprintf("  🟡 AMARILLO (Medio):   %3d casos (%5.1f%%) - Revisión documental recomendada",
                  amarillos, 100 * amarillos / total)),
    paste(sprintf("  🟢 VERDE (Normal):     %3d casos (%5.1f%%) - Procesamiento normal",
                  verdes, 100 * verdes / total)),
    "",
    "TOP 5 INDICADORES DE ALERTA DETECTADOS",
    paste0(strrep("─", 60)),
    {
      paste(sprintf("  %d. %s (%d casos)",
                    seq_along(indicadores),
                    names(indicadores),
                    as.numeric(indicadores)), collapse = "\n")
    },
    "",
    "ANÁLISIS GEOGRÁFICO (Top 5 Ciudades con Mayor Riesgo)",
    paste0(strrep("─", 60)),
    {
      aplicar_fmt_tabla <- function() {
        paste(apply(dist_ciudad, 1, function(row) {
          sprintf("  • %s: %d casos (%d ROJOS)", row["ciudad"], as.numeric(row["total"]), as.numeric(row["rojos"]))
        }), collapse = "\n")
      }
      tryCatch(aplicar_fmt_tabla(), error = function(e) "  (No hay datos geográficos disponibles)")
    },
    "",
    "ANÁLISIS DE PROVEEDORES (Top 5 con Mayor Alerta)",
    paste0(strrep("─", 60)),
    {
      aplicar_fmt_prov <- function() {
        paste(apply(dist_prov, 1, function(row) {
          sprintf("  • Proveedor %s: %d casos (%d ROJOS)",
                  row["proveedor"], as.numeric(row["total"]), as.numeric(row["rojos"]))
        }), collapse = "\n")
      }
      tryCatch(aplicar_fmt_prov(), error = function(e) "  (No hay datos de proveedores disponibles)")
    },
    "",
    "CASOS CRÍTICOS - TOP 3 PUNTUACIONES MÁS ALTAS",
    paste0(strrep("─", 60))
  )

  # Agregar casos críticos
  for (i in 1:nrow(top_casos)) {
    caso <- top_casos[i, ]
    informe <- c(
      informe,
      paste0("\n  Caso #", i, " - ID: ", caso$id_siniestro),
      paste0("  Score: ", caso$score, " (", caso$nivel_riesgo, ")"),
      paste0("  Indicadores: ", caso$alertas),
      ""
    )
  }

  informe <- c(
    informe,
    "ANÁLISIS DE TENDENCIAS",
    paste0(strrep("─", 60)),
    paste0("  • ", round(100 * rojos / total, 1), "% de casos requieren revisión especializada"),
    paste0("  • ", round(100 * amarillos / total, 1), "% de casos requieren revisión documental"),
    paste0("  • Concentración de riesgo: ",
           ifelse(rojos > total * 0.1, "ALTA (>10%)",
                  ifelse(rojos > total * 0.05, "MEDIA (5-10%)", "BAJA (<5%)"))),
    "",
    "RECOMENDACIONES",
    paste0(strrep("─", 60)),
    paste0("  1. Revisar inmediatamente los ", rojos, " casos ROJOS"),
    paste0("  2. Auditar indicador más frecuente: ", names(indicadores)[1]),
    paste0("  3. Investigar patrones en proveedores con mayor concentración de riesgos"),
    paste0("  4. Validar proceso de reporte en casos con demora >7 días"),
    "",
    paste0(strrep("═", 60)),
    paste("Reporte generado:", format(Sys.time(), "%Y-%m-%d %H:%M:%S")),
    paste0(strrep("═", 60))
  )

  return(paste(informe, collapse = "\n"))
}

# ============================================================
# 4. FUNCIÓN PRINCIPAL
# ============================================================

analizar_dataset <- function(ruta_csv, output_dir = "data/processed") {

  # Crear directorio de salida si no existe
  if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  }

  # 1. Leer CSV
  cat("[1/5] Leyendo archivo CSV...\n")
  df <- read_csv(ruta_csv, show_col_types = FALSE)

  # 2. Mapear columnas
  cat("[2/5] Detectando y mapeando columnas...\n")
  mapeo <- mapear_columnas(df)

  # Seleccionar columnas mapeadas
  cols_a_usar <- unlist(mapeo[!sapply(mapeo, is.null)])
  df <- df %>% select(all_of(cols_a_usar))
  names(df) <- names(mapeo)[!sapply(mapeo, is.null)]

  # 3. Limpiar datos
  cat("[3/5] Limpiando datos...\n")
  df <- procesar_tipos(df)
  df <- limpiar_valores_faltantes(df)

  # Agregar columnas por defecto si faltan
  if (!"ramo" %in% names(df)) {
    df$ramo <- "General"
  }
  if (!"ciudad" %in% names(df)) {
    df$ciudad <- "No especificada"
  }
  if (!"id_proveedor" %in% names(df)) {
    df$id_proveedor <- "No especificado"
  }

  # 4. Calcular scores de fraude
  cat("[4/5] Aplicando reglas de detección de fraude...\n")
  df <- calcular_score_fraude(df)

  # 5. Generar reportes
  cat("[5/6] Generando reportes...\n")

  # CSV limpio
  write_csv(df, file.path(output_dir, "cleaned_data.csv"))

  # Reporte de limpieza
  reporte_limpieza <- generar_reporte_limpieza(df, mapeo)
  writeLines(reporte_limpieza, file.path(output_dir, "cleaning_report.txt"))

  # Informe detallado de alertas
  informe_alertas <- generar_informe_alertas(df)
  writeLines(informe_alertas, file.path(output_dir, "alertas_detalle.txt"))

  # 6. Generar gráficos
  cat("[6/6] Generando gráficos...\n")
  graficos_dir <- generar_graficos(df, output_dir)

  cat("✅ Análisis completado exitosamente\n")
  cat("   📁 Archivos guardados en:", output_dir, "\n")
  cat("   📊 Gráficos generados en:", graficos_dir, "\n")

  return(list(
    data = df,
    cleaning_report = reporte_limpieza,
    fraud_report = informe_alertas,
    graficos_dir = graficos_dir
  ))
}

# ============================================================
# 5. PUNTO DE ENTRADA
# ============================================================

if (interactive()) {
  # Debugging mode
  message("Script de limpieza de datos FraudIA cargado.")
  message("Usar: analizar_dataset('ruta/archivo.csv')")
} else {
  # CLI mode - obtener ruta desde argumentos de línea de comandos
  args <- commandArgs(trailingOnly = TRUE)

  if (length(args) < 1) {
    cat("Uso: Rscript data_cleaner.R <ruta_archivo.csv> [output_dir]\n")
    quit(status = 1)
  }

  ruta_csv <- args[1]
  output_dir <- if (length(args) > 1) args[2] else "data/processed"

  if (!file.exists(ruta_csv)) {
    cat(sprintf("Error: Archivo no encontrado: %s\n", ruta_csv))
    quit(status = 1)
  }

  resultado <- analizar_dataset(ruta_csv, output_dir)
}

library(ggplot2)
library(dplyr)
library(readr)
library(jsonlite)

# Cargar datos
df <- read_csv("data/processed/siniestros_scored.csv")

# Crear carpeta de salida
dir.create("data/graficos", showWarnings = FALSE)

# GRAFICO 1: Distribucion de niveles de riesgo
g1 <- ggplot(df, aes(x = nivel_riesgo, fill = nivel_riesgo)) +
  geom_bar() +
  scale_fill_manual(values = c("ROJO" = "#E24B4A", "AMARILLO" = "#EF9F27", "VERDE" = "#4CAF50")) +
  labs(
    title = "Distribucion de Casos por Nivel de Riesgo",
    subtitle = "Sistema detector de posibles fraudes - Aseguradora del Sur",
    x = "Nivel de Riesgo",
    y = "Cantidad de Casos",
    fill = "Nivel"
  ) +
  theme_minimal() +
  theme(plot.title = element_text(face = "bold", size = 14))

ggsave("data/graficos/distribucion_riesgo.png", g1, width = 8, height = 5, dpi = 150)

# GRAFICO 2: Score por ramo
g2 <- ggplot(df, aes(x = reorder(ramo, score, median), y = score, fill = ramo)) +
  geom_boxplot(alpha = 0.7) +
  coord_flip() +
  labs(
    title = "Distribucion de Score de Riesgo por Ramo",
    x = "Ramo",
    y = "Score de Riesgo"
  ) +
  theme_minimal() +
  theme(legend.position = "none", plot.title = element_text(face = "bold", size = 14))

ggsave("data/graficos/score_por_ramo.png", g2, width = 8, height = 5, dpi = 150)

# GRAFICO 3: Top proveedores con mas alertas rojas
top_proveedores <- df %>%
  filter(nivel_riesgo == "ROJO") %>%
  group_by(beneficiario) %>%
  summarise(casos_rojos = n()) %>%
  arrange(desc(casos_rojos)) %>%
  head(8)

g3 <- ggplot(top_proveedores, aes(x = reorder(beneficiario, casos_rojos), y = casos_rojos, fill = casos_rojos)) +
  geom_col() +
  coord_flip() +
  scale_fill_gradient(low = "#EF9F27", high = "#E24B4A") +
  labs(
    title = "Proveedores con Mayor Concentracion de Alertas Rojas",
    x = "Proveedor",
    y = "Casos Rojos",
    fill = "Casos"
  ) +
  theme_minimal() +
  theme(plot.title = element_text(face = "bold", size = 14))

ggsave("data/graficos/top_proveedores.png", g3, width = 8, height = 5, dpi = 150)

# GRAFICO 4: Alertas por ciudad
alertas_ciudad <- df %>%
  filter(nivel_riesgo %in% c("ROJO", "AMARILLO")) %>%
  group_by(ciudad, nivel_riesgo) %>%
  summarise(casos = n(), .groups = "drop")

g4 <- ggplot(alertas_ciudad, aes(x = reorder(ciudad, casos), y = casos, fill = nivel_riesgo)) +
  geom_col(position = "stack") +
  coord_flip() +
  scale_fill_manual(values = c("ROJO" = "#E24B4A", "AMARILLO" = "#EF9F27")) +
  labs(
    title = "Concentracion de Alertas por Ciudad",
    x = "Ciudad",
    y = "Casos Sospechosos",
    fill = "Nivel"
  ) +
  theme_minimal() +
  theme(plot.title = element_text(face = "bold", size = 14))

ggsave("data/graficos/alertas_ciudad.png", g4, width = 8, height = 5, dpi = 150)

cat("Graficos generados exitosamente en data/graficos/\n")
cat("Total graficos: 4\n")
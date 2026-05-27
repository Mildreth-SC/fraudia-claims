import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv
import os

load_dotenv()

def entrenar_modelo(df):
    features = [
        'monto_reclamado',
        'dias_desde_inicio_poliza',
        'dias_entre_ocurrencia_reporte',
        'historial_siniestros_asegurado',
        'suma_asegurada'
    ]
    
    X = df[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    modelo = IsolationForest(
        contamination=0.15,
        random_state=42,
        n_estimators=100
    )
    modelo.fit(X_scaled)
    
    df['anomalia_score'] = modelo.decision_function(X_scaled)
    df['es_anomalia'] = modelo.predict(X_scaled)
    df['es_anomalia'] = df['es_anomalia'].map({-1: 1, 1: 0})
    
    return df, modelo, scaler

def evaluar_modelo(df):
    if 'etiqueta_fraude_simulada' not in df.columns:
        return
    
    from sklearn.metrics import classification_report, roc_auc_score
    
    print("\n=== MÉTRICAS DEL MODELO ===")
    print(classification_report(
        df['etiqueta_fraude_simulada'],
        df['es_anomalia'],
        target_names=['Normal','Posible Fraude']
    ))
    
    try:
        auc = roc_auc_score(df['etiqueta_fraude_simulada'], -df['anomalia_score'])
        print(f"AUC-ROC: {round(auc, 3)}")
    except:
        pass

if __name__ == "__main__":
    df = pd.read_csv("data/processed/siniestros_scored.csv")
    print("Entrenando modelo Isolation Forest...")
    df, modelo, scaler = entrenar_modelo(df)
    evaluar_modelo(df)
    df.to_csv("data/processed/siniestros_scored.csv", index=False)
    print(f"\nAnomalías detectadas: {df['es_anomalia'].sum()}")
    print("✅ Modelo entrenado y guardado")
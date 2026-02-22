import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
from db_connection import get_db_connection

# Carregar variáveis de ambiente
load_dotenv()

def ingest_brfss(csv_path):
    if not os.path.exists(csv_path):
        print(f"Erro: O ficheiro {csv_path} não foi encontrado.")
        return

    print("A carregar dataset BRFSS... (isto pode demorar dependendo do tamanho)")
    # low_memory=False é importante devido à mistura de tipos nas centenas de colunas
    df = pd.read_csv(csv_path, low_memory=False)

    # Mapeamento completo baseado no teu schema de diagnósticos e indicadores
    cols_map = {
        '_state': 'state_code',
        'seqno': 'sequence_no',
        
        # Diagnósticos (Doenças)
        'diabete4': 'diagnosed_diabetes',
        'asthma3': 'diagnosed_asthma',
        'asthnow': 'asthma_now',
        'cvdstrk3': 'diagnosed_stroke',
        'cvdinfr4': 'diagnosed_heart_attack',
        'cvdcrhd4': 'diagnosed_heart_dis',
        'chccopd3': 'diagnosed_copd',
        'addepev3': 'diagnosed_depressive',
        'chckdny2': 'diagnosed_kidney_dis',
        'havarth4': 'diagnosed_arthritis',
        'chcscnc1': 'diagnosed_skin_cancer',
        'chcocnc1': 'diagnosed_other_cancer',
        
        # Fatores de Risco e Prevenção
        'bphigh6': 'high_blood_pressure',
        'toldhi3': 'high_cholesterol',
        'smoke100': 'smoke_100',
        '_rfbing6': 'alcohol_binge',
        'exerany2': 'exercise_any',
        
        # Auto-avaliação e Biometria
        'genhlth': 'general_health',
        'physhlth': 'physical_health_days',
        'menthlth': 'mental_health_days',
        'wtkg3': 'weight_kg',
        'htm4': 'height_cm',
        '_bmi5': 'bmi'
    }

    # Filtrar apenas as colunas que realmente existem no ficheiro
    available_cols = [c for c in cols_map.keys() if c in df.columns]
    df_final = df[available_cols].rename(columns=cols_map)

    print(f"Campos mapeados: {len(df_final.columns)} de {len(cols_map)}")

    # --- Limpeza e Transformação de Dados ---

    # 1. O BRFSS armazena IMC e Peso com duas casas decimais implícitas (ex: 2856 significa 28.56)
    if 'bmi' in df_final.columns:
        df_final['bmi'] = pd.to_numeric(df_final['bmi'], errors='coerce') / 100
    
    if 'weight_kg' in df_final.columns:
        df_final['weight_kg'] = pd.to_numeric(df_final['weight_kg'], errors='coerce') / 100

    # 2. Converter outras colunas para numérico (tratar strings vazias ou erros)
    for col in df_final.columns:
        if col not in ['bmi', 'weight_kg']:
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce')

    # 3. No BRFSS, 7 e 9 costumam significar "Não sabe" ou "Recusou". 
    # Dependendo da análise, podes querer manter ou transformar em NULL.
    # Aqui substituímos NaNs por None para o psycopg2 inserir como NULL.
    df_final = df_final.replace({np.nan: None})

    # --- Inserção na Base de Dados ---
    
    conn = get_db_connection()
    cur = conn.cursor()

    columns = list(df_final.columns)
    insert_query = f"""
        INSERT INTO brfss_responses ({', '.join(columns)}) 
        VALUES %s 
        ON CONFLICT (sequence_no) DO NOTHING
    """

    # Converter para lista de tuplos
    data_tuples = [tuple(x) for x in df_final.to_numpy()]

    try:
        execute_values(cur, insert_query, data_tuples)
        conn.commit()
        print(f"Sucesso! {len(df_final)} registos processados na tabela brfss_responses.")
    except Exception as e:
        conn.rollback()
        print(f"Erro na ingestão: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Substitui pelo nome correto do teu ficheiro CSV
    ingest_brfss('/Users/matildefernandes/Desktop/PEC/BRFSS2023.csv')
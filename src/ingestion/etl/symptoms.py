"""ETL de sintomas/doenças: ficheiros CSV para PostgreSQL (doenças, sintomas, mapeamentos, precauções)."""

import pandas as pd
from dotenv import load_dotenv

from db_connection import get_db_connection

load_dotenv()


def ingest_data(
    symptom_description_path="symptom_Description.csv",
    symptom_precaution_path="symptom_precaution.csv",
    symptom_severity_path="Symptom-severity.csv",
    dataset_path="dataset.csv",
):
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Carregar CSVs
    df_desc = pd.read_csv(symptom_description_path)
    df_prec = pd.read_csv(symptom_precaution_path)
    df_sev = pd.read_csv(symptom_severity_path)
    df_mapping = pd.read_csv(dataset_path)

    # 2. Ingestão de doenças e descrições
    for _, row in df_desc.iterrows():
        cur.execute(
            (
                "INSERT INTO diseases (name, description) "
                "VALUES (%s, %s) "
                "ON CONFLICT (name) DO NOTHING"
            ),
            (row["Disease"].strip(), row["Description"]),
        )

    # 3. Ingestão de sintomas e respetivas severidades
    for _, row in df_sev.iterrows():
        cur.execute(
            (
                "INSERT INTO symptoms (name, severity_weight)"
                " VALUES (%s, %s) "
                "ON CONFLICT (name) DO NOTHING",
            ),
            (row["Symptom"].strip().replace("_", " "), row["weight"]),
        )

    # 4. Ingestão dos mapeamentos doença‑sintoma
    for _, row in df_mapping.iterrows():
        disease_name = row["Disease"].strip()
        cur.execute("SELECT disease_id FROM diseases WHERE name = %s", (disease_name,))
        res = cur.fetchone()
        if res:
            disease_id = res[0]
            for i in range(1, 18):
                s_name = row[f"Symptom_{i}"]
                if pd.notna(s_name):
                    s_name = s_name.strip().replace("_", " ")
                    cur.execute("SELECT symptom_id FROM symptoms WHERE name = %s", (s_name,))
                    s_res = cur.fetchone()
                    if s_res:
                        cur.execute(
                            (
                                "INSERT INTO disease_symptoms (disease_id, symptom_id) "
                                "VALUES (%s, %s) "
                                "ON CONFLICT DO NOTHING"
                            ),
                            (disease_id, s_res[0]),
                        )

    # 5. Ingestão de precauções
    for _, row in df_prec.iterrows():
        cur.execute("SELECT disease_id FROM diseases WHERE name = %s", (row["Disease"].strip(),))
        res = cur.fetchone()
        if res:
            d_id = res[0]
            for i in range(1, 5):
                prec = row[f"Precaution_{i}"]
                if pd.notna(prec):
                    cur.execute(
                        "INSERT INTO disease_precautions (disease_id, precaution) VALUES (%s, %s)",
                        (d_id, prec),
                    )

    conn.commit()
    cur.close()
    conn.close()
    print("Ingestão concluída com sucesso!")


if __name__ == "__main__":
    ingest_data()

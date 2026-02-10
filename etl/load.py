from utils.db import get_connection

def load_to_postgres(df):
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO records (source, title, value, created_at)
            VALUES (%s, %s, %s, %s)
            """,
            (
                row.get("source"),
                row.get("title"),
                row.get("value"),
                row.get("created_at"),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()

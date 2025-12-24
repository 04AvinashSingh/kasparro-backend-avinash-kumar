import csv
import psycopg2
import json

conn = psycopg2.connect(
    host="db",
    database="kasparro_db",
    user="postgres",
    password="avinash79"
)
cursor = conn.cursor()

with open("data/assets.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Save raw CSV data
        cursor.execute(
            "INSERT INTO raw_csv_assets (data) VALUES (%s)",
            [json.dumps(row)]
        )

        # Save clean data
        cursor.execute(
            """
            INSERT INTO assets (symbol, name, price_usd, source)
            VALUES (%s, %s, %s, %s)
            """,
            (
                row["symbol"],
                row["name"],
                row["price"],
                "csv"
            )
        )

conn.commit()
cursor.close()
conn.close()

print("CSV ETL completed")

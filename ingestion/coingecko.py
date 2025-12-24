import requests
import psycopg2
import json


conn = psycopg2.connect(
    host="db",
    database="kasparro_db",
    user="postgres",
    password="avinash79"
)

cursor = conn.cursor()

url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "per_page": 5
}

response = requests.get(url, params=params)
coins = response.json()
for coin in coins:
    cursor.execute(
        "INSERT INTO raw_coingecko (data) VALUES (%s)",
        [json.dumps(coin)]
    )


for coin in coins:
    cursor.execute(
        """
        INSERT INTO assets (symbol, name, price_usd, source)
        VALUES (%s, %s, %s, %s)
        """,
        (
            coin["symbol"],
            coin["name"],
            coin["current_price"],
            "coingecko"
        )
    )
conn.commit()
cursor.close()
conn.close()

print("ETL finished successfully")

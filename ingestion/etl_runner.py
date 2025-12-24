import time
import subprocess

def run_etl_periodically(interval_seconds=300):
    while True:
        try:
            subprocess.run(
                ["python", "/app/ingestion/csv_weird_loader.py"],
                check=True
            )
        except Exception as e:
            print("ETL failed:", e)

        time.sleep(interval_seconds)

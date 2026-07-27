import csv
import json
import os
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.nseindia.com"
PAGE_URL = "https://www.nseindia.com/products-services/indices-nifty50"

DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "nifty50.csv")
JSON_FILE = os.path.join(DATA_DIR, "nifty50.json")


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/127.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
}


class NSERobot:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        os.makedirs(DATA_DIR, exist_ok=True)

    def discover_csv(self):

        page = self.session.get(PAGE_URL, timeout=30)
        page.raise_for_status()

        soup = BeautifulSoup(page.text, "html.parser")

        for link in soup.find_all("a", href=True):

            href = link["href"]

            if ".csv" in href.lower():
                return urljoin(BASE_URL, href)

        raise Exception("CSV download link not found.")

    def download_csv(self):

        csv_url = self.discover_csv()

        print("Downloading")
        print(csv_url)

        response = self.session.get(csv_url, timeout=60)
        response.raise_for_status()

        with open(CSV_FILE, "wb") as f:
            f.write(response.content)

        print("CSV saved")

    def csv_to_json(self):

        companies = []

        with open(CSV_FILE, newline="", encoding="utf-8-sig") as f:

            reader = csv.DictReader(f)

            for row in reader:
                companies.append(dict(row))

        data = {
            "updated": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "count": len(companies),
            "companies": companies,
        }

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print("JSON saved")

    def run(self):

        self.download_csv()

        self.csv_to_json()

        print()

        print("Done")
        print(f"Companies : {len(json.load(open(JSON_FILE))['companies'])}")


if __name__ == "__main__":
    NSERobot().run()

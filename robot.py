from __future__ import annotations

import csv
import json
import os
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.nseindia.com"
NIFTY50_PAGE_URL = "https://www.nseindia.com/static/products-services/indices-nifty50-index"
KNOWN_CSV_URL = "https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv"

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "nifty50.csv")
JSON_PATH = os.path.join(DATA_DIR, "nifty50.json")

IST = ZoneInfo("Asia/Kolkata")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "keep-alive",
    "Referer": BASE_URL,
}


def _now_ist() -> datetime:
    return datetime.now(tz=IST)


def _ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


class NSENifty50Robot:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def warm_up(self) -> None:
        """Prime cookies/session with the official NSE page."""
        response = self.session.get(NIFTY50_PAGE_URL, timeout=30)
        response.raise_for_status()

    def discover_csv_url(self) -> str:
        """Find the current official CSV link from the NSE page, with a safe fallback."""
        self.warm_up()

        response = self.session.get(NIFTY50_PAGE_URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for anchor in soup.select("a[href]"):
            href = anchor.get("href", "")
            if not href:
                continue

            text = _clean_text(anchor.get_text(" ", strip=True)).lower()
            href_l = href.lower()

            if href_l.endswith(".csv") and (
                "nifty 50" in text or "nifty50" in text or "stocks" in text
            ):
                return urljoin(BASE_URL, href)

        return KNOWN_CSV_URL

    def download_csv(self) -> str:
        csv_url = self.discover_csv_url()

        response = self.session.get(csv_url, timeout=60)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        body_preview = response.text[:200] if hasattr(response, "text") else ""

        if "csv" not in content_type and "text" not in content_type and "," not in body_preview:
            raise RuntimeError(f"Unexpected CSV response from {csv_url!r}")

        with open(CSV_PATH, "wb") as f:
            f.write(response.content)

        return csv_url

    def csv_to_json(self, csv_url: str) -> dict:
        rows: list[dict[str, str]] = []

        with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            fieldnames = reader.fieldnames or []

            for raw_row in reader:
                if not raw_row:
                    continue

                row = {
                    str(k).strip(): _clean_text(str(v))
                    for k, v in raw_row.items()
                    if k is not None
                }

                if any(value for value in row.values()):
                    rows.append(row)

        payload = {
            "dataset": "NSE Nifty 50",
            "source_page": NIFTY50_PAGE_URL,
            "source_csv_url": csv_url,
            "updated_ist": _now_ist().strftime("%d %b %Y, %I:%M %p IST"),
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "count": len(rows),
            "columns": fieldnames if fieldnames else (list(rows[0].keys()) if rows else []),
            "rows": rows,
        }

        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return payload

    def run(self) -> dict:
        _ensure_dirs()
        csv_url = self.download_csv()
        payload = self.csv_to_json(csv_url)
        print(f"Downloaded CSV: {csv_url}")
        print(f"Rows: {payload['count']}")
        print(f"JSON saved: {JSON_PATH}")
        return payload


if __name__ == "__main__":
    NSENifty50Robot().run()

# Lensor V2

Static GitHub Pages dashboard for the official NSE Nifty 50 CSV.

## What it does
- Python robot downloads the official NSE Nifty 50 CSV
- Converts CSV to `data/nifty50.json`
- Static front end renders the table in the browser
- GitHub Actions refresh the data daily at 6:30 PM IST
- GitHub Pages serves the site from the repository branch

## Files
- `robot.py` — NSE downloader and CSV → JSON converter
- `index.html` — static page
- `style.css` — dashboard styling
- `script.js` — loads JSON and renders the table
- `.github/workflows/update-data.yml` — scheduled refresh

## Local test
```bash
pip install -r requirements.txt
python robot.py

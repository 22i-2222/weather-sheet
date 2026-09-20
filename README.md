# Weather -> Google Sheet (every 30s)

## 1. Google setup
1. Google Cloud Console -> new project -> enable **Google Sheets API**.
2. IAM & Admin -> Service Accounts -> create one -> Keys -> Add key -> JSON. Download it.
3. Create a Google Sheet. Share it (Editor) with the service account's `client_email`.
4. Copy the sheet ID from the URL: `docs.google.com/spreadsheets/d/<SHEET_ID>/edit`

## 2. GitHub
```
git init
git add .
git commit -m "weather sheet worker"
git branch -M main
git remote add origin https://github.com/<you>/weather-sheet.git
git push -u origin main
```
Do NOT commit the service account JSON.

## 3. Railway
1. New Project -> Deploy from GitHub repo -> pick this repo.
2. Variables tab, add:
   - `GOOGLE_CREDENTIALS` = entire contents of the JSON file (paste it as one value)
   - `SHEET_ID` = your sheet id
   - `LAT` = e.g. 33.6844
   - `LON` = e.g. 73.0479
   - optional: `WORKSHEET` (default Sheet1), `INTERVAL_SECONDS` (default 30), `MODE` (`append` or `update`)
3. Deploy. Check the Logs tab, you should see "written: ..." every 30s.

## Notes
- Open-Meteo refreshes its "current" data about every 15 min, so consecutive rows can look identical. That's the source, not a bug.
- `append` adds ~2,880 rows/day. Google Sheets caps at 10M cells, so use `MODE=update` if this runs for months.

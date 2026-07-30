# LinkedIn Company Enrichment Scraper

Selenium pipeline that reads LinkedIn profile URLs from Excel, opens each profile’s experience, and enriches the workbook with the first company’s About fields.

> **Important:** Automating LinkedIn may violate [LinkedIn’s User Agreement](https://www.linkedin.com/legal/user-agreement). Use only on accounts/data you are authorized to process, keep volumes low, and prefer official APIs when available. This tool is for controlled internal enrichment — not bulk harvesting.

## Features

- Modular package (`linkedin_scraper/`) instead of one giant script
- Credentials via `.env` (never hardcoded)
- Resume: skips rows that already have company data
- Atomic Excel saves + Ctrl+C graceful stop
- Fallback XPath strategies (LinkedIn DOM changes often)
- CLI: `status` / `run` / `doctor`
- Optional persistent Chrome profile for fewer re-logins
- Structured logging to console + `logs/scraper.log`

## Setup

```bash
cd linkeDIn_scraping
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with LINKEDIN_EMAIL / LINKEDIN_PASSWORD
```

Place (or keep) your workbook at `data/scalezia.xlsx`. On first run, the CLI copies root `scalezia.xlsx` there if needed.

### Expected columns

Required:

- `linkedIn` — profile URL

Written / updated:

- `Link_Linkdin_company`
- `company_name`, `Phone`, `Website`, `Industry`, `Company size`, `Headquarters`, `Founded`, `Specialties`

## Usage

```bash
# Coverage
python main.py status

# Dry-run: see which rows would be processed
python main.py run --dry-run --limit 20

# Smoke test (3 pending rows, visible browser — complete CAPTCHA/2FA if asked)
python main.py run --limit 3

# Batch from index 256, max 50 rows
python main.py run --start 256 --limit 50

# Reprocess everything in a range
python main.py run --start 0 --end 100 --all

# Headless (often blocked by LinkedIn login challenges — prefer headed)
python main.py run --limit 5 --headless
```

### Warm Chrome session (recommended)

Set in `.env`:

```env
CHROME_PROFILE_DIR=.chrome_profile
```

Log in once with the browser UI; later runs reuse cookies.

## Config (env)

| Variable | Default | Meaning |
|---|---|---|
| `LINKEDIN_EMAIL` | — | Account email |
| `LINKEDIN_PASSWORD` | — | Account password |
| `HEADLESS` | `false` | Headless Chrome |
| `SAVE_EVERY` | `5` | Checkpoint every N rows |
| `MIN_DELAY` / `MAX_DELAY` | `2` / `5` | Random pause range (seconds) |
| `PAGE_TIMEOUT` | `20` | Element wait timeout |
| `MANUAL_LOGIN_WAIT` | `90` | Seconds to finish CAPTCHA/2FA |
| `CHROME_PROFILE_DIR` | — | Persistent Chrome user-data dir |

## Project layout

```
linkeDIn_scraping/
├── main.py                 # CLI entry
├── requirements.txt
├── .env.example
├── data/                   # Excel workbooks
├── logs/                   # scraper.log
├── linkedin_scraper/
│   ├── config.py
│   ├── browser.py
│   ├── auth.py
│   ├── profile.py
│   ├── company.py
│   ├── excel_store.py
│   ├── pipeline.py
│   └── selectors.py        # XPath fallbacks — edit here when DOM breaks
└── legacy/                 # previous scripts (reference only)
```

## When LinkedIn breaks selectors

Edit `linkedin_scraper/selectors.py` and add new XPaths at the **front** of each list. Keep old ones as fallbacks.

## Security

- Never commit `.env`
- Rotate any passwords that were previously hardcoded in old scripts
- Treat Excel exports as sensitive PII

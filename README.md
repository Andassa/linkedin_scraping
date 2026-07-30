# LinkedIn company enrichment

Reads profile URLs from an Excel workbook, opens each experience section, and fills company About fields for the first employer.

Automating LinkedIn can breach their [User Agreement](https://www.linkedin.com/legal/user-agreement). Use only on data you are allowed to process; prefer the official API when possible.

## Setup

```bash
cd linkeDIn_scraping
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` in `.env`.

Workbook path: `data/scalezia.xlsx`. If missing, the CLI copies a root `scalezia.xlsx` into `data/` on first run.

### Columns

| Role | Name |
|------|------|
| Input | `linkedIn` |
| Output | `Link_Linkdin_company`, `company_name`, `Phone`, `Website`, `Industry`, `Company size`, `Headquarters`, `Founded`, `Specialties` |

Rows that already have a company link or name are skipped unless `--all` is set.

## Commands

```bash
python main.py status
python main.py doctor
python main.py run --dry-run --limit 20
python main.py run --limit 3
python main.py run --start 256 --limit 50
python main.py run --start 0 --end 100 --all
python main.py run --limit 5 --headless
```

Headless login often hits LinkedIn challenges; prefer a visible browser. For CAPTCHA/2FA, leave Chrome open until login completes.

Persistent session (optional) in `.env`:

```env
CHROME_PROFILE_DIR=.chrome_profile
```

Log in once; later runs reuse the profile cookies.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `LINKEDIN_EMAIL` | — | Account email |
| `LINKEDIN_PASSWORD` | — | Account password |
| `HEADLESS` | `false` | Headless Chrome |
| `SAVE_EVERY` | `5` | Checkpoint interval (rows) |
| `MIN_DELAY` / `MAX_DELAY` | `2` / `5` | Pause range (seconds) |
| `PAGE_TIMEOUT` | `20` | Wait timeout (seconds) |
| `MANUAL_LOGIN_WAIT` | `90` | Time allowed for CAPTCHA/2FA |
| `CHROME_PROFILE_DIR` | — | Chrome user-data directory |

## Layout

```
linkeDIn_scraping/
├── main.py
├── requirements.txt
├── .env.example
├── data/
├── logs/
├── linkedin_scraper/
│   ├── config.py
│   ├── browser.py
│   ├── auth.py
│   ├── profile.py
│   ├── company.py
│   ├── excel_store.py
│   ├── pipeline.py
│   └── selectors.py
└── legacy/
```

If LinkedIn changes the DOM, update XPaths in `linkedin_scraper/selectors.py` (prepend new selectors; keep existing ones as fallbacks).

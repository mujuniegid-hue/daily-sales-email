# Daily Sales Email Summary

Automated end-of-day sales report for small retail shops. The script reads the day's sales from a CSV file and emails the shop owner a clean HTML summary, so he never has to open a spreadsheet.

Built by **HamTech Ltd**

---

## The problem

A shop owner in Kampala wants to know how the day went without sitting down with spreadsheets. His cashier already records every sale in a CSV file. This tool turns that file into a short email he can read on his phone in seconds.

## What the email shows

| Metric | Description |
|---|---|
| **Total revenue** | Sum of quantity x price across all sales, in UGX |
| **Number of transactions** | Count of sales recorded |
| **Top-selling item** | The item with the highest total quantity sold |
| **Restock alert** | Every item whose remaining stock is below the restock level, highlighted in red. If nothing is low, the email says so |

### Example result (from the included sample data)

| Metric | Value |
|---|---|
| Total revenue | UGX 163,500 |
| Transactions | 14 |
| Top-selling item | Soda 500ml (16 sold) |
| Restock alert | Bread loaf (3 left), Bottled water 1.5L (3 left), Eggs tray (4 left) |

## How it works

1. `report.py` reads `sales.csv` using Python's built-in `csv` module.
2. It calculates the four metrics.
3. It builds an HTML email (with a plain-text fallback).
4. It logs in to Gmail over SMTP using an **app password** and sends the email.

Credentials are never written in the code. They are read from a private `.env` file that is excluded from Git.

## Tech stack

- Python 3
- Standard library: `csv`, `smtplib`, `email`, `html`, `os`, `datetime`
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) for loading credentials
- Gmail SMTP (`smtp.gmail.com`)

## Project structure

```
shop-sales-email/
|-- report.py      # calculates metrics, builds the email, sends it
|-- sales.csv      # sample sales data
|-- .env           # private credentials (NOT uploaded to GitHub)
|-- .gitignore     # keeps .env out of Git
`-- README.md
```

## Sales file format

`sales.csv` has one row per transaction:

```csv
item,quantity,price,stock_left
Sugar 1kg,2,5000,20
Bread loaf,3,3500,10
```

| Column | Meaning |
|---|---|
| `item` | Product name |
| `quantity` | Units sold in that transaction |
| `price` | Price per unit in UGX (digits only, no commas) |
| `stock_left` | Stock remaining after that sale |

## Setup

### 1. Install Python and the dependency

```bash
pip install python-dotenv
```

### 2. Create a Gmail app password

An app password is a separate 16-character password that works only for scripts, so your real Gmail password is never used.

1. Turn on **2-Step Verification** in your Google Account (Security settings).
2. Open **App passwords** in your Google Account and create one named `shop-sales-email`.
3. Copy the 16 characters shown. Google displays them only once.

### 3. Create the `.env` file

Create a file named `.env` in the project folder. Use no spaces around `=`, no quotes, and no spaces inside the password:

```
GMAIL_ADDRESS=your_gmail_address
GMAIL_APP_PASSWORD=your_16_character_app_password
RECIPIENT_EMAIL=where_to_send_the_report
```

### 4. Run it

```bash
python report.py
```

On success the terminal prints `Email sent to <recipient>`, and the summary arrives in the recipient's inbox (check Spam on the first run).

## Security

- `.env` is listed in `.gitignore` and must never be committed.
- Only the app password is stored, never the main Gmail password.
- If an app password is ever exposed, delete it in your Google Account and create a new one. Removing the file from GitHub is not enough, because it stays in Git history.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Missing details in .env file` | `.env` is missing, misnamed, or a setting name is misspelled | Keep `.env` next to `report.py`; check the three setting names |
| `SMTPAuthenticationError 535` | Gmail rejects the address and app password pair | Create a fresh app password for the same Gmail address |
| `SMTPServerDisconnected: Connection unexpectedly closed` | Often a hidden 535 rejection (Python retries another login method and Gmail hangs up) | Create a fresh app password; test the login on its own before blaming the network |
| `ValueError: invalid literal for int()` | A blank or non-numeric cell in `sales.csv` | Check every row has numbers, with no stray commas or spaces |
| Email not in inbox | Filtered to Spam, or wrong recipient | Check Spam and `RECIPIENT_EMAIL` |

## Assumptions and limitations

- Each CSV row is one transaction.
- `stock_left` is the stock after that sale, and rows are in time order, so the last row for an item holds its latest stock.
- The restock level is **5**: items with stock **below** 5 are flagged. Change `RESTOCK_LEVEL` in `report.py` (use `<=` instead of `<` to flag items at exactly 5).
- The script runs once when executed. The **6pm daily schedule** is set up on the client's computer at deployment (for example with Windows Task Scheduler) and is part of the setup service below. The computer must be on and online at that time.
- Gmail limits how many emails an account can send per day. This is far above what a once-a-day report needs.

---
## Setup (3 steps)

**Before you start:** install [Python 3](https://www.python.org/downloads/) (tick "Add Python to PATH") and create a Gmail app password.

1. **Install the one library:** open a terminal in this folder and run `pip install python-dotenv`
2. **Add your details:** copy `.env.example` to `.env` and fill in your Gmail address, app password and recipient email.
3. **Schedule it:** double-click `setup_schedule.bat`. The report now sends daily at 6pm.

**Check that it works:** run `python report.py` once. A new line appears in `run_log.txt`.

## Reading the log

Each run adds one line to `run_log.txt`:

`2026-11-12 | 18:00:02 | success | rows=14`

Format: date, time, status (`success` or `error`), rows processed. See `sample_run_log.txt` for an example.

## Limits

- The computer must be on at 6pm.
- Change the time by editing `18:00` in `setup_schedule.bat` and running it again.

## Commercial offer: what I would charge a shop owner

*Prices are my proposal, in Ugandan shillings, reviewed November 2026. They are estimates based on published Ugandan freelance rate ranges, not a guarantee of what any client will pay.*

### Recommendation: a one-off setup fee plus an optional monthly care plan

| | Price | What it covers |
|---|---|---|
| **One-off setup** | **UGX 350,000** | Installing and configuring the tool on the shop's computer, connecting it to the cashier's CSV, creating the Gmail app password, scheduling the daily 6pm send, testing with real data, a 30-minute walkthrough for the owner, and 30 days of free support |
| **Monthly care plan** (optional) | **UGX 60,000 / month** | Fixing the tool if Gmail credentials or the CSV layout change, small adjustments (for example, changing the restock level or the recipient list), up to one hour of changes per month, and phone or WhatsApp support |
| **Extra work** | UGX 30,000 / hour | New metrics, extra recipients, weekly or monthly reports, or connecting to a POS system |

**Payment terms:** 50% before work starts and 50% on delivery. Mobile money or bank transfer.

**Year-one cost to the shop owner:** UGX 350,000 setup + 12 x UGX 60,000 care = **UGX 1,070,000**, or **UGX 350,000** if he skips the care plan.

### How the price was worked out

- **Hourly rate:** about **UGX 30,000 per hour**. Published Ugandan freelance guides place beginner developers at roughly UGX 20,000 to 40,000 per hour and juniors at UGX 40,000 to 80,000, so I price at the upper part of the beginner band because this is a finished, tested tool and not a quote for raw hours.
- **Setup effort:** about 10 hours (configuration, Gmail setup, scheduling, testing, owner walkthrough) = UGX 300,000, plus UGX 50,000 for travel, buffer, and the 30-day support window = **UGX 350,000**.
- **Market check:** entry-level website projects in Uganda are commonly quoted between roughly UGX 500,000 and 1,500,000, and entry-level monthly social media management between UGX 150,000 and 300,000. A small single-purpose automation sits below a website, and the care plan sits well below a monthly service that involves daily content work.

### Why not one-off only, or retainer only?

**A one-off fee alone** leaves the work unpaid when things inevitably change: Gmail passwords get revoked, the cashier renames a CSV column, or the shop buys a new computer. The client would still expect it to keep working.

**A retainer alone** is a hard sell to a small shop. The owner has not yet seen the value, and a monthly bill for something invisible feels like a risk. A clear one-off price for a clear result is easier to say yes to.

**The hybrid** lets the owner buy once, see the email arrive every evening, and then choose ongoing protection. It also gives me predictable income from clients who value reliability.

### How the value is explained to the client

- It replaces the daily chore of opening the sales file and adding things up. Even 15 minutes a day is about 7 hours a month of the owner's time.
- The restock alert shows low stock before the shelf is empty, so he can reorder in time and avoid lost sales.
- The owner sees the day's result without being in the shop.

These benefits depend on the shop's own data and habits, so I do not promise a specific saving or return.

### Prototype versus client-ready

This repository is a working prototype. Before selling it to a real shop I would add:

- Automatic scheduling and logging, so failures are visible
- An email alert to me if the report fails to send
- Input checks for a blank or malformed CSV
- A one-page user guide for the owner

---

## License

Provided for learning and portfolio demonstration.
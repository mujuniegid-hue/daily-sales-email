import csv
import html
import os
import smtplib
from datetime import date, datetime
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

# Full addresses, so the script works no matter where the scheduler starts it
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "sales.csv"
LOG_FILE = BASE_DIR / "run_log.txt"

load_dotenv(BASE_DIR / ".env")

RESTOCK_LEVEL = 5


def calculate_metrics(filename):
    total_revenue = 0
    transactions = 0
    quantity_by_item = {}
    stock_by_item = {}

    with open(filename, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            item = row["item"]
            quantity = int(row["quantity"])
            price = int(row["price"])
            stock_left = int(row["stock_left"])

            total_revenue += quantity * price
            transactions += 1
            quantity_by_item[item] = quantity_by_item.get(item, 0) + quantity
            stock_by_item[item] = stock_left

    top_item = max(quantity_by_item, key=quantity_by_item.get)
    top_quantity = quantity_by_item[top_item]

    low_stock = {
        item: stock
        for item, stock in stock_by_item.items()
        if stock < RESTOCK_LEVEL
    }

    return {
        "total_revenue": total_revenue,
        "transactions": transactions,
        "top_item": top_item,
        "top_quantity": top_quantity,
        "low_stock": low_stock,
    }


def build_html_email(metrics, report_date):
    if metrics["low_stock"]:
        list_items = ""
        for item, stock in metrics["low_stock"].items():
            list_items += f"<li>{html.escape(item)}: only <b>{stock}</b> left</li>"
        restock_html = f'<ul style="color:#b00020;">{list_items}</ul>'
    else:
        restock_html = "<p>All items are above the restock level.</p>"

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #222;">
        <h2>Daily Sales Summary: {report_date}</h2>
        <table style="border-collapse: collapse; width: 100%; max-width: 480px;">
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Total revenue</td>
            <td style="padding: 8px; border: 1px solid #ddd;"><b>UGX {metrics['total_revenue']:,}</b></td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Number of transactions</td>
            <td style="padding: 8px; border: 1px solid #ddd;"><b>{metrics['transactions']}</b></td>
          </tr>
          <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Top-selling item</td>
            <td style="padding: 8px; border: 1px solid #ddd;"><b>{html.escape(metrics['top_item'])}</b> ({metrics['top_quantity']} sold)</td>
          </tr>
        </table>
        <h3>Restock alert (below {RESTOCK_LEVEL})</h3>
        {restock_html}
      </body>
    </html>
    """


def send_email(subject, html_body):
    sender = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL")

    # Collect the NAMES of any missing settings (never print the values)
    missing = [
        name
        for name, value in [
            ("GMAIL_ADDRESS", sender),
            ("GMAIL_APP_PASSWORD", password),
            ("RECIPIENT_EMAIL", recipient),
        ]
        if not value
    ]
    if missing:
        raise ValueError("Missing in .env file: " + ", ".join(missing))

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content("Your email app cannot show HTML. Please open this email in Gmail.")
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(message)

    print(f"Email sent to {recipient}")


def write_log(status, rows):
    now = datetime.now()
    line = f"{now:%Y-%m-%d} | {now:%H:%M:%S} | {status} | rows={rows}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(line)


if __name__ == "__main__":
    rows = 0
    try:
        metrics = calculate_metrics(CSV_FILE)
        rows = metrics["transactions"]
        today = date.today().strftime("%d %b %Y")
        email_html = build_html_email(metrics, today)
        send_email(f"Daily Sales Summary: {today}", email_html)
        write_log("success", rows)
    except Exception as e:
        write_log("error", rows)
        print(f"Error: {e}")
        raise
import requests
import pandas as pd
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import datetime

# -----------------------------
# ⏰ 只在台灣 20:00 執行
# -----------------------------
now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)

if now.hour != 20:
    print(f"現在時間 {now}，非執行時間，跳過")
    exit()

# 👉 防止同一天重複執行（重要）
today = now.strftime("%Y-%m-%d")
if os.path.exists("last_run.txt"):
    with open("last_run.txt", "r") as f:
        last_day = f.read().strip()
        if last_day == today:
            print("今天已執行過，跳過")
            exit()

# -----------------------------
# 1️⃣ 抓網頁
# -----------------------------
url = "https://stock.wespai.com/p/75713"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers, timeout=15)
response.raise_for_status()

tables = pd.read_html(io.StringIO(response.text))
df = tables[0]

print("抓到表格前五筆：")
print(df.head())

# -----------------------------
# 2️⃣ Google Sheet
# -----------------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ['GOOGLE_SHEETS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
client = gspread.authorize(creds)

sheet = client.open("Getrawdata").worksheet("Rawdata")

# -----------------------------
# 3️⃣ 清空 + 一次寫入（避免429）
# -----------------------------
sheet.clear()
data = [df.columns.values.tolist()] + df.values.tolist()
sheet.update(data)

print("資料已成功寫入 Google Sheet！")

# -----------------------------
# 4️⃣ 記錄今天已執行
# -----------------------------
with open("last_run.txt", "w") as f:
    f.write(today)

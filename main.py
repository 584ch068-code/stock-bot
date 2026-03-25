import requests
import pandas as pd
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# -----------------------------
# 1️⃣ 抓網頁表格
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
# 2️⃣ 登入 Google Sheet
# -----------------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# 從 GitHub Secrets 讀 JSON
creds_dict = json.loads(os.environ['GOOGLE_SHEETS_JSON'])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "Getrawdata"
WORKSHEET_NAME = "Rawdata"

sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

# -----------------------------
# 3️⃣ 清空舊資料
# -----------------------------
sheet.clear()

# -----------------------------
# 4️⃣ 一次更新整個表格（表頭 + 內容）
# -----------------------------
data_to_write = [df.columns.values.tolist()] + df.values.tolist()
sheet.update(data_to_write)

print("資料已成功寫入 Google Sheet！")

#!/usr/bin/env python3
"""
monday_pull_updated.py
---------------------------------
Export a Monday board and its views—even behind an SSL-intercepting proxy,
and optionally apply a saved view’s filters to your export, with full pagination.

• Requires: requests, pandas, openpyxl
• Usage:
    python monday_pull_updated.py                    # default BOARD_ID, VIEW_ID from env
    BOARD_ID=[ENTER BOARD ID] VIEW_ID=[ENTER VIEW ID] python monday_pull_updated.py
"""

import os
import json
import urllib3
import requests
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────
# 1) CONFIG ── token + board + optional view
# ──────────────────────────────────────────────────────────────────────────
API_TOKEN = os.getenv("MONDAY_API_TOKEN", "TOKEN HERE")
BOARD_ID = int(os.getenv("BOARD_ID", 6345860769))
VIEW_ID = os.getenv("VIEW_ID")
if VIEW_ID:
    VIEW_ID = str(VIEW_ID)

# ──────────────────────────────────────────────────────────────────────────
# 2) REQUEST SETUP
# ──────────────────────────────────────────────────────────────────────────
URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json",
}
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ──────────────────────────────────────────────────────────────────────────
# 3) FETCH BOARD METADATA (views) ─
# ──────────────────────────────────────────────────────────────────────────
meta_query = f"""
{{
  boards(ids: {BOARD_ID}) {{
    id
    name
    views {{ id name type settings_str view_specific_data_str }}
  }}
}}
"""
resp = requests.post(URL, json={"query": meta_query}, headers=HEADERS, verify=False)
resp.raise_for_status()
meta_payload = resp.json()
if "errors" in meta_payload:
    raise RuntimeError(json.dumps(meta_payload["errors"], indent=2))
board_meta = meta_payload["data"]["boards"][0]
print(f"🔎 Board Views for '{board_meta['name']}':")
for v in board_meta["views"]:
    print(f" • [{v['id']}] {v['name']} ({v['type']})")

# ──────────────────────────────────────────────────────────────────────────
# 4) PAGINATION LOOP ── fetch all items in pages of 500
# ──────────────────────────────────────────────────────────────────────────
items = []
cursor = None
while True:
    page_query = f"""
    {{
      boards(ids: {BOARD_ID}) {{
        items_page(limit: 500{f', cursor: \"{cursor}\"' if cursor else ''}) {{
          cursor
          items {{ id name column_values {{ id text }} }}
        }}
      }}
    }}
    """
    resp = requests.post(URL, json={"query": page_query}, headers=HEADERS, verify=False)
    resp.raise_for_status()
    data = resp.json()["data"]["boards"][0]["items_page"]
    items.extend(data["items"])
    cursor = data.get("cursor")
    if not cursor:
        break

print(f"📥 Fetched total items: {len(items)}")

# ──────────────────────────────────────────────────────────────────────────
# 5) BUILD DATAFRAME from all items
# ──────────────────────────────────────────────────────────────────────────
rows = []
for it in items:
    row = {"Item ID": it["id"], "Item Name": it["name"]}
    for col in it["column_values"]:
        row[col["id"]] = col.get("text")
    rows.append(row)
df = pd.DataFrame(rows)

# ──────────────────────────────────────────────────────────────────────────
# 6) APPLY CUSTOM FILTER: only keep status_1 == "Pending PDM Processing"
# ──────────────────────────────────────────────────────────────────────────
if "status_1" in df.columns:
    original_count = len(df)
    df = df[df["status_1"] == "Pending PDM Processing"]
    print(f"🔍 Custom filter applied: status_1=='Pending PDM Processing' ({len(df)}/{original_count} rows)")
else:
    print("⚠️  Column status_1 not found—skipping custom filter.")

# ──────────────────────────────────────────────────────────────────────────
# 7) OPTIONAL: apply view filters if VIEW_ID provided
# ──────────────────────────────────────────────────────────────────────────
if VIEW_ID:
    selected = next((v for v in board_meta["views"] if v["id"] == VIEW_ID), None)
    if not selected:
        print(f"⚠️  View {VIEW_ID} not found on board; exporting full dataset.")
    else:
        settings = json.loads(selected["settings_str"] or "{}")
        filters = settings.get("filters") or settings.get("filter_by") or []
        for f in filters:
            col_id = f.get("column_id") or f.get("columnId")
            operator = f.get("operator")
            value = f.get("value")
            if col_id and operator == "clear" and value:
                df = df[df[col_id] == value]
        print(f"✅ Applied view '{selected['name']}' filters; {len(df)} rows remain.")

# ──────────────────────────────────────────────────────────────────────────
# 8) SAVE TO EXCEL
# ──────────────────────────────────────────────────────────────────────────
out_name = f"monday_board_{BOARD_ID}" + (f"_view_{VIEW_ID}" if VIEW_ID else "") + ".xlsx"
df.to_excel(out_name, index=False)
print(f"✅ Board '{board_meta['name']}' exported to {out_name}")

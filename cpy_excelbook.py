#!/usr/bin/env python3
import os
import shutil
from openpyxl import load_workbook

def safe_excel_copy():
    # Prompt for source and destination
    src = input("Enter path to the Excel workbook: ").strip().strip('"')
    dest_dir = input("Enter output directory: ").strip().strip('"')

    # Validate inputs
    if not os.path.isfile(src):
        print(f"❌ Error: Source file not found: {src}")
        return
    if not os.path.isdir(dest_dir):
        print(f"❌ Error: Destination folder not found: {dest_dir}")
        return

    # Optional: open read-only to verify it's a valid Excel file
    try:
        wb = load_workbook(filename=src, read_only=True)
        wb.close()
    except Exception as e:
        print(f"⚠️ Warning: Could not open workbook read-only ({e}); proceeding with raw copy.")

    # Build a safe destination path (avoid overwrites)
    base = os.path.basename(src)
    dest = os.path.join(dest_dir, base)
    if os.path.exists(dest):
        name, ext = os.path.splitext(base)
        dest = os.path.join(dest_dir, f"{name}_copy{ext}")

    # Perform a metadata-preserving copy
    shutil.copy2(src, dest)
    print(f"✅ Successfully copied to: {dest}")

if __name__ == "__main__":
    safe_excel_copy()

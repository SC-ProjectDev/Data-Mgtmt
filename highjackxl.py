#!/usr/bin/env python3
import os
import pandas as pd

def clean_path(raw: str) -> str:
    """
    Strip wrapping parentheses or quotes from a pasted path.
    """
    return raw.strip().strip('()"\'')

def main():
    raw = input("📂  Enter path to your Excel file: ")
    path = clean_path(raw)
    if not os.path.isfile(path):
        print(f"❌ File not found: {path}")
        return

    # read the first sheet
    df = pd.read_excel(path, sheet_name=0)

    # mapping: {original Monday column ID → desired New_Excel_Header}
    mapping = {
        "Item Name":   "Name",
        "status_11":   "PDM Status",
        "ipa_name4":   "IPA Name",
        "contract_type": "Contract Type",
        "numbers__1":   "# of Providers Excluded",
        "number8":     "# of Providers/Facilities",
        "single_select9":  "Amendment Type",
        "single_select2":  "Vendor Type",
        "status7":     "Status",
        "status_1":    "Sub Status",
        "status_15":   "Contract Config Status",
        "single_select76": "Relationship History",
        "date5":       "Eff. Date",
        "text":        "File Path",
        "tax_id_number": "Tax ID Number",
        "single_select29": "Business Type",
        "date":        "Date Started",
        "single_select7":  "Compensation Schedule",
        "status_19":   "Credentialing Status",
        "group_npi":   "Group NPI",
        "short_text8": "Specialty",
        "single_select0":  "Priority",
        "long_text1":  "Note",
        "people_1":    "Handled By",
        "long_text13": "Request Description",
        "date54":      "Date Completed",
        "email":       "Submitted by Email",
        "creation_log7":"Creation Log",
        "people2":     "Processed by",
        "ipa_type__1": "IPA Type",
        "status_1__1": "Payment Structure",
        "last_updated__1":"Last Updated",
        "color_mkp5jrj3":  "Client Acknowledgment",
        "file_mkp57r5x":   "Signed Document",
        "status_1_Mjj5XVyM":"Signature Status",
    }

    # keep only the columns that actually exist in the sheet
    present = {orig: new for orig, new in mapping.items() if orig in df.columns}
    missing = set(mapping) - set(present)
    if missing:
        print("⚠️  Warning—these columns were not found and will be skipped:")
        for m in sorted(missing):
            print("   –", m)

    # slice + rename
    mini = df[list(present)].rename(columns=present)

    # write out a new workbook
    base, ext = os.path.splitext(path)
    out_path = f"{base}_curated.xlsx"
    mini.to_excel(out_path, index=False)
    print(f"✅  Wrote {len(mini)} rows to '{out_path}'")

if __name__ == "__main__":
    main()

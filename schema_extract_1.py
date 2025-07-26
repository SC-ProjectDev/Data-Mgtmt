#!/usr/bin/env python3
"""
Script to extract schema from an Excel workbook and output it to a new Excel file.

Usage:
    python excel_schema_extractor.py input_workbook.xlsx output_schema.xlsx
"""
import argparse
import pandas as pd


def extract_schema(input_file: str, output_file: str) -> None:
    """
    Extracts table schema from each sheet in the given Excel workbook and writes to a new Excel file.

    Args:
        input_file: Path to the input Excel workbook (.xlsx).
        output_file: Path where the schema Excel file will be saved.
    """
    # Load workbook with pandas
    xls = pd.ExcelFile(input_file, engine='openpyxl')
    schema_rows = []

    # Iterate over each sheet/tab
    for sheet_name in xls.sheet_names:
        # Read sheet without treating any row as header
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None, engine='openpyxl')
        if df.empty:
            continue

        # FullName is the value in cell A1 (row 0, col 0)
        full_name = df.iat[0, 0]

        # Field names are all values from B1 onward (row 0, cols 1...)
        headers = df.iloc[0, 1:]
        for header in headers:
            if pd.isna(header):
                continue
            field_name = str(header)
            # Determine data type: 'Date' if 'Date' appears in field name, case-insensitive
            data_type = 'Date' if 'date' in field_name.lower() else 'Short Text'

            schema_rows.append({
                'TableName': sheet_name,
                'FullName': full_name,
                'FieldName': field_name,
                'DataType': data_type
            })

    # Create DataFrame for schema and write to Excel
    schema_df = pd.DataFrame(schema_rows, columns=['TableName', 'FullName', 'FieldName', 'DataType'])
    schema_df.to_excel(output_file, index=False)
    print(f"Schema extracted from '{input_file}' and saved to '{output_file}'")


def main():
    parser = argparse.ArgumentParser(description='Extract Excel workbook schema.')
    parser.add_argument('input_file', help='Path to the input Excel workbook (.xlsx)')
    parser.add_argument('output_file', help='Path to the output Excel file for schema')
    args = parser.parse_args()
    extract_schema(args.input_file, args.output_file)


if __name__ == '__main__':
    main()

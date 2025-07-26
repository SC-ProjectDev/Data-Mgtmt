#!/usr/bin/env python3
"""
Script to extract headers from an Excel workbook and output schema to a new Excel file.

Usage:
    python excel_header_extractor.py input_workbook.xlsx output_schema.xlsx
"""
import argparse
import pandas as pd


def extract_schema(input_file: str, output_file: str) -> None:
    """
    Extracts headers from each sheet in the given Excel workbook and writes schema to a new Excel file.

    Args:
        input_file: Path to the input Excel workbook (.xlsx).
        output_file: Path where the schema Excel file will be saved.
    """
    # Load workbook
    xls = pd.ExcelFile(input_file, engine='openpyxl')
    schema_rows = []

    # Iterate over each sheet/tab
    for sheet_name in xls.sheet_names:
        # Read sheet treating first row as header
        df = pd.read_excel(xls, sheet_name=sheet_name, header=0, engine='openpyxl')
        if df.empty:
            continue

        # Field names are the header row values
        headers = df.columns
        for header in headers:
            if pd.isna(header):
                continue
            field_name = str(header)
            # Determine data type: 'Date' if 'date' appears in field name, else 'Short Text'
            data_type = 'Date' if 'date' in field_name.lower() else 'Short Text'

            schema_rows.append({
                'TableName': sheet_name,
                'FieldName': field_name,
                'DataType': data_type
            })

    # Create DataFrame for schema and write to Excel
    schema_df = pd.DataFrame(schema_rows, columns=['TableName', 'FieldName', 'DataType'])
    schema_df.to_excel(output_file, index=False)
    print(f"Schema extracted from '{input_file}' and saved to '{output_file}'")


def main():
    parser = argparse.ArgumentParser(description='Extract Excel headers schema.')
    parser.add_argument('input_file', help='Path to the input Excel workbook (.xlsx)')
    parser.add_argument('output_file', help='Path to the output Excel schema file (.xlsx)')
    args = parser.parse_args()
    extract_schema(args.input_file, args.output_file)


if __name__ == '__main__':
    main()

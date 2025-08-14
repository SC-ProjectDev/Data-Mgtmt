#!/usr/bin/env python3
"""
This script processes an Excel workbook of provider credentialing sheets and transforms them into a single master sheet.
Usage:
    python credentialing_master_script.py input_file.xlsx -o output_file.xlsx
"""
import pandas as pd
import argparse

# Mapping from full network names to short codes
network_map = {
    'Access Primary Care Medical Group': 'APCMG',
    'Accountable Health Care': 'AHC',
    'Allied Pacific of California': 'APC',
    'All American Medical Group': 'AAMG',
    'Alpha Care Medical Group': 'ALPHA',
    'American Acupuncture Chinese Medicine': 'AACM',
    'Associated Hispanic Physicians': 'AHISP',
    'Arroyo Vista Family Health Clinic': 'AVISTA',
    'Bay Area Care Partners': 'BACP',
    'Beverly Alianza IPA': 'BAIPA',
    'Central Valley Medical Group': 'CVMG',
    'Community Family Care IPA': 'CFC',
    'Diamond Bar Medical Group': 'GOM',
    'For Your Benefit': 'FYB',
    'Hana Hou Medical Group': 'HHMG',
    'Central California Physician Partners': 'CCPP',
    'Jade Health IPA': 'JADE',
}

# Define the output columns, including legacy networks to track history
output_columns = [
    'APC', 'APCMG', 'AHC', 'ALPHA', 'AVISTA', 'BAIPA', 'CFC', 'GOM',
    'JADE', 'AAMG', 'CVMG', 'AHISP', 'AACM', 'CCPP', 'BACP', 'HHMG',
    'FYB', 'ADV', 'CVIPA', 'GSGP', 'NCPN',
    'COMMITTEE (Astrana Health)', 'LEVEL       (1 or 2)', 'LAST',
    'FIRST', 'DEGREE', 'TYPE', 'SPECIALTY', 'NPI', 'Vendor',
    'COUNTY', 'COMMITTEE SUBMISSION DATE', 'STATUS'
]

def normalize_sheet(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize one sheet into the master row format.
    """
    rows = []
    for _, row in df.iterrows():
        # Initialize new row dict with blanks
        new_row = {col: '' for col in output_columns}

        # Copy provider and credentialing info
        new_row['COMMITTEE (Astrana Health)'] = row.get('COMMITTEE (Astrana Health)', '')
        new_row['LEVEL       (1 or 2)'] = row.get('LEVEL       (1 or 2)', '')
        new_row['LAST'] = row.get('LAST/HDO Name', '')
        new_row['FIRST'] = row.get('FIRST', '')
        new_row['DEGREE'] = row.get('DEGREE', '')
        new_row['TYPE'] = row.get('TYPE (PCP/SCP/AHP/HDO)', '')
        new_row['SPECIALTY'] = row.get('SPECIALTY', '')
        new_row['NPI'] = row.get('NPI', '')
        new_row['Vendor'] = row.get('Vendor', '')
        new_row['COUNTY'] = row.get('COUNTY', '')
        new_row['COMMITTEE SUBMISSION DATE'] = row.get('COMMITTEE SUBMISSION DATE', '')
        new_row['STATUS'] = row.get('STATUS', '')

        # Mark network participation with 'x'
        for full_name, code in network_map.items():
            # check for 'x' (case-insensitive) in the source column
            val = str(row.get(full_name, '')).strip().lower()
            if val == 'x':
                new_row[code] = 'x'

        rows.append(new_row)

    return pd.DataFrame(rows, columns=output_columns)


def process_credentialing_file(file_path: str) -> pd.DataFrame:
    """
    Read all sheets from the Excel file and concatenate into a master DataFrame.
    """
    xl = pd.ExcelFile(file_path)
    normalized_dfs = []
    for sheet_name in xl.sheet_names:
        df_sheet = xl.parse(sheet_name)
        normalized_dfs.append(normalize_sheet(df_sheet))
    # Combine all providers into one DataFrame
    master_df = pd.concat(normalized_dfs, ignore_index=True)
    return master_df


def main():
    parser = argparse.ArgumentParser(
        description="Generate a master credentialing sheet from multi-sheet input"
    )
    parser.add_argument(
        'input_file', help='Path to the input Excel file with multiple sheets'
    )
    parser.add_argument(
        '-o', '--output_file', default='master_output.xlsx',
        help='Path for the output master Excel file'
    )
    args = parser.parse_args()

    # Process and save
    master_df = process_credentialing_file(args.input_file)
    master_df.to_excel(args.output_file, index=False)
    print(f"Master credentialing sheet saved to {args.output_file}")

if __name__ == '__main__':
    main()

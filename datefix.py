import pandas as pd
from dateutil import parser

# Prompt user for the Excel file path
file_path = input("Enter the path to the Excel (.xlsx) file: ")

# Load the first sheet of the Excel file
df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl')

# Create a copy of the data for processing
processing_df = df.copy()

# Function to extract and reformat the date from the "Last Updated" column
def extract_date(cell):
    # Leave empty/missing values alone
    if pd.isna(cell):
        return cell
    try:
        # parser.parse with fuzzy=True ignores any non-date words (like names),
        # then we format only the date portion.
        dt = parser.parse(str(cell), fuzzy=True)
        return dt.strftime("%m/%d/%Y")
    except (ValueError, TypeError):
        # If parsing fails completely, return the original
        return cell

# Apply the date extraction function to the "Last Updated" column
if "Last Updated" in processing_df.columns:
    processing_df["Last Updated"] = processing_df["Last Updated"].apply(extract_date)
else:
    print("Column 'Last Updated' not found in the sheet.")

# Write the processed data to a new sheet named 'processing'
with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    processing_df.to_excel(writer, sheet_name='processing', index=False)

print("Processing complete. The 'processing' sheet has been added to the Excel file.")

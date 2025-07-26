import requests
import pandas as pd
from openpyxl import load_workbook

# Prompt for the file location of the spreadsheet
file_path = input("Please enter the full file path of the spreadsheet with NPIs in column A: ")

# Load the Excel workbook and read the NPIs from the first sheet
workbook = load_workbook(filename=file_path)
sheet = workbook.active  # Assuming the first sheet has the NPIs
npi_list = [cell.value for cell in sheet['A'] if cell.value]  # Reads all values in column A

# Prepare a list to store the API results
results = []

# Loop through each NPI, request data from the NPI Registry API, and append to results
for npi in npi_list:
    response = requests.get(f"https://npiregistry.cms.hhs.gov/api/?number={npi}&version=2.1")
    data = response.json()
    
    if data.get("results"):
        result = data["results"][0]
        
        # Identify the NPI type (1 for individual, 2 for organization)
        npi_type = result.get("enumeration_type", "N/A")
        
        # Initialize variables
        first_name = ''
        last_name = ''
        organization_name = ''
        dba_name = ''  # Default to empty
        provider_gender = "N/A"  # Default to "N/A" if not available

        # Extract provider name and gender based on NPI type
        if npi_type == "NPI-1":  # Individual
            first_name = result['basic'].get('first_name', '')
            last_name = result['basic'].get('last_name', '')
            provider_gender = result["basic"].get("sex", "N/A")
        elif npi_type == "NPI-2":  # Organization
            organization_name = result['basic'].get("organization_name", "N/A")
        
        # Extract the DBA name from the "other_names" field if available
        other_names = result.get("other_names", [])
        if other_names:
            dba_name = other_names[0].get("organization_name", "")  # Take the first "organization_name" entry
        
        # Extract address details
        address_info = result["addresses"][0]  # Assuming the first address is the primary
        address = address_info.get("address_1", "N/A")
        city = address_info.get("city", "N/A")
        state = address_info.get("state", "N/A")
        zip_code = address_info.get("postal_code", "N/A")
        phone = address_info.get("telephone_number", "N/A")
        fax = address_info.get("fax_number", "N/A")

        # Collect all taxonomies and prioritize primary
        taxonomies = result.get("taxonomies", [])
        primary_taxonomy = [t for t in taxonomies if t.get("primary")]
        non_primary_taxonomies = [t for t in taxonomies if not t.get("primary")]

        # Ensure primary taxonomy is listed first, followed by others
        ordered_taxonomies = primary_taxonomy + non_primary_taxonomies

        # Initialize provider information dictionary
        provider_info = {
            "NPI": npi,
            "NPI Type": npi_type,
            "Last Name": last_name,
            "First Name": first_name,
            "Organization Name": organization_name,
            "Doing Business As": dba_name,  # Include DBA name
            "Gender": provider_gender,
            "Address": address,
            "City": city,
            "State": state,
            "Zip Code": zip_code,
            "Phone": phone,
            "Fax": fax,
        }

        # Dynamically add taxonomy information with primary listed first
        for i, taxonomy in enumerate(ordered_taxonomies, start=1):
            provider_info[f"Taxonomy{i}"] = taxonomy.get("code", "N/A")
            provider_info[f"Taxonomy Description{i}"] = taxonomy.get("desc", "N/A")

        results.append(provider_info)
    else:
        # If no results are found for the NPI
        provider_info = {
            "NPI": npi,
            "NPI Type": "Not Found",
            "Last Name": '',
            "First Name": '',
            "Organization Name": '',
            "Doing Business As": '',
            "Gender": "N/A",
            "Address": "",
            "City": "",
            "State": "",
            "Zip Code": "",
            "Phone": "",
            "Fax": "",
        }
        results.append(provider_info)

# Convert results to a DataFrame
results_df = pd.DataFrame(results)

# Base columns expected in the output
base_columns = [
    "NPI", "NPI Type", "Last Name", "First Name", "Organization Name",
    "Doing Business As", "Gender", "Address", "City", "State", "Zip Code", "Phone", "Fax"
]

# Separate and sort taxonomy columns to interleave pairs of 'Taxonomy' and 'Taxonomy Description'
taxonomy_columns = sorted(
    [col for col in results_df.columns if col.startswith('Taxonomy') and 'Description' not in col],
    key=lambda x: int(x[len('Taxonomy'):])  # Sort Taxonomy columns by number
)

taxonomy_description_columns = sorted(
    [col for col in results_df.columns if col.startswith('Taxonomy Description')],
    key=lambda x: int(x[len('Taxonomy Description'):])  # Sort Taxonomy Description columns by number
)

# Combine base columns with interleaved taxonomy and description columns
columns_order = base_columns
for tax_col, desc_col in zip(taxonomy_columns, taxonomy_description_columns):
    columns_order.extend([tax_col, desc_col])

# Reorder the DataFrame
results_df = results_df[columns_order]

# Save the results to a new sheet in the same workbook
with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
    results_df.to_excel(writer, sheet_name="NPI_Results", index=False)

print("Results have been saved")

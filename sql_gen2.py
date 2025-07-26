import os
import subprocess
import shutil
from math import ceil

# --- Config ---
TEMPLATE_DIR = r"C:\Users\scadena\OneDrive - Apollo Medical Management\Desktop\Scripts\Queries_gen\queries_temps"
TEMP_OUTPUT_FILE = "temp_query.txt"

# --- Database options (alphabetized) ---
DB_NAMES = [
    "AAMG", "AACM", "ACPAZ", "ACPHI", "ADV", "AHC", "AHISP", "ALPHA", "AMNV", "AMTX", "APC", "APCMG",
    "AVISTA", "BAIPA", "BACP", "CAIPA", "CFC", "CFCImages", "CFCHP", "CCHCA", "CIPA", "CCPP", "CSMS",
    "CVIPA", "CVMG", "distribution", "ECD", "EM", "EZCARE60", "EZDATAREP", "FYB", "GAMC", "GOM", "GSGP",
    "GTPA", "HHMG", "HPN", "JADE", "LSMA", "master", "MDPTN", "model", "msdb", "NCPN", "PHL", "SEEN",
    "SLMS6", "spherical", "SSISDB", "STAGECARE", "tempdb", "UTILS", "WMMC", "ZELIS"
]

# --- Helpers ---
def list_templates():
    return [f for f in os.listdir(TEMPLATE_DIR) if f.endswith(".txt")]

def select_from_list(options, prompt_text, num_cols=3):
    print(f"\n=== {prompt_text} ===\n")

    rows = ceil(len(options) / num_cols)
    col_width = max(len(item) for item in options) + 4  # Padding for spacing and numbers

    for r in range(rows):
        line = ""
        for c in range(num_cols):
            idx = r + c * rows
            if idx < len(options):
                num = idx + 1
                item = options[idx]
                line += f"{num:>3}. {item:<{col_width}}"
        print(line)

    choice = int(input("\nEnter the number of your choice: ")) - 1
    if 0 <= choice < len(options):
        return options[choice]
    else:
        raise ValueError("Choice out of range")

def load_template(file_path):
    with open(file_path, "r") as f:
        return f.read()

def create_temp_query(template, dbname):
    return template.replace("{DBNAME}", dbname)

def write_temp_file(query):
    with open(TEMP_OUTPUT_FILE, "w") as f:
        f.write(query)

def open_in_notepad():
    subprocess.Popen(["notepad.exe", TEMP_OUTPUT_FILE])

# --- Main ---
def main():
    print("=== Interactive SQL Query Generator ===")

    # Step 1: Pick a template
    templates = list_templates()
    if not templates:
        print("No query templates found.")
        return
    selected_template = select_from_list(templates, "Select a query template")
    full_template_path = os.path.join(TEMPLATE_DIR, selected_template)

    # Step 2: Pick a database (with 4-column layout)
    selected_db = select_from_list(DB_NAMES, "Select a database", num_cols=4)

    # Step 3: Load and replace
    raw_template = load_template(full_template_path)
    final_query = create_temp_query(raw_template, selected_db)

    # Step 4: Output and open
    write_temp_file(final_query)
    print(f"\n✅ Built query with database '{selected_db}'. Opening in Notepad...")
    open_in_notepad()

if __name__ == "__main__":
    main()

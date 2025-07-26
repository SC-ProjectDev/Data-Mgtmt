import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import openpyxl
from tkinter import filedialog
from tksheet import Sheet

def fetch_npi_data():
    # Get all entered NPI numbers
    npi_numbers = [entry.get().strip() for entry in npi_entries if entry.get().strip()]
    if not npi_numbers:
        messagebox.showwarning("Input Error", "Please enter at least one NPI number.")
        return

    results = []
    for npi in npi_numbers:
        try:
            response = requests.get(f"https://npiregistry.cms.hhs.gov/api/?number={npi}&version=2.1")
            response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            data = response.json()
        except Exception as e:
            messagebox.showerror("Network/API Error", f"An error occurred for NPI {npi}: {e}")
            continue

        if data.get("results"):
            result = data["results"][0]
            npi_type = result.get("enumeration_type", "N/A")

            # Default placeholders
            last_name = "N/A"
            first_name = "N/A"
            provider_gender = "N/A"
            
            if npi_type == "NPI-1":  
                # For Individuals
                last_name = result["basic"].get("last_name", "N/A")
                first_name = result["basic"].get("first_name", "N/A")
                provider_gender = result["basic"].get("sex", "N/A")
            elif npi_type == "NPI-2":
                # For Organizations
                org_name = result["basic"].get("organization_name", "N/A")
                last_name = org_name

                dba = result["basic"].get("dba_name", "").strip()
                first_name = dba if dba else "N/A"

            # Primary address info
            primary_address = result.get("addresses", [{}])[0]
            address = primary_address.get("address_1", "N/A")
            city = primary_address.get("city", "N/A")
            state = primary_address.get("state", "N/A")
            zip_code = primary_address.get("postal_code", "N/A").split('-')[0]
            phone = primary_address.get("telephone_number", "N/A").replace("-", "")
            fax = primary_address.get("fax_number", "N/A").replace("-", "")

            # TAXONOMIES (Updated logic)
            all_taxonomies = result.get("taxonomies", [])

            # Separate into primary vs. non-primary
            primary_list = [t for t in all_taxonomies if t.get("primary") == True]
            non_primary_list = [t for t in all_taxonomies if not t.get("primary")]

            # 1) Taxonomy1 Code/Desc (use first primary if exists)
            if len(primary_list) > 0:
                taxonomy1_code = primary_list[0].get("code", "N/A")
                taxonomy1_desc = primary_list[0].get("desc", "N/A")
            else:
                taxonomy1_code = "N/A"
                taxonomy1_desc = "N/A"

            # 2) Taxonomy2 Code/Desc -> first non-primary
            if len(non_primary_list) > 0:
                taxonomy2_code = non_primary_list[0].get("code", "N/A")
                taxonomy2_desc = non_primary_list[0].get("desc", "N/A")
            else:
                taxonomy2_code = "N/A"
                taxonomy2_desc = "N/A"

            # 3) Taxonomy3 Code/Desc -> second non-primary
            if len(non_primary_list) > 1:
                taxonomy3_code = non_primary_list[1].get("code", "N/A")
                taxonomy3_desc = non_primary_list[1].get("desc", "N/A")
            else:
                taxonomy3_code = "N/A"
                taxonomy3_desc = "N/A"

            # Build a row with the desired columns
            row = [
                npi,
                last_name,
                first_name,
                provider_gender,
                npi_type,
                address,
                city,
                state,
                zip_code,
                phone,
                fax,
                taxonomy1_code,
                taxonomy1_desc,
                taxonomy2_code,
                taxonomy2_desc,
                taxonomy3_code,
                taxonomy3_desc
            ]
            results.append(row)
        else:
            # No results found
            row = [
                npi, "N/A", "N/A", "N/A", "N/A", 
                "N/A", "N/A", "N/A", "N/A", "N/A", 
                "N/A", "N/A", "N/A", "N/A", "N/A",
                "N/A", "N/A"
            ]
            results.append(row)

    # Clear existing table entries
    for row_id in table.get_children():
        table.delete(row_id)

    # Insert new results into the table
    for result_row in results:
        table.insert("", "end", values=result_row)

    update_record_count()
    # Update tksheet with new data
    update_provider_sheet()

def display_details(event):
    selected_item = table.selection()
    if selected_item:
        record = table.item(selected_item, "values")
        details_text.config(state="normal")
        details_text.delete("1.0", tk.END)
        details_text.insert(
            tk.END, 
            "\n".join([
                f"{columns[i]}: {record[i]}" 
                for i in range(min(len(columns), len(record)))
            ])
        )
        details_text.config(state="disabled")

def clear_entries():
    for entry in npi_entries:
        entry.delete(0, tk.END)
    for row_id in table.get_children():
        table.delete(row_id)
    details_text.config(state="normal")
    details_text.delete("1.0", tk.END)
    details_text.config(state="disabled")

    # Clear the sheet data
    provider_sheet.set_sheet_data([])

    update_record_count()

def update_record_count():
    count = len(table.get_children())
    record_count_label.config(text=f"Record count: {count}")

def save_results_to_excel():
    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
    )
    if not filepath:
        return
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "NPI Results"
    ws.append([col for col in columns])
    
    for row_id in table.get_children():
        row_data = table.item(row_id, "values")
        ws.append(row_data)
    
    wb.save(filepath)
    messagebox.showinfo("Success", "Results saved successfully!")

def update_provider_sheet():
    """
    Grabs the Last Name, First Name, and NPI from each row in the Treeview
    and populates the Tksheet with that data.
    """
    sheet_data = []
    for row_id in table.get_children():
        row_values = table.item(row_id, "values")
        # row_values[0] = NPI
        # row_values[1] = Last Name
        # row_values[2] = First Name
        # So columns in tksheet will be: [LastName, FirstName, NPI]
        sheet_data.append([row_values[1], row_values[2], row_values[0]])
    
    provider_sheet.set_sheet_data(sheet_data)

# --------------------------------------------------------------------------------
# GUI Setup
app = tk.Tk()
app.title("NPI Registry Lookup")
app.geometry("1200x600")
app.attributes("-alpha", 0.9)  # 90% opacity
app.configure(bg="#000000")

left_frame = tk.Frame(app, bg="#000000")
left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

instructions = tk.Label(left_frame, text="NPI Search:", bg="#000000", fg="white", font=("Helvetica", 10, "bold"))
instructions.pack()

# Create entry boxes for up to 15 NPI numbers
npi_entries = []
for i in range(15):
    entry = tk.Entry(left_frame, width=20, bg="#404040", fg="white")
    entry.pack(pady=2)
    npi_entries.append(entry)

submit_button = tk.Button(left_frame, text="Fetch NPI Data", command=fetch_npi_data, bg="#000000", fg="white", font=("Helvetica", 9, "bold"))
submit_button.pack(pady=10)

clear_button = tk.Button(left_frame, text="Clear Entries", command=clear_entries, bg="#000000", fg="white", font=("Helvetica", 9, "bold"))
clear_button.pack(pady=10)

save_button = tk.Button(left_frame, text="Save to Excel", command=save_results_to_excel, bg="#000000", fg="white", font=("Helvetica", 9, "bold"))
save_button.pack(pady=10)

# Define table columns
columns = (
    "NPI",
    "Last Name",
    "First Name",
    "Gender",
    "NPI-Type",
    "Address",
    "City",
    "State",
    "Zip",
    "Phone",
    "Fax",
    "Taxonomy1 Code",
    "Taxonomy1 Desc",
    "Taxonomy2 Code",
    "Taxonomy2 Desc",
    "Taxonomy3 Code",
    "Taxonomy3 Desc"
)

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#000000", foreground="#FFFFFF", fieldbackground="#000000")
style.configure("Treeview.Heading", background="#000000", foreground="white")

right_frame = tk.Frame(app, bg="#2b2b2b")
right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

table_frame = tk.Frame(right_frame, bg="#000000")
table_frame.pack(fill="both", expand=True)

h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10,
    xscrollcommand=h_scrollbar.set,
    style="Treeview"
)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=70, anchor="w")

h_scrollbar.config(command=table.xview)
h_scrollbar.pack(side="bottom", fill="x")
table.pack(side="top", fill="both", expand=True)
table.bind("<<TreeviewSelect>>", display_details)

text_boxes_frame = tk.Frame(right_frame, bg="#000000")
text_boxes_frame.pack(fill="x", expand=True)

details_text = tk.Text(
    text_boxes_frame,
    height=15,
    width=50,
    bg="#2b2b2b",
    fg="white",
    wrap="word",
    state="disabled"
)
details_text.pack(side="left", fill="both", expand=True)

# Tksheet for "Last Name", "First Name", "NPI"
provider_sheet = Sheet(
    text_boxes_frame,
    data=[],
    headers=["Last Name", "First Name", "NPI"],
    height=15,
    width=400
)
provider_sheet.enable_bindings((
    "single_select",
    "rc_select",
    "drag_select",
    "select_all",
    "column_select",
    "row_select",
    "arrowkeys",
    "row_height_resize",
    "column_width_resize",
    "double_click_column_resize",
    "copy"
))
provider_sheet.pack(side="right", fill="both", expand=True)

record_count_label = tk.Label(
    right_frame,
    text="Record count: 0",
    bg="#000000",
    fg="white",
    font=("Helvetica", 9, "bold")
)
record_count_label.pack(fill="x", padx=10, pady=5)

app.mainloop()

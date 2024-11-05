import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import openpyxl
from tkinter import filedialog

# Function to retrieve NPI data from the NPI Registry API
def fetch_npi_data():
    npi_numbers = [entry.get() for entry in npi_entries if entry.get().strip()]
    if not npi_numbers:
        messagebox.showwarning("Input Error", "Please enter at least one NPI number.")
        return

    results = []
    for npi in npi_numbers:
        response = requests.get(f"https://npiregistry.cms.hhs.gov/api/?number={npi}&version=2.1")
        data = response.json()
        if data.get("results"):
            result = data["results"][0]
            npi_type = result.get("enumeration_type", "N/A")

            provider_name = "Not Found"
            provider_gender = "N/A"
            if npi_type == "NPI-1":  # Individual
                provider_name = f"{result['basic'].get('last_name', '')}, {result['basic'].get('first_name', '')}".strip(", ")
                provider_gender = result["basic"].get("gender", "N/A")
            elif npi_type == "NPI-2":  # Organization
                provider_name = result['basic'].get("organization_name", "N/A")
            
            primary_address = result["addresses"][0]
            address = primary_address.get("address_1", "N/A")
            city = primary_address.get("city", "N/A")
            state = primary_address.get("state", "N/A")
            zip_code = primary_address.get("postal_code", "N/A").split('-')[0]
            phone = primary_address.get("telephone_number", "N/A").replace("-","")
            fax = primary_address.get("fax_number", "N/A").replace("-","")

            taxonomies = result.get("taxonomies", [])
            primary_taxonomies = [
                taxonomy for taxonomy in taxonomies
                if taxonomy.get('primary', False)
            ]
            taxonomy_data = [f"{taxonomy.get('code', 'N/A')} - {taxonomy.get('desc', 'N/A')}" for taxonomy in primary_taxonomies]

            results.append([npi, provider_name, provider_gender, npi_type, address, city, state, zip_code, phone, fax] + taxonomy_data[:3])
        else:
            results.append([npi, "Not Found", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])

    for row in table.get_children():
        table.delete(row)

    for result in results:
        table.insert("", "end", values=result)

    update_record_count()

def display_details(event):
    selected_item = table.selection()
    if selected_item:
        record = table.item(selected_item, "values")
        details_text.config(state="normal")
        details_text.delete("1.0", tk.END)
        details_text.insert(tk.END, "\n".join([f"{columns[i]}: {record[i]}" for i in range(min(len(columns), len(record)))]))
        details_text.config(state="disabled")

def clear_entries():
    for entry in npi_entries:
        entry.delete(0, tk.END)

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
    
    for row in table.get_children():
        row_data = table.item(row, "values")
        ws.append(row_data)
    
    wb.save(filepath)
    messagebox.showinfo("Success", "Results saved successfully!")

app = tk.Tk()
app.title("NPI Registry Lookup")
app.geometry("1000x500")
app.configure(bg="#2b2b2b")

left_frame = tk.Frame(app, bg="#2b2b2b")
left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

instructions = tk.Label(left_frame, text="NPI Search:", bg="#2b2b2b", fg="white")
instructions.pack()

npi_entries = []
for i in range(15):
    entry = tk.Entry(left_frame, width=20)
    entry.pack(pady=2)
    npi_entries.append(entry)

submit_button = tk.Button(left_frame, text="Fetch NPI Data", command=fetch_npi_data, bg="#404040", fg="white")
submit_button.pack(pady=10)
clear_button = tk.Button(left_frame, text="Clear Entries", command=clear_entries, bg="#404040", fg="white")
clear_button.pack(pady=10)
save_button = tk.Button(left_frame, text="Save to Excel", command=save_results_to_excel, bg="#404040", fg="white")
save_button.pack(pady=10)

right_frame = tk.Frame(app, bg="#2b2b2b")
right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

table_frame = tk.Frame(right_frame, bg="#2b2b2b")
table_frame.pack(fill="both", expand=True)

h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")

columns = ("NPI", "Provider Name", "Gender", "NPI-Type", "Address", "City", "State", "Zip", "Phone", "Fax", "Taxonomy1", "Taxonomy2", "Taxonomy3")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10, xscrollcommand=h_scrollbar.set)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=80, anchor="w")

h_scrollbar.config(command=table.xview)
h_scrollbar.pack(side="bottom", fill="x")

table.pack(side="top", fill="both", expand=True)
table.bind("<<TreeviewSelect>>", display_details)

details_text = tk.Text(right_frame, height=12, bg="#2b2b2b", fg="white", wrap="word", state="disabled")
details_text.pack(fill="x", expand=True)

record_count_label = tk.Label(right_frame, text="Record count: 0", bg="#2b2b2b", fg="white")
record_count_label.pack(fill="x", padx=10, pady=5)

app.mainloop()

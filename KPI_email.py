import datetime
import win32com.client as client

# Calculate the current week's Sunday and Saturday (Sunday-Saturday range)
today = datetime.date.today()
# In Python, weekday(): Monday=0 ... Sunday=6
# Compute days since last Sunday
days_since_sunday = (today.weekday() + 1) % 7
sunday = today - datetime.timedelta(days=days_since_sunday)
saturday = sunday + datetime.timedelta(days=6)

# Format dates as MM/DD/YYYY
sunday_str = sunday.strftime("%m/%d/%Y")
saturday_str = saturday.strftime("%m/%d/%Y")

# Prepare email fields
to_address = "Francisco Hernandez <francisco.hernandez@astranahealth.com>"
cc_address = "Jester Palad <jester.palad@astranahealth.com>"
subject = f"Agreement KPIs: {sunday_str} - {saturday_str}"
body = f"""
Hello Frank,

Attached are the agreement KPIs for the week of {sunday_str} - {saturday_str}

Best
"""

# Initialize Outlook application
outlook = client.Dispatch("Outlook.Application")
mail = outlook.CreateItem(0)  # 0: olMailItem

# Set email properties
mail.To = to_address
mail.CC = cc_address
mail.Subject = subject
mail.Body = body

# Uncomment and set your file path to attach files
# mail.Attachments.Add(r"C:\path\to\your\KPI_report.xlsx")

# Display the email for review (use .Send() to send immediately)
mail.Display()

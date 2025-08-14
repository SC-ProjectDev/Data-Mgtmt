import os
import re
import logging
# win32com.client and pdfplumber imports remain as-is

logging.basicConfig(level=logging.INFO)

def _mask_npi(npi: str) -> str:
    if not npi: return "****"
    return "*" * max(0, len(npi) - 4) + npi[-4:]

MAILBOX_NAME = os.getenv("OUTLOOK_MAILBOX_NAME", "").strip()
MAIL_FOLDER  = os.getenv("OUTLOOK_MAIL_FOLDER", "Inbox").strip()

KNOWN_PHRASES = {p.strip() for p in os.getenv(
    "KNOWN_SUBJECT_PHRASES",
    "Provider Provider Profile,Allied Health Provider Profile"
).split(",") if p.strip()}

def _safe_subj(s: str, limit: int = 80) -> str:
    s = (s or "").replace("\n", " ").strip()
    return (s[:limit] + "…") if len(s) > limit else s

def parse_email_subject(subject):
    subject = subject.strip()
    if subject.lower().startswith('fw:'):
        subject = subject[3:].strip(': ').strip()

    parts = [part.strip() for part in subject.split('|') if part.strip()]
    network_name = provider_npi = None

    if parts:
        network_name = parts[0]
        if len(parts) >= 4 and parts[1] in KNOWN_PHRASES:
            provider_npi = parts[3]
        elif len(parts) >= 3:
            provider_npi = parts[2]
        else:
            logging.debug("Unrecognized subject layout: %s", _safe_subj(subject))
            return None, None
        return network_name, provider_npi

    logging.debug("Empty or malformed subject: %s", _safe_subj(subject))
    return None, None

def process_all_unread_emails(file_path, max_emails=None):
    if not MAILBOX_NAME:
        raise RuntimeError("Set OUTLOOK_MAILBOX_NAME in the environment.")

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.Folders(MAILBOX_NAME).Folders(MAIL_FOLDER)
    messages = inbox.Items
    unread_messages = messages.Restrict("[Unread]=True")

    processed_count = 0
    for message in unread_messages:
        if max_emails is not None and processed_count >= max_emails:
            break
        message_success = False
        if message.Attachments.Count > 0:
            subject = message.Subject or ""
            network_name, provider_npi = parse_email_subject(subject)
            if network_name and provider_npi:
                for attachment in message.Attachments:
                    if attachment.FileName.lower().endswith('.pdf'):
                        temp_pdf_path = os.path.join(file_path, attachment.FileName)
                        attachment.SaveAsFile(temp_pdf_path)
                        provider_name, current_appointment_date = extract_provider_info(temp_pdf_path)
                        if provider_name and current_appointment_date:
                            safe_date = current_appointment_date.replace('/', '-')
                            new_filename = f"{network_name}_{provider_name}_{_mask_npi(provider_npi)}_{safe_date}.pdf"
                            final_filename = get_unique_filename(file_path, new_filename)
                            new_file_path = os.path.join(file_path, final_filename)
                            os.rename(temp_pdf_path, new_file_path)
                            logging.info("Saved PDF -> %s", new_file_path)
                            message_success = True
                        else:
                            os.remove(temp_pdf_path)
                            logging.warning("Missing info in PDF: %s (subj: %s)", attachment.FileName, _safe_subj(subject))
            else:
                logging.debug("Could not parse network/NPI from subject: %s", _safe_subj(subject))
        if message_success:
            message.Unread = False
        processed_count += 1

    logging.info("Processed %d unread email(s).", processed_count)

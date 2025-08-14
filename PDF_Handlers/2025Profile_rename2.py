#!/usr/bin/env python3
#This script renames profiles recursively so target the top directory and itl rename them based on sharepoint folder structure Cred Date/IPA/Profile Prov Name
import os
import re
import sys
from pathlib import Path

from PyPDF2 import PdfReader

# regex to detect dates like 6/20/2025 or 06-20-2025
DATE_REGEX = re.compile(r'^\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*$')

# Windows-reserved filename chars
ILLEGAL = r'[\\/:"*?<>|]+'

def sanitize(s: str) -> str:
    """Remove any illegal filename characters and trim."""
    return re.sub(ILLEGAL, '', s).strip()

def extract_provider_name(pdf_path: Path) -> str:
    """
    Reads the first page of the PDF and returns the provider name.
    If line1 is a date, returns line2; otherwise returns line1.
    """
    reader = PdfReader(str(pdf_path))
    if not reader.pages:
        raise ValueError(f"No pages found in {pdf_path}")
    text = reader.pages[0].extract_text() or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"No text found in first page of {pdf_path}")
    # decide which line is the name
    if DATE_REGEX.match(lines[0]):
        if len(lines) < 2:
            raise ValueError(f"Expected provider name on line 2 in {pdf_path}")
        return lines[1]
    else:
        return lines[0]

def rename_pdfs(base_dir: Path, dry_run: bool = False):
    """
    Walk through base_dir, find all PDFs, extract approval date and network
    from their path, parse the PDF for provider name, and rename.

    Only processes PDFs located under a network subdirectory (i.e. base_dir/<approval_date>/<network>/<file.pdf>).
    """
    for root, dirs, files in os.walk(base_dir):
        for fname in files:
            if not fname.lower().endswith('.pdf'):
                continue
            old_path = Path(root) / fname

            # ensure file is at least two levels under base_dir (approval_date/network)
            try:
                rel_parts = old_path.relative_to(base_dir).parts
            except Exception:
                print(f"Skipping {old_path}: not within base directory")
                continue
            if len(rel_parts) < 3:
                # e.g., directly under approval_date or deeper than expected
                print(f"Skipping {old_path.name}: not in a network subdirectory")
                continue

            # extract approval date and network directory names
            approval_dir, network_dir = rel_parts[0], rel_parts[1]

            # extract provider name from PDF
            try:
                provider = extract_provider_name(old_path)
            except Exception as e:
                print(f"Error reading {old_path}: {e}")
                continue

            # sanitize components
            net  = sanitize(network_dir)
            prov = sanitize(provider)
            date = sanitize(approval_dir)

            # build and sanitize full filename
            raw_name  = f"{net} - {prov} - {date}.pdf"
            new_fname = sanitize(raw_name)
            new_path  = old_path.with_name(new_fname)

            # skip if target already exists
            if new_path.exists():
                print(f"Skipping {old_path.name}: target already exists as {new_fname}")
                continue

            if old_path == new_path:
                print(f"Already named correctly: {old_path.name}")
                continue

            if dry_run:
                print(f"[DRY RUN] Would rename:\n  {old_path.name}\n→ {new_fname}")
            else:
                print(f"Renaming:\n  {old_path.name}\n→ {new_fname}")
                old_path.rename(new_path)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(
        description="Recursively rename provider PDFs to '[Network] - [Provider] - [Approval Date].pdf'")
    p.add_argument('base_dir', help="Path to your main directory")
    p.add_argument('--dry-run', action='store_true',
                   help="Show what would be renamed, but don't actually rename")
    args = p.parse_args()

    base = Path(args.base_dir)
    if not base.is_dir():
        print(f"Error: {base} is not a directory.")
        sys.exit(1)

    rename_pdfs(base, dry_run=args.dry_run)

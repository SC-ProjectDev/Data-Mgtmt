import os
import argparse
import logging
import secrets
import sys
from pathlib import Path

def shred_file(file_path: Path, passes: int = 3, chunk_size: int = 64 * 1024, dry_run: bool = False):
    """
    Securely delete a file by overwriting it with random data multiple times in chunks.
    """
    if dry_run:
        logging.info(f"[DRY RUN] Would shred file: {file_path}")
        return

    try:
        file_size = file_path.stat().st_size
    except (FileNotFoundError, PermissionError) as e:
        logging.warning(f"Cannot access {file_path}: {e}")
        return

    try:
        for pass_num in range(1, passes + 1):
            logging.debug(f"Pass {pass_num}/{passes} on {file_path}")
            with open(file_path, 'r+b', buffering=0) as f:
                f.seek(0)
                bytes_written = 0
                while bytes_written < file_size:
                    write_size = min(chunk_size, file_size - bytes_written)
                    f.write(secrets.token_bytes(write_size))
                    bytes_written += write_size
                f.flush()
                os.fsync(f.fileno())
        # Optionally wipe metadata by updating timestamps
        now = None
        os.utime(file_path, times=now)
        # Finally remove file
        file_path.unlink()
        logging.info(f"Shredded file: {file_path}")
    except Exception as e:
        logging.error(f"Error shredding {file_path}: {e}")


def shred_directory(directory: Path, passes: int = 3, chunk_size: int = 64 * 1024, dry_run: bool = False):
    """
    Securely delete all files in a directory and its subdirectories, leaving the top-level directory intact.
    """
    if dry_run:
        logging.info(f"[DRY RUN] Would shred contents of: {directory}")
    if not directory.exists():
        logging.error(f"Directory not found: {directory}")
        return

    for root, dirs, files in os.walk(directory, topdown=False):
        root_path = Path(root)
        for file_name in files:
            shred_file(root_path / file_name, passes, chunk_size, dry_run)
        for dir_name in dirs:
            dir_path = root_path / dir_name
            try:
                dir_path.rmdir()
                logging.info(f"Removed empty subdirectory: {dir_path}")
            except OSError:
                logging.debug(f"Could not remove directory (not empty or in use): {dir_path}")

    logging.info(f"Completed shredding contents of {directory}")


def parse_args():
    parser = argparse.ArgumentParser(description="Securely shred files or directories.")
    parser.add_argument('path', type=Path, help='File or directory to shred')
    parser.add_argument('-p', '--passes', type=int, default=3, help='Number of overwrite passes')
    parser.add_argument('-c', '--chunk-size', type=int, default=64 * 1024, help='Chunk size in bytes')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without deleting')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable debug output')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt')
    return parser.parse_args()


def main():
    args = parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')

    target = args.path.resolve()

    if not args.yes:
        confirm = input(f"Are you sure you want to shred '{target}'? [y/N]: ").strip().lower()
        if confirm != 'y':
            logging.info("Operation cancelled by user.")
            sys.exit(0)

    if target.is_file():
        shred_file(target, args.passes, args.chunk_size, args.dry_run)
    elif target.is_dir():
        shred_directory(target, args.passes, args.chunk_size, args.dry_run)
    else:
        logging.error(f"Invalid path: {target}")


if __name__ == '__main__':
    main()

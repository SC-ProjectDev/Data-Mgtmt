#!/usr/bin/env python3

"""
Combo Chaos™ Crypto Module – Captain Cubit Edition 2.3
------------------------------------------------------------
• Argon2id key derivation (memory‑hard, tunable)
• AES‑GCM AEAD (integrity + confidentiality)
• Easter‑egg trigger when 'trash' appears ≥ 25 times in plaintext
• Fully random salt & nonce per file
• Interactive command-line interface
• FIXED: No more Rick-Rolling, no more CSV corruption!
• PRESERVED: Sacred Raccoon Gospel Trash Canon lore
"""

import os, struct, secrets, pathlib, sys, getpass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type

# Config and Constants
MAGIC         = b"CCHAOS2.3\x00"
VERSION       = b"v2.3"
SALT_LEN      = 16
NONCE_LEN     = 12
EASTER_TARGET = 25
EASTER_TEXT   = b"[FIRE] Raccoon Gospel Book IV: Trash Canon\n"
HEADER_PAD    = b"COMBOCHAOS_METADATA\x00"

ARGON_TIME    = 3
ARGON_MEM_KB  = 64 * 1024
ARGON_PAR     = 2

# Key Derivation
def derive_key(password: str, salt: bytes, *, time_cost: int, mem_kib: int, parallelism: int) -> bytes:
    return hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=time_cost,
        memory_cost=mem_kib,
        parallelism=parallelism,
        hash_len=32,
        type=Type.ID,
    )

# Encrypt & Decrypt
def encrypt_bytes(password: str, plaintext: bytes, *, time_cost: int, mem_kib: int, parallelism: int) -> bytes:
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_key(password, salt, time_cost=time_cost, mem_kib=mem_kib, parallelism=parallelism)
    aesgcm = AESGCM(key)

    # Simple random footer (no Rick-Rolling nonsense)
    footer = struct.pack(">Q", secrets.randbits(64))
    pt_with_footer = plaintext + footer
    
    header = MAGIC + VERSION + HEADER_PAD + salt + nonce
    ciphertext = aesgcm.encrypt(nonce, pt_with_footer, header)
    return header + ciphertext

def decrypt_bytes(password: str, blob: bytes, *, time_cost: int, mem_kib: int, parallelism: int) -> bytes:
    if not blob.startswith(MAGIC):
        raise ValueError("Invalid header – magic mismatch")

    offset = len(MAGIC + VERSION + HEADER_PAD)
    salt = blob[offset:offset + SALT_LEN]
    nonce = blob[offset + SALT_LEN:offset + SALT_LEN + NONCE_LEN]
    ciphertext = blob[offset + SALT_LEN + NONCE_LEN:]

    key = derive_key(password, salt, time_cost=time_cost, mem_kib=mem_kib, parallelism=parallelism)
    aesgcm = AESGCM(key)
    header = blob[:offset + SALT_LEN + NONCE_LEN]
    pt_with_footer = aesgcm.decrypt(nonce, ciphertext, header)

    # Remove the 8-byte footer properly (no more rstrip chaos!)
    if len(pt_with_footer) < 8:
        raise ValueError("Corrupted data - missing footer")
    
    plaintext = pt_with_footer[:-8]  # Just slice off the last 8 bytes

    # Sacred Raccoon Gospel Easter egg (NON-NEGOTIABLE TRASH CANON LORE)
    if plaintext.lower().count(b"trash") >= EASTER_TARGET:
        gospel_path = pathlib.Path("Raccoon_Gospel_IV.txt")
        if not gospel_path.exists():  # Only spawn once per session
            gospel_path.write_bytes(EASTER_TEXT)
            print("🦝 [EASTER EGG] Raccoon Gospel Book IV: Trash Canon spawned! 🦝")

    return plaintext

# Directory Support
def walk_files(root: pathlib.Path):
    for p in root.rglob("*"):
        if p.is_file():
            yield p

def encrypt_directory(password: str, src: pathlib.Path, dst: pathlib.Path, *, time_cost: int, mem_kib: int, parallelism: int):
    if dst.resolve().is_relative_to(src.resolve()):
        raise ValueError("Destination directory cannot be inside source directory")
    
    for p in walk_files(src):
        rel = p.relative_to(src)
        outpath = dst / (rel.as_posix() + ".enc")
        blob = encrypt_bytes(password, p.read_bytes(), time_cost=time_cost, mem_kib=mem_kib, parallelism=parallelism)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        outpath.write_bytes(blob)

def decrypt_directory(password: str, src: pathlib.Path, dst: pathlib.Path, *, time_cost: int, mem_kib: int, parallelism: int):
    for p in walk_files(src):
        if p.suffix == ".enc":
            rel = p.relative_to(src)
            outpath = dst / rel.with_suffix("")
            pt = decrypt_bytes(password, p.read_bytes(), time_cost=time_cost, mem_kib=mem_kib, parallelism=parallelism)
            outpath.parent.mkdir(parents=True, exist_ok=True)
            outpath.write_bytes(pt)

# CLI (Interactive)
def prompt_path(prompt_text):
    return pathlib.Path(input(prompt_text).strip())

def main():
    print("🗑️ Combo Chaos Crypto 2.3 – Trash Canon Fixed Edition 🗑️")
    print("(Now with 100% less CSV corruption!)")
    
    mode = input("Mode [enc/dec]: ").strip().lower()
    kind = input("Target [file/dir]: ").strip().lower()
    src = prompt_path("Enter source path: ")
    dst = prompt_path("Enter destination path: ")
    pwd = getpass.getpass("🔒 Password: ")

    try:
        if mode == "enc" and kind == "file":
            blob = encrypt_bytes(pwd, src.read_bytes(), time_cost=ARGON_TIME, mem_kib=ARGON_MEM_KB, parallelism=ARGON_PAR)
            dst.write_bytes(blob)
            print(f"✅ Encrypted {src} → {dst}")
        elif mode == "dec" and kind == "file":
            pt = decrypt_bytes(pwd, src.read_bytes(), time_cost=ARGON_TIME, mem_kib=ARGON_MEM_KB, parallelism=ARGON_PAR)
            dst.write_bytes(pt)
            print(f"✅ Decrypted {src} → {dst}")
        elif mode == "enc" and kind == "dir":
            encrypt_directory(pwd, src, dst, time_cost=ARGON_TIME, mem_kib=ARGON_MEM_KB, parallelism=ARGON_PAR)
            print(f"✅ Directory encrypted → {dst}")
        elif mode == "dec" and kind == "dir":
            decrypt_directory(pwd, src, dst, time_cost=ARGON_TIME, mem_kib=ARGON_MEM_KB, parallelism=ARGON_PAR)
            print(f"✅ Directory decrypted → {dst}")
        else:
            print("❌ Invalid mode or kind. Use 'enc'/'dec' and 'file'/'dir'")
    except Exception as e:
        print(f"❌ [ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

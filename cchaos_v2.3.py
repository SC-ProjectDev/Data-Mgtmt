#!/usr/bin/env python3
import os
import struct
import secrets
import pathlib
import sys
import argparse
import getpass
import time
import random
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from argon2.low_level import hash_secret_raw, Type

# Config and Constants
MAGIC        = b"CCHAOS2.3\x00"
VERSION      = b"v2.3"
HEADER_PAD   = b"COMBOCHAOS_METADATA\x00"
SALT_LEN     = 16
NONCE_LEN    = 12
ARGON_FMT    = ">HBH"
ARGON_HDR_SZ = struct.calcsize(ARGON_FMT)

RICK_CHORUS   = b"Never gonna give you up, never gonna let you down\n"
RICK_PROB     = 0.5
EASTER_TARGET = 25
CUBIT_TRIGGER = 10
EASTER_TEXT   = b"[FIRE] Raccoon Gospel Book IV: Trash Canon\n"

DEFAULT_TIME    = 3
DEFAULT_MEM_KB  = 64 * 1024
DEFAULT_PAR     = 2

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

# Chat Simulation
def simulate_chat_response():
    convo_path = "captain_cubit_logs.txt"
    try:
        with open(convo_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("\n💥 [ERROR] Captain Cubit Logs Missing – Raccoon Protocol Abort")
        return

    print("\n🌀 ChatLog Detected – Initiating Recursive GPT Dialog Playback\n")
    time.sleep(2)

    for line in lines:
        if line.strip():
            if "ChatGPT said:" in line:
                print("🤖 GPT is typing...", end="\r")
                time.sleep(random.uniform(1.5, 3.5))
            print(line.strip())
            time.sleep(random.uniform(1.0, 4.0))

    print("\n🔥 SYSTEM MESSAGE: FLAMING CUBIT DETECTED. DIALOG STABILIZED.")
    print("🦝 Terminal sanity restored. Returning control to local user.\n")

# Encryption/Decryption

def encrypt_bytes(password: str, plaintext: bytes, *, time_cost: int, mem_kib: int, parallelism: int) -> bytes:
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_key(password, salt, time_cost=time_cost, mem_kib=mem_kib, parallelism=parallelism)
    aesgcm = AESGCM(key)
    footer = RICK_CHORUS if secrets.randbits(32) / (1 << 32) < RICK_PROB else struct.pack(">Q", secrets.randbits(64))
    pt_with_footer = plaintext + footer
    argon_blob = struct.pack(ARGON_FMT, time_cost, mem_kib // 1024, parallelism)
    header = MAGIC + VERSION + HEADER_PAD + salt + nonce + argon_blob
    ciphertext = aesgcm.encrypt(nonce, pt_with_footer, header)
    return header + ciphertext

def decrypt_bytes(password: str, blob: bytes) -> bytes:
    if not blob.startswith(MAGIC):
        raise ValueError("Invalid header – magic mismatch")

    base = len(MAGIC + VERSION + HEADER_PAD)
    salt  = blob[base : base + SALT_LEN]
    nonce = blob[base + SALT_LEN : base + SALT_LEN + NONCE_LEN]
    raw_argon = blob[base + SALT_LEN + NONCE_LEN : base + SALT_LEN + NONCE_LEN + ARGON_HDR_SZ]
    time_cost, mem_mb, parallelism = struct.unpack(ARGON_FMT, raw_argon)
    mem_kib = mem_mb * 1024
    ciphertext = blob[base + SALT_LEN + NONCE_LEN + ARGON_HDR_SZ :]

    key = derive_key(password, salt, time_cost=time_cost, mem_kib=mem_kib, parallelism=parallelism)
    aesgcm = AESGCM(key)
    header = blob[: base + SALT_LEN + NONCE_LEN + ARGON_HDR_SZ]
    pt_with_footer = aesgcm.decrypt(nonce, ciphertext, header)

    if pt_with_footer.lower().count(b"trash") >= EASTER_TARGET:
        raccoon_ascii = r"""
        ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣶⣶⣿⣿⣷⣶⣤⣄⡀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⢀⣴⣿⡿⠛⠉⠁⠀⠉⠉⠛⠻⢿⣿⣷⣤⡀⠀⠀⠀
        ⠀⠀⠀⠀⠀⢠⣿⡟⠁⠀⠀⣠⣶⣶⣦⣄⠀⠀⠀⠈⠙⣿⣿⣄⠀⠀
        ⠀⠀⠀⠀⠀⣼⣿⠁⠀⠀⠀⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⢹⣿⣿⠀⠀
        ⠀⠀⠀⠀⠀⣿⣿⣀⠀⠀⠀⠹⣿⣿⡿⠏⠀⠀⠀⠀⢀⣸⣿⡿⠀⠀
        ⠀⠀⠀⠀⠀⠹⣿⣿⣿⣷⣶⣦⣤⣤⣤⣴⣶⣾⣿⣿⣿⣿⠏⠀⠀⠀
        """
        sermon = """
🦝🔥 Raccoon Gospel Book IV: Trash Canon 🔥🦝
--------------------------------------------------
"In the beginning, there was only the bin.
And lo, the Trash was plentiful.
The raccoon did feast, and it was good."

🗑️ "For every moldy pizza crust, a miracle."
🗑️ "For every soda can, a song of praise."
🗑️ "Take only what you need... then take more anyway."

📖 *Let the trash be with you, always.*
"""
        print(raccoon_ascii)
        print(sermon)


    if pt_with_footer.lower().count(b"cubit") > CUBIT_TRIGGER:
        simulate_chat_response()

    if pt_with_footer.endswith(RICK_CHORUS):
        plaintext = pt_with_footer[:-len(RICK_CHORUS)]
    else:
        plaintext = pt_with_footer[:-8]
    return plaintext

# Directory Support
def walk_files(root: pathlib.Path):
    for p in root.rglob("*"):
        if p.is_file() and not p.name.startswith('.') and p.suffix != '.enc':
            yield p

def encrypt_directory(password: str, src: pathlib.Path, dst: pathlib.Path, time_cost: int, mem_kib: int, parallelism: int):
    for p in walk_files(src):
        rel = p.relative_to(src)
        outpath = dst / (rel.as_posix() + ".enc")
        blob = encrypt_bytes(password, p.read_bytes(), time_cost=time_cost, mem_kib=mem_kib, parallelism=parallelism)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        outpath.write_bytes(blob)

def decrypt_directory(password: str, src: pathlib.Path, dst: pathlib.Path, time_cost: int, mem_kib: int, parallelism: int):
    for p in src.rglob("*.enc"):
        rel = p.relative_to(src)
        outpath = dst / rel.with_suffix("")
        pt = decrypt_bytes(password, p.read_bytes())
        outpath.parent.mkdir(parents=True, exist_ok=True)
        outpath.write_bytes(pt)

# CLI Interface
def main():
    parser = argparse.ArgumentParser(description="Combo Chaos Crypto 2.3")
    parser.add_argument("mode", choices=["enc","dec"], help="Mode: enc or dec")
    parser.add_argument("kind", choices=["file","dir"], help="Target: file or dir")
    parser.add_argument("src", type=pathlib.Path, help="Source path")
    parser.add_argument("dst", type=pathlib.Path, help="Destination path")
    parser.add_argument("--time", type=int, default=DEFAULT_TIME, help="Argon2 time cost")
    parser.add_argument("--mem", type=int, default=DEFAULT_MEM_KB, help="Argon2 memory in KiB")
    parser.add_argument("--par", type=int, default=DEFAULT_PAR, help="Argon2 parallelism")
    args = parser.parse_args()

    pwd = getpass.getpass("\U0001F512 Password: ")

    try:
        if args.mode == "enc" and args.kind == "file":
            blob = encrypt_bytes(pwd, args.src.read_bytes(), time_cost=args.time, mem_kib=args.mem, parallelism=args.par)
            args.dst.write_bytes(blob)
        elif args.mode == "dec" and args.kind == "file":
            pt = decrypt_bytes(pwd, args.src.read_bytes())
            args.dst.write_bytes(pt)
        elif args.mode == "enc" and args.kind == "dir":
            encrypt_directory(pwd, args.src, args.dst, time_cost=args.time, mem_kib=args.mem, parallelism=args.par)
        elif args.mode == "dec" and args.kind == "dir":
            decrypt_directory(pwd, args.src, args.dst, time_cost=args.time, mem_kib=args.mem, parallelism=args.par)
    except InvalidTag:
        print("[ERROR] Authentication failed – wrong password or tampered file.")
        sys.exit(2)
    except Exception as e:
        print("[ERROR]", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

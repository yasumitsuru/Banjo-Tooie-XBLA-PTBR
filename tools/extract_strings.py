#!/usr/bin/env python3
"""Extractor de strings para X360_strings.dat (Banjo-Tooie XBLA).

Formato (little-endian), ver docs/x360-strings-format.md:
  0x0000  u32 magic/version (0x000605F1)
  0x0004  6 x u32 (propósito desconhecido)
  0x001C  N x u32 comprimentos (bytes, incluindo null terminator)
  0x8E98  7 x u32 (gap, propósito desconhecido)
  0x8EB4  pool de strings null-terminated
Codificação por string:
  - single-byte (cp1252; bytes 0x80-0x8F = placeholders [0xNN];
    bytes 0x90-0x9F = cp1252 (0x92 = U+2019); bytes 0xA0-0xFF = cp1252)
  - UTF-16BE (quando a string contém chars fora do single-byte)
Detecção: se >=80% dos bytes em posições pares forem 0x00 => UTF-16BE.

Uso:
  python tools/extract_strings.py [--dat PATH] [--out DIR]
Saída: <out>/strings.json e <out>/strings.csv
"""
import argparse
import csv
import json
import os
import struct

MAGIC = 0x000605F1
LENGTH_TABLE_OFF = 0x1C
POOL_OFF = 0x8EB4



def decode_single_byte(raw: bytes) -> str:
    """Decodifica string single-byte: ASCII + placeholders [0x80]..[0x8F] + cp1252.

    Bytes 0x80-0x8F: controller glyph placeholders [0xNN].
    Bytes 0x90-0x9F: decoded via cp1252 codec (0x92 = U+2019).
    Bytes 0xA0-0xFF: decoded via cp1252 codec.
    Undefined cp1252 bytes in 0x90-0x9F produce U+FFFD via errors='replace'.
    """
    out = []
    for b in raw:
        if b == 0:
            break  # null terminator
        if b < 0x80:
            out.append(chr(b))
        elif b <= 0x8F:
            out.append(f"[0x{b:02X}]")  # placeholder de botão/fonte
        else:
            # 0x90-0xFF: decode via cp1252
            try:
                out.append(bytes([b]).decode("cp1252"))
            except UnicodeDecodeError:
                out.append("\ufffd")  # replacement char for undefined bytes
    return "".join(out)


def is_utf16be(s: bytes) -> bool:
    n = len(s) // 2
    if n < 2:
        return False
    even_zero = sum(1 for i in range(0, len(s), 2) if s[i] == 0)
    return even_zero >= 0.8 * n


def extract(data: bytes):
    magic = struct.unpack_from("<I", data, 0x0)[0]
    if magic != MAGIC:
        raise ValueError(f"magic inesperado: {magic:#010x} (esperado {MAGIC:#010x})")

    # Determina N: maior N tal que soma(lens[0:N]) == POOL_END - POOL_OFF,
    # onde POOL_END é o menor offset >= POOL_OFF com a propriedade de que
    # o byte seguinte à última string seja o fim da região de strings.
    # Estratégia: caminhar somando comprimentos até a soma exceder o fim do
    # arquivo ou o próximo "comprimento" deixar de ser plausível.
    n = 0
    off = POOL_OFF
    total = 0
    while True:
        lv = struct.unpack_from("<I", data, LENGTH_TABLE_OFF + 4 * n)[0]
        if lv == 0 or lv > 0x10000 or off + lv > len(data):
            break
        # plausibilidade: byte do terminador deve ser 0x00
        if data[off + lv - 1] != 0:
            break
        off += lv
        total += lv
        n += 1
    pool_end = off
    return magic, n, pool_end


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dat", default=os.path.join(
        "game", "Banjo-Tooie XBLA Extract", "RAWFiles", "X360_strings.dat"))
    ap.add_argument("--out", default="work/strings")
    args = ap.parse_args()

    with open(args.dat, "rb") as f:
        data = f.read()

    magic, n, pool_end = extract(data)
    lens = struct.unpack_from(f"<{n}I", data, LENGTH_TABLE_OFF)

    rows = []
    off = POOL_OFF
    for i, lv in enumerate(lens):
        raw = data[off:off + lv]
        enc = "utf-16-be" if is_utf16be(raw) else "cp1252"
        if enc == "utf-16-be":
            text = raw[:-2].decode("utf-16-be", errors="replace")
        else:
            text = decode_single_byte(raw)
        rows.append({
            "index": i,
            "offset": off,
            "byte_length": lv,
            "encoding": enc,
            "text": text,
        })
        off += lv

    os.makedirs(args.out, exist_ok=True)
    jpath = os.path.join(args.out, "strings.json")
    cpath = os.path.join(args.out, "strings.csv")
    # Canonicalize source path to forward slashes for cross-platform stability
    source_path = args.dat.replace(os.sep, "/")
    with open(jpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump({
            "source": source_path,
            "magic": f"{magic:#010x}",
            "count": n,
            "pool_offset": f"{POOL_OFF:#x}",
            "pool_end": f"{pool_end:#x}",
            "strings": rows,
        }, f, ensure_ascii=False, indent=1)
    with open(cpath, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["index", "offset", "byte_length", "encoding", "text"])
        w.writeheader()
        for r in rows:
            w.writerow({**r, "offset": f"{r['offset']:#x}"})

    # Relatório curto (saída limitada)
    print(f"magic={magic:#010x} strings={n} pool={POOL_OFF:#x}..{pool_end:#x}")
    encs = {}
    for r in rows:
        encs[r["encoding"]] = encs.get(r["encoding"], 0) + 1
    print("encodings:", encs)
    print("--- amostra (primeiras 15) ---")
    for r in rows[:15]:
        print(f"{r['index']:>5} {r['offset']:#06x} {r['encoding']:<9} {r['text'][:60]!r}")
    # Validação contra strings conhecidas
    known = ["PLAY GAME", "LEADERBOARDS", "ACHIEVEMENTS", "HELP & OPTIONS",
             "UNLOCK FULL GAME", "RETURN TO GAME LIBRARY", "HOW TO PLAY",
             "CONTROLS", "SETTINGS", "CREDITS", "MUSIC VOLUME",
             "SOUND EFFECTS VOLUME", "GAME TOTAL", "RANK", "JIGGIES", "NOTES",
             "TIME", "GAMERTAG", "SCORE", "BOSSES", "CONTROL METHOD",
             "RESUME GAME", "VIEW TOTALS", "TRIAL GAME", "BASIC MOVES",
             "SPECIAL MOVES", "MULTIPLAYER HINTS", "MINI-GAMES HINTS",
             "HIGH / BACKFLIP JUMP", "BEAK BARGE ATTACK", "BEAK BUSTER ATTACK"]
    texts = {r["text"] for r in rows}
    # algumas strings conhecidas podem conter glifos; checa por prefixo/substring
    found, missing = [], []
    for k in known:
        if k in texts:
            found.append(k)
        elif any(k in t for t in texts):
            found.append(k + " (substring)")
        else:
            missing.append(k)
    print(f"--- validação: {len(found)}/{len(known)} conhecidas presentes ---")
    for m in missing:
        print("  FALTA:", m)
    print("out:", jpath, cpath)


if __name__ == "__main__":
    main()

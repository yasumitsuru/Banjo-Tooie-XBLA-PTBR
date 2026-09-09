#!/usr/bin/env python3
"""Translate source indices 100..149 to pt-BR and produce batch artifact + merge.

Deterministic: running twice produces byte-identical output.

Terminology decisions for this batch:
  - LEADERBOARD -> PLACAR DE LÍDERES (idiomatic pt-BR)
  - PLAY GAME -> JOGAR (consistent with TM proposed entry)
  - ZUBBA'S NEST -> NINHO DOS ZUBBAS (ZUBBAS = creature name)
  - ISLE O' HAGS -> ILHA DOS HAGS (HAGS = creature name)
  - GAME TOTAL -> TOTAL DO JOGO (consistent with index 13)
  - Legal: Microsoft/Dolby/ESRB names preserved
"""

import json
import os
import sys

TRANSLATIONS = {
    100: "NINHO DOS ZUBBAS",
    101: "TOWER OF TRAGEDY",
    102: "SELECIONAR",
    103: "VOLTAR",
    104: "BAIXAR VOLUME",
    105: "AUMENTAR VOLUME",
    106: "SUBIR",
    107: "DESCER",
    108: "PRESSIONE START PARA JOGAR",
    109: "JOGAR",
    110: "APAGAR SALVAMENTO",
    111: "DESBLOQUEAR O JOGO COMPLETO",
    112: "VOLTAR À BIBLIOTECA DE JOGOS",
    113: "APAGAR SALVAMENTO",
    114: "CANCELAR",
    115: "ACEITAR TREINAMENTO",
    116: "RECUSAR TREINAMENTO",
    117: "AMIGOS",
    118: "MINHA PONTUAÇÃO",
    119: "GERAL",
    120: "NENHUM JOGADOR ESTÁ CLASSIFICADO NESTE PLACAR DE LÍDERES AINDA.",
    121: "SEUS AMIGOS AINDA NÃO ESTÃO CLASSIFICADOS NESTE PLACAR DE LÍDERES",
    122: "VOCÊ AINDA NÃO ESTÁ CLASSIFICADO NESTE PLACAR DE LÍDERES",
    123: "POR FAVOR, AGUARDE",
    124: "NÚMERO TOTAL DE JOGADORES",
    125: "ANTERIOR",
    126: "PRÓXIMO",
    127: "TENTAR DE NOVO",
    128: "CONTINUAR OFFLINE",
    129: "SALVANDO...",
    130: "CHEAT ATIVADO - SALVAMENTO E ATUALIZAÇÕES DO PLACAR DE LÍDERES DESATIVADOS",
    131: "AVISO DO ESRB: INTERAÇÕES ONLINE NÃO AVALIADAS PELO ESRB",
    132: "FALHA AO SALVAR",
    133: "CONTINUAR JOGANDO",
    134: "DESISTIR E SAIR",
    135: "CARREGANDO JOGO...",
    136: "ERRO AO CARREGAR PLACARES DE LÍDERES",
    137: "SALVANDO CONTEÚDO. POR FAVOR, NÃO DESLIGUE SEU CONSOLE.",
    138: "TROCAR DISPOSITIVO DE ARMAZENAMENTO",
    139: "MELHOR TEMPO PESSOAL!",
    140: "INTERAGIR",
    141: "PULAR",
    142: "x 2009 MICROSOFT CORPORATION.",
    143: "TODOS OS DIREITOS RESERVADOS.",
    144: "DOLBY E O SÍMBOLO DE DUPLA-D SÃO",
    145: "MARCAS REGISTRADAS DE DOLBY LABORATORIES.",
    146: "TOTAL DO JOGO",
    147: "ILHA DOS HAGS",
    148: "MAYAHEM TEMPLE",
    149: "GLITTER GULCH MINE",
}

# Load source
with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

# Validate source indices
expected_indices = list(range(100, 150))
actual_indices = sorted([s["index"] for s in src_strings if 100 <= s["index"] <= 149])
if actual_indices != expected_indices:
    print(f"ERROR: Expected indices {expected_indices}, got {actual_indices}")
    sys.exit(1)
print(f"Source indices 100..149: {len(actual_indices)} entries found")

# Build batch artifact
batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 100 <= idx <= 149:
        batch_entries.append({
            "index": idx,
            "source_text": s["text"],
            "translation": TRANSLATIONS[idx],
        })

batch_artifact = {
    "batch_id": "batch-0100-0149",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": list(range(100, 150)),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0100-0149.json"
with open(batch_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(batch_artifact, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
print(f"Batch artifact written to {batch_path}")
print(f"Total entries: {len(batch_entries)}")

# Merge into translated.json
with open("translation/pt-BR/translated.json", "r", encoding="utf-8") as f:
    trans_data = json.load(f)

trans_strings = trans_data["strings"]
trans_map = {idx: TRANSLATIONS[idx] for idx in range(100, 150)}

merged_count = 0
for i, rec in enumerate(trans_strings):
    idx = rec.get("index", i)
    if idx in trans_map:
        trans_strings[i]["translation"] = trans_map[idx]
        merged_count += 1

merged_path = "translation/pt-BR/translated.json"
with open(merged_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(trans_data, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
print(f"Merged {merged_count} translations into {merged_path}")

# Verify
with open(merged_path, "r", encoding="utf-8") as f:
    verify_data = json.load(f)
verify_strings = verify_data["strings"]

translated_in_range = [s for s in verify_strings if 100 <= s["index"] <= 149 and s.get("translation") is not None]
incomplete_in_range = [s for s in verify_strings if 100 <= s["index"] <= 149 and s.get("translation") is None]
all_translated = [s for s in verify_strings if s.get("translation") is not None]
all_incomplete = [s for s in verify_strings if s.get("translation") is None]
en_strings = [s for s in verify_strings if s["index"] < 1521]
non_en = [s for s in verify_strings if s["index"] >= 1521]
en_incomplete = [s for s in en_strings if s.get("translation") is None]
non_en_translated = [s for s in non_en if s.get("translation") is not None]

print(f"\nVerification:")
print(f"  Translated in range 100..149: {len(translated_in_range)}")
print(f"  Incomplete in range 100..149: {len(incomplete_in_range)}")
print(f"\nTotals:")
print(f"  Total strings: {len(verify_strings)}")
print(f"  Translated: {len(all_translated)}")
print(f"  Incomplete: {len(all_incomplete)}")
print(f"  EN (0-1520): {len(en_strings)}")
print(f"  Non-EN: {len(non_en)}")

# No duplicates
assigned = [s["index"] for s in batch_entries]
print(f"\nNo duplicates: {len(assigned) == len(set(assigned))}")

# No null/blank
null_trans = [e for e in batch_entries if not e["translation"]]
blank_trans = [e for e in batch_entries if e["translation"].strip() == ""]
print(f"Null translations in batch: {len(null_trans)}")
print(f"Blank translations in batch: {len(blank_trans)}")

# Source matches
mismatch = []
for entry in batch_entries:
    idx = entry["index"]
    src_rec = next((s for s in src_strings if s["index"] == idx), None)
    if src_rec and src_rec["text"] != entry["source_text"]:
        mismatch.append(idx)
print(f"Source text mismatches: {len(mismatch)}")

# Seeds
for idx, expected in {101: "TOWER OF TRAGEDY", 148: "MAYAHEM TEMPLE", 149: "GLITTER GULCH MINE"}.items():
    entry = next((e for e in batch_entries if e["index"] == idx), None)
    status = "OK" if entry and entry["translation"] == expected else "MISMATCH"
    print(f"  Seed {idx} ({expected}): {status}")

# cp1252
cp1252_errors = []
for entry in batch_entries:
    for ch in entry["translation"]:
        code = ord(ch)
        if code > 0xFF:
            cp1252_errors.append((entry["index"], ch, code))
        if ch == "\r":
            cp1252_errors.append((entry["index"], "\r", 0x0D))
if cp1252_errors:
    print(f"\nWARNING: cp1252 errors:")
    for idx, ch, code in cp1252_errors:
        print(f"  Index {idx}: char={repr(ch)} ord=U+{code:04X}")
else:
    print(f"\nAll translations are cp1252 compatible")

# Expected counts
print(f"\nExpected post-merge counts:")
print(f"  Total: {len(verify_strings)} (expected 5174) {'OK' if len(verify_strings) == 5174 else 'MISMATCH'}")
print(f"  Translated: {len(all_translated)} (expected 155) {'OK' if len(all_translated) == 155 else 'MISMATCH'}")
print(f"  EN incomplete: {len(en_incomplete)} (expected 880) {'OK' if len(en_incomplete) == 880 else 'MISMATCH'}")
print(f"  EN: {len(en_strings)} (expected 1035) {'OK' if len(en_strings) == 1035 else 'MISMATCH'}")
print(f"  Non-EN: {len(non_en)} (expected 4139) {'OK' if len(non_en) == 4139 else 'MISMATCH'}")
print(f"  Non-EN translated: {len(non_en_translated)}")
print("\nDone.")

#!/usr/bin/env python3
"""Translate source indices 200..249 to pt-BR and produce batch artifact + merge.

Deterministic: running twice produces byte-identical output.

Terminology decisions for this batch:
  - Banjo-Tooie (202): título do jogo — manter em inglês (título completo).
  - Mini-jogos (203-214): manter em inglês
    (padrão estabelecido: Balloon Burst, Hoop Hurry, Saucer of Peril,
     Trash Can Germs, Chompa's Belly, Pot O'Gold, ZUBBA'S HIVE,
     TWINKLIES PACKING, DODGEMS CHALLENGE, MINI-SUB CHALLENGE).
  - TRIAL GAME (215): "DEMONSTRAÇÃO" (consistente com índice 32, all-caps).
  - Achievement names (225-230 title case / 231-237 all caps):
    manter em inglês — nomes próprios de conquistas.
  - "WELL DONE!" (221): "BOM TRABALHO!" (paralelo ao glossário índice 175).
  - "CONGRATULATIONS!" (239-240): "PARABÉNS!" (pt-BR natural; distinto de "WELL DONE!" = "BOM TRABALHO!").
  - "MODERN" / "CLASSIC" (241-244): traduzir para pt-BR.
  - JIGGY (245-247): nome próprio do coletável — manter em inglês;
    HINT/TIPS traduzidos como DICA(S) DE JIGGY (padrão DE/ES/IT: JIGGY-HINWEIS,
    CONSEJOS SOBRE LOS JIGGYS, SUGGERIMENTI JIGGY).
  - TARGITZAN (248-249): nome próprio — manter em inglês.
  - "Stop 'n' Swop" (223): franquia/nome próprio — manter em inglês.
  - KLUNGO (222): nome próprio — manter em inglês.
"""

import json
import os
import sys

TRANSLATIONS = {
    200: "Sobrescrever e salvar",
    201: "FALHA AO SALVAR AS CONFIGURAÇÕES NO PERFIL DE JOGADOR",
    202: "Banjo-Tooie",
    203: "BALLOON BURST CHALLENGE",
    204: "HOOP HURRY CHALLENGE",
    205: "SAUCER OF PERIL RIDE",
    206: "DODGEMS CHALLENGE (1-ON-1)",
    207: "DODGEMS CHALLENGE (2-ON-1)",
    208: "DODGEMS CHALLENGE (3-ON-1)",
    209: "MINI-SUB CHALLENGE",
    210: "CHOMPA'S BELLY",
    211: "TWINKLIES PACKING",
    212: "POT O'GOLD",
    213: "TRASH CAN GERMS",
    214: "ZUBBA'S HIVE",
    215: "DEMONSTRAÇÃO",
    216: "ESTA É APENAS UMA VERSÃO DE DEMONSTRAÇÃO DE BANJO-TOOIE.  DESBLOQUEIE A VERSÃO COMPLETA PARA MAIS DIVERSÃO!",
    217: "Opção indisponível",
    218: "Esta opção está disponível apenas no jogo completo",
    219: "Desbloquear o jogo completo",
    220: "Continuar com a demonstração",
    221: "BOM TRABALHO!",
    222: "VOCÊ GANHOU UMA CONQUISTA POR DERROTAR KLUNGO, MAS PRECISA DESBLOQUEAR A VERSÃO COMPLETA PARA RECEBÊ-LA!",
    223: "Stop 'n' Swop II encontrado",
    224: "- Oh não, não de novo...",
    225: "- Lucky Loser",
    226: "- Better Than A Slap",
    227: "- And The Winner Is…",
    228: "- Now Who’s Boss?",
    229: "- Calmer Chameleon",
    230: "- Heroic Failure",
    231: "OH NO, NOT AGAIN...",
    232: "LUCKY LOSER",
    233: "BETTER THAN A SLAP",
    234: "AND THE WINNER IS...",
    235: "NOW WHO'S BOSS?",
    236: "CALMER CHAMELEON",
    237: "HEROIC FAILURE",
    238: "SUA PONTUAÇÃO SUPERA",
    239: "PARABÉNS! MELHOR MARCA PESSOAL!",
    240: "PARABÉNS! VOCÊ DERROTOU",
    241: "MODERNO",
    242: "MODERNO - INVERTIDO",
    243: "CLÁSSICO",
    244: "CLÁSSICO - INVERTIDO",
    245: "JIGGY",
    246: "DICA DE JIGGY",
    247: "DICAS DE JIGGY",
    248: " DERROTAR TARGITZAN",
    249: " DENTRO DO TEMPLO DE TARGITZAN",
}

# Load source
with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

# Validate source indices
expected_indices = list(range(200, 250))
actual_indices = sorted([s["index"] for s in src_strings if 200 <= s["index"] <= 249])
if actual_indices != expected_indices:
    print(f"ERROR: Expected indices {expected_indices}, got {actual_indices}")
    sys.exit(1)
print(f"Source indices 200..249: {len(actual_indices)} entries found")

# Build batch artifact
batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 200 <= idx <= 249:
        batch_entries.append({
            "index": idx,
            "source_text": s["text"],
            "translation": TRANSLATIONS[idx],
        })

batch_artifact = {
    "batch_id": "batch-0200-0249",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": list(range(200, 250)),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0200-0249.json"
with open(batch_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(batch_artifact, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
print(f"Batch artifact written to {batch_path}")
print(f"Total entries: {len(batch_entries)}")

# Merge into translated.json
with open("translation/pt-BR/translated.json", "r", encoding="utf-8") as f:
    trans_data = json.load(f)

trans_strings = trans_data["strings"]
trans_map = {idx: TRANSLATIONS[idx] for idx in range(200, 250)}

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

translated_in_range = [s for s in verify_strings if 200 <= s["index"] <= 249 and s.get("translation") is not None]
incomplete_in_range = [s for s in verify_strings if 200 <= s["index"] <= 249 and s.get("translation") is None]
all_translated = [s for s in verify_strings if s.get("translation") is not None]
all_incomplete = [s for s in verify_strings if s.get("translation") is None]
en_strings = [s for s in verify_strings if s["index"] < 1521]
non_en = [s for s in verify_strings if s["index"] >= 1521]
en_incomplete = [s for s in en_strings if s.get("translation") is None]
non_en_translated = [s for s in non_en if s.get("translation") is not None]

print(f"\nVerification:")
print(f"  Translated in range 200..249: {len(translated_in_range)}")
print(f"  Incomplete in range 200..249: {len(incomplete_in_range)}")
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

# cp1252 (real encoding check — U+2026/U+2019 etc. are cp1252-encodable)
cp1252_errors = []
for entry in batch_entries:
    try:
        entry["translation"].encode("cp1252")
    except UnicodeEncodeError as e:
        cp1252_errors.append((entry["index"], str(e)))
if cp1252_errors:
    print(f"\nWARNING: cp1252 errors:")
    for idx, err in cp1252_errors:
        print(f"  Index {idx}: {err}")
else:
    print(f"\nAll translations are cp1252 compatible")

# Expected counts
print(f"\nExpected post-merge counts:")
print(f"  Total: {len(verify_strings)} (expected 5174) {'OK' if len(verify_strings) == 5174 else 'MISMATCH'}")
print(f"  Translated: {len(all_translated)} (expected 250) {'OK' if len(all_translated) == 250 else 'MISMATCH'}")
print(f"  EN incomplete: {len(en_incomplete)} (expected 785) {'OK' if len(en_incomplete) == 785 else 'MISMATCH'}")
print(f"  EN: {len(en_strings)} (expected 1035) {'OK' if len(en_strings) == 1035 else 'MISMATCH'}")
print(f"  Non-EN: {len(non_en)} (expected 4139) {'OK' if len(non_en) == 4139 else 'MISMATCH'}")
print(f"  Non-EN translated: {len(non_en_translated)}")

# Selective reusable TM proposals (short, reusable terms only — long one-off
# messages are intentionally excluded).
SELECTIVE_TM_NOTES = {
    200: "UI label — botão de ação",
    201: "UI erro — paralelo a índice 186",
    202: "título do jogo",
    203: "mini-jogo — nome próprio",
    204: "mini-jogo — nome próprio",
    205: "mini-jogo — nome próprio",
    206: "mini-jogo — nome próprio",
    207: "mini-jogo — nome próprio",
    208: "mini-jogo — nome próprio",
    209: "mini-jogo — nome próprio",
    210: "mini-jogo — nome próprio",
    211: "mini-jogo — nome próprio",
    212: "mini-jogo — nome próprio",
    213: "mini-jogo — nome próprio",
    214: "mini-jogo — nome próprio",
    215: "UI — consistente com índice 28 e 174",
    217: "UI label",
    218: "UI mensagem",
    219: "UI label — consistente com índice 30 e 176",
    220: "UI label — consistente com índice 177",
    221: "UI label — paralelo a 'WELL DONE' (glossário 175)",
    223: "UI mensagem — 'Stop 'n' Swop' franquia mantida",
    238: "UI label",
    239: "UI label — 'PARABÉNS!' distinto de 'BOM TRABALHO!'",
    240: "UI label",
    241: "modo de jogo",
    242: "modo de jogo",
    243: "modo de jogo",
    244: "modo de jogo",
    245: "coletável — nome próprio",
    246: "UI label — JIGGY nome próprio",
    247: "UI label — JIGGY nome próprio",
    248: "UI instrução — TARGITZAN nome próprio",
    249: "UI instrução — TARGITZAN nome próprio",
}

# New TM entries to add (selective set only)
new_tm_entries = []
for idx in sorted(SELECTIVE_TM_NOTES):
    trans = TRANSLATIONS[idx]
    src_rec = next((s for s in src_strings if s["index"] == idx), None)
    if src_rec:
        new_tm_entries.append({
            "source": src_rec["text"],
            "translation": trans,
            "status": "proposed",
            "source_index": idx,
            "notes": f"batch 0200-0249 - {SELECTIVE_TM_NOTES[idx]}",
        })

tm_path = "translation/pt-BR/tm.json"
with open(tm_path, "r", encoding="utf-8") as f:
    tm_data = json.load(f)

existing_sources = {e["source"] for e in tm_data["entries"]}
# Upsert by (source, source_index) so corrected notes/translations are
# reproduced on rerun (append-only would leave stale entries unchanged).
by_pair = {(e["source"], e.get("source_index")): e for e in tm_data["entries"]}
added_count = 0
updated_count = 0
for entry in new_tm_entries:
    pair = (entry["source"], entry["source_index"])
    if pair in by_pair:
        existing = by_pair[pair]
        existing["source"] = entry["source"]
        existing["translation"] = entry["translation"]
        existing["notes"] = entry["notes"]
        updated_count += 1
    elif entry["source"] not in existing_sources:
        tm_data["entries"].append(entry)
        existing_sources.add(entry["source"])
        by_pair[pair] = entry
        added_count += 1
    # else: source already exists under a different source_index (dedup) -> skip

with open(tm_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(tm_data, f, ensure_ascii=False, indent=2, sort_keys=False)
    f.write("\n")
print(f"\nTM: added {added_count} new, updated {updated_count} existing (total: {len(tm_data['entries'])})")

# EN translated count
en_translated_count = len([s for s in en_strings if s.get("translation") is not None])
print(f"\nFinal EN counts: translated={en_translated_count} incomplete={len(en_incomplete)}")
print("\nDone.")

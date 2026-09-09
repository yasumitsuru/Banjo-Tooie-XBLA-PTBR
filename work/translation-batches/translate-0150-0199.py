#!/usr/bin/env python3
"""Translate source indices 150..199 to pt-BR and produce batch artifact + merge.

Deterministic: running twice produces byte-identical output.

Terminology decisions for this batch:
  - WITCHY WORLD, GRUNTY INDUSTRIES, HAILFIRE PEAKS, CLOUD CUCKOOLAND,
    CAULDRON KEEP: approved seeds — preserve byte-for-byte.
  - JOLLY ROGER'S LAGOON, TERRYDACTYLAND: fase (proper name) — keep EN.
  - STOP 'N' SWOP: franchise / proper name — keep EN.
  - BOSS TOTAL: UI label — "TOTAL DO CHEFE" (parallel to "GAME TOTAL" → "TOTAL DO JOGO").
  - PERSONAL BEST: UI label — "MELHOR MARCA PESSOAL" (parallel to "PERSONAL BEST TIME!" → "MELHOR TEMPO PESSOAL!").
  - Guest Gamer Profile / Gamer Profile: UI — "PERFIL DE JOGADOR".
  - Trial Game: "Jogo de Demonstração" (consistent with index 28).
  - BACK: UI — "VOLTAR" (consistent with index 103).
  - Connect to Xbox LIVE: UI — "CONECTAR AO XBOX LIVE".
  - OK: UI button — "OK" (standard pt-BR UI convention).
"""

import json
import os
import sys

TRANSLATIONS = {
    150: "WITCHY WORLD",
    151: "JOLLY ROGER'S LAGOON",
    152: "TERRYDACTYLAND",
    153: "GRUNTY INDUSTRIES",
    154: "HAILFIRE PEAKS",
    155: "CLOUD CUCKOOLAND",
    156: "CAULDRON KEEP",
    157: "STOP 'N' SWOP",
    158: "TOTAL DO CHEFE",
    159: "MELHOR MARCA PESSOAL",
    160: "PERFIL DE JOGADOR CONVIDADO",
    161: "O perfil de jogador convidado não pode acessar esta funcionalidade. Use um perfil de jogador diferente.",
    162: "OK",
    163: "SALVAMENTO CORROMPIDO",
    164: "Seus dados de salvamento parecem corrompidos. Criar um novo salvamento e sobrescrever o corrompido?",
    165: "Criar novo salvamento",
    166: "Jogar sem salvar",
    167: "ESTA FUNCIONALIDADE REQUER UM PERFIL DE JOGADOR CONECTADO AO XBOX LIVE",
    168: "TROCAR PERFIL DE JOGADOR",
    169: "VOLTAR",
    170: "Perfil de jogador não está online",
    171: "Este jogo tem algumas funcionalidades que exigem um perfil de jogador com Xbox LIVE, mas você está atualmente offline.",
    172: "Conectar ao Xbox LIVE",
    173: "Continuar jogando offline",
    174: "Jogo de Demonstração",
    175: "Bom trabalho! Esta conquista só pode ser concedida no jogo completo do Banjo-Tooie, o que torna este o momento ideal para gastar seu dinheiro, desbloquear o jogo completo e recebê-la. Não concorda?",
    176: "Desbloquear o jogo completo",
    177: "Continuar com a demonstração",
    178: "PERFIL DE JOGADOR OFFLINE",
    179: "SEU PERFIL DE JOGADOR ESTÁ ATUALMENTE OFFLINE. PARA ENVIAR SUA PONTUAÇÃO AO PLACAR DE LÍDERES ONLINE, PRESSIONE O BOTÃO DO GUIA XBOX E CONECTE-SE AO XBOX LIVE.",
    180: "Sessão encerrada",
    181: "Você voltou à tela de título porque a sessão do seu perfil de jogador foi encerrada.",
    182: "Continuar jogando",
    183: "Erro ao carregar",
    184: "\"Banjo-Tooie\" falhou ao carregar e não pode continuar.",
    185: "Voltar à biblioteca de jogos",
    186: "Falha ao salvar",
    187: "Seu dispositivo de armazenamento não está disponível ou apresenta um erro",
    188: "Selecionar um novo dispositivo",
    189: "Continuar sem salvar",
    190: "Perfil de jogador não encontrado",
    191: "Seu perfil de jogador não está mais disponível. Sua conquista será armazenada com seu salvamento de jogo.",
    192: "OK",
    193: "OLHAR AO REDOR",
    194: "Desconectado",
    195: "Você voltou ao menu porque foi desconectado do Xbox LIVE.",
    196: "Continuar jogando",
    197: "Sobrescrever salvamento?",
    198: "Esse dispositivo de armazenamento já contém um salvamento. Deseja sobrescrevê-lo?",
    199: "Não - não sobrescrever",
}

# Load source
with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

# Validate source indices
expected_indices = list(range(150, 200))
actual_indices = sorted([s["index"] for s in src_strings if 150 <= s["index"] <= 199])
if actual_indices != expected_indices:
    print(f"ERROR: Expected indices {expected_indices}, got {actual_indices}")
    sys.exit(1)
print(f"Source indices 150..199: {len(actual_indices)} entries found")

# Build batch artifact
batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 150 <= idx <= 199:
        batch_entries.append({
            "index": idx,
            "source_text": s["text"],
            "translation": TRANSLATIONS[idx],
        })

batch_artifact = {
    "batch_id": "batch-0150-0199",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": list(range(150, 200)),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0150-0199.json"
with open(batch_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(batch_artifact, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
print(f"Batch artifact written to {batch_path}")
print(f"Total entries: {len(batch_entries)}")

# Merge into translated.json
with open("translation/pt-BR/translated.json", "r", encoding="utf-8") as f:
    trans_data = json.load(f)

trans_strings = trans_data["strings"]
trans_map = {idx: TRANSLATIONS[idx] for idx in range(150, 200)}

merged_count = 0
for i, rec in enumerate(trans_strings):
    idx = rec.get("index", i)
    if idx in trans_map:
        # Preserve existing seed translations byte-for-byte
        if idx in (150, 153, 154, 155, 156):
            existing = trans_strings[i].get("translation")
            if existing is not None and existing != trans_map[idx]:
                print(f"  WARNING: Seed index {idx} has different existing value: {repr(existing)} vs {repr(trans_map[idx])}")
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

translated_in_range = [s for s in verify_strings if 150 <= s["index"] <= 199 and s.get("translation") is not None]
incomplete_in_range = [s for s in verify_strings if 150 <= s["index"] <= 199 and s.get("translation") is None]
all_translated = [s for s in verify_strings if s.get("translation") is not None]
all_incomplete = [s for s in verify_strings if s.get("translation") is None]
en_strings = [s for s in verify_strings if s["index"] < 1521]
non_en = [s for s in verify_strings if s["index"] >= 1521]
en_incomplete = [s for s in en_strings if s.get("translation") is None]
non_en_translated = [s for s in non_en if s.get("translation") is not None]

print(f"\nVerification:")
print(f"  Translated in range 150..199: {len(translated_in_range)}")
print(f"  Incomplete in range 150..199: {len(incomplete_in_range)}")
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
for idx, expected in {150: "WITCHY WORLD", 153: "GRUNTY INDUSTRIES", 154: "HAILFIRE PEAKS", 155: "CLOUD CUCKOOLAND", 156: "CAULDRON KEEP"}.items():
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
print(f"  Translated: {len(all_translated)} (expected 200) {'OK' if len(all_translated) == 200 else 'MISMATCH'}")
print(f"  EN incomplete: {len(en_incomplete)} (expected 835) {'OK' if len(en_incomplete) == 835 else 'MISMATCH'}")
print(f"  EN: {len(en_strings)} (expected 1035) {'OK' if len(en_strings) == 1035 else 'MISMATCH'}")
print(f"  Non-EN: {len(non_en)} (expected 4139) {'OK' if len(non_en) == 4139 else 'MISMATCH'}")
print(f"  Non-EN translated: {len(non_en_translated)}")

# Selective reusable TM proposals (short, reusable terms only — long one-off
# messages are intentionally excluded). Matches the glossary table
# "Novos termos propostos — Lote 0150–0199".
SELECTIVE_TM_NOTES = {
    151: "fase — nome próprio",
    152: "fase — nome próprio",
    157: "franquia — nome próprio",
    158: "UI label — paralelo a GAME TOTAL",
    159: "UI label",
    160: "UI",
    163: "UI",
    165: "UI",
    166: "UI",
    168: "UI",
    170: "UI",
    172: "UI",
    173: "UI",
    174: "UI — consistente com índice 28",
    176: "UI — consistente com índice 30",
    177: "UI",
    178: "UI",
    180: "UI",
    182: "UI — consistente com índice 133",
    183: "UI",
    186: "UI — consistente com índice 132",
    188: "UI",
    189: "UI",
    190: "UI",
    193: "UI",
    194: "UI",
    197: "UI",
    199: "UI",
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
            "notes": f"batch 0150-0199 - {SELECTIVE_TM_NOTES[idx]}",
        })

tm_path = "translation/pt-BR/tm.json"
with open(tm_path, "r", encoding="utf-8") as f:
    tm_data = json.load(f)

existing_sources = {e["source"] for e in tm_data["entries"]}
added_count = 0
for entry in new_tm_entries:
    if entry["source"] not in existing_sources:
        tm_data["entries"].append(entry)
        existing_sources.add(entry["source"])
        added_count += 1

with open(tm_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(tm_data, f, ensure_ascii=False, indent=2, sort_keys=False)
    f.write("\n")
print(f"\nTM: added {added_count} new entries (total: {len(tm_data['entries'])})")

# Expected totals
en_translated_count = len([s for s in en_strings if s.get("translation") is not None])
print(f"\nFinal EN counts: translated={en_translated_count} incomplete={len(en_incomplete)}")
print("\nDone.")

#!/usr/bin/env python3
"""Translate source indices 50..99 to pt-BR and produce batch artifact + merge."""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Translations for indices 50..99
# Rules:
#   - Proper names (Banjo, Kazooie, Jiggies, Mumbo, Grunty, Chompa, Zubbas,
#     etc.) → keep EN
#   - Minigame names per glossary: Mayan Kickball, Dodgems, Mini-Sub,
#     Tower of Tragedy, Saucer of Peril → keep EN
#   - Approved seeds (59, 96, 97, 99) → reuse exactly
#   - Items/mechanics/UI → pt-BR
#   - Preserve [0x80]..[0x8F] and raw \x7f exactly
#   - Preserve newline-run structure exactly
#   - cp1252-compatible characters only
#   - No U+FFFD/CR
# ---------------------------------------------------------------------------

TRANSLATIONS = {
    50: (
        "MOCHILA PEQUENA, 765 NOTAS\n"
        "ESTE MOVIMENTO EXCLUSIVO DO BANJO AJUDA A EVITAR QUE ELE SE MACHUQUE "
        "COM OBJETOS NO CHÃO. SEGURE [0x88] OU [0x81] E EMPURRE O STICK "
        "DIREITO PARA CIMA."
    ),
    51: (
        "MAYAN KICKBALL\n"
        "QUARTAS DE FINAL: \n"
        "CHUTE AS BOLAS NO SEU GOL PARA MARCAR 2 PONTOS. \n"
        "\n"
        "SEMIFINAL: \n"
        "AS BOLAS VERMELHAS REDUZEM SUA PONTUAÇÃO EM UM PONTO. "
        "TENTE CHUTÁ-LAS NOS GOLS DOS ADVERSÁRIOS! \n"
        "\n"
        "FINAL: \n"
        "CHUTE AS BOMBAS NOS ADVERSÁRIOS PARA ATORDOÁ-LOS. "
        "O JOGADOR COM MAIS PONTOS NO GOL AO FIM DO TEMPO VENCE A PARTIDA.\n"
        "\n"
        "ORDNANCE STORAGE\n"
        "DESARME A DINAMITE COM A BAIONETA DE BICO PARA VENCER!\n"
        "\n"
        "DODGEMS CHALLENGE\n"
        "TWINKLES AZUIS VALEM 3 PONTOS, TWINKLES VERDES VALEM 2 PONTOS "
        "E TWINKLES VERMELHAS VALEM 1 PONTO. QUEM FIZER MAIS PONTOS VENCE!\n"
        "\n"
        "HOOP HURRY\n"
        "ATRAVESSE O MAIOR NÚMERO POSSÍVEL DE AROS PARA MARCAR MUITOS PONTOS. "
        "AROS AZUIS VALEM 3 PONTOS, AROS VERDES VALEM 2 PONTOS "
        "E UM ARO VERMELHO VALE 1 PONTO.\n"
        "\n"
        "BALLOON BURST\n"
        "VOE PELA SALA E ATIRE OVOS NOS BALÕES. "
        "BALÕES AZUIS VALEM 3 PONTOS, BALÕES VERDES VALEM 2 PONTOS "
        "E BALÕES VERMELHOS VALEM 1 PONTO.\n"
        "\n"
        "SAUCER OF PERIL RIDE\n"
        "ALVOS AZUIS VALEM 3 PONTOS, ALVOS VERDES 2 PONTOS "
        "E ALVOS VERMELHOS VALEM 1 PONTO.\n"
        "\n"
        "MINI-SUB CHALLENGE\n"
        "MINAS AZUIS VALEM 3 PONTOS, MINAS VERDES VALEM 2 PONTOS "
        "E MINAS VERMELHAS VALEM 1 PONTO. "
        "ATIRE NO MAIOR NÚMERO DE MINAS POSSÍVEL DENTRO DO TEMPO!\n"
        "\n"
        "CHOMPA'S BELLY\n"
        "GERMS AZUIS VALEM 3 PONTOS, GERMS VERDES VALEM 2 PONTOS "
        "E GERMS VERMELHOS VALEM 1 PONTO.\n"
        "\n"
        "COLOSSEUM KICKBALL\n"
        "VENCE QUEM TIVER MENOS PONTOS! CHUTE AS BOLAS BOAS NO SEU PRÓPRIO GOL! "
        "AS BOLAS AMARELAS AUMENTAM SUA PONTUAÇÃO; AS VERMELHAS A DIMINUEM. "
        "BOLAS PISCANTES DUPLICAM O EFEITO NA PONTUAÇÃO. "
        "BOMBAS ATORDOAM.\n"
        "\n"
        "POT O' GOLD\n"
        "ATIRE NO MAIOR NÚMERO POSSÍVEL DE JIGGIES O MAIS RÁPIDO QUE PUDER!\n"
        "\n"
        "TRASH CAN GERMS\n"
        "DESTRUA OS GERMS O MAIS RÁPIDO POSSÍVEL PARA MARCAR PONTOS. "
        "GERMS AZUIS VALEM 3 PONTOS, GERMS VERDES VALEM 2 PONTOS "
        "E GERMS VERMELHOS 1 PONTO.\n"
        "\n"
        "ZUBBAS' HIVE\n"
        "ATIRE NOS ZUBBAS QUE SURGIREM DAS PAREDES. "
        "ZUBBAS AZUIS VALEM 3 PONTOS, ZUBBAS VERDES 2 PONTOS "
        "E ZUBBAS VERMELHOS 1 PONTO.\n"
        "\n"
        "TOWER OF TRAGEDY\n"
        "APERTE O BOTÃO E TESTE SEUS CONHECIMENTOS SOBRE O JOGO!"
    ),
    52: (
        "DICAS DO MATA-MATA\n"
        "O JOGADOR COM MAIS PONTOS VENCE E LEMBRE-SE: OVOS GRANADA, "
        "MECÂNICOS E DE PROXIMIDADE FAZEM O MAIOR DANO!\n"
        "\n"
        "MAYAN KICKBALL CHALLENGE\n"
        "CHUTE AS BOLAS NO SEU GOL PARA MARCAR 2 PONTOS. "
        "AS BOLAS VERMELHAS REDUZEM SUA PONTUAÇÃO EM UM PONTO. "
        "CHUTE AS BOMBAS NOS ADVERSÁRIOS PARA ATORDOÁ-LOS. "
        "O JOGADOR COM MAIS PONTOS NO GOL AO FIM DO TEMPO VENCE A PARTIDA.\n"
        "\n"
        "DODGEMS CHALLENGE\n"
        "TWINKLES AZUIS VALEM 3 PONTOS, TWINKLES VERDES VALEM 2 PONTOS "
        "E TWINKLES VERMELHAS VALEM 1 PONTO. QUEM FIZER MAIS PONTOS VENCE!\n"
        "\n"
        "HOOP HURRY CHALLENGE\n"
        "ATRAVESSE O MAIOR NÚMERO POSSÍVEL DE AROS PARA MARCAR MUITOS PONTOS. "
        "AROS AZUIS VALEM 3 PONTOS, AROS VERDES VALEM 2 PONTOS "
        "E UM ARO VERMELHO VALE 1 PONTO.\n"
        "\n"
        "BALLOON BURST CHALLENGE\n"
        "VOE PELA SALA E ATIRE OVOS NOS BALÕES. "
        "BALÕES AZUIS VALEM 3 PONTOS, BALÕES VERDES VALEM 2 PONTOS "
        "E BALÕES VERMELHOS VALEM 1 PONTO.\n"
        "\n"
        "MINI-SUB SHOOTOUT\n"
        "CHEGUE PERTO DO SEU ADVERSÁRIO PARA QUE SEUS TORPEDOS ACERTEM O ALVO! "
        "QUEM FIZER MAIS PONTOS VENCE!\n"
        "\n"
        "CHOMPA'S BELLY CHALLENGE\n"
        "ATIRE NO MAIOR NÚMERO POSSÍVEL DE GERMS! "
        "GERMS AZUIS VALEM 3 PONTOS, GERMS VERDES VALEM 2 PONTOS "
        "E GERMS VERMELHOS VALEM 1 PONTO.\n"
        "\n"
        "PACKING ROOM CHALLENGE\n"
        "OS AZUIS VALEM 3 PONTOS, OS VERDES VALEM 2 PONTOS E OS VERMELHOS VALEM 1 PONTO. "
        "MARQUE O MAIOR NÚMERO POSSÍVEL!\n"
        "\n"
        "COLOSSEUM KICKBALL CHALLENGE\n"
        "VENCE QUEM TIVER MENOS PONTOS! CHUTE AS BOLAS AMARELAS NO GOL DOS "
        "ADVERSÁRIOS E AS BOLAS VERMELHAS NO SEU GOL!\n"
        "\n"
        "TRASH CAN CHALLENGE\n"
        "DESTRUA OS GERMS O MAIS RÁPIDO POSSÍVEL PARA MARCAR PONTOS. "
        "GERMS AZUIS VALEM 3 PONTOS, GERMS VERDES VALEM 2 PONTOS "
        "E GERMS VERMELHOS 1 PONTO. "
        "VENCE O JOGADOR COM A MAIOR PONTUAÇÃO!\n"
        "\n"
        "TOWER OF TRAGEDY QUIZ\n"
        "APERTE O BOTÃO E TESTE SEUS CONHECIMENTOS SOBRE O JOGO!"
    ),
    53: "TEM CERTEZA?",
    54: "NÃO",
    55: "SIM",
    56: "CLASSIFICAÇÃO",
    57: "GAMERTAG",
    58: "NOTAS",
    59: "JIGGIES",  # approved seed — reuse
    60: "TEMPO",
    61: "SAIR DO JOGO",
    62: "MOVER",
    63: "CONTROLES DA CÂMERA",
    64: "PAUSAR",
    65: "PULAR",
    66: "ATACAR/MERGULHAR",
    67: "AGACHAR",
    68: "CÂMERA SEGUIDORA",
    69: "MIRAR",
    70: "ABRIR PORTA",
    71: "ATACAR DE INVESTIDA",
    72: "ATIRAR",
    73: "TROCAR MUNIÇÃO",
    74: "OLHAR PARA CIMA",
    75: "OLHAR PARA BAIXO",
    76: "DESLOCAR À ESQUERDA",
    77: "DESLOCAR À DIREITA",
    78: "MIRAR/TROCAR MUNIÇÃO",
    79: "ATACAR CARREGADO",
    80: "ATIRAR",
    81: "ROTAR SUBMARINO",
    82: "IMPULSIONAR SUBMARINO",
    83: "TROCAR CÂMERA",
    84: "PRIMEIRA PESSOA",
    85: "ATACAR",
    86: "PULAR/SUBIR",
    87: "AUMENTAR A VELOCIDADE",
    88: "PERCORRER AS RESPOSTAS",
    89: "APERTE O BOTÃO",
    90: "RESPONDER",
    91: "UM JOGADOR",
    92: "MATA-MATA MODERNO",
    93: "MATA-MATA CLÁSSICO",
    94: "KICKBALL",
    95: "DODGEMS",
    96: "HOOP HURRY",  # approved seed — reuse
    97: "BALLOON BURST",  # approved seed — reuse
    98: "MINI-SUB",
    99: "TRASH CAN",  # approved seed — reuse
}

# ---------------------------------------------------------------------------
# Load source
# ---------------------------------------------------------------------------

with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

# ---------------------------------------------------------------------------
# Validate source indices
# ---------------------------------------------------------------------------

expected_indices = list(range(50, 100))
actual_indices = sorted([s["index"] for s in src_strings if 50 <= s["index"] <= 99])

if actual_indices != expected_indices:
    print(f"ERROR: Expected indices {expected_indices}, got {actual_indices}")
    sys.exit(1)

print(f"Source indices 50..99: {len(actual_indices)} entries found")

# ---------------------------------------------------------------------------
# Build batch artifact
# ---------------------------------------------------------------------------

batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 50 <= idx <= 99:
        batch_entries.append({
            "index": idx,
            "source_text": s["text"],
            "translation": TRANSLATIONS[idx],
        })

batch_artifact = {
    "batch_id": "batch-0050-0099",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": list(range(50, 100)),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0050-0099.json"
with open(batch_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(batch_artifact, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")

print(f"Batch artifact written to {batch_path}")
print(f"Total entries: {len(batch_entries)}")
print(f"Assigned indices: {batch_artifact['assigned_indices']}")

# ---------------------------------------------------------------------------
# Merge into translated.json
# ---------------------------------------------------------------------------

with open("translation/pt-BR/translated.json", "r", encoding="utf-8") as f:
    trans_data = json.load(f)

trans_strings = trans_data["strings"]

# Build a map of index → translation for 50..99
trans_map = {idx: TRANSLATIONS[idx] for idx in range(50, 100)}

# Merge: update translation field for indices 50..99
merged_count = 0
for i, rec in enumerate(trans_strings):
    idx = rec.get("index", i)
    if idx in trans_map:
        # Only update the translation field, preserve all other fields
        trans_strings[i]["translation"] = trans_map[idx]
        merged_count += 1

# Write merged file
merged_path = "translation/pt-BR/translated.json"
with open(merged_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(trans_data, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")

print(f"\nMerged {merged_count} translations into {merged_path}")

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

# Re-read and verify
with open(merged_path, "r", encoding="utf-8") as f:
    verify_data = json.load(f)

verify_strings = verify_data["strings"]
translated_in_range = [
    s for s in verify_strings
    if 50 <= s["index"] <= 99 and s.get("translation") is not None
]
incomplete_in_range = [
    s for s in verify_strings
    if 50 <= s["index"] <= 99 and s.get("translation") is None
]

print(f"\nVerification:")
print(f"  Translated in range 50..99: {len(translated_in_range)}")
print(f"  Incomplete in range 50..99: {len(incomplete_in_range)}")

# Count totals
all_translated = [s for s in verify_strings if s.get("translation") is not None]
all_incomplete = [s for s in verify_strings if s.get("translation") is None]
en_strings = [s for s in verify_strings if s["index"] < 1521]
non_en = [s for s in verify_strings if s["index"] >= 1521]
en_incomplete = [s for s in en_strings if s.get("translation") is None]
non_en_translated = [s for s in non_en if s.get("translation") is not None]

print(f"\nTotals:")
print(f"  Total strings: {len(verify_strings)}")
print(f"  Translated: {len(all_translated)}")
print(f"  Incomplete: {len(all_incomplete)}")
print(f"  EN (0-1520): {len(en_strings)}")
print(f"  Non-EN: {len(non_en)}")

# Verify no duplicates in assigned indices
assigned = [s["index"] for s in batch_entries]
print(f"\nAssigned indices count: {len(assigned)}")
print(f"Unique assigned indices: {len(set(assigned))}")
print(f"No duplicates: {len(assigned) == len(set(assigned))}")

# Verify no null/blank translations in batch
null_trans = [e for e in batch_entries if not e["translation"]]
blank_trans = [e for e in batch_entries if e["translation"].strip() == ""]
print(f"Null translations in batch: {len(null_trans)}")
print(f"Blank translations in batch: {len(blank_trans)}")

# Verify exact source matches
mismatch = []
for entry in batch_entries:
    idx = entry["index"]
    src_rec = next((s for s in src_strings if s["index"] == idx), None)
    if src_rec and src_rec["text"] != entry["source_text"]:
        mismatch.append(idx)
print(f"Source text mismatches: {len(mismatch)}")

# Verify approved seeds preserved
seed_checks = {
    59: "JIGGIES",
    96: "HOOP HURRY",
    97: "BALLOON BURST",
    99: "TRASH CAN",
}
for idx, expected in seed_checks.items():
    entry = next((e for e in batch_entries if e["index"] == idx), None)
    if entry and entry["translation"] == expected:
        print(f"  Seed {idx} ({expected}): OK")
    else:
        print(f"  Seed {idx}: MISMATCH (expected '{expected}', got '{entry['translation'] if entry else 'NONE'}')")

# Verify cp1252 compatibility
cp1252_errors = []
for entry in batch_entries:
    for ch in entry["translation"]:
        code = ord(ch)
        if code > 0xFF:
            cp1252_errors.append((entry["index"], ch, code))
        # Also check for CR
        if ch == "\r":
            cp1252_errors.append((entry["index"], "\\r", 0x0D))

if cp1252_errors:
    print(f"\nWARNING: cp1252 errors found:")
    for idx, ch, code in cp1252_errors:
        print(f"  Index {idx}: char={repr(ch)} ord=U+{code:04X}")
else:
    print(f"\nAll translations are cp1252 compatible")

# Verify expected post-merge counts
expected_translated = 108
expected_incomplete = 927
expected_en = 1035
expected_non_en = 4139
expected_total = 5174

print(f"\nExpected post-merge counts:")
print(f"  Total: {len(verify_strings)} (expected {expected_total}) {'OK' if len(verify_strings) == expected_total else 'MISMATCH'}")
print(f"  Translated: {len(all_translated)} (expected {expected_translated}) {'OK' if len(all_translated) == expected_translated else 'MISMATCH'}")
print(f"  EN incomplete: {len(en_incomplete)} (expected {expected_incomplete}) {'OK' if len(en_incomplete) == expected_incomplete else 'MISMATCH'}")
print(f"  EN: {len(en_strings)} (expected {expected_en}) {'OK' if len(en_strings) == expected_en else 'MISMATCH'}")
print(f"  Non-EN: {len(non_en)} (expected {expected_non_en}) {'OK' if len(non_en) == expected_non_en else 'MISMATCH'}")
print(f"  Non-EN translated: {len(non_en_translated)}")

print("\nDone.")

#!/usr/bin/env python3
"""Translate source indices 0..49 to pt-BR and produce batch artifact + merge."""

import json
import os

# ---------------------------------------------------------------------------
# Translations for indices 0..49
# Rules:
#   - Proper names (Banjo, Kazooie, Mumbo, Grunty, Jiggies, Breegull, etc.) → keep EN
#   - Items/mechanics/UI → pt-BR
#   - Preserve [0x80]..[0x8F] and raw \x7f exactly
#   - Preserve newline-run structure exactly
#   - cp1252-compatible characters only
#   - No U+FFFD/CR
# ---------------------------------------------------------------------------

TRANSLATIONS = {
    0: "JOGAR",
    1: "PLACAR DE LÍDERES",
    2: "CONQUISTAS",
    3: "AJUDA E OPÇÕES",
    4: "DESBLOQUEAR O JOGO COMPLETO",
    5: "VOLTAR À BIBLIOTECA DE JOGOS",
    6: "COMO JOGAR",
    7: "CONTROLES",
    8: "CONFIGURAÇÕES",
    9: "CRÉDITOS",
    10: "VOLUME DA MÚSICA",
    11: "VOLUME DOS EFEITOS SONOROS",
    12: "RESTAURAR CONFIGURAÇÕES PADRÃO",
    13: "TOTAL DO JOGO",
    14: "CLASSIFICAÇÃO",
    15: "JIGGIES",  # proper name — per TM approved
    16: "NOTAS",  # per TM approved
    17: "TEMPO",
    18: "GAMERTAG",  # Xbox brand term — keep
    19: "PONTUAÇÃO",
    20: "CHEFES",
    21: "MÉTODO DE CONTROLE",
    22: "CONTINUAR JOGO",
    23: "VER TOTAIS",
    24: "Sem espaço disponível",
    25: "O dispositivo selecionado não tem espaço suficiente para criar um jogo salvo",
    26: "Selecionar novamente",
    27: "Jogar sem salvar",
    28: "Jogo de Demonstração",
    29: "Esta é a demonstração de Banjo-Tooie. Para continuar jogando, desbloqueie o jogo completo. Vamos, você sabe que quer.",
    30: "Desbloquear o jogo completo",
    31: "Sair para o menu principal",
    32: "DEMONSTRAÇÃO",
    33: (
        "ESTA É A DEMONSTRAÇÃO DE TOOIE. O SALVAMENTO FOI DESATIVADO, "
        "E VOCÊ SÓ PODE JOGAR POR 20 MINUTOS NO PRIMEIRO MUNDO. "
        "POR QUE NÃO SE AVENTURA E DESBLOQUEIA O JOGO COMPLETO? "
        "HÁ JIGGIES AOS MONTES E MUITAS OUTRAS COISAS PARA DESCOBRIR."
    ),
    34: "MOVIMENTOS BÁSICOS",
    35: "MOVIMENTOS ESPECIAIS",
    36: "DICAS PARA MULTIJOGADOR",
    37: "DICAS PARA MINIJOGOS",
    38: (
        "SALTO ALTO / SALTO MORTAL\n"
        "SEGURE [0x88] OU [0x81] E PRESSIONE [0x87].\n\n"
        "INVESTIDA DE BICO\n"
        "SEGURE [0x88] OU [0x81] E PRESSIONE [0x86] PARA USAR A INVESTIDA DE BICO.\n\n"
        "ATAQUE BICO-MARTELO\n"
        "PRESSIONE [0x87] PARA PULAR E DEPOIS [0x88] OU [0x81] PARA USAR O ATAQUE BICO-MARTELO.\n\n"
        "BICADA SALTITANTE\n"
        "PULE E PRESSIONE [0x86] PARA DAR UMA BICADA NO AR.\n\n"
        "ATAQUE DE ROLAMENTO\n"
        "CORRA E PRESSIONE [0x86] PARA ROLAR E ATACAR.\n\n"
        "ATAQUE DE BICADA\n"
        "PRESSIONE [0x86] QUANDO ESTIVER PARADO OU ANDANDO DEVAGAR.\n\n"
        "NADAR\n"
        "USE O STICK ESQUERDO PARA NADAR NA SUPERFÍCIE. PARA NADAR DEBAIXO D’ÁGUA, "
        "PRESSIONE [0x86] PARA MERGULHAR. DEBAIXO D’ÁGUA, BANJO PODE PRESSIONAR [0x87] "
        "PARA BATER AS PERNAS, E KAZOOIE PODE PRESSIONAR [0x86] PARA USAR AS ASAS.\n\n"
        "DISPARO DE OVOS\n"
        "SEGURE [0x88] OU [0x81] E PRESSIONE [0x84] PARA ATIRAR UM OVO PELA BOCA. "
        "PRESSIONE [0x85] PARA ATIRÁ-LOS PARA TRÁS.\n\n"
        "ATAQUE BOMBA DE BICO\n"
        "ENQUANTO VOA, PRESSIONE [0x86] PARA EXECUTAR UM ATAQUE AÉREO.\n\n"
        "TROTE DE GARRAS\n"
        "PRESSIONE [0x88] E [0x81] E CONTINUE SEGURANDO [0x88] OU [0x81] ENQUANTO "
        "MOVE KAZOOIE COM O STICK ESQUERDO.\n\n"
        "INVULNERABILIDADE DAS ASAS MARAVILHOSAS\n"
        "SEGURE [0x88] OU [0x81] E PRESSIONE O STICK DIREITO PARA A DIREITA. MANTENHA "
        "[0x88] OU [0x81] PRESSIONADO E USE O STICK ESQUERDO PARA SE MOVER. USE COM "
        "CUIDADO, POIS ESTE MOVIMENTO CONSOME PENAS DOURADAS."
    ),
    39: (
        "HABILIDADE DE OVOS TELEGUIADOS\n"
        "APLICADA AUTOMATICAMENTE A TODOS OS DISPAROS DE OVOS DEPOIS DE OBTIDA.\n\n"
    ),
    40: (
        "BOMBA DE KAZOOIE MECÂNICA.\n"
        "TOQUE EM [0x89] OU [0x80] PARA MUDAR PARA OVOS MECÂNICOS E LANÇAR O OVO "
        "COMO DE COSTUME. DEPOIS DE LANÇÁ-LO, USE O STICK ESQUERDO PARA MOVÊ-LO "
        "E PRESSIONE [0x86] PARA DETONAR. A BOMBA DE KAZOOIE MECÂNICA PODE ENTRAR "
        "EM ESPAÇOS PEQUENOS E TAMBÉM COLETAR OBJETOS PARA VOCÊ.\n\n"
    ),
    41: (
        "GOLPE BREEGULL\n"
        "TOQUE DUAS VEZES EM [0x86] PARA EXECUTAR ESTE ATAQUE ESPECIAL DE KAZOOIE.\n\n"
    ),
    42: (
        "OVOS\n"
        "TOQUE EM [0x80] OU [0x89] PARA ALTERNAR ENTRE OS DIFERENTES OVOS!\n\n"
        "OVOS DE FOGO, 45 NOTAS\n\n"
        "OVOS DE GRANADA, 100 NOTAS\n"
        "OVOS EXPLOSIVOS DEVASTADORES.\n\n"
        "OVOS DE GELO, 200 NOTAS\n"
        "EFEITO CONGELANTE\n\n"
        "OVOS DE KAZOOIE MECÂNICA, 315 NOTAS\n"
        "COMO OVOS DE GRANADA, MAS COM UMA AVE QUE PODE SER DETONADA À DISTÂNCIA "
        "PRESSIONANDO [0x86]."
    ),
    43: (
        "MIRA DE OVOS, 25 NOTAS\n"
        "PRESSIONE [0x84] E DEPOIS [0x88] OU [0x81] PARA MIRAR E ATIRAR COM MAIS PRECISÃO.\n\n"
        "LANÇADOR BREEGULL, 30 NOTAS\n"
        "USA KAZOOIE COMO ARMA. MUDA AUTOMATICAMENTE PARA ESTE MODO EM ÁREAS ESPECÍFICAS.\n\n"
        "AGARRE DE BORDAS, 35 NOTAS\n"
        "PERMITE AGARRAR BORDAS AUTOMATICAMENTE E SE MOVER POR ELAS COM O STICK ESQUERDO. "
        "PRESSIONE [0x86] E MOVA PARA A ESQUERDA OU DIREITA PARA ATACAR."
    ),
    44: (
        "BROCA DE BICO, 85 NOTAS\n"
        "PERMITE DESTRUIR OBJETOS MAIS RESISTENTES DO QUE O BICO-MARTELO. "
        "USE [0x87] PARA PULAR E DEPOIS PRESSIONE E SEGURE [0x88] OU [0x81].\n\n"
        "BAIONETA DE BICO, 95 NOTAS\n"
        "ATAQUE DE CURTA DISTÂNCIA NO MODO LANÇADOR BREEGULL (EM PRIMEIRA PESSOA). "
        "PRESSIONE [0x86] PARA ATACAR OS INIMIGOS COM O BICO DE KAZOOIE."
    ),
    45: (
        "GOLPE DA MOCHILA, 120 NOTAS\n"
        "VOCÊ PODE USAR A MOCHILA VAZIA DE BANJO COMO ATAQUE QUANDO ELE ESTIVER SOZINHO. "
        "PRESSIONE [0x86].\n\n"
        "SEPARAR, 160 NOTAS\n"
        "FIQUE SOBRE UMA PLATAFORMA COM UMA IMAGEM DE BANJO E KAZOOIE E "
        "PRESSIONE [0x85] PARA SEPARÁ-LOS.\n\n"
        "MIRA DE OVOS NO AR, 180 NOTAS\n"
        "PRESSIONE [0x84] PARA ENTRAR NA VISÃO PELOS OLHOS DE BANJO E DEPOIS [0x88] OU [0x81] "
        "PARA ATIRAR OVOS ENQUANTO VOA."
    ),
    46: (
        "GOLPE DAS ASAS, 265 NOTAS\n"
        "COMO KAZOOIE, PRESSIONE [0x86] PARA SE DEFENDER COM AS ASAS.\n\n"
        "MIRA DE OVOS SUBAQUÁTICA, 275 NOTAS\n"
        "PRESSIONE [0x84] PARA ENTRAR NA VISÃO PELOS OLHOS DE BANJO E DEPOIS [0x88] OU [0x81] "
        "PARA ATIRAR OVOS.\n\n"
        "TORPEDO DE GARRAS, 290 NOTAS\n"
        "DEBAIXO D’ÁGUA, PRESSIONE [0x88] OU [0x81] PARA LANÇAR KAZOOIE COMO "
        "UM TORPEDO. PRESSIONE [0x87] PARA ACELERÁ-LA OU [0x86] PARA DEVOLVÊ-LA A BANJO."
    ),
    47: (
        "TÊNIS SALTITÕES, 390 NOTAS\n"
        "PRESSIONE [0x87] PARA PULAR A GRANDES ALTURAS. PODE SER USADO POR BANJO COM KAZOOIE "
        "OU APENAS POR KAZOOIE.\n\n"
        "MOCHILA TÁXI, 405 NOTAS\n"
        "BANJO PODE CARREGAR OBJETOS MAIORES E PERSONAGENS SEGURANDO [0x88] OU [0x81] "
        "E EMPURRANDO O STICK DIREITO PARA A ESQUERDA.\n\n"
        "CHOCAR, 420 NOTAS\n"
        "PERMITE QUE KAZOOIE CHOQUE OVOS: SEGURE [0x88] OU [0x81] E PRESSIONE [0x86]."
    ),
    48: (
        "BOTAS DE GARRA, 505 NOTAS\n"
        "AS BOTAS DE GARRA PERMITEM ESCALAR PAREDES VERTICAIS QUE TENHAM "
        "PEGADAS DE KAZOOIE.\n\n"
        "MOCHILA SONECA, 525 NOTAS\n"
        "CANSADO? A MOCHILA SONECA PERMITE QUE BANJO TIRE UMA SONECA "
        "DENTRO DA MOCHILA PARA RECUPERAR ENERGIA. SEGURE [0x88] OU [0x81] E "
        "PRESSIONE O STICK DIREITO PARA A DIREITA.\n\n"
        "MOLA DE PERNA, 545 NOTAS\n"
        "PERMITE QUE KAZOOIE DÊ UM SALTO ALTO SOZINHA: SEGURE [0x88] OU [0x81] "
        "E PRESSIONE [0x87]."
    ),
    49: (
        "MOCHILA GRANDE, 640 NOTAS\n"
        "PERMITE QUE BANJO ENTRE EM BURACOS PEQUENOS: SEGURE [0x88] OU [0x81] "
        "E PRESSIONE O STICK DIREITO PARA BAIXO.\n\n"
        "PLANAR, 660 NOTAS\n"
        "KAZOOIE PODE PLANAR PELO AR SEM PLATAFORMAS DE VOO OU PENAS VERMELHAS. "
        "É ÓTIMO COMBINADO COM A MOLA DE PERNA. PRESSIONE [0x88] OU [0x81] NO AR."
    ),
}

# ---------------------------------------------------------------------------
# Load source
# ---------------------------------------------------------------------------

with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

# ---------------------------------------------------------------------------
# Build batch artifact
# ---------------------------------------------------------------------------

batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 0 <= idx <= 49:
        batch_entries.append({
            "index": idx,
            "source_text": s["text"],
            "translation": TRANSLATIONS[idx],
        })

batch_artifact = {
    "batch_id": "batch-0000-0049",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": list(range(0, 50)),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0000-0049.json"
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

# Build a map of index → translation for 0..49
trans_map = {idx: TRANSLATIONS[idx] for idx in range(0, 50)}

# Merge: update translation field for indices 0..49
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
    if 0 <= s["index"] <= 49 and s.get("translation") is not None
]
incomplete_in_range = [
    s for s in verify_strings
    if 0 <= s["index"] <= 49 and s.get("translation") is None
]

print(f"\nVerification:")
print(f"  Translated in range 0..49: {len(translated_in_range)}")
print(f"  Incomplete in range 0..49: {len(incomplete_in_range)}")

# Count totals
all_translated = [s for s in verify_strings if s.get("translation") is not None]
all_incomplete = [s for s in verify_strings if s.get("translation") is None]
en_strings = [s for s in verify_strings if s["index"] < 1521]
non_en = [s for s in verify_strings if s["index"] >= 1521]

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

print("\nDone.")

#!/usr/bin/env python3
"""Filtro de strings traduzíveis para o pipeline pt-BR (Banjo-Tooie XBLA).

Lê work/strings/strings.json (produzido por tools/extract_strings.py) e
classifica cada entrada como `translatable` ou `binary`.

Por que ler de forma robusta:
  O strings.json é JSON UTF-8 válido, mas o campo `text` contém texto
  decodificado de bytes cp1252/binários crus. Registros binários do pool
  viram lixo "imprimível" após a decodificação cp1252, pois cp1252 mapeia
  quase todos os bytes. Por isso a classificação não pode confiar apenas
  em "decodificou sem erro".

Critério final de classificação (determinístico, stdlib only):
  Uma entrada é `binary` se QUALQUER das condições abaixo for verdadeira;
  caso contrário é `translatable`:

  B1. Região binária: index >= 7605.
      Evidência: o pool é organizado em 5 blocos contíguos de 1521
      entradas cada — EN 0-1520, FR 1521-3041, DE 3042-4562,
      ES 4563-6083, IT 6084-7604 (âncoras verificadas: 1267 EN,
      2788 FR, 4309 DE, 5830 ES, 7351 IT; fronteiras verificadas em
      1521/3042/4563/6084) — e a região 7605-9125 é dominada por
      registros binários. Verificado: 938 entradas da região 7605+
      passam no allowlist (B2-B4) isolado; delas, 865 são lixo binário
      único e 73 são texto legítimo (créditos/avisos legais) que são
      DUPLICATAS exatas de entradas da seção EN (0-7604). Logo, B1
      rejeita as 938 com 0 falsos negativos únicos.

  B2. `text` vazio ou contém U+FFFD (replacement character).

  B3. Após remover placeholders de glifo `[0xNN]`, não sobra texto com
      caracteres não-brancos (strip() vazio).

  B4. Allowlist estrita de caracteres: TODOS os caracteres restantes
      devem pertencer a:
        - ASCII imprimível 0x20-0x7E;
        - \n, \t, \r (quebras de linha presentes em textos do jogo);
        - 0x7F (glifo de botão emitido cru pelo extractor);
        - cp1252: qualquer caractere Unicode que possa ser re-encodificado
          por Python cp1252 (inclui 0xA0-0xFF e caracteres como U+2019);
        - utf-16-be: qualquer caractere Unicode >= 0x20 (o decode
          utf-16-be só produz texto real ou U+FFFD).
      Qualquer byte de controle (0x01-0x1F) => `binary`.

  B5. Razão mínima de letras ASCII para strings longas: se o texto (após
      remover placeholders e strip) tem comprimento > 20, a razão de
      letras ASCII sobre o total de caracteres deve ser >= 0.30.
      Evidência: a menor razão entre strings longas legítimas é 0.455
      (índice 5879, "JUGADOR ~ : ~ - ~ PTS."); as únicas
      strings com razão < 0.20 são as numéricas curtas "13" (índices
      1243, 2764, 4285, 5806, 7327), isentas pelo limite de comprimento.
      Guard de defesa em profundidade contra lixo que passe o allowlist.

Por que limiar de proporção imprimível NÃO funciona (verificado):
  cp1252 mapeia quase todos os bytes para caracteres imprimíveis, então
  os 938 registros binários da região 7605+ têm razão imprimível 1.0
  sob decodificação cp1252-aware. Qualquer critério baseado em limiar de
  proporção (ex.: >= 0.90) deixaria passar os 938. A região binária
  explícita (B1) é o critério efetivo; B2-B5 são guardas complementares.

Resultado verificado (pool atual, 9126 entradas):
  - translatable: 5174 / binary: 3952
  - 0 falsos positivos: as 938 entradas binárias de 7605+ são rejeitadas
    por B1; na região legítima 0-7604, B2-B4 rejeita 2431 entradas
    (vazias, bytes de controle, U+FFFD) e nenhum lixo binário passa.
  - 0 falsos negativos: todo texto legítimo de 0-7604 é preservado,
    incluindo strings numéricas curtas ("13") e strings com
    placeholders `[0xNN]`/`0x7F`.

Saída: translation/pt-BR/source.json (UTF-8), somente entradas
`translatable`, preservando index, offset, byte_length, encoding, text.
Imprime resumo (totais, contagens, amostras).

Uso:
  python tools/filter_translatable.py [--input PATH] [--out PATH]
"""
import argparse
import json
import os
import re

PLACEHOLDER_RE = re.compile(r"\[0x[0-9A-F]{2}\]")
# Região binária do pool (ver evidência B1 no docstring).
BINARY_REGION_START = 7605
# B5: razão mínima de letras ASCII para strings longas (ver docstring).
MIN_LETTER_RATIO = 0.30
LONG_STRING_LEN = 20


def _allowed(ch: str, encoding: str) -> bool:
    o = ord(ch)
    if ch in "\n\t\r" or o == 0x7F:
        return True
    if 0x20 <= o <= 0x7E:
        return True
    if encoding == "cp1252":
        # Accept any character encodable by Python cp1252 codec
        # (includes 0xA0-0xFF plus characters like U+2019, U+201C, etc.)
        try:
            ch.encode("cp1252")
            return True
        except UnicodeEncodeError:
            return False
    if encoding == "utf-16-be" and o >= 0x20:
        return True
    return False


def classify(entry: dict) -> str:
    # B1: região binária
    if entry["index"] >= BINARY_REGION_START:
        return "binary"
    text = entry["text"]
    # B2: vazio ou replacement character
    if not text or "\ufffd" in text:
        return "binary"
    core = PLACEHOLDER_RE.sub("", text)
    # B3: sem conteúdo não-branco após remover placeholders
    stripped = core.strip()
    if not stripped:
        return "binary"
    # B4: allowlist estrita
    if not all(_allowed(c, entry["encoding"]) for c in core):
        return "binary"
    # B5: razão mínima de letras ASCII para strings longas
    if len(stripped) > LONG_STRING_LEN:
        letters = sum(c.isascii() and c.isalpha() for c in stripped)
        if letters / len(stripped) < MIN_LETTER_RATIO:
            return "binary"
    return "translatable"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default="work/strings/strings.json")
    ap.add_argument("--out", default="translation/pt-BR/source.json")
    args = ap.parse_args()

    # Leitura robusta: bytes -> json.loads (UTF-8)
    with open(args.input, "rb") as f:
        data = json.loads(f.read())

    entries = data["strings"]
    out_entries = []
    counts = {"translatable": 0, "binary": 0}
    enc_counts = {}
    for e in entries:
        cls = classify(e)
        counts[cls] += 1
        if cls == "translatable":
            out_entries.append({
                "index": e["index"],
                "offset": e["offset"],
                "byte_length": e["byte_length"],
                "encoding": e["encoding"],
                "text": e["text"],
            })
            enc_counts[e["encoding"]] = enc_counts.get(e["encoding"], 0) + 1

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({
            "source": data.get("source"),
            "filter": "tools/filter_translatable.py",
            "criterion": "binary region index>=7605 (B1) + strict printable allowlist (B2-B4) + min ASCII letter ratio 0.30 for long strings (B5); see docstring for evidence",
            "total_input": len(entries),
            "translatable": counts["translatable"],
            "binary": counts["binary"],
            "strings": out_entries,
        }, f, ensure_ascii=False, indent=1)

    # Validação: recarregar como UTF-8 estrito
    with open(args.out, "rb") as f:
        reloaded = json.loads(f.read().decode("utf-8"))
    assert len(reloaded["strings"]) == counts["translatable"]

    print(f"input: {args.input} ({len(entries)} entradas)")
    print(f"translatable: {counts['translatable']}  binary: {counts['binary']}")
    print(f"encodings (translatable): {enc_counts}")
    print(f"out: {args.out} (UTF-8 válido, {len(reloaded['strings'])} strings)")
    print("--- amostras (primeiras 10) ---")
    for e in out_entries[:10]:
        print(f"{e['index']:>5} {e['encoding']:<9} {e['text'][:60]!r}")
    # Spot-check de strings conhecidas
    texts = {e["text"] for e in out_entries}
    for k in ["PLAY GAME", "LEADERBOARDS", "ACHIEVEMENTS", "JIGGIES", "NOTES"]:
        print(f"spot-check {k!r}: {'OK' if k in texts else 'FALTA'}")


if __name__ == "__main__":
    main()

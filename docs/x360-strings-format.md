# Formato de X360_strings.dat (Banjo-Tooie XBLA)

Arquivo analisado: `game/Banjo-Tooie XBLA Extract/RAWFiles/X360_strings.dat`
Tamanho: **423808 bytes (0x67780)**
Extractor: `tools/extract_strings.py` (stdlib apenas; regenera `work/strings/strings.json` e `work/strings/strings.csv`)
Base: análise documentada em `work/notes/notes.md` (sessão anterior), revalidada na finalização.

## Estrutura geral (little-endian)

| Offset | Tamanho | Conteúdo |
|--------|---------|----------|
| `0x0000` | 4 | magic/version u32 = `0x000605F1` |
| `0x0004` | 24 | 6 × u32 — **propósito desconhecido** |
| `0x001C` | 9126 × 4 = 36504 | Tabela de comprimentos (u32; bytes **incluindo** null terminator) |
| `0x8E98` | 28 | 7 × u32 — **propósito desconhecido** (gap) |
| `0x8EB4` | 269525 | Pool de strings null-terminated (9126 strings) |
| `0x4AB89` | 117751 | Região trailing — **propósito desconhecido** (provável tabela de índice/hash) |

### Evidências

- **Magic**: `struct.unpack_from('<I', data, 0) == 0x000605F1`.
- **6 u32 do header** (0x0004..0x001B): `0x0000A8EC, 0x0000CB88, 0x0000C648, 0x0000BB4D, 0x0000BA76, 0x00006C56`. Valores plausíveis como offsets/contagens, mas sem confirmação de uso.
- **Tabela de comprimentos**: walk a partir de `0x001C` somando os u32 e avançando no pool a partir de `0x8EB4` produz exatamente **9126** strings cuja soma dos comprimentos é **269525 = 0x4AB89 − 0x8EB4** (match exato com o fim do pool). Todas as 9126 strings têm null terminator válido (`data[off+len-1] == 0` em 100% dos casos).
- **Gap de 7 u32** (0x8E98..0x8EB3): `0x10, 0x0B, 0x12, 0x0C, 0x0E, 0x12, 0x0C`. Pequenos valores; propósito desconhecido.
- **Pool**: 269525 bytes de strings null-terminated, terminando exatamente em `0x4AB89`.
- **Região trailing** (0x4AB89..0x67780): 117751 bytes; interpretada como u32 little-endian, tem 29437 slots dos quais **8248 são não-nulos** (esparsa). Primeiros u32: `0xC1BB6AAD, 0xCECFBCDF, 0x42EFE2, 0x42EFC9, ...` — padrão consistente com hashes/índices, mas **não confirmado**.

## Organização por idioma (seções contíguas)

O pool de 9126 strings está organizado em **5 blocos contíguos de 1521
entradas cada**, seguidos da região binária (7605–9125):

| Seção | Índices | Âncora verificada |
|---|---|---|
| EN (inglês) | 0–1520 | 1267: "PICK A CONTROL STYLE AND PRESS 0x7F TO PLAY!" |
| FR (francês) | 1521–3041 | 2788: "CHOISIS UN STYLE DE COMMANDES..." |
| DE (alemão) | 3042–4562 | 4309: "W[HLE EINE STEUERUNGSART..." |
| ES (espanhol) | 4563–6083 | 5830: "tSELECCIONA UN TIPO DE CONTROL..." |
| IT (italiano) | 6084–7604 | 7351: "SCEGLI UNO STILE DI CONTROLLO..." |
| Binário | 7605–9125 | lixo binário |

Fronteiras verificadas: 1521 ("JOUER"), 3042 ("SPIEL STARTEN"),
4563 ("JUGAR"), 6084 ("GIOCA"). A mesma string-âncora aparece a cada
1521 índices (1267, 2788, 4309, 5830, 7351), confirmando o passo do
bloco.

## Encoding por string

O encoding é uma propriedade **de cada string**, não de blocos contíguos (múltiplos idiomas — EN, FR, ... — estão intercalados).

| Encoding | Contagem | Regra |
|----------|----------|-------|
| `cp1252` (single-byte) | 8793 | bytes 0x00–0x7F = ASCII; 0x80–0x8F = glifos de fonte (placeholders); 0x90–0x9F = cp1252 (0x92 = U+2019); 0xA0–0xFF = cp1252 |
| `utf-16-be` | 333 | usado quando a heurística de detecção (≥80% zeros em posições pares) indica UTF-16BE. Os caracteres podem estar dentro ou fora de cp1252 (ex.: acentos, `…` U+2026); U+2019 é cp1252 (via 0x92) e não exige utf-16-be.

**Detecção (heurística validada):** uma string é UTF-16BE se ≥ 80% dos bytes em posições pares forem `0x00`. Racional: em strings single-byte válidas, `0x00` interno não ocorre (apenas o terminator); em UTF-16BE, caracteres ASCII têm byte alto `0x00` em posição par.

### Glifos 0x80–0x8F e bytes 0x90–0x9F

Em strings single-byte, bytes `0x80`–`0x8F` são glifos de fonte (botões do controle Xbox 360), mapeados via `xarialuni.ttf`. Como o cmap da fonte não está disponível, o extractor os representa como placeholders `[0xNN]` (ex.: `[0x80]` = A, `[0x81]` = B, `[0x82]` = X, `[0x83]` = Y, `[0x84]` = LB, `[0x85]` = RB, `[0x86]` = LT, `[0x87]` = RT, `[0x88]` = Start, `[0x89]` = Back, `[0x8A]` = D-pad up, `[0x8B]` = D-pad down, `[0x8C]` = D-pad left, `[0x8D]` = D-pad right, `[0x8E]` = LB+RB, `[0x8F]` = LT+RT).

Bytes `0x90`–`0x9F` **não são glifos de controle** — são bytes cp1252. O extractor os decodifica via codec cp1252 de Python:
- `0x92` = U+2019 (RIGHT SINGLE QUOTATION MARK, `’`), usado em possessivos/contracções inglesas como `BANJO’S`.
- `0x93` = U+201C (LEFT DOUBLE QUOTATION MARK, `"`).
- `0x94` = U+201D (RIGHT DOUBLE QUOTATION MARK, `"`).
- Bytes indefinidos em cp1252 (`0x90` e `0x9D`) produzem U+FFFD (replacement character). `0x9F` é definido como U+0178 (Ÿ).

**Limitação**: a região binária (índices >= 7605) também contém bytes 0x90–0x9F que são decodificados como cp1252, mas não representam texto legítimo — são lixo binário. O filtro (B1) rejeita essa região independentemente.

## Saída do extractor

`tools/extract_strings.py` (sem dependências além da stdlib) gera:

- `work/strings/strings.json` — metadados (`source`, `magic`, `count`, `pool_offset`, `pool_end`) + array de 9126 objetos `{index, offset, byte_length, encoding, text}` (offset decimal).
- `work/strings/strings.csv` — colunas `index, offset (hex), byte_length, encoding, text`.

### Reprodutibilidade (verificada na finalização, na revisão e na correção 0x92)

Hashes SHA-256 atuais (após a correção de revisão do formato de glifo `[0xNN]` + correção 0x92 → U+2019):

| Arquivo | SHA-256 |
|---------|---------|
| `work/strings/strings.json` | `7ea146666c9039126183fbc7f34222b1d811a0bc4d5f614ae61d36dd535d64c7` |
| `work/strings/strings.csv` | `b78c96518fe8ec9f88d6680bbd00c61474078c2d92a067a88b52b56cca095481` |
| `translation/pt-BR/source.json` | `96953ac5b95c81bc4da1b7d749a6b5d162bb3f64cb39b1364b66acf0e1ba77cf` |

> Nota de revisão: na finalização original o hash do CSV estava truncado (56 hex) e o
> extractor emitia glifos como `[NN]` (sem prefixo `0x`), divergindo desta documentação
> (`[0xNN]`). A revisão corrigiu o extractor para `[0xNN]` e regenerou a saída; os hashes
> acima refletem o estado corrigido. Hashes da finalização original (saída pré-correção):
> JSON `4dc4b292…33c72`, CSV `03148ea5…d78234391b88cfc530745d782`.

Validação de conteúdo: 31/31 strings conhecidas presentes (ex.: `PLAY GAME`, `LEADERBOARDS`, `ACHIEVEMENTS`, `HELP & OPTIONS`, `UNLOCK FULL GAME`, `RETURN TO GAME LIBRARY`, `HOW TO PLAY`, `CONTROLS`, `SETTINGS`, `CREDITS`, `MUSIC VOLUME`, `SOUND EFFECTS VOLUME`, `GAME TOTAL`, `RANK`, `JIGGIES`, `BOSSES`, `BEAK BARGE ATTACK`, ...).

## Campos de propósito desconhecido (documentados como tal)

1. **6 u32 do header** (`0x0004`..`0x001B`) — valores: `0xA8EC, 0xCB88, 0xC648, 0xBB4D, 0xBA76, 0x6C56`.
2. **7 u32 do gap** (`0x8E98`..`0x8EB3`) — valores: `0x10, 0x0B, 0x12, 0x0C, 0x0E, 0x12, 0x0C`.
3. **Região trailing** (`0x4AB89`..`0x67780`) — 117751 bytes, 8248 u32 não-nulos; hipótese: tabela de índice/hash por string (não confirmada).

## Limitações conhecidas

- Glifos 0x80–0x8F ficam como placeholders `[0xNN]` até que o cmap de `xarialuni.ttf` seja extraído.
- A heurística de detecção UTF-16BE (≥80% zeros em posições pares) é validada para este arquivo (contagem 8793/333 consistente com a análise original), mas não é formalmente infalível para strings muito curtas.
- Os três grupos de campos desconhecidos permanecem sem interpretação confirmada.

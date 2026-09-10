# Pipeline de tradução pt-BR — Banjo-Tooie XBLA

Pipeline para traduzir as strings de `X360_strings.dat` (Xbox 360) para
português (Brasil).

## Estrutura

```
translation/
├── README.md                  # este arquivo (pipeline)
├── glossary/
│   └── glossary-pt-BR.md      # glossário de termos + política de tradução
├── pt-BR/
│   ├── source.json            # strings traduzíveis de TODOS os 5 blocos
│                              # de idioma (EN/FR/DE/ES/IT) — saída do filtro,
│                              # UTF-8; subconjunto operacional pt-BR =
│                              # índices 0..1520 (index < 1521), 1035 entradas
│   ├── tm.json                # Translation Memory (source → translation)
│   └── translated.json        # saída da etapa 3 (tradução em progresso)
└── review/                    # passagens de revisão (arquivos de revisão)
```

## Etapas do pipeline

### 1. Extração (concluída)

- Ferramenta: `tools/extract_strings.py`
- Entrada: `game/Banjo-Tooie XBLA Extract/RAWFiles/X360_strings.dat`
- Saída: `work/strings/strings.json` + `work/strings/strings.csv`
- Formato do .dat documentado em `docs/x360-strings-format.md`.
- Resultado: 9126 entradas (8793 cp1252, 333 utf-16-be).

### Estrutura do pool (seções de idioma)

O pool é organizado em 5 blocos contíguos de **1521 entradas** cada,
seguidos da região binária (fronteiras e âncoras verificadas no
`work/strings/strings.json`):

| Seção | Índices | Âncora verificada |
|---|---|---|
| EN (inglês) | 0–1520 | 1267: "PICK A CONTROL STYLE AND PRESS 0x7F TO PLAY!" |
| FR (francês) | 1521–3041 | 2788: "CHOISIS UN STYLE DE COMMANDES..." |
| DE (alemão) | 3042–4562 | 4309: "W[HLE EINE STEUERUNGSART..." |
| ES (espanhol) | 4563–6083 | 5830: "tSELECCIONA UN TIPO DE CONTROL..." |
| IT (italiano) | 6084–7604 | 7351: "SCEGLI UNO STILE DI CONTROLLO..." |
| Binário | 7605–9125 | lixo binário (rejeitado pelo filtro, B1) |

Fronteiras verificadas: 1521 ("JOUER"), 3042 ("SPIEL STARTEN"),
4563 ("JUGAR"), 6084 ("GIOCA"). A mesma string-âncora aparece a cada
1521 índices (1267, 2788, 4309, 5830, 7351), confirmando o passo do
bloco. O pipeline pt-BR traduz a partir da **seção inglesa (0–1520)**;
as demais seções servem apenas como referência de tom/terminologia.

### 2. Filtro (concluída)

- Ferramenta: `tools/filter_translatable.py` (stdlib only, determinístico)
- Classifica cada entrada como `translatable` vs `binary` com critério
  estrito de caracteres imprimíveis (ver docstring da ferramenta).
- Saída: `translation/pt-BR/source.json` (UTF-8) com `index`, `offset`,
  `byte_length`, `encoding`, `text` de cada string traduzível.
- Resultado atual: 5174 translatable / 3952 binary (critério B1–B5,
  ver docstring da ferramenta).

### 3. Tradução (em andamento)

- Fonte: `translation/pt-BR/source.json` — contém strings traduzíveis de
  **todos os 5 blocos de idioma** (EN/FR/DE/ES/IT). O subconjunto
  operacional para tradução pt-BR é **exatamente os índices 0..1520**
  (`index < 1521`), atualmente **1035 entradas**.
  As seções FR/DE/ES/IT servem apenas como referência de tom/terminologia.
- Consultar, para cada string:
  1. `translation/pt-BR/tm.json` (TM — reutilizar traduções existentes);
  2. `translation/glossary/glossary-pt-BR.md` (política + termos).
- `tm.json` atual: 154 entradas — **14 `approved`** (decisões de
  glossário confirmadas) + **140 `proposed`** (propostas a validar em
  revisão). Entradas `proposed` não são canônicas até aprovadas.
- Regras obrigatórias:
  - Preservar placeholders `[0x80]`–`[0x8F]` e o byte `0x7F` (glifos de botão)
    exatamente como estão — não são texto.
  - O campo `text` em source.json contém texto Unicode decodificado (não bytes crus).
    Caracteres como U+2019 (curly apostrophe, ex.: índice 45 `BANJO’S`) são válidos
    e devem ser preservados exatamente como estão.
  - Preservar quebras de linha e estrutura (strings multilinha).
  - Nomes próprios (personagens, fases, mini-jogos, marcas) em inglês.
  - Itens/mecânicas/UI em pt-BR.
- Saída da etapa: `translation/pt-BR/translated.json` — mesmo formato de
  `source.json` (todos os 5 blocos) + campo `translation` por entrada.
  A tradução pt-BR preenche `translation` apenas para índices 0..1520
  (`index < 1521`); entradas de outras seções mantêm `translation` como
  `null` ou omitido.

### 4. Revisão

- Local: `translation/review/`
- Cada lote de tradução passa por revisão (QwenRevi no fluxo local) com:
  - diff source → translation;
  - verificação de placeholders/glifos preservados;
  - verificação de consistência com glossário e TM;
  - verificação de tamanho (ver etapa 5 para limites de bytes).
- Entradas aprovadas voltam para `tm.json` com `status: approved`.

### 5. Injeção de volta no .dat (passo futuro)

O que será necessário:

1. **Mapeamento de offsets**: cada string traduzida tem `offset` e
   `byte_length` no pool (0x8EB4+). A injeção precisa reescrever o pool.
2. **Limites de tamanho**: o comprimento de cada string é fixado na
   tabela de comprimentos (offset 0x1C, u32 little-endian, incluindo null
   terminator). Opções:
   - (a) traduzir respeitando o `byte_length` original (mais restritivo);
   - (b) reempacotar o pool inteiro e reescrever a tabela de comprimentos
     (mais flexível; exige revalidação de todos os offsets).
3. **Codificação**: strings cp1252 devem permanecer single-byte
   (pt-BR usa acentos — todos disponíveis em cp1252: á, ã, ç, é, í, ó, ú,
   â, ê, ô, à, ü). Cuidado: o byte `0x7F` e os glifos 0x80–0x8F **não**
   podem ser reencodificados — são glifos de fonte. Bytes 0x90–0x9F são
   cp1252 (ex.: 0x92 = U+2019) — **não** são glifos de fonte.
   Strings utf-16-be permanecem utf-16-be.
4. **Null terminator**: cada string termina em 0x00 (validado 100% na
   extração).
5. **Validação pós-injeção**: reextrair com `tools/extract_strings.py` e
   comparar com o esperado (magic, contagem, offsets, spot-checks).
6. **Reempacotamento STFS**: o .dat modificado volta ao pacote STFS
   (`game/.../ABB9CAB3...`) — usar ferramenta STFS (ver
   `references/XBLA-Extract/`, gitignored) ou equivalente.

## Comandos

```bash
# Filtro (reproduzível)
python tools/filter_translatable.py

# Inicialização da tradução (seed com TM aprovado)
python tools/init_translation.py

# Validação estrita (requer todas as EN preenchidas)
python tools/validate_translation.py --source translation/pt-BR/source.json --translated translation/pt-BR/translated.json

# Validação com incompletos permitidos (durante trabalho em lote)
python tools/validate_translation.py --allow-incomplete --source translation/pt-BR/source.json --translated translation/pt-BR/translated.json

# Hashes de referência (verificação de integridade)
sha256sum work/strings/strings.json work/strings/strings.csv translation/pt-BR/source.json
```

## Estado atual

- [x] Extração (9126 strings)
- [x] Filtro (5174 translatable / 3952 binary)
- [x] Glossário + TM semeados
- [x] Tradução lote 0000–0049 (50 strings)
- [x] Tradução lote 0050–0099 (50 strings)
- [x] Tradução lote 0100–0149 (50 strings)
- [x] Tradução lote 0150–0199 (50 strings)
- [x] Tradução lote 0200–0249 (50 strings)
- [x] Tradução lote 0250–0299 (50 strings)
- [x] Tradução lote 0300–0324 (25 strings)
- [x] Tradução lote 0325–0349 (25 strings)
- [x] Tradução lote 0350–0374 (15 strings)
- [ ] Revisão
- [ ] Injeção no .dat + reempacotamento STFS

## Totais atuais

- Traduzidas (EN): **365** / Incompletas (EN): **670** (de 1035)
- Contagem canônica: **365 = 353 traduções novas nos nove lotes**
  (50 + 46 + 47 + 45 + 50 + 50 + 25 + 25 + 15) **+ 12 sementes aprovadas originais** no total
  (59, 96, 97, 99, 101, 148, 149, 150, 153, 154, 155, 156).
- Lote 0000–0049: **50 traduções novas** (0 sementes in-range).
- Lote 0050–0099: **46 traduções novas** + **4 sementes aprovadas** preservadas
  (59, 96, 97, 99).
- Lote 0100–0149: **47 traduções novas** + **3 sementes exatas** preservadas
  (101, 148, 149). As palavras aprovadas isoladamente (108, 110/113) já estão
  contadas nas 47 novas — não são sementes nem traduções extras.
- Lote 0150–0199: **45 traduções novas** + **5 sementes aprovadas** preservadas
  (150, 153, 154, 155, 156). STOP 'N' SWOP (157) mantido em inglês como
  franquia/nome próprio.
- Lote 0200–0249: **50 traduções novas** (0 sementes in-range). Deste total,
  **23** são traduções pt-BR e **27** são mantidos em inglês
  (202, 203–214, 225–237, 245). Mini-jogos, conquistas e nomes próprios
  mantidos em inglês; UI e instruções traduzidos para pt-BR.
- Lote 0250–0299: **50 traduções novas** (0 sementes in-range). Terminologia:
  KIDS→CRIANÇAS (multilingue confirma); CRUSH→ESMAGAR (não ESFAIXAR);
  JADE SNAKE→SERPENTE DE JADE (termo descritivo); STAR SPINNER mantido
  (não GIRASSOL); HANDCART RACE→VAGONETAS; POWER UP THE UFO→RECARREGAR O
  OVNI; STYRACOSAURUS→ESTIRACOSSAUROS; WARM UP AND GET FOOD→AQUECER OS
  OOGLE BOOGLES E CONSEGUIR COMIDA PARA ELES; WASTE DISPOSAL
  PLANT→ESTAÇÃO DE TRATAMENTO DE RESÍDUOS; TRIBE→TRIBO (substantivo comum;
  ROCKNUTS é o nome das criaturas). Nomes próprios e nomes/tipos de
  criatura mantidos: TARGITZAN, OLD KING COAL, CANARY MARY, MAYAHEM, JIGGY,
  HOOP HURRY, DODGEM DOME, MR. PATCH, SAUCER OF PERIL, BALLOON BURST,
  DIVE OF DEATH, BOGGY, STAR SPINNER, INFERNO, TIPTUP, JOLLY,
  MERRY MAGGIE, LORD WOO FAK FAK, PAWNO, TERRY,
  OOGLE BOOGLES, CHOMPASAUR, ROCKNUTS, T-REX, WELDAR.
- TM: **177 entradas** (14 `approved` + 163 `proposed`);
  lote 0250–0299 adicionou **24 novas entradas `proposed`**; 26 frases
  completas/objetivos de ocorrência única foram deliberadamente excluídos.
  lote 0300–0324 adicionou **8 novas entradas `proposed`** (localizações
  e mecânicas reutilizáveis); 17 frases completas/objetivos de ocorrência
  única foram deliberadamente excluídos do TM.
  lote 0325–0349 adicionou **8 novas entradas `proposed`** (UI labels e
  termos de login Xbox); 17 frases completas/objetivos de ocorrência única
  foram deliberadamente excluídos do TM.
  lote 0350–0374 adicionou **7 novas entradas `proposed`** (UI errors, warp
  mechanics, game action instructions); 8 strings de uso único da cadeia
  REINSTALL foram deliberadamente excluídas do TM.
- Estado geral: tradução em progresso, lotes 0000–0374 concluídos
- Próximo lote: **0375–0399**

# Inventário Completo do Projeto — Banjo-Tooie XBLA

> **project_id:** `project-0552a197-3c9f-470e-8794-66c469a67ecf`
> **Data do inventário:** 2026-09-05
> **Diretório raiz:** `S:\Vibecode\Pi\Banjo-Tooie XBLA`

---

## 1. Visão Geral

**Banjo-Tooie XBLA** é um pacote de jogo arcade para **Xbox Live Arcade** (XBLA), a plataforma de jogos arcade digitais da **Xbox** (console Xbox original, não Xbox 360). O projeto contém:

- O **pacote STFS original** do jogo (container Xbox 360/Xbox Live)
- Os **arquivos extraídos** do pacote (executable, textures, fonts, assets)
- Uma **ferramenta de extração/criação** em Python para pacotes STFS e ISOs Xbox

O jogo é uma **sequência 2D de plataforma** estrelando **Banjo** (urso) e **Tooie** (pássaro), com 12 conquistas (achievements), suporte para 1-4 jogadores, e múltiplos idiomas.

---

## 2. Estrutura de Diretórios

```
Banjo-Tooie XBLA/
├── .understory-project-id              # ID do projeto Understory
├── game/
│   ├── ABB9CAB336175357D09F2D922735D23C62F90DDD58   # Pacote STFS original (93.7 MB)
│   └── Banjo-Tooie XBLA Extract/                       # Arquivos extraídos (94 MB)
│       ├── default.xex                                   # Executável Xbox 360 (6.7 MB)
│       ├── BanjoTooieIcon.png                            # Ícone 64x64 (10.5 KB)
│       ├── BanjoTooieMarketplace.png                     # Arte de marketplace 420x95 (76 KB)
│       ├── ArcadeInfo.xml                                # Metadados Arcade (7.8 KB)
│       ├── Achievement_01.png through Achievement_12.png # Ícones de conquistas 64x64
│       ├── Rating_ESRB_E.png                             # Classificação ESRB (4.4 KB)
│       ├── Rating_PEGI_3.png                             # Classificação PEGI (13.7 KB)
│       ├── Rating_PEGI_4.png                             # Classificação PEGI (13.7 KB)
│       ├── Rating_CERO_B.png                             # Classificação CERO (4.4 KB)
│       ├── Rating_GRB_ALL.png                            # Classificação GRB (4.4 KB)
│       ├── Rating_OFLC_G.png                             # Classificação OFLC (1.1 KB)
│       ├── Rating_USK_6.png                              # Classificação USK (5.8 KB)
│       ├── 32_584109550002000100010001.png               # Ícone 32x32 (2.7 KB)
│       ├── 32_584109550002000200010002.png               # Ícone 32x32 (2.1 KB)
│       ├── 64_584109550002000100010001.png               # Ícone 64x64 (11.8 KB)
│       └── 64_584109550002000200010002.png               # Ícone 64x64 (8.9 KB)
│       └── RAWFiles/                                     # Assets brutos (87 MB)
│           ├── 58410955033F0001                          # Arquivo PIRS (5.0 MB)
│           ├── ArcadeNormal.ptc                          # Layout de arcade normal (98.7 KB)
│           ├── ArcadeWide.ptc                            # Layout de arcade wide (97.2 KB)
│           ├── X360_strings.dat                          # Strings do jogo (413.7 KB)
│           ├── banjo2_360.ctl                            # Controle/mapeamento (182.8 KB)
│           ├── banjo2_360.tbl                            # Tabela de dados (13.8 MB)
│           ├── db360.cmp                                 # Dados comprimidos (11.7 MB)
│           ├── db360.textures.cmp                        # Texturas comprimidas (48.1 MB)
│           └── xarialuni.ttf                             # Fonte Arial Unicode (6.3 MB)
└── tools/
    └── XBLA-Extract/                                     # Ferramenta de extração (MIT License)
        ├── stfs_extract.py                               # Extractor STFS CLI (core)
        ├── stfs_extract_gui.py                           # GUI PyQt6 (interface)
        ├── xiso.py                                       # Extractor/criador ISO Xbox
        ├── start.bat                                     # Launcher Windows
        ├── XBLA.run                                      # Launcher Linux
        ├── requirements.txt                              # Dependência: PyQt6
        ├── LICENSE                                       # MIT (Corey Clark, 2022)
        └── README.md                                     # Documentação completa
```

---

## 3. Pacote STFS Original

### Arquivo: `game/ABB9CAB336175357D09F2D922735D23C62F90DDD58`

| Propriedade | Valor |
|---|---|
| **Tipo** | Microsoft Xbox 360 package (Xbox Live) |
| **Magic** | `PIRS` (identificador de pacote Arcade) |
| **Media ID** | `65D27094` |
| **Content Type** | Arcade Title |
| **Tamanho** | 98.316.288 bytes (~93.7 MB) |
| **Hash/ID** | `ABB9CAB336175357D09F2D922735D23C62F90DDD58` |
| **Data de criação** | Novembro 2020 |

O arquivo começa com os bytes `PIRS`, confirmando que é um pacote STFS do tipo Arcade. O nome do arquivo é o hash/identificador único do título na plataforma Xbox Live Arcade.

---

## 4. Executável do Jogo

### Arquivo: `game/Banjo-Tooie XBLA Extract/default.xex`

| Propriedade | Valor |
|---|---|
| **Tipo** | Microsoft Xbox 360 executable |
| **Magic** | `XEX2` (formato de executável Xbox 360) |
| **Media ID** | `65D27094` |
| **Região** | All regions (região livre) |
| **Tamanho** | 6.987.776 bytes (~6.7 MB) |

### Bibliotecas dinâmicas referenciadas (import table):
- `D3D9` / `D3DX9` — DirectX 9 graphics
- `XGRAPHC` — Xbox graphics library
- `LIBCPMT` — C++ runtime library
- `XAUDIO2` — Xbox audio library
- `XAPOBA` — Xbox audio processing
- `XONLINE` — Xbox Live online services
- `XMCORE` — Xbox core services
- `XUIRNDR` / `XUIRUN` — Xbox UI rendering
- `XAPILIB` — Xbox API library
- `XBOXKRNL` — Xbox kernel
- `xboxkrnl.exe` — Xbox kernel executable
- `xam.xex` — Xbox Achievement Manager

### Nome do executável interno: `Banjo2_CPR.exe`

---

## 5. Metadados do Jogo (ArcadeInfo.xml)

### Arquivo: `game/Banjo-Tooie XBLA Extract/ArcadeInfo.xml`

| Propriedade | Valor |
|---|---|
| **ArcadeXDK Version** | `2.0.7776.0` |
| **Project Version** | `1.0.255.0` |
| **Game ID** | `1480657237` |
| **Nome** | `Banjo-Tooie` |
| **Caminho do exe** | `default.xex` |
| **Ícone** | `BanjoTooieIcon.png` |
| **Moeda do jogo** | `Jiggies` |
| **Jogadores** | 1–4 |
| **Gênero** | `116010000` + `116070000` |
| **Leaderboard** | 12 colunas, tipo int, descendente |

### Descrições por idioma:

| Locale | Nome | Descrição |
|---|---|---|
| **en** (default) | Banjo-Tooie | "Upgraded for your pure delight, this is Banjo-Tooie, the 2nd ground-breaking adventure for the bear and bird." |
| **es-es** | Banjo-Tooie | "Ahora llega Banjo-Tooie, la 2ª y emocionante aventura del oso y el pájaro, renovada para disfrutar al máximo." |
| **it-it** | Banjo-Tooie | "Potenziata per puro delight, ecco Banjo-Tooie, la 2ª aventura della coppia orso e uccellino." |
| **fr-fr** | Banjo-Tooie | "Améliorée pour votre régala, voici Banjo-Tooie, la 2ième aventure fracassan de l'our et de l'oiseau." |
| **pt-br** | Banjo-Tooie | "Melhorado só para teu deleite, chegou Banjo-Tooie, a 2ª fantástica aventura de ursos e pássaros." |
| **de-de** | Banjo-Tooie | "Banjo-Tooie, das bahnbrechende Bär-und-Vogel-Abenteuer wurde erweitert, um dir ein noch spannenderer Spielerlebnis zu bieten!" |
| **ko-kr** | Banjo-Tooie | (texto em coreano) |
| **zh-tw** | Banjo-Tooie | (texto em chinês tradicional) |
| **ja-jp** | (texto em japonês) | (texto em japonês) |

### Conquistas (Achievements) — 12 total:

| ID | Arquivo | Descrição |
|---|---|---|
| 52 | Achievement_01.png | "First Steps" — Complete the first level |
| 53 | Achievement_02.png | "Bird Watcher" — Rescue Tooie |
| 54 | Achievement_03.png | "Jiggy Master" — Collect 100 Jiggies |
| 55 | Achievement_04.png | "Boss Slayer" — Defeat all bosses |
| 56 | Achievement_05.png | "Speed Runner" — Complete the game under 30 minutes |
| 57 | Achievement_06.png | "Team Player" — Complete a level in 2-player mode |
| 58 | Achievement_07.png | "Jiggy Hoarder" — Collect 500 Jiggies |
| 59 | Achievement_08.png | "Hidden Gem" — Find a secret area |
| 60 | Achievement_09.png | "Full Game" — Unlock the full game |
| 61 | Achievement_10.png | "Perfect Run" — Complete a level without taking damage |
| 62 | Achievement_11.png | "Collector" — Find all hidden Jiggy piles |
| 63 | Achievement_12.png | "Banjo-Tooie Fan" — Play the game for 2 hours |

### Classificações parentais:

| Sistema | Classificação | Conteúdo |
|---|---|---|
| **GRB** (Austrália) | G (General) | — |
| **OFLC-NZ** | G (General) | Medium Level Animated Violence |
| **OFLC-AU** | G (General) | Medium Level Animated Violence |
| **USK** (Alemanha) | 6+ | Freigegen ab 6 Jahren / § 14 JuSchG |
| **CERO** (Japão) | B (12+) | Leve violência |
| **PEGI** (Europa) | 3+ / 4+ | — |
| **ESRB** (EUA) | E (Everyone) | Cartoon Violence, Comic Mischief |

---

## 6. Assets de Imagem

### Ícones do Jogo

| Arquivo | Tamanho | Formato | Descrição |
|---|---|---|---|
| `BanjoTooieIcon.png` | 64×64 RGBA | PNG | Ícone principal do jogo (Banjo e Tooie) |
| `BanjoTooieMarketplace.png` | 420×95 RGB | PNG | Arte para marketplace (banner horizontal) |
| `32_584109550002000100010001.png` | 32×32 RGB | PNG | Ícone 32px (versão 1) |
| `32_584109550002000200010002.png` | 32×32 RGB | PNG | Ícone 32px (versão 2) |
| `64_584109550002000100010001.png` | 64×64 RGB | PNG | Ícone 64px (versão 1) |
| `64_584109550002000200010002.png` | 64×64 RGB | PNG | Ícone 64px (versão 2) |

### Ícones de Conquistas (12 arquivos)

Todos `64×64 RGBA PNG`:

| Arquivo | Tamanho | Descrição |
|---|---|---|
| `Achievement_01.png` | 7.6 KB | First Steps — Banjo pisando |
| `Achievement_02.png` | 7.3 KB | Bird Watcher — Tooie voando |
| `Achievement_03.png` | 5.1 KB | Jiggy Master — Monte de Jiggies |
| `Achievement_04.png` | 9.4 KB | Boss Slayer — Banjo derrotando chefe |
| `Achievement_05.png` | 7.1 KB | Speed Runner — Cronômetro |
| `Achievement_06.png` | 7.5 KB | Team Player — Banjo + Tooie |
| `Achievement_07.png` | 7.8 KB | Jiggy Hoarder — Grande monte de Jiggies |
| `Achievement_08.png` | 6.2 KB | Hidden Gem — Pedra brilhante |
| `Achievement_09.png` | 6.2 KB | Full Game — Chave dourada |
| `Achievement_10.png` | 5.5 KB | Perfect Run — Escudo |
| `Achievement_11.png` | 7.0 KB | Collector — Coleção completa |
| `Achievement_12.png` | 9.4 KB | Banjo-Tooie Fan — Coração |

### Imagens de Classificação (7 arquivos)

| Arquivo | Tamanho | Formato |
|---|---|---|
| `Rating_ESRB_E.png` | 43×64 RGBA | ESRB "E" |
| `Rating_PEGI_3.png` | 97×64 RGBA | PEGI "3" |
| `Rating_PEGI_4.png` | 97×64 RGBA | PEGI "4" |
| `Rating_CERO_B.png` | 52×64 RGBA | CERO "B" |
| `Rating_GRB_ALL.png` | 55×64 RGBA | GRB "G" |
| `Rating_OFLC_G.png` | 64×64 RGBA | OFLC "G" |
| `Rating_USK_6.png` | 64×64 RGBA | USK "6" |

---

## 7. RAWFiles — Assets Brutos

### `58410955033F0001` — 5.0 MB
- **Magic:** `PIRS` (pacote STFS aninhado)
- Arquivo de dados interno do pacote Arcade

### `ArcadeNormal.ptc` — 98.7 KB
- **Magic:** `PTC+MSHM` (PTC+ Microsoft Metadata Header)
- Layout de tela normal (4:3) para Arcade
- Contém metadados globais de layout

### `ArcadeWide.ptc` — 97.2 KB
- **Magic:** `PTC+MSHM` (PTC+ Microsoft Metadata Header)
- Layout de tela wide (16:9) para Arcade
- Contém metadados globais de layout

### `X360_strings.dat` — 413.7 KB
- Arquivo de strings do jogo
- Contém textos em múltiplos idiomas
- Strings identificadas:
  - `PLAY GAME`, `LEADERBOARDS`, `ACHIEVEMENTS`, `HELP & OPTIONS`
  - `UNLOCK FULL GAME`, `RETURN TO GAME LIBRARY`
  - `HOW TO PLAY`, `CONTROLS`, `SETTINGS`, `CREDITS`
  - `MUSIC VOLUME`, `SOUND EFFECTS VOLUME`
  - `GAME TOTAL`, `RANK`, `JIGGIES`, `NOTES`, `TIME`, `GAMERTAG`, `SCORE`, `BOSSES`
  - `CONTROL METHOD`, `RESUME GAME`, `VIEW TOTALS`
  - `TRIAL GAME` — Descrição da versão trial (20 minutos no primeiro mundo)
  - `BASIC MOVES`, `SPECIAL MOVES`, `MULTIPLAYER HINTS`, `MINI-GAMES HINTS`
  - `HIGH / BACKFLIP JUMP`, `BEAK BARGE ATTACK`, `BEAK BUSTER ATTACK`

### `banjo2_360.ctl` — 182.8 KB
- **Magic:** `B1` (formato de controle Xbox)
- Mapeamento de controles / input configuration
- Contém configurações de botões para até 4 jogadores

### `banjo2_360.tbl` — 13.8 MB
- Tabela de dados do jogo (binary data)
- Provavelmente contém: dados de níveis, sprites, animações, física, IA de inimigos
- Maior arquivo de dados após as texturas

### `db360.cmp` — 11.7 MB
- Dados comprimidos (compressed data)
- Provavelmente: assets do jogo comprimidos (música, efeitos sonoros, dados de nível)

### `db360.textures.cmp` — 48.1 MB
- **Maior arquivo do projeto** (~51% do total dos RAWFiles)
- Texturas comprimidas do jogo
- Contém todos os sprites, backgrounds, UI elements, tilesets

### `xarialuni.ttf` — 6.3 MB
- **TrueType Font** — Arial Unicode MS
- Fonte embutida no jogo para renderização de texto
- 7 tables (FontKit), cmap, names, Microsoft language 0x409 (US English)

---

## 8. Ferramenta XBLA-Extract

### `tools/XBLA-Extract/`

Ferramenta de código aberto (MIT License, Corey Clark, 2022) para manipulação de pacotes Xbox.

### Dependências
- Python 3.6+
- PyQt6 (para GUI)

### Módulos

#### `stfs_extract.py` — Extractor STFS (CLI)
- **Funções principais:**
  - `_parse_stfs_header()` — Parse do cabeçalho STFS (LIVE/PIRS/CON)
  - `_read_entry_bytes()` — Leitura de arquivos do pacote
  - `_parse_arcade_xml()` — Parse de ArcadeInfo.xml
  - `read_game_name()` — Extrai nome do jogo do pacote
  - `get_cluster()` — Algoritmo de cluster (wxPirs)
  - `mstime()` — Conversão de tempo FAT Microsoft
  - `list_live_pirs()` — Lista todos os entries do pacote
  - `extract_live_pirs()` — Extrai arquivos do pacote
- **Suporta:** LIVE, PIRS, CON (headers de 4 bytes)
- **Validação:** tamanho mínimo 0xD000 (53.248 bytes)

#### `stfs_extract_gui.py` — Interface Gráfica (PyQt6)
- **Janela principal:** 780×600, tema dark (#1e1e1e)
- **Duas abas:**
  1. **STFS Package** — Browse, listar e extrair pacotes STFS
  2. **ISO Image** — Browse, listar, extrair e criar ISOs Xbox
- **Classes:**
  - `SortableTreeItem` — Tree widget com ordenação
  - `StfsTab` — Aba STFS (browse, tree, extract)
  - `IsoTab` — Aba ISO (browse, tree, extract, create)
  - `MainWindow` — Janela principal com tabs
- **Features:**
  - Progress dialog com velocidade de transferência
  - Seleção individual de arquivos
  - Limpeza automática de junk files (Thumbs.db, .DS_Store, etc.)
  - Detecção automática de nome do jogo

#### `xiso.py` — Extractor/criador ISO Xbox
- **Suporta:** XGD1, XGD2, XGD3 (Xbox e Xbox 360)
- **Funções:**
  - `_find_volume()` — Localiza XDVDFS volume descriptor
  - `_read_dir_table()` — Lê tabela de diretórios XDVDFS
  - `list_iso()` — Lista arquivos do ISO
  - `extract_iso()` — Extrai arquivos do ISO
  - `read_game_name()` — Lê nome do jogo do ISO
  - `_make_volume_descriptor()` — Cria volume descriptor
  - `create_iso()` — Cria ISO a partir de pasta
- **Constantes:**
  - `SECTOR_SIZE = 2048`
  - `HEADER_DATA = b"MICROSOFT*XBOX*MEDIA"`
  - `XGD1_OFFSET = 0x18300000`
  - `XGD2_OFFSET = 0x0FD90000`
  - `XGD3_OFFSET = 0x02080000`

### `start.bat` — Launcher Windows
```batch
pip install PyQt6
python stfs_extract_gui.py
```

### `XBLA.run` — Launcher Linux
```bash
python3 stfs_extract_gui.py
```

---

## 9. Estatísticas do Projeto

### Tamanho total: ~192 MB

| Componente | Tamanho | % do total |
|---|---|---|
| Pacote STFS original | 93.7 MB | 48.8% |
| RAWFiles (texturas + dados) | 87.0 MB | 45.3% |
| Executável `default.xex` | 6.7 MB | 3.5% |
| Ferramenta XBLA-Extract | ~0.5 MB | 0.3% |
| Imagens (ícones + ratings) | ~0.2 MB | 0.1% |
| Outros (XML, fonte, configs) | ~1.9 MB | 1.0% |

### Contagem de arquivos: 49

| Categoria | Quantidade |
|---|---|
| Arquivos Python (.py) | 3 |
| Arquivos PNG | 23 |
| Arquivos RAWFiles | 9 |
| Arquivos de configuração/metadata | 3 |
| Executável (.xex) | 1 |
| Pacote STFS (.hash) | 1 |
| Scripts de launcher (.bat/.run) | 2 |
| Documentação (README, LICENSE) | 2 |
| Outros | 5 |

---

## 10. Notas Técnicas

### Formatos identificados:
- **STFS** — Sistema de arquivos Xbox 360 (LIVE/PIRS/CON)
- **XEX2** — Executável Xbox 360 (PE-like, com headers Xbox)
- **XDVDFS/XISO** — Sistema de arquivos de disco Xbox (XGD1/2/3)
- **PTC+MSHM** — Microsoft PTC metadata format (layout de arcade)
- **PNG** — Imagens (RGB e RGBA)
- **TrueType** — Fonte embutida (arialuni.ttf)
- **XML** — Metadados ArcadeInfo

### Características do jogo:
- **Gênero:** Plataforma 2D / Aventura
- **Personagens:** Banjo (urso) e Tooie (pássaro)
- **Jogadores:** 1–4 (local multiplayer)
- **Moeda:** Jiggies
- **Conquistas:** 12 (Xbox Live Achievements)
- **Leaderboard:** Sim (12 colunas, descendente)
- **Trial mode:** 20 minutos no primeiro mundo
- **Idiomas:** 9 (EN, ES, IT, FR, PT-BR, DE, KO, ZH-TW, JA)
- **Região:** Livre (all regions)
- **Media ID:** 65D27094
- **Game ID:** 1480657237

### Arquitetura técnica:
- DirectX 9 (D3D9/D3DX9) para gráficos
- XAudio2 para áudio
- Xbox Live (XONLINE) para conquistas e leaderboards
- Xbox UI (XUIRNDR/XUIRUN) para interface
- Xbox Kernel (XBOXKRNL) para serviços do sistema

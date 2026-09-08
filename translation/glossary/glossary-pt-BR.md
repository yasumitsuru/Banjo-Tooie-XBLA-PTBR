# Glossário pt-BR — Banjo-Tooie XBLA

Glossário de termos do jogo para o pipeline de tradução pt-BR.
Baseado nas strings extraídas de `X360_strings.dat` (ver `work/strings/strings.csv`
e `translation/pt-BR/source.json`). `source_index` = índice da entrada em
`work/strings/strings.json`.

## Política de tradução

1. **Nomes próprios (personagens, chefes, fases, mini-jogos, marcas)**:
   **manter em inglês**. São nomes próprios consagrados e a comunidade pt-BR
   os conhece assim.
2. **Itens/equipamento**: **traduzir** para pt-BR (nomes descritivos).
3. **Mecânicas/ataques**: **traduzir** para pt-BR.
4. **Interface/sistema (UI)**: **traduzir** para pt-BR.
5. **Moedas**: `Jiggies` = nome próprio → manter; `Notes` → `Notas`.
6. **Glifos de botão**: placeholders `[0x80]`–`[0x8F]` (bytes 0x80–0x8F) e o byte
   `0x7F` são glifos da fonte do jogo — **manter como estão** na tradução
   (não são texto). Bytes 0x90–0x9F são cp1252 (ex.: 0x92 = U+2019) — **não** são placeholders.
7. **Marcas legais** (Dolby, ESRB, etc.): manter em inglês.
8. **Trial Game**: traduzir como `Demonstração`/`Jogo de Demonstração`, por ser uma versão limitada para experimentar o jogo.
9. **Movimentos, habilidades e itens**: traduzir nomes descritivos para pt-BR; manter somente o nome próprio dentro de um composto (`Kazooie`, `Breegull`). Assim, `Baby Clockwork Kazooie` é descritivo, não um nome próprio independente: usar `Kazooie Mecânica`, não retenção híbrida em inglês. `HATCH` = `Chocar`, `LEG SPRING` = `Mola de Perna`, `GLIDE` = `Planar`; `take the plunge` = `se aventurar` no texto promocional.

## Personagens e NPCs (manter em inglês)

| Termo | Decisão | Evidência (source_index) |
|---|---|---|
| Banjo | manter | 45 (texto: "YOU CAN USE BANJO’S EMPTY PACK...") |
| Kazooie | manter | 40, 41 |
| Mumbo (Mighty Mumbo) | manter | 377 ("PRESS [0x85] TO SEE MIGHTY MUMBO MAGIC!") |
| Grunty | manter | 153 ("GRUNTY INDUSTRIES") |
| Jiggies / Jiggy | manter (nome próprio) | 59, 245 |
| Captain Blubber | manter | 1350 |
| Mr. Patch | manter | 270 ("DEFEAT MR. PATCH") |
| Mrs. Boggy | manter | 274 ("RETURN KIDS TO MRS. BOGGY") |
| Old King Coal | manter | 258 ("DEFEAT OLD KING COAL") |
| Targitzan | manter | 248 ("DEFEAT TARGITZAN") |

## Fases (manter em inglês — nomes próprios)

| Fase | source_index |
|---|---|
| Mayahem Temple | 148 |
| Glitter Gulch Mine | 149 |
| Witchy World | 150 |
| Grunty Industries | 153 |
| Hailfire Peaks | 154 |
| Cloud Cuckooland | 155 |
| Cauldron Keep | 156 |

## Itens, movimentos e habilidades (traduzir — propostas em `tm.json` com status `proposed`)

As decisões abaixo são a referência terminológica para as strings 38–49. Elas foram revisadas por significado e fluência; não representam aprovação de workflow.

| Termo (EN) | Proposta (pt-BR) | source_index |
|---|---|---|
| High / Backflip Jump | Salto Alto / Salto Mortal | 38 |
| Beak Barge Attack | Investida de Bico | 38 |
| Beak Buster Attack | Ataque Bico-Martelo | 38 |
| Rat-a-Tap-Rap | Bicada Saltitante | 38 |
| Roll Attack | Ataque de Rolamento | 38 |
| Peck Attack | Ataque de Bicada | 38 |
| Swim | Nadar | 38 |
| Egg Firing | Disparo de Ovos | 38 |
| Beak Bomb Attack | Ataque Bomba de Bico | 38 |
| Talon Trot | Trote de Garras | 38 |
| Wonder Wing Invulnerability | Invulnerabilidade das Asas Maravilhosas | 38 |
| Homing Eggs Ability | Habilidade de Ovos Teleguiados | 39 |
| Baby Clockwork Kazooie Bomb | Bomba de Kazooie Mecânica | 40 |
| Clockwork-Kazooie Eggs | Ovos de Kazooie Mecânica | 42 |
| Breegull Bash | Golpe Breegull | 41 |
| Egg Aim | Mira de Ovos | 43 |
| Breegull Blaster | Lançador Breegull | 43 |
| Grip Grab | Agarre de Bordas | 43 |
| Bill Drill | Broca de Bico | 44 |
| Beak Bayonet | Baioneta de Bico | 44 |
| Pack Whack | Golpe da Mochila | 45 |
| Split Up | Separar | 45 |
| Airborne Egg Aiming | Mira de Ovos no Ar | 45 |
| Wing Whack | Golpe das Asas | 46 |
| Sub-Aqua Egg Aiming | Mira de Ovos Subaquática | 46 |
| Talon Torpedo | Torpedo de Garras | 46 |
| Springy Step Shoes | Tênis Saltitões | 47 |
| Taxi Pack | Mochila Táxi | 47 |
| Hatch | Chocar | 47 |
| Claw Clamber Boots | Botas de Garra | 48 |
| Snooze Pack | Mochila Soneca | 48 |
| Leg Spring | Mola de Perna | 48 |
| Shack Pack | Mochila Grande | 49 |
| Glide | Planar | 49 |
| Sack Pack | Mochila Pequena | 50 |

## Moedas e pontuação

| Termo | Decisão | source_index |
|---|---|---|
| Jiggies | manter | 59 |
| Notes | Notas | 1579 |
| Score | Pontuação | (UI) |
| Rank | Classificação | (UI) |

## Mini-jogos (manter em inglês — nomes próprios)

| Mini-jogo | source_index |
|---|---|
| Hoop Hurry | 96 |
| Balloon Burst | 97 |
| Trash Can / Trash Can Germs | 99, 213 |
| Tower of Tragedy | 101 |
| Saucer of Peril | 205 |
| Mini-Sub | 209 |
| Twinklies / Twinklies Packing | 211 |
| Mayan Kickball | 51 |

## Marcas e títulos

| Termo | Decisão | source_index |
|---|---|---|
| Banjo-Kazooie: Nuts & Bolts | manter | 2769 |
| Grunty Industries | manter | 153 |
| Dolby / ESRB etc. | manter | 144-145 (Dolby), 131 (ESRB); PEGI não presente no pool |

## Notas

- Strings multilíngues: o pool contém seções EN, FR, DE, ES, IT (e outras).
  O pipeline pt-BR traduz a partir da seção **inglesa**; as demais seções
  servem apenas como referência de tom/terminologia.
- Placeholders `[0x80]`–`[0x8F]` e `0x7F` devem ser preservados byte a byte na
  tradução (ver política item 6). Bytes 0x90–0x9F são cp1252 (ex.: U+2019) —
  não são placeholders.
- Tradução de item com sufixo de custo (ex.: `SPRINGY STEP SHOES, 390 NOTES`)
  mantém o padrão `NOME, NNN NOTAS`.

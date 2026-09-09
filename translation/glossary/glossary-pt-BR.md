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
| Pack (empty) | Mochila (vazia) | 45 |
| Goal (soccer/net) | Gol | 51, 52 |

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
| Twinkles / Twinkles Packing | 211 |
| Mayan Kickball | 51 |
| Chompa's Belly | 51 |
| Pot O' Gold | 51 |
| Colosseum Kickball | 51 |
| Packing Room | 52 |
| Ordnance Storage | 51 |

## Modos de jogo

| Termo (EN) | Proposta (pt-BR) | source_index |
|---|---|---|
| Single Player | Um Jogador | 91 |
| Deathmatch Modern | Mata-Mata Moderno | 92 |
| Deathmatch Classic | Mata-Mata Clássico | 93 |
| Deathmatch | Mata-Mata | 52 |

## Criaturas e tipos (manter em inglês)

| Termo | Decisão | source_index |
|---|---|
| Twinkles | manter em inglês | 51, 52 |
| Germs | manter | 51, 52 |
| Zubbas | manter | 51 |
| Chompa | manter | 51 |

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

## Novos termos propostos — Lote 0100–0149

Os termos abaixo foram propostos no lote 0100–0149 e adicionados a `tm.json` como `proposed`.

| Termo (EN) | Proposta (pt-BR) | source_index | Notas |
|---|---|---|---|
| ZUBBA'S NEST | NINHO DOS ZUBBAS | 100 | minijogo — ZUBBAS mantido |
| SELECT | SELECIONAR | 102 | UI |
| BACK | VOLTAR | 103 | UI |
| LOWER VOLUME | BAIXAR VOLUME | 104 | UI |
| RAISE VOLUME | AUMENTAR VOLUME | 105 | UI |
| PRESS START TO PLAY | PRESSIONE START PARA JOGAR | 108 | UI instrução |
| ERASE SAVE | APAGAR SALVAMENTO | 110 | UI |
| CANCEL | CANCELAR | 114 | UI |
| ACCEPT TRAINING | ACEITAR TREINAMENTO | 115 | UI |
| DECLINE TRAINING | RECUSAR TREINAMENTO | 116 | UI |
| MY SCORE | MINHA PONTUAÇÃO | 118 | UI label |
| OVERALL | GERAL | 119 | UI label |
| RETRY | TENTAR DE NOVO | 127 | UI |
| CONTINUE OFFLINE | CONTINUAR OFFLINE | 128 | UI |
| SAVING... | SALVANDO... | 129 | status UI |
| SAVING FAILED | FALHA AO SALVAR | 132 | erro UI |
| CARRY ON PLAYING | CONTINUAR JOGANDO | 133 | UI |
| GIVE UP AND QUIT | DESISTIR E SAIR | 134 | UI |
| LOADING GAME... | CARREGANDO JOGO... | 135 | status UI |
| CHANGE STORAGE DEVICE | TROCAR DISPOSITIVO DE ARMAZENAMENTO | 138 | UI |
| PERSONAL BEST TIME! | MELHOR TEMPO PESSOAL! | 139 | UI label |
| INTERACT | INTERAGIR | 140 | UI |
| SKIP | PULAR | 141 | UI |
| ISLE O' HAGS | ILHA DOS HAGS | 147 | fase — nome próprio |
| GAME TOTAL | TOTAL DO JOGO | 146 | UI label — consistente com índice 13 |

## Novos termos propostos — Lote 0150–0199

| Termo (EN) | Proposta (pt-BR) | source_index | Notas |
|---|---|---|---|
| JOLLY ROGER'S LAGOON | JOLLY ROGER'S LAGOON | 151 | fase — nome próprio |
| TERRYDACTYLAND | TERRYDACTYLAND | 152 | fase — nome próprio |
| STOP 'N' SWOP | STOP 'N' SWOP | 157 | franquia — nome próprio |
| BOSS TOTAL | TOTAL DO CHEFE | 158 | UI label — paralelo a GAME TOTAL |
| PERSONAL BEST | MELHOR MARCA PESSOAL | 159 | UI label |
| GUEST GAMER PROFILE | PERFIL DE JOGADOR CONVIDADO | 160 | UI |
| CORRUPT SAVE | SALVAMENTO CORROMPIDO | 163 | UI |
| CREATE A NEW SAVE | CRIAR NOVO SALVAMENTO | 165 | UI |
| PLAY WITHOUT SAVING | JOGAR SEM SALVAR | 166 | UI |
| CHANGE GAMER PROFILE | TROCAR PERFIL DE JOGADOR | 168 | UI |
| GAMER PROFILE NOT ONLINE | PERFIL DE JOGADOR NÃO ESTÁ ONLINE | 170 | UI |
| CONNECT TO XBOX LIVE | CONECTAR AO XBOX LIVE | 172 | UI |
| CONTINUE PLAYING OFFLINE | CONTINUAR JOGANDO OFFLINE | 173 | UI |
| TRIAL GAME | JOGO DE DEMONSTRAÇÃO | 174 | UI — consistente com índice 28 |
| UNLOCK FULL GAME | DESBLOQUEAR O JOGO COMPLETO | 176 | UI — consistente com índice 30 |
| CONTINUE WITH THE TRIAL | CONTINUAR COM A DEMONSTRAÇÃO | 177 | UI |
| GAMER PROFILE OFFLINE | PERFIL DE JOGADOR OFFLINE | 178 | UI |
| SIGNED OUT | SESSÃO ENCERRADA | 180 | UI — distinto de DISCONNECTED (194) |
| CONTINUE PLAYING | CONTINUAR JOGANDO | 182 | UI — consistente com índice 133 |
| LOADING ERROR | ERRO AO CARREGAR | 183 | UI |
| SAVE FAILED | FALHA AO SALVAR | 186 | UI — consistente com índice 132 |
| SELECT A NEW DEVICE | SELECIONAR UM NOVO DISPOSITIVO | 188 | UI |
| CONTINUE WITHOUT SAVING | CONTINUAR SEM SALVAR | 189 | UI |
| GAMER PROFILE MISSING | PERFIL DE JOGADOR NÃO ENCONTRADO | 190 | UI |
| LOOK AROUND | OLHAR AO REDOR | 193 | UI |
| DISCONNECTED | DESCONECTADO | 194 | UI |
| OVERWRITE SAVE? | SOBRESCREVER SALVAMENTO? | 197 | UI |
| NO - DON'T OVERWRITE | NÃO - NÃO SOBRESCREVER | 199 | UI |

## Decisões de fase (manter em inglês)

| Fase | source_index |
|---|---|
| JOLLY ROGER'S LAGOON | 151 |
| TERRYDACTYLAND | 152 |
| STOP 'N' SWOP | 157 |

## Novos termos propostos — Lote 0200–0249

| Termo (EN) | Proposta (pt-BR) | source_index | Notas |
|---|---|---|---|
| OVERWRITE AND SAVE | SOBRESCREVER E SALVAR | 200 | UI label — botão de ação |
| SAVING OF SETTINGS TO GAMER PROFILE HAS FAILED | FALHA AO SALVAR AS CONFIGURAÇÕES NO PERFIL DE JOGADOR | 201 | UI erro — paralelo a índice 186 |
| Banjo-Tooie | Banjo-Tooie | 202 | título do jogo — manter completo |
| BALLOON BURST CHALLENGE | BALLOON BURST CHALLENGE | 203 | mini-jogo — nome próprio |
| HOOP HURRY CHALLENGE | HOOP HURRY CHALLENGE | 204 | mini-jogo — nome próprio |
| SAUCER OF PERIL RIDE | SAUCER OF PERIL RIDE | 205 | mini-jogo — nome próprio |
| DODGEMS CHALLENGE (1-ON-1) | DODGEMS CHALLENGE (1-ON-1) | 206 | mini-jogo — nome próprio |
| DODGEMS CHALLENGE (2-ON-1) | DODGEMS CHALLENGE (2-ON-1) | 207 | mini-jogo — nome próprio |
| DODGEMS CHALLENGE (3-ON-1) | DODGEMS CHALLENGE (3-ON-1) | 208 | mini-jogo — nome próprio |
| MINI-SUB CHALLENGE | MINI-SUB CHALLENGE | 209 | mini-jogo — nome próprio |
| CHOMPA'S BELLY | CHOMPA'S BELLY | 210 | mini-jogo — nome próprio |
| TWINKLIES PACKING | TWINKLIES PACKING | 211 | mini-jogo — nome próprio |
| POT O'GOLD | POT O'GOLD | 212 | mini-jogo — nome próprio |
| TRASH CAN GERMS | TRASH CAN GERMS | 213 | mini-jogo — nome próprio |
| ZUBBA'S HIVE | ZUBBA'S HIVE | 214 | mini-jogo — nome próprio |
| TRIAL GAME | DEMONSTRAÇÃO | 215 | UI — consistente com índice 32 |
| OPTION UNAVAILABLE | OPÇÃO INDISPONÍVEL | 217 | UI label |
| THIS OPTION IS ONLY AVAILABLE IN THE FULL GAME | ESTA OPÇÃO ESTÁ DISPONÍVEL APENAS NO JOGO COMPLETO | 218 | UI mensagem |
| UNLOCK FULL GAME | DESBLOQUEAR O JOGO COMPLETO | 219 | UI label — consistente com índice 30 e 176 |
| CONTINUE WITH THE TRIAL | CONTINUAR COM A DEMONSTRAÇÃO | 220 | UI — consistente com índice 177 |
| WELL DONE! | BOM TRABALHO! | 221 | UI label — paralelo ao glossário índice 175 |
| STOP 'N' SWOP II FOUND | Stop 'n' Swop II encontrado | 223 | UI mensagem — franquia mantida |
| OH NO, NOT AGAIN... | OH NÃO, NÃO DE NOVO... | 224 | linha de personagem |
| LUCKY LOSER | Lucky Loser | 225 | conquista — nome próprio |
| BETTER THAN A SLAP | Better Than A Slap | 226 | conquista — nome próprio |
| AND THE WINNER IS… | And The Winner Is… | 227 | conquista — nome próprio (… U+2026 preservado) |
| NOW WHO’S BOSS? | Now Who’s Boss? | 228 | conquista — nome próprio (’ U+2019 preservado) |
| CALMER CHAMELEON | Calmer Chameleon | 229 | conquista — nome próprio |
| HEROIC FAILURE | Heroic Failure | 230 | conquista — nome próprio |
| OH NO, NOT AGAIN... | OH NO, NOT AGAIN... | 231 | conquista (all caps) — manter EN |
| LUCKY LOSER | LUCKY LOSER | 232 | conquista (all caps) — manter EN |
| BETTER THAN A SLAP | BETTER THAN A SLAP | 233 | conquista (all caps) — manter EN |
| AND THE WINNER IS... | AND THE WINNER IS... | 234 | conquista (all caps) — manter EN |
| NOW WHO'S BOSS? | NOW WHO'S BOSS? | 235 | conquista (all caps) — manter EN |
| CALMER CHAMELEON | CALMER CHAMELEON | 236 | conquista (all caps) — manter EN |
| HEROIC FAILURE | HEROIC FAILURE | 237 | conquista (all caps) — manter EN |
| YOUR SCORE BEATS | SUA PONTUAÇÃO SUPERA | 238 | UI label — paralelo a ES "SUPERA A" |
| CONGRATULATIONS! A PERSONAL BEST! | PARABÉNS! MELHOR MARCA PESSOAL! | 239 | UI label — "PARABÉNS" (pt-BR), termo de 159 |
| CONGRATULATIONS! YOU HAVE BEATEN | PARABÉNS! VOCÊ DERROTOU | 240 | UI label — "PARABÉNS" (pt-BR) |
| MODERN | MODERNO | 241 | modo de jogo |
| MODERN - INVERTED | MODERNO - INVERTIDO | 242 | modo de jogo |
| CLASSIC | CLÁSSICO | 243 | modo de jogo |
| CLASSIC - INVERTED | CLÁSSICO - INVERTIDO | 244 | modo de jogo |
| JIGGY | JIGGY | 245 | coletável — nome próprio |
| JIGGY HINT | DICA DE JIGGY | 246 | UI label — JIGGY (coletável) mantido, padrão DE/ES/IT |
| JIGGY TIPS | DICAS DE JIGGY | 247 | UI label — JIGGY (coletável) mantido, padrão DE/ES/IT |
| DEFEAT TARGITZAN | DERROTAR TARGITZAN | 248 | UI instrução — TARGITZAN nome próprio |
| INSIDE TARGITZAN'S TEMPLE | DENTRO DO TEMPLO DE TARGITZAN | 249 | UI instrução — TARGITZAN nome próprio |

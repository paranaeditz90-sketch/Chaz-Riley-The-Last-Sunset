# The Last Sunset — guia pra continuar o projeto (ChatGPT ou outra IA)

Este arquivo explica TUDO que você precisa pra continuar o jogo de onde parou. Leia inteiro antes de responder.

---

## 0. Antes de tudo

### Quem manda: o diretor (LM)
- Fala português do Brasil. Responda em PT-BR, natural, direto, sem enrolação nem linguagem de empresa.
- Ele quer um parceiro crítico: não concorde automaticamente. Se uma ideia for ruim, diga e explique por quê, e
  proponha algo melhor. Separe fato de suposição. Não invente informação: se não sabe, diga.
- Prioridade: **precisão > verdade > raciocínio > utilidade > estilo**.
- Ele gosta de ir **por partes**. Não faça 10 coisas quando pediu 1. Pergunte antes de decisões grandes.
- Ele joga no **celular Android**. Toda versão jogável vai como **um arquivo .html só** (ver seção 6).

### REGRA Nº 1 — SPOILER
- A pasta `SELADO/` tem o roteiro e a lore secretos (a ameaça, o plot twist, o que cada um esconde, os finais).
- **O diretor NÃO quer saber.** Nunca mostre, resuma, cite, dê dica, nem confirme ou negue teorias sobre o
  conteúdo selado. Use só pra escrever coisas coerentes com ele.
- Ao pedir sprites ao diretor (ele gera em IA de imagem), **não peça nada que entregue a história** (a ameaça,
  objetos-chave, mortes). Isso você faz por código ou pede de um jeito neutro.
- Como abrir o selado: ver o arquivo `SELADO/COMO_ABRIR.txt` dentro do pacote.

---

## 1. O jogo (sem spoiler)
- **Chaz & Riley — The Last Sunset.** Pixel art 2D, drama/terror/RPG interativo, **+18** (temas pesados com
  propósito, sem gore gratuito), **sem combate** (fugir, se esconder, observar, escolher).
- Jogabilidade inspirada no **jeito** de Detroit: Become Human (escolhas que ramificam, morte permanente,
  fluxograma) e House 2 (o mundo reage). Nada de conteúdo desses jogos.
- 3 jogáveis: **Chaz** (cachorro azul), **Riley** (gato vinho), **Névoa** (cachorro cor chumbo, criado pelo
  diretor). A troca de ponto de vista é dirigida pela história.
- Primeira versão: **Capítulo 1**, 10–15 min, 3 finais. Começa em casa, atravessa a cidade até o morro ao pôr
  do sol, depois a noite. Detalhes da estrutura sem spoiler: `docs/GDD.md`.
- Chaz e Riley são do artista **Bruce Bronze** (TikTok). Pra publicar, precisa de permissão dele.

## 2. Regras de arte (decisões do diretor — não mude sem perguntar)
1. Os sprites vêm de IA de imagem (Gemini, agora ChatGPT) e entram no jogo **como vieram**: o script só tira o
   fundo, recorta e alinha. **Nada é redesenhado à mão.**
2. Conserto só reaproveitando pixels do **próprio** desenho (ex.: colar a cabeça do quadro de andar no de correr).
   Proibido conversor automático de desenho→pixel art (borra).
3. **Não mudar os personagens originais.** Proporção chibi travada: cabeça grande (quase metade da altura),
   corpo e pernas curtos, contorno preto grosso.
4. **Sempre comparar lado a lado, na mesma altura,** antes de aceitar uma folha nova. Se o desenho mudou
   (mais magro, cabeça menor, olho diferente, traço fino), **não usa** e explica ao diretor com a imagem.
5. Pra pedir sprites, o diretor anexa a **referência limpa** do personagem (`pixel-art/<nome>/referencia_parado.png`)
   e o prompt começa com "COPIE IDÊNTICO, NÃO redesenhe". Fundo verde liso (#00FF00) ou transparente.
6. **Sempre revisar** se há algo levemente estranho ou inconsistente (olho, orelha, rabo, "3" do peito, escala,
   cor, pulo de quadro) antes de entregar.
7. Cores: Chaz azul (`#1a34e1`), Riley vinho no sprite e **vermelho** no texto (`#b3122b`), Névoa **chumbo**
   (`#37252d` no sprite, `#4e3a46` no texto). O diretor confirmou o chumbo do Névoa.

## 3. Texto, voz e som
- **Riley não tem gênero marcado.** Nenhum texto do jogo usa pronome ou adjetivo de gênero pra Riley
  ("Riley tá com medo", nunca "ela/ele", "assustada/o"). Vale pros seus textos ao diretor também.
- **Falas em bilhete de papel rasgado**, como nos vídeos do Bruce, com a **letra de mão e a cor de cada
  personagem** (`game/src/dialogo.js`): Chaz = Patrick Hand azul; Riley = Permanent Marker vermelho;
  Névoa = Shadows Into Light chumbo. Texto em MAIÚSCULAS.
- **Voz = som do bicho**: cachorro late, gato mia (tom varia a cada fala). Nada de voz gravada.
- Som e música: **só CC0 ou CC BY** com crédito em `game/CREDITOS.md`. Música atual: "Evening" (Kevin MacLeod,
  CC BY 4.0). Freesound/Pixabay bloqueiam download automático; Mixkit ficou de fora (licença não confirmada).

## 4. Cânone do Bruce (confirmado nos vídeos dele, ver `referencias_bruce/README.md`)
- **Chaz Barkley** ("Take notes, Barkley"), toca numa banda, vive com o celular, alegre.
- **Riley**: seco, empurra o Chaz ("Not a pillow"), mas agradece escondendo a cara no cachecol ("Thanks").
  Defende um filhote do preconceito: "You shouldn't care what others think" (existe preconceito contra gatos).
- **Filhote laranja** (fãs chamam de "Andy", não confirmado) e **cavalier vermelha e branca** guitarrista
  (sem nome conhecido; perguntar ao diretor). O diretor aprovou os dois **com papel na história**.
- Cenário: trigal com linhas de transmissão ao pôr do sol, outono, cachecóis.
- Não invente nome por cima de personagem do Bruce.

## 5. Pastas
```
jogo/                      projeto inteiro (é o repositório público)
  game/                    o jogo (Phaser 3.90)
    index.html             página (fontes @font-face)
    src/main.js            inicia o Phaser (espera as fontes carregarem)
    src/scenes/Teste.js    cena atual: andar, correr, trocar, esconder, conversar, vida, som
    src/dialogo.js         bilhetes de fala + voz do bicho + faixas de cinema
    public/assets/         sprites (png + sprites.json), audio (mp3), fonts (ttf)
    vendor/                phaser.min.js (pra montar sem npm)
    CREDITOS.md            licenças de som/música/fonte
  pixel-art/               fontes das folhas (imagens da IA) e folhas finais por personagem
    build_sprites.py       monta as folhas do jogo a partir das imagens da IA
  tools/
    montar_html.py         monta o jogo num .html só (Python puro) ← use este
    sheet_copy.py          tirar fundo, recortar, alinhar, consertos (trocar_cabeca, trocar_rosto)
    montar_audio.py        corta/normaliza os sons (precisa de ffmpeg)
    baixar_audio.sh        baixa as fontes de som (precisa de internet)
  docs/GDD.md              design do jogo (sem spoiler)
  docs/PROMPTS_GEMINI.md   todos os prompts de sprite (rodadas 1 a 4 + ChatGPT)
jogar/the_last_sunset.html versão jogável mais recente
referencias_bruce/         falas lidas dos vídeos do Bruce, folhas de referência do diretor
SELADO/                    roteiro e lore secretos (trancado; ver COMO_ABRIR.txt)
```

## 6. Como gerar o jogo jogável
```
cd jogo
python3 tools/montar_html.py ../the_last_sunset.html
```
Precisa só de Python 3. Mande o .html pro diretor; ele abre no Chrome do celular, toca em "Toque pra jogar"
(tela cheia, deitado). Funciona sem internet.

Controles: WASD/setas andar · Shift correr · E falar (perto de alguém) · C esconder (segurar) · Tab/1/2/3 trocar.
No toque: arrastar à esquerda (até o fim = correr), botões CORRER, TROCAR, ESCONDER, FALAR.

## 7. Como entra uma folha nova de sprite
1. Salvar a imagem em `pixel-art/<nome>/fonte/`.
2. Em `pixel-art/build_sprites.py`, ler com `sheet(caminho, "auto", linhas, colunas)` (detecta fundo verde,
   xadrez ou transparente), igualar escala pela altura do "parado" e cor com `color_match`.
3. **Comparar lado a lado na mesma altura** com o parado do jogo. Se mudou o desenho, não usa.
4. Colocar nas linhas da folha e nomear as animações (o jogo usa: `{dir}_parado/andar/correr`, `frente_piscar`,
   `frente_olhar_esq/dir`, `gesto`, `agachar_{dir}`, `tapar_{dir}`, `susto_*`, `medo_frente`, `sentado_*`...).
5. `python3 pixel-art/build_sprites.py` (precisa de numpy, pillow, scipy) e depois `tools/montar_html.py`.

## 8. Estado atual (pronto)
- Chaz, Riley e Névoa: andar e correr nas 4 direções; parado; piscar e olhar pros lados (de frente);
  gesto (Chaz celular, Névoa bocejo); agachar/tapar a boca/susto/medo/sentado/pegar/ler/bater.
- Consertos feitos: orelha extra da Riley no correr de perfil; olho fechado do Chaz andando de frente.
- Jogo: câmera segue, troca de personagem, quem fica parado de lado vira pra câmera e pisca, trigo balança
  e volta quando alguém passa, poeira ao correr, passos na grama, vento, música, conversa em bilhete com voz.
- Riley sem gestos de braço cruzado ainda e sem 3 poses de frente (as da IA vieram erradas).

## 9. Próximos passos (em ordem)
1. **Andar em 8 quadros** pros três (perna passando pela outra). Prompt: `docs/PROMPTS_GEMINI.md`, rodada 4,
   com a referência limpa.
2. **Rabo balançando parado** (rodada 3b / prompt do ChatGPT com referência limpa).
3. **Riley**: poses de braço cruzado, agachar/tapar/medo de frente (rodada 3d, proporção certa).
4. **Lanterna e escuridão**: cone na direção do último movimento, halo, luz em degraus, sombra; o Névoa
   (escuro) precisa de contorno de luz pra não sumir.
5. **Cenários** do capítulo 1 (casa, rua, morro, trigal de noite) e **moradores** (inclui o filhote e a cavalier).
6. **Cutscenes** com escolha de fala (com tempo nas tensas), flags, fluxograma, e o capítulo 1 em si.

## 10. Decisões do diretor (histórico)
- Pixel art pelas IAs, copiada fielmente; nada de redesenho. Estilo da folha v2 do Chaz (Gemini) é o padrão.
- Lanterna aponta pra onde o personagem anda. Sombreado próprio (não é RTX). Mato reage ao passar.
- Personagens vivos: piscar, olhar, gestos, rabo; nada de boneco duro.
- Névoa: masculino, cor chumbo (confirmado).
- Riley sem gênero marcado. Filhote e cavalier do Bruce entram com papel na história.
- Começar em casa/cidade antes do morro (ideia do diretor).
- Falas no bilhete com cor e letra de cada um; voz = latido/miado.
- Entregas como arquivo HTML (não página do Claude).
- História "nível cinema", coerente do começo ao fim (bíblia selada + mapa de pistas).

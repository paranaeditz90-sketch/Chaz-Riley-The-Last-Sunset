# Chaz & Riley — The Last Sunset · GDD (sem spoilers)

> A ameaça, o plot twist e o roteiro completo ficam num documento **selado**, fora deste
> repositório público. Este arquivo só descreve escopo, sistemas e produção.

## 1. Decisões de escopo (fechadas com o diretor)

| Tema | Decisão |
|---|---|
| Gênero | Drama / terror / RPG interativo de decisões. **Sem combate**: fugir, se esconder, observar, escolher. |
| Classificação | **+18**. Temas pesados tratados sem aliviar. Momentos felizes, tristes e de ameaça. |
| Personagens jogáveis | **3**: Chaz, Riley e Névoa (masculino). A troca de perspectiva é dirigida pela história: quando um morre ou quando a trama precisa daquele ponto de vista. |
| Referência de jogabilidade | O *jeito de jogar* de **Detroit: Become Human** (escolhas que ramificam, morte permanente, fluxograma de capítulo) e **House 2** (o mundo reage ao que você faz). Nenhum conteúdo, personagem ou trama desses jogos. |
| Primeira versão | **Capítulo 1**, 10–15 min, **3 finais**. |
| Plataforma | HTML5 + JavaScript (Phaser 3), Android via Capacitor. Controle por toque **e** teclado. |
| Arte | Estilo da folha do Chaz feita no Gemini (v2), **aprovado pelo diretor**: pixel art chibi, cor chapada, contorno preto grosso. As folhas vêm do Gemini (prompts em `docs/PROMPTS_GEMINI.md`) e entram no jogo **como vieram**: o script (`pixel-art/build_sprites.py`) só tira o fundo, recorta e alinha. Nada é redesenhado; o que sair errado volta pro Gemini. **Proibido** conversor de desenho→pixel (o que borra). Quadro 184×192 (resolução original da folha). Volume e sombra vêm da iluminação do jogo, não do sprite. |

## 2. Pilares

1. **O que você vê é o que você sabe.** Só existe o que o personagem controlado vê. A lanterna é o olhar.
2. **Escolha tem peso e memória.** Toda escolha relevante grava uma flag. O jogo lembra entre capítulos.
3. **Gente, não boneco.** Personagens com vontade própria, segredos e reações. Ninguém existe só pra morrer.
4. **Medo por tensão, não por susto barato.** Silêncio, escuridão, regras que o jogador aprende e depois teme.

## 3. Sistemas

### Movimento e câmera
- Top-down, sprites em 3 direções desenhadas (frente, costas, perfil) e perfil espelhado pra esquerda.
- Ciclo de andar em passos (sem interpolação), pose segurada ~4–5 frames a 30 fps, bob de 1 px. Medido no clipe de referência.
- Câmera trava no personagem controlado.

### Lanterna
- Cone na direção do **último movimento**; parado, mantém a direção. Confirmado pelo diretor.
- Duas camadas medidas na referência: **halo** redondo em volta do personagem + **cone** que abre ~55–70°.
- Luz em degraus (3–4 níveis), não gradiente liso. Fora da luz, preto.
- Coisas que só aparecem dentro da luz (pistas, marcas no chão).
- Bateria limitada em trechos específicos (não é gerência de inventário).

### Esconder e fugir
- Esconderijos de contexto (trigo alto, armário, debaixo da varanda).
- Prender a respiração: segurar o botão enquanto algo passa; soltar cedo ou tarde demais tem consequência.
- Perseguição: rotas curtas com escolha de caminho, sem combate.

### Escolhas e consequências
- Diálogo com 2–3 opções e algumas **com tempo** (silêncio também é escolha).
- Escolhas de **ação** no mundo: fechar uma porta, ligar ou não uma luz, ir ou ficar.
- Flags persistentes: confiança entre cada par de personagens, segredos contados ou guardados, quem está vivo ou desaparecido, e outras métricas internas que não são mostradas.
- **Fluxograma de fim de capítulo** com os ramos descobertos e os bloqueados (incentiva rejogar).

### Troca de personagem
- Ocorre em pontos de história e quando alguém morre ou desaparece.
- Morte é permanente no save. Se todos caem, o capítulo termina num final próprio.

## 4. Capítulo 1 — estrutura (sem spoiler)

Ramifica e depois converge em 3 finais:

1. **Fim de tarde no trigal** (feliz). Os três no morro, linhas de transmissão, o pôr do sol. Escolhas pequenas de relacionamento.
2. **A escuridão.** Algo errado acontece com o pôr do sol. Primeira regra do mundo.
3. **Separação.** Ponto de vista de um, depois de outro. Esconder, lanterna, pistas.
4. **A casa.** Reencontro e uma decisão de ação com consequência imediata.
5. **Final A / B / C** + fluxograma.

Só um personagem fica garantido vivo no Cap. 1. Os outros dois podem ser perdidos conforme as escolhas.

## 5. Aviso de conteúdo (mostrado no início do jogo)

Violência e morte, sangue, luto e culpa, ideação suicida, abuso, medo e paranoia.
Todo esse conteúdo está a serviço da história.

## 6. Produção — ordem de trabalho

1. **Sprites** (Gemini, cópia fiel): Chaz, Riley e Névoa no jogo. Consertos pendentes: orelha da Riley no correr de perfil, linha de costas do Chaz. Depois, extras de terror (agachar/esconder, susto, medo). Cada passo revisado com o diretor antes do próximo.
2. **Protótipo jogável**: Vite + Phaser 3, joystick virtual + botão de ação, teclado (WASD/setas + E/Espaço), escuridão + lanterna, esconderijo. Testado com Playwright (screenshot e gravação).
3. **Cenários** do Cap. 1 (trigal ao pôr do sol, trigal à noite, casa da fazenda).
4. **Conteúdo**: diálogos, escolhas, flags, 3 finais, fluxograma.
5. **Som** (busca de efeitos com licença livre) e empacotamento Android.

## 7. Referências de arte (resumo do estudo)

- O traço do Bruce Bronze evoluiu de quase sem linha (set/2026) para linha preta média/grossa e cor chapada (out–nov/2026). Os sprites seguem a fase atual: **contorno escuro em todo o personagem**.
- O Bruce não usa hue shift, e o estilo Gemini aprovado também é chapado. Hue shift fica pra cenário e iluminação.
- Proporção: Chaz ≈ 3 cabeças de altura. Na Riley, as orelhas somam ~14% da altura e são a silhueta dela.
- Paleta do Chaz (folha final): `#2a3be8` (corpo) `#000000` (contorno) `#ffffff` (olho e "3") `#8a4fd8` (íris) `#3a1a6a` (pupila) `#ff6f91` (boca). Riley e Névoa: definidas quando as folhas chegarem.

## 8. Avisos de projeto

- Chaz e Riley são personagens do Bruce Bronze. Pra publicar, precisa de permissão do criador.
- O repositório do jogo é **público**. Material de terceiros (vídeos, frames) e o roteiro selado ficam no repositório privado.

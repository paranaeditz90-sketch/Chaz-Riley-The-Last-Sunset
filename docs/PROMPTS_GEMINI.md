# Prompts pro Gemini (folhas de sprite)

Estilo aprovado pelo diretor: o da folha v2 do Chaz feita no Gemini
(`pixel-art/chaz/fonte/chaz_gemini_v2.jpg`). As folhas novas seguem o **mesmo layout**,
pra passarem pelo mesmo processo (`tools/restore_gemini.py` + build do personagem).

## Como pedir

1. Se der, usar a **mesma conversa** do Gemini onde saiu a folha v2 do Chaz (ele mantém o estilo).
2. Anexar **2 imagens**: a folha v2 do Chaz + a folha de referência do personagem.
3. Colar o prompt.
4. Baixar pelo **botão de download** do Gemini (arquivo original). Print ou "compartilhar" vem em JPEG reduzido.
5. Se só uma linha sair errada, pedir pra refazer **só aquela linha**, não a folha toda.

**Por que fundo verde:** a Riley é vermelho-escura e o Névoa é cinza bem escuro. No fundo xadrez
branco/cinza, ou com contorno preto, o restaurador confunde corpo com fundo ou com linha. Verde
chapado não existe em nenhum dos três.

**Layout (igual ao Chaz v2):** 7 colunas × 4 linhas. Linhas: frente, esquerda, direita, costas.
Colunas: parado, andar ×3, correr ×3.

---

## Riley

```
Use a primeira imagem (folha do Chaz azul) como modelo EXATO de estilo e de layout. Use a segunda imagem só como referência de como a personagem é.

Crie a mesma folha de sprites, agora com a RILEY: gata vermelho-escura (cor de vinho), orelhas grandes e pontudas, tufos de pelo nas bochechas e no peito, rabo comprido e curvado, marca "3" branca no peito, olhos roxos com a parte branca creme e pálpebras meio caídas (cara de tédio, meio emburrada), boca pequena e séria.

Estilo (igual ao do Chaz): pixel art chibi, cabeça grande, cor chapada sem sombra e sem degradê, contorno preto grosso em volta de tudo, pixels quadrados e nítidos, sem anti-aliasing, sem borrado.

Layout: grade de 7 colunas × 4 linhas, com o mesmo espaçamento entre os quadros. A personagem tem o mesmo tamanho em todos os quadros, os pés ficam todos na mesma linha e nada encosta no quadro vizinho.
- Linha 1, de frente: parada, andando (3 quadros), correndo (3 quadros).
- Linha 2, virada pra esquerda: parada, andando (3), correndo (3).
- Linha 3, virada pra direita: parada, andando (3), correndo (3).
- Linha 4, de costas: parada, andando (3), correndo (3).
Andando = passo com a perna esquerda, pernas passando juntas, passo com a perna direita.
Correndo = perna esquerda esticada à frente, corpo no ar, perna direita esticada à frente.

Regras:
- Olhos SEMPRE iguais em todos os quadros (mesmo formato, tamanho e pálpebra meio caída), olhando pra direção do corpo. Nunca fechados, nunca vesgos.
- O "3" do peito igual em todos os quadros (de costas não aparece).
- O corpo tem a mesma altura do Chaz da primeira imagem; as orelhas ficam acima disso.
- Fundo verde liso (#00FF00). Sem xadrez, sem sombra no chão, sem texto, sem números e sem molduras.
```

## Névoa

```
Use a primeira imagem (folha do Chaz azul) como modelo EXATO de estilo e de layout. Use a segunda imagem só como referência de como o personagem é.

Crie a mesma folha de sprites, agora com o NÉVOA (menino): cachorro de pelo cinza bem escuro puxado pro ameixa (como na segunda imagem), pelo desgrenhado com topete espetado no alto da cabeça, orelhas grandes, caídas e peludas, tufo de pelo no peito, desenho de uma nuvem em traço rosa-claro no peito, rabo peludo, olhos roxos semicerrados (cara de sono), boca pequena.

Estilo (igual ao do Chaz): pixel art chibi, cabeça grande, cor chapada sem sombra e sem degradê, contorno preto grosso em volta de tudo, pixels quadrados e nítidos, sem anti-aliasing, sem borrado.

Layout: grade de 7 colunas × 4 linhas, com o mesmo espaçamento entre os quadros. O personagem tem o mesmo tamanho em todos os quadros, os pés ficam todos na mesma linha e nada encosta no quadro vizinho.
- Linha 1, de frente: parado, andando (3 quadros), correndo (3 quadros).
- Linha 2, virado pra esquerda: parado, andando (3), correndo (3).
- Linha 3, virado pra direita: parado, andando (3), correndo (3).
- Linha 4, de costas: parado, andando (3), correndo (3).
Andando = passo com a perna esquerda, pernas passando juntas, passo com a perna direita.
Correndo = perna esquerda esticada à frente, corpo no ar, perna direita esticada à frente.

Regras:
- Olhos SEMPRE iguais em todos os quadros (mesmo formato, tamanho e semicerrados), olhando pra direção do corpo. Nunca fechados, nunca vesgos.
- A nuvem do peito igual em todos os quadros (de costas não aparece).
- O corpo tem a mesma altura do Chaz da primeira imagem (o topete pode passar um pouco).
- Fundo verde liso (#00FF00). Sem xadrez, sem sombra no chão, sem texto, sem números e sem molduras.
```

## Chaz — linha que faltou (correr de costas)

Anexar só a folha v2 do Chaz.

```
Use esta imagem (folha do Chaz azul) como modelo EXATO. Faça só UMA linha com 4 quadros do Chaz DE COSTAS: parado, e correndo em 3 quadros (perna esquerda esticada à frente, corpo no ar, perna direita esticada à frente). Mesmo estilo, mesmo tamanho e mesmo espaçamento da folha. Rabo de cachorro peludo e comprido, balançando de lado (não uma bolinha de coelho). Fundo verde liso (#00FF00). Sem xadrez, sem sombra, sem texto.
```

---

## Consertos (rodada 2)

### Riley — orelha a mais no correr de perfil (RESOLVIDO sem Gemini)
O Gemini repetiu o erro. Resolvido no script: a cabeça dos quadros de andar (pixels do Gemini) foi colada
nos 6 quadros de correr (`trocar_cabeca` em `tools/sheet_copy.py`), com autorização do diretor.
Prompt usado (não funcionou):

```
Use esta imagem (folha da Riley) como modelo EXATO. Nas linhas 2 e 3 (Riley de perfil), os 3 quadros de CORRER ganharam uma orelha caída de cachorro além das orelhas de gata. Refaça só esses 6 quadros, em 2 linhas de 3: correndo virada pra esquerda (3) e correndo virada pra direita (3), com SÓ as duas orelhas de gata pontudas, iguais às dos quadros de andar. Mesmo estilo, tamanho, olhos e espaçamento. Fundo verde liso (#00FF00), sem xadrez, sem texto.
```

### Chaz — linha de costas inteira (FEITO: `chaz_costas_linha_gemini.jpg`)
O correr de costas veio com a cabeça menor e mais redonda que a do andar de costas da folha v2.
Uma linha só, gerada de uma vez, fica igual entre si. Anexar a folha v2 do Chaz.

```
Use esta imagem (folha do Chaz azul) como modelo EXATO. Faça só UMA linha com 7 quadros do Chaz DE COSTAS, todos com a mesma cabeça larga e as orelhas caídas dos lados, iguais à linha de costas da folha: parado, andando (3 quadros) e correndo (3 quadros: perna esquerda esticada à frente, corpo no ar, perna direita esticada à frente). Rabo de cachorro peludo, balançando de lado. Mesmo tamanho e espaçamento. Fundo verde liso (#00FF00), sem xadrez, sem sombra, sem texto.
```

---

## Rodada 3 — poses extras (vida, esconder, susto, cenas)

Mesma grade pros três (7 colunas × 4 linhas), pra entrar no jogo pelo mesmo processo.
Linha 1 = de frente parado (piscar, olhar, gesto próprio). Linhas 2 e 3 = perfil esquerda/direita
(piscar, esconder, tapar a boca, susto, pegar do chão, ler papel, bater na porta).
Linha 4 = frente/costas (esconder, susto, medo, sentado).
Anexar a folha do próprio personagem que o Gemini já fez. Ordem: Chaz → Riley → Névoa.
Os prompts completos estão na conversa (mensagem da rodada 3) e abaixo.

### Chaz (anexar a folha v2 do Chaz)
```
Use a imagem (folha do Chaz azul) como modelo EXATO de estilo, tamanho e traço. Faça uma folha NOVA com o mesmo Chaz em outras poses.

Estilo igual: pixel art chibi, cor chapada, contorno preto grosso, pixels nítidos, sem borrado. O Chaz tem o mesmo tamanho dos quadros da folha modelo, o "3" branco no peito sempre legível (nunca espelhado) e os olhos ABERTOS em todas as poses, menos onde eu peço olho fechado.

Grade de 7 colunas × 4 linhas, mesmo espaçamento, pés na mesma linha, nada encostando no quadro vizinho.

Linha 1 — de frente, parado:
1) piscando, olhos meio fechados
2) piscando, olhos fechados
3) olhando pra esquerda (só a cabeça vira)
4) olhando pra direita (só a cabeça vira)
5) tirando o celular do bolso
6) olhando a tela do celular, sorrindo
7) segurando o celular de lado, filmando, animado

Linha 2 — virado pra esquerda:
1) piscando, olho fechado
2) agachado, escondido
3) agachado, tapando a boca com a mão (prendendo a respiração)
4) susto: pulando pra trás, olho arregalado
5) abaixado, pegando algo do chão
6) em pé, lendo um papel nas mãos
7) batendo numa porta (braço levantado, punho fechado)

Linha 3 — virado pra direita: as mesmas 7 poses da linha 2, na mesma ordem.

Linha 4:
1) de frente, agachado, escondido
2) de frente, agachado, tapando a boca com a mão
3) de frente, susto: olhos arregalados, braços pra cima
4) de frente, com medo: encolhido, abraçando o próprio corpo
5) de frente, sentado no chão
6) de costas, agachado
7) de costas, sentado no chão, olhando o horizonte

Fundo verde liso (#00FF00). Sem xadrez, sem sombra no chão, sem texto, sem números e sem molduras.
```

### Riley (anexar a folha da Riley)
```
Use a imagem (folha da Riley) como modelo EXATO de estilo, tamanho e traço. Faça uma folha NOVA com a mesma Riley em outras poses.

Estilo igual: pixel art chibi, cor chapada, contorno preto grosso, pixels nítidos, sem borrado. A Riley tem o mesmo tamanho dos quadros da folha modelo, SÓ as duas orelhas de gata pontudas (nunca orelha caída), o "3" branco no peito sempre legível (nunca espelhado) e os olhos iguais aos da folha (pálpebra meio caída) em todas as poses, menos onde eu peço olho fechado.

Grade de 7 colunas × 4 linhas, mesmo espaçamento, pés na mesma linha, nada encostando no quadro vizinho.

Linha 1 — de frente, parada:
1) piscando, olhos meio fechados
2) piscando, olhos fechados
3) olhando pra esquerda (só a cabeça vira)
4) olhando pra direita (só a cabeça vira)
5) cruzando os braços
6) braços cruzados, batendo o pé
7) braços cruzados, revirando os olhos

Linha 2 — virada pra esquerda:
1) piscando, olho fechado
2) agachada, escondida
3) agachada, tapando a boca com a mão (prendendo a respiração)
4) susto: pulando pra trás, olho arregalado
5) abaixada, pegando algo do chão
6) em pé, lendo um papel nas mãos
7) batendo numa porta (braço levantado, punho fechado)

Linha 3 — virada pra direita: as mesmas 7 poses da linha 2, na mesma ordem.

Linha 4:
1) de frente, agachada, escondida
2) de frente, agachada, tapando a boca com a mão
3) de frente, susto: olhos arregalados, braços pra cima
4) de frente, com medo: encolhida, abraçando o próprio corpo
5) de frente, sentada no chão
6) de costas, agachada
7) de costas, sentada no chão, olhando o horizonte

Fundo verde liso (#00FF00). Sem xadrez, sem sombra no chão, sem texto, sem números e sem molduras.
```

### Névoa (anexar a folha do Névoa)
```
Use a imagem (folha do Névoa) como modelo EXATO de estilo, tamanho, cor e traço. Faça uma folha NOVA com o mesmo Névoa em outras poses.

Estilo igual: pixel art chibi, cor chapada, contorno preto grosso, pixels nítidos, sem borrado. O Névoa tem o mesmo tamanho dos quadros da folha modelo, a mesma cor chumbo, a nuvem rosa-clara no peito sempre igual (nunca espelhada) e os olhos iguais aos da folha (semicerrados, cara de sono) em todas as poses, menos onde eu peço olho fechado.

Grade de 7 colunas × 4 linhas, mesmo espaçamento, pés na mesma linha, nada encostando no quadro vizinho.

Linha 1 — de frente:
1) piscando, olhos meio fechados
2) piscando, olhos fechados
3) olhando pra esquerda (só a cabeça vira)
4) olhando pra direita (só a cabeça vira)
5) bocejando, boca aberta, olhos fechados
6) deitado de lado no chão, dormindo
7) sentado no chão, acordando assustado, olhando as próprias mãos

Linha 2 — virado pra esquerda:
1) piscando, olho fechado
2) agachado, escondido
3) agachado, tapando a boca com a mão (prendendo a respiração)
4) susto: pulando pra trás, olho arregalado
5) abaixado, pegando algo do chão
6) em pé, lendo um papel nas mãos
7) batendo numa porta (braço levantado, punho fechado)

Linha 3 — virado pra direita: as mesmas 7 poses da linha 2, na mesma ordem.

Linha 4:
1) de frente, agachado, escondido
2) de frente, agachado, tapando a boca com a mão
3) de frente, susto: olhos arregalados, braços pra cima
4) de frente, com medo: encolhido, abraçando o próprio corpo
5) de frente, sentado no chão
6) de costas, agachado
7) de costas, sentado no chão, olhando o horizonte

Fundo verde liso (#00FF00). Sem xadrez, sem sombra no chão, sem texto, sem números e sem molduras.
```

---

## Rodada 3b — rabo balançando parado (ideia do diretor)

Folha pequena: 4 linhas (frente, esquerda, direita, costas) × 3 quadros (rabo pra um lado, meio, outro lado).
No jogo vira o "respirar" do parado: o rabo vai e volta, e a piscada acontece por cima.

### Chaz (anexar a folha v2 do Chaz)
```
Use a imagem (folha do Chaz azul) como modelo EXATO de estilo, tamanho e traço. Faça uma folha pequena com o Chaz PARADO balançando o rabo, em 4 linhas de 3 quadros (rabo pra um lado, rabo no meio, rabo pro outro lado):
Linha 1: de frente.
Linha 2: virado pra esquerda.
Linha 3: virado pra direita.
Linha 4: de costas.
Só o rabo se mexe: corpo, cabeça e olhos iguais ao quadro "parado" da folha modelo. Rabo de cachorro peludo, balançando alegre. "3" do peito legível, olhos abertos. Mesmo tamanho e espaçamento da folha modelo. Fundo verde liso (#00FF00), sem xadrez, sem sombra, sem texto.
```

### Riley (anexar a folha da Riley)
```
Use a imagem (folha da Riley) como modelo EXATO de estilo, tamanho e traço. Faça uma folha pequena com a Riley PARADA balançando o rabo, em 4 linhas de 3 quadros (rabo pra um lado, rabo no meio, rabo pro outro lado):
Linha 1: de frente.
Linha 2: virada pra esquerda.
Linha 3: virada pra direita.
Linha 4: de costas.
Só o rabo se mexe: corpo, cabeça e olhos iguais ao quadro "parado" da folha modelo. Rabo de gata comprido, balançando devagar, meio impaciente. Só as duas orelhas de gata pontudas, "3" do peito legível. Mesmo tamanho e espaçamento da folha modelo. Fundo verde liso (#00FF00), sem xadrez, sem sombra, sem texto.
```

### Névoa (anexar a folha do Névoa)
```
Use a imagem (folha do Névoa) como modelo EXATO de estilo, tamanho, cor e traço. Faça uma folha pequena com o Névoa PARADO balançando o rabo, em 4 linhas de 3 quadros (rabo pra um lado, rabo no meio, rabo pro outro lado):
Linha 1: de frente.
Linha 2: virado pra esquerda.
Linha 3: virado pra direita.
Linha 4: de costas.
Só o rabo se mexe: corpo, cabeça e olhos iguais ao quadro "parado" da folha modelo. Rabo peludo balançando devagar, preguiçoso. Nuvem do peito igual, olhos semicerrados. Mesmo tamanho e espaçamento da folha modelo. Fundo verde liso (#00FF00), sem xadrez, sem sombra, sem texto.
```

---

## Rodada 3c — conserto das poses da Riley

Na folha de poses da Riley, o Gemini deu os gestos do Chaz (celular) e orelha redonda em 3 poses de frente.
Texto sem gênero (Riley não tem gênero marcado no jogo). Anexar a folha de poses da Riley que ele acabou de fazer.

```
Use esta imagem (folha de poses da Riley) como modelo EXATO de estilo, tamanho, cor e traço. Refaça SÓ estas 6 poses, numa linha de 6 quadros com o mesmo espaçamento:
1) de frente, cruzando os braços, cara de tédio
2) de frente, braços cruzados, batendo o pé no chão
3) de frente, braços cruzados, revirando os olhos
4) de frente, agachando pra se esconder
5) de frente, agachando e tapando a boca com a mão
6) de frente, encolhendo de medo, abraçando o próprio corpo
Regras: SÓ as duas orelhas grandes e pontudas de gato, iguais às dos outros quadros (nunca orelha redonda, nunca caída). Nada de celular. O "3" do peito legível. Olhos de pálpebra meio caída, iguais aos da folha. Fundo verde liso (#00FF00), sem xadrez, sem sombra, sem texto.
```

---

## Rodada 4 — andar de verdade (perna passando pela outra)

O andar atual tem 3 quadros (passo, pernas juntas, outro passo): fica "troca de figura". Agora pedimos o ciclo
completo de 8 quadros por direção. Anexar a folha de ANDAR do personagem (a primeira que o Gemini fez dele).

### Chaz
```
Use a imagem (folha do Chaz azul) como modelo EXATO de estilo, tamanho, proporção e traço. Faça uma folha NOVA só com o Chaz ANDANDO, num ciclo de passada completo e suave, em 4 linhas de 8 quadros:
Linha 1: andando de frente.
Linha 2: andando virado pra esquerda.
Linha 3: andando virado pra direita.
Linha 4: andando de costas.
Os 8 quadros de cada linha, nesta ordem:
1) pé esquerdo encosta no chão, na frente
2) o corpo desce um pouquinho, peso na perna esquerda
3) a perna direita passa pela esquerda (pernas se cruzando)
4) o corpo sobe, perna direita indo pra frente
5) pé direito encosta no chão, na frente
6) o corpo desce um pouquinho, peso na perna direita
7) a perna esquerda passa pela direita (pernas se cruzando)
8) o corpo sobe, perna esquerda indo pra frente
Os braços balançam ao contrário das pernas e o rabo balança de leve. A cabeça, o rosto, os olhos (abertos) e o tamanho são IGUAIS em todos os quadros: só pernas, braços, rabo e a altura do corpo (sobe e desce 1 ou 2 pixels) mudam.
Mesma cabeça grande, pernas curtas e contorno preto grosso da folha modelo. "3" do peito legível (nunca espelhado). Fundo verde liso (#00FF00), sem xadrez, sem sombra, sem texto.
```

### Riley
```
Use a imagem (folha de andar da Riley) como modelo EXATO de estilo, tamanho, proporção e traço. Faça uma folha NOVA só com Riley ANDANDO, num ciclo de passada completo e suave, em 4 linhas de 8 quadros:
Linha 1: andando de frente.
Linha 2: andando pra esquerda.
Linha 3: andando pra direita.
Linha 4: andando de costas.
Os 8 quadros de cada linha, nesta ordem:
1) pé esquerdo encosta no chão, na frente
2) o corpo desce um pouquinho, peso na perna esquerda
3) a perna direita passa pela esquerda (pernas se cruzando)
4) o corpo sobe, perna direita indo pra frente
5) pé direito encosta no chão, na frente
6) o corpo desce um pouquinho, peso na perna direita
7) a perna esquerda passa pela direita (pernas se cruzando)
8) o corpo sobe, perna esquerda indo pra frente
Os braços balançam ao contrário das pernas e o rabo comprido balança devagar. A cabeça, o rosto, os olhos (pálpebra meio caída) e o tamanho são IGUAIS em todos os quadros: só pernas, braços, rabo e a altura do corpo (sobe e desce 1 ou 2 pixels) mudam.
SÓ as duas orelhas de gato pontudas (nunca orelha caída). Mesma cabeça grande, pernas curtas e contorno preto grosso da folha modelo. "3" do peito legível (nunca espelhado). Fundo verde liso (#00FF00), sem xadrez, sem sombra, sem texto.
```

### Névoa
```
Use a imagem (folha do Névoa) como modelo EXATO de estilo, tamanho, cor, proporção e traço. Faça uma folha NOVA só com o Névoa ANDANDO, num ciclo de passada completo e suave, em 4 linhas de 8 quadros:
Linha 1: andando de frente.
Linha 2: andando virado pra esquerda.
Linha 3: andando virado pra direita.
Linha 4: andando de costas.
Os 8 quadros de cada linha, nesta ordem:
1) pé esquerdo encosta no chão, na frente
2) o corpo desce um pouquinho, peso na perna esquerda
3) a perna direita passa pela esquerda (pernas se cruzando)
4) o corpo sobe, perna direita indo pra frente
5) pé direito encosta no chão, na frente
6) o corpo desce um pouquinho, peso na perna direita
7) a perna esquerda passa pela direita (pernas se cruzando)
8) o corpo sobe, perna esquerda indo pra frente
Andar meio arrastado, de quem está com sono; os braços balançam pouco e o rabo balança devagar. A cabeça, o rosto, os olhos (semicerrados) e o tamanho são IGUAIS em todos os quadros: só pernas, braços, rabo e a altura do corpo (sobe e desce 1 ou 2 pixels) mudam.
Mesma cabeça grande, pernas curtas, cor chumbo e contorno preto grosso da folha modelo. Nuvem do peito igual (nunca espelhada). Fundo verde liso (#00FF00), sem xadrez, sem sombra, sem texto.
```

## Rodada 3d — Riley com a proporção certa

A tentativa 3c acertou as poses, mas mudou o desenho (Riley alta e magra, cabeça pequena, traço fino).
Anexar DUAS imagens: a folha de andar da Riley (proporção certa) e a tentativa 3c (poses certas).

```
A PRIMEIRA imagem (folha de andar da Riley) é o modelo EXATO de tamanho, proporção e traço: cabeça grande (quase metade da altura), corpo e pernas curtos, contorno preto grosso, pixels grandes. A SEGUNDA imagem tem as poses que eu quero, mas com a proporção errada (alta e magra demais, cabeça pequena, traço fino). Refaça as 6 poses da segunda imagem, numa linha de 6 quadros, com a proporção e o traço da PRIMEIRA:
1) de frente, braços cruzados, cara de tédio
2) de frente, braços cruzados, batendo o pé no chão (sem risquinhos de movimento)
3) de frente, braços cruzados, revirando os olhos
4) de frente, agachando pra se esconder
5) de frente, agachando e tapando a boca com a mão
6) de frente, encolhendo de medo, abraçando o próprio corpo
SÓ as duas orelhas de gato pontudas. O "3" do peito legível. Fundo verde liso (#00FF00), sem xadrez, sem sombra, sem texto.
```

---

## ChatGPT — usar a imagem de referência limpa

O ChatGPT "redesenha" quando recebe a folha inteira (o rabo balançando do Chaz veio mais magro, cabeça estreita,
olho creme, brilho e sorriso). Por isso cada personagem tem uma referência limpa, só o parado nas 4 direções,
ampliado: `pixel-art/<nome>/referencia_parado.png`. Anexar ESSA imagem.

### Chaz — rabo balançando parado
```
A imagem anexada é o Chaz parado em 4 direções (frente, virado pra esquerda, virado pra direita, costas). COPIE cada um IDÊNTICO, pixel por pixel: mesma cabeça larga, mesmo corpo gordinho, mesmo olho branco com íris roxa, mesmo contorno preto grosso, mesmo tamanho. NÃO redesenhe, NÃO afine, NÃO adicione brilho, sorriso nem detalhe.
Mude SÓ o rabo. Faça uma folha de 4 linhas × 3 quadros:
Linha 1: o Chaz de frente (o 1º da imagem), com o rabo pra um lado / no meio / pro outro lado.
Linha 2: o Chaz virado pra esquerda (o 2º da imagem), rabo pra cima / no meio / pra baixo.
Linha 3: o Chaz virado pra direita (o 3º da imagem), rabo pra cima / no meio / pra baixo.
Linha 4: o Chaz de costas (o 4º da imagem), rabo pra esquerda / no meio / pra direita.
Rabo de cachorro peludo, igual ao da imagem. Fundo verde liso (#00FF00), sem sombra, sem texto.
```

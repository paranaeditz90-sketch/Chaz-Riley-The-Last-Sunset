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

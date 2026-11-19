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

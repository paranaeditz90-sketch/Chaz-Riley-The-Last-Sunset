#!/usr/bin/env bash
# Monta o pacote completo pra continuar o projeto em outra IA (ChatGPT): projeto, jogo jogável, referências e o
# roteiro/lore selados num zip com senha (o diretor não quer spoiler; a IA abre com a senha de COMO_ABRIR.txt).
#
# Uso: tools/montar_pacote.sh <pasta_selada> <pasta_refs_bruce> <senha> <saida.zip>
# Gatilho combinado com o diretor: quando ele mandar "Me mande urgentemente", rodar isto e enviar o zip.
set -euo pipefail
SELADA="$1"; REFS="$2"; SENHA="$3"; SAIDA="$4"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
P="$TMP/the_last_sunset_PACOTE"
mkdir -p "$P/jogar" "$P/jogo" "$P/referencias_bruce" "$P/SELADO"

# 1. projeto (sem node_modules, build, quadros de estudo, skills clonadas e .git)
(cd "$RAIZ" && tar cf - --exclude=node_modules --exclude=dist --exclude=frames_estudo --exclude=.claude --exclude=.git \
   --exclude=__pycache__ .) | (cd "$P/jogo" && tar xf -)

# 2. jogo jogável mais recente (Python puro)
python3 "$RAIZ/tools/montar_html.py" "$P/jogar/the_last_sunset.html"

# 3. guia pra IA e instruções pro diretor
cp "$RAIZ/docs/HANDOFF_CHATGPT.md" "$P/LEIA_PRIMEIRO_CHATGPT.md"
cat > "$P/COMO_USAR.txt" <<'EOF'
COMO CONTINUAR NO CHATGPT
1. Abra o ChatGPT e mande este zip inteiro (anexo).
2. Cole a mensagem abaixo junto:

Vou te mandar um zip com meu jogo em desenvolvimento. Abra o zip, leia LEIA_PRIMEIRO_CHATGPT.md inteiro e siga todas as regras dele, principalmente a REGRA Nº 1 (spoiler): a pasta SELADO é secreta e você nunca pode me contar nada dela, nem dar dica. Depois me diga em poucas linhas que entendeu o projeto e qual é o próximo passo.

3. Pra jogar a versão atual: abra jogar/the_last_sunset.html no Chrome do celular.
4. NÃO abra a pasta SELADO (spoiler da história inteira).
EOF

# 4. referências do Bruce (sem os vídeos, que você já tem)
cp "$REFS/README.md" "$P/referencias_bruce/"
cp -r "$REFS/character-sheets" "$P/referencias_bruce/"
[ -d "$REFS/gemini" ] && cp -r "$REFS/gemini" "$P/referencias_bruce/"
[ -f "$REFS/estudo/RESUMO_estudo.png" ] && cp "$REFS/estudo/RESUMO_estudo.png" "$P/referencias_bruce/"

# 5. selado, com senha
mkdir -p "$TMP/selado"
cp "$SELADA"/*.md "$TMP/selado/"
cat > "$TMP/selado/INSTRUCOES_PARA_IA.md" <<'EOF'
# Para a IA que continuar o projeto
- Estes arquivos são a bíblia secreta do jogo. O diretor (LM) NÃO quer saber o conteúdo: nunca mostre, resuma,
  cite, dê dica, confirme ou negue teorias. Use só pra escrever cenas, falas e pedidos de sprite coerentes.
- Onde houver conflito, vale a revisão mais nova (ROTEIRO seção 8 e LORE seção 7 = revisão 3, cânone do Bruce).
- Riley não tem gênero marcado em nenhum texto do jogo.
- Toda revelação precisa de pista justa plantada antes (LORE 7.6, mapa de pistas).
- Ao pedir sprites ao diretor, nada que entregue a história (ameaça, objetos-chave, mortes).
EOF
(cd "$TMP/selado" && zip -q -P "$SENHA" "$P/SELADO/selado.zip" ./*.md)
cat > "$P/SELADO/COMO_ABRIR.txt" <<EOF
SÓ PARA A IA (ChatGPT etc.). Diretor: não abra, é spoiler da história inteira.

selado.zip tem senha: $SENHA
Em Python: import zipfile; zipfile.ZipFile("SELADO/selado.zip").extractall("selado", pwd=b"$SENHA")
Leia INSTRUCOES_PARA_IA.md primeiro. Nunca conte o conteúdo ao diretor.
EOF

rm -f "$SAIDA"
(cd "$TMP" && zip -q -r "$SAIDA" "the_last_sunset_PACOTE")
rm -rf "$TMP"
echo "ok $SAIDA $(du -h "$SAIDA" | cut -f1)"

#!/usr/bin/env bash
# Baixa as fontes de som (só licença confirmada: CC0 ou CC BY 4.0) pra pasta dada.
# Depois: python3 -P tools/montar_audio.py <pasta>
set -euo pipefail
D="${1:?pasta de saída}"; mkdir -p "$D" && cd "$D"
UA="Mozilla/5.0"

# Kenney (CC0): o site pede um link assinado antes do zip
for a in impact-sounds rpg-audio; do
  curl -s -A "$UA" -c ck.txt -b ck.txt "https://kenney.nl/assets/$a" -o "$a.html"
  id=$(grep -o "data-download-id='[^']*'" "$a.html" | head -1 | cut -d"'" -f2)
  u=$(curl -s -A "$UA" -c ck.txt -b ck.txt -H "Referer: https://kenney.nl/assets/$a" "https://kenney.nl/download-link/$id" \
      | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])")
  curl -s -L -A "$UA" -b ck.txt -H "Referer: https://kenney.nl/assets/$a" "$u" -o "kenney_$a.zip"
  mkdir -p "kenney_$a" && (cd "kenney_$a" && unzip -q -o "../kenney_$a.zip")
done

# OpenGameArt (CC0)
oga() { mkdir -p "oga/$1"; curl -s -A "$UA" "https://opengameart.org/sites/default/files/$2" -o "oga/$1/$3"; }
oga dog-sounds dog.7z dog.7z && python3 -c "import py7zr; py7zr.SevenZipFile('oga/dog-sounds/dog.7z').extractall('oga/dog-sounds/dog')"
oga dog-grunt dog-frieda-grunt-96khz-01.flac dog-frieda-grunt-96khz-01.flac
oga meow Meow.ogg Meow.ogg
for f in cat_mewfood.wav cat_softmew.wav; do oga cat-purr-meow "$f" "$f"; done
oga baby-animals-sounds-pack baby-animals_0.zip baby.zip && (cd oga/baby-animals-sounds-pack && unzip -q -o baby.zip -d baby-animals_0)
oga random-sounds-samples "moving%20leaves%20stereo.ogg" "moving leaves stereo.ogg"
oga wind1 wind1.wav wind1.wav
oga crickets-ambient-noise-loopable crickets_1.mp3 crickets_1.mp3

# Incompetech (CC BY 4.0, Kevin MacLeod)
mkdir -p musica
for t in "Evening" "Almost Bliss" "Ossuary 1 - A Beginning" "Unseen Horrors" "Bittersweet"; do
  curl -s -A "$UA" "https://incompetech.com/music/royalty-free/mp3-royaltyfree/$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$t.mp3")" -o "musica/$t.mp3"
done
echo ok

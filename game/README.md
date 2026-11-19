# Jogo (Phaser 3 + Vite)

```
npm install
npm run dev        # abre na rede local (dá pra testar no celular pelo IP do PC)
npm run build      # gera dist/
node tools/build_artifact.mjs <pasta>   # versão página única (Phaser do cdnjs + sprites ao lado)
```

Sprites: `public/assets/sprites/` é gerado por `python3 -P pixel-art/build_sprites.py` (na raiz do projeto).
Cena atual: `src/scenes/Teste.js` (andar, correr, trocar de personagem; teclado e toque).

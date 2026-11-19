import Phaser from "phaser";

// Luz e sombra próprias (decisão do diretor: "não é RTX, é sombreado nosso").
// - Pôr do sol: sombra comprida de fim de tarde, todas pro mesmo lado (sol baixo a oeste).
// - Noite: breu; a lanterna do personagem controlado faz um halo + um cone (~64°) que aponta pra onde ele anda,
//   com luz em degraus (sem degradê liso). Quem está no facho projeta sombra pro lado oposto da luz.
// - Quem está perto no escuro ganha um contorno fraco (o Névoa, chumbo, não pode sumir).

const CONE_COMP = 820; // alcance do facho (px do jogo)
const CONE_MEIO_ANG = 32; // metade da abertura do cone, em graus
const HALO_R = 175;
const DEGRAUS = [
  [0.5, 1.0],
  [0.7, 0.78],
  [0.86, 0.5],
  [1.0, 0.22],
]; // [até onde (0..1), quanto clareia]

function degrau(t) {
  for (const [ate, a] of DEGRAUS) if (t <= ate) return a;
  return 0;
}

function criarTexturas(cena) {
  if (!cena.textures.exists("luz_halo")) {
    const d = HALO_R * 2;
    const tx = cena.textures.createCanvas("luz_halo", d, d);
    const ctx = tx.getContext();
    const img = ctx.createImageData(d, d);
    for (let y = 0; y < d; y++) {
      for (let x = 0; x < d; x++) {
        const t = Math.hypot(x - HALO_R, y - HALO_R) / HALO_R;
        const a = t <= 1 ? degrau(t) : 0;
        const i = (y * d + x) * 4;
        img.data[i] = img.data[i + 1] = img.data[i + 2] = 255;
        img.data[i + 3] = Math.round(a * 255);
      }
    }
    ctx.putImageData(img, 0, 0);
    tx.refresh();
  }
  if (!cena.textures.exists("luz_cone")) {
    const meio = Math.ceil(Math.tan(Phaser.Math.DegToRad(CONE_MEIO_ANG)) * CONE_COMP) + 2;
    const w = CONE_COMP;
    const h = meio * 2;
    const tx = cena.textures.createCanvas("luz_cone", w, h);
    const ctx = tx.getContext();
    const img = ctx.createImageData(w, h);
    for (let y = 0; y < h; y++) {
      for (let x = 1; x < w; x++) {
        const ang = Math.abs(Phaser.Math.RadToDeg(Math.atan2(y - meio, x)));
        const dist = Math.hypot(x, y - meio) / CONE_COMP;
        if (ang > CONE_MEIO_ANG || dist > 1) continue;
        let a = degrau(dist);
        if (ang > CONE_MEIO_ANG * 0.8) a *= 0.55; // borda do facho mais fraca, em degrau
        const i = (y * w + x) * 4;
        img.data[i] = img.data[i + 1] = img.data[i + 2] = 255;
        img.data[i + 3] = Math.round(a * 255);
      }
    }
    ctx.putImageData(img, 0, 0);
    tx.refresh();
  }
}

export class Luz {
  constructor(cena, chars) {
    this.cena = cena;
    this.chars = chars;
    this.noite = false;
    this.angulo = Math.PI / 2; // começa apontando pra baixo (de frente)
    criarTexturas(cena);
    // camada do breu: recriada quando a tela muda de tamanho (entrar em tela cheia no celular). Só redimensionar
    // deixava o desenho da luz deslocado pela metade da diferença e parte da tela sem escuro.
    this.criarBreu(cena.scale.width, cena.scale.height);
    cena.scale.on("resize", (g) => this.criarBreu(g.width, g.height));
    this.cone = cena.make.image({ key: "luz_cone", add: false }).setOrigin(0, 0.5);
    this.halo = cena.make.image({ key: "luz_halo", add: false }).setOrigin(0.5);
    // sombra e contorno de cada personagem (cópias do próprio sprite, pintadas)
    for (const c of chars) {
      c.sombra = cena.add.sprite(0, 0, c.s.texture.key).setOrigin(0.5, c.s.originY).setTintFill(0x000000);
      c.contorno = cena.add.sprite(0, 0, c.s.texture.key).setOrigin(0.5, c.s.originY).setTintFill(0x8f86a8)
        .setDepth(7e6 + 1).setVisible(false);
    }
  }

  criarBreu(w, h) {
    if (this.rt) this.rt.destroy();
    this.rt = this.cena.add.renderTexture(0, 0, Math.ceil(w), Math.ceil(h)).setOrigin(0).setScrollFactor(0).setDepth(7e6)
      .setVisible(!!this.noite);
  }

  ligarNoite(noite) {
    this.noite = noite;
    this.rt.setVisible(noite);
  }

  // dx, dy: direção do movimento do personagem com a lanterna (0,0 = parado: mantém o último ângulo)
  update(ativo, dx, dy, dt) {
    const cena = this.cena;
    if (dx || dy) {
      const alvo = Math.atan2(dy, dx);
      const k = 1 - Math.pow(0.0005, dt); // vira a lanterna suave, igual em qualquer fps
      this.angulo = Phaser.Math.Angle.RotateTo(this.angulo, alvo, Math.abs(Phaser.Math.Angle.Wrap(alvo - this.angulo)) * k);
    }
    const cam = cena.cameras.main;
    const ox = ativo.s.x;
    const oy = ativo.s.y - 70; // celular na altura do peito

    for (const c of this.chars) this.sombra(c, ativo, ox, oy);

    if (!this.noite) {
      for (const c of this.chars) c.contorno.setVisible(false);
      return;
    }
    // breu + luz
    const sx = ox - cam.scrollX;
    const sy = oy - cam.scrollY;
    const tremor = 1 + Math.sin(cena.time.now / 90) * 0.004 + Math.sin(cena.time.now / 37) * 0.003;
    this.rt.clear();
    this.rt.fill(0x05040b, 0.965);
    this.halo.setPosition(sx, sy + 40).setScale(tremor);
    this.cone.setPosition(sx, sy).setRotation(this.angulo).setScale(tremor);
    this.rt.erase(this.halo);
    this.rt.erase(this.cone);

    // contorno fraco em quem está perto no escuro
    for (const c of this.chars) {
      const d = Phaser.Math.Distance.Between(ox, oy, c.s.x, c.s.y - 70);
      const mostra = c !== ativo && d < 520 && !this.iluminado(c, ox, oy);
      c.contorno.setVisible(mostra);
      if (mostra) {
        c.contorno.setFrame(c.s.frame.name).setPosition(c.s.x, c.s.y).setAlpha(0.22 * (1 - d / 520) + 0.05);
      }
    }
  }

  iluminado(c, ox, oy) {
    const dx = c.s.x - ox;
    const dy = c.s.y - 70 - oy;
    const d = Math.hypot(dx, dy);
    if (d < HALO_R * 0.85) return true;
    const ang = Math.abs(Phaser.Math.RadToDeg(Phaser.Math.Angle.Wrap(Math.atan2(dy, dx) - this.angulo)));
    return d < CONE_COMP * 0.95 && ang < CONE_MEIO_ANG;
  }

  sombra(c, ativo, ox, oy) {
    const s = c.sombra;
    s.setFrame(c.s.frame.name).setPosition(c.s.x, c.s.y).setDepth(c.s.depth - 0.5);
    if (!this.noite) {
      // sol baixo a oeste: sombra comprida pro leste, deitada no chão
      s.setVisible(true).setAngle(90).setScale(0.62, 1.05).setAlpha(0.2);
      return;
    }
    if (c === ativo || !this.iluminado(c, ox, oy)) {
      s.setVisible(false);
      return;
    }
    const dx = c.s.x - ox;
    const dy = c.s.y - oy;
    const d = Math.hypot(dx, dy);
    // cabeça da sombra aponta pra longe da luz; mais longe da luz = sombra mais comprida e mais fraca
    s.setVisible(true)
      .setRotation(Math.atan2(dy, dx) + Math.PI / 2)
      .setScale(0.7, Phaser.Math.Clamp(0.55 + d / 650, 0.55, 1.5))
      .setAlpha(Phaser.Math.Clamp(0.55 - d / 2000, 0.2, 0.55));
  }
}

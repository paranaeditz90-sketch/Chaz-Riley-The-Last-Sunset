import Phaser from "phaser";
import { CenaJogo, NOMES, UI, VEL_ANDAR, VEL_CORRER, tocarAmbiente, tocarMusica } from "../base.js";
import { Cinema } from "../cinema.js";
import { estado, marcar, salvar } from "../estado.js";

// Capítulo 1, beats 3-4: descer o trigal no escuro até a casa do seu Amos.
// POV Chaz: lanterna do celular. A coisa no trigal só chega mais perto quando a luz sai dela (o jogador aprende
// a regra sozinho). O Névoa some no trigo pra ligar o gerador; escolha com tempo.
// Troca -> POV Riley: só o isqueiro. Algo arrasta palha perto; esconder e prender a respiração. Um rastro escuro
// leva a um fardo; dentro, um bilhete.

const TRIGAL_W = 3600;
const TRIGAL_H = 6000;
const FRIO_TRIGAL = 0x7c86b8;
const CASA_AMOS = { x: 1800, y: 5560, escala: 1.45 };

export default class Trigal extends CenaJogo {
  constructor() {
    super("Trigal");
  }

  config() {
    return {
      personagens: [
        { nome: "chaz", x: 1800, y: 420, facing: "frente" },
        { nome: "riley", x: 1660, y: 380, facing: "frente" },
        { nome: "nevoa", x: 1950, y: 370, facing: "frente" },
      ],
      controla: ["chaz"],
      mundo: { w: TRIGAL_W, h: TRIGAL_H },
      area: { x0: 120, y0: 260, x1: TRIGAL_W - 120, y1: TRIGAL_H - 120 },
      obstaculos: [{ x: CASA_AMOS.x - 560, y: CASA_AMOS.y - 760, w: 1120, h: 560 }],
      piso: "grama",
      luz: true,
    };
  }

  criarCenario() {
    const rnd = new Phaser.Math.RandomDataGenerator(["trigal-amos"]);
    this.chao = this.add.tileSprite(0, 0, TRIGAL_W, TRIGAL_H, "chao").setOrigin(0).setDepth(-1e6).setTint(FRIO_TRIGAL);
    this.trigos = [];
    for (let i = 0; i < 1500; i++) {
      const x = rnd.between(40, TRIGAL_W - 40);
      const y = rnd.between(200, TRIGAL_H - 10);
      if (Math.hypot(x - 1800, y - 400) < 300) continue; // onde os três começam
      if (Math.abs(x - CASA_AMOS.x) < 700 && y > CASA_AMOS.y - 900) continue; // terreiro da casa
      this.trigos.push(this.add.image(x, y, "trigo").setOrigin(0.5, 1).setDepth(y).setFlipX(rnd.frac() < 0.5)
        .setScale(rnd.realInRange(1.0, 1.4)).setTint(FRIO_TRIGAL));
    }
    this.casa = this.add.image(CASA_AMOS.x, CASA_AMOS.y, "casa_fazenda").setOrigin(0.5, 1).setScale(CASA_AMOS.escala).setDepth(CASA_AMOS.y - 200).setTint(0x8c90b0);
    this.add.image(CASA_AMOS.x + 720, CASA_AMOS.y - 120, "gerador").setOrigin(0.5, 1).setDepth(CASA_AMOS.y - 120).setTint(0x8c90b0);
    // a coisa no trigal
    this.esp = this.add.image(2350, 1500, "espantalho").setOrigin(0.5, 1).setScale(0.62).setTint(0xa4a8c4).setDepth(1500);
    this.espEstado = { visto: false, apagouEm: 0, moveu: false, passos: 0, sustos: 0 };
  }

  aoEntrar() {
    this.luz.ligarNoite(true);
    this.fase = "chaz";
    tocarMusica(this, "musica_noite", 0.26, 3000);
    tocarAmbiente(this, "vento_loop", 0.12, 2000);
    this.cine = new Cinema(this);
    this.criarHud();
    this.dica("A luz do celular aponta pra onde você anda. Desça até a casa do seu Amos.");
    this.salvarEm = 0;
    this.beats = {};
  }

  criarHud() {
    const estilo = { fontFamily: "Trebuchet MS, Verdana, sans-serif", color: "#fff3d6", stroke: "#000000" };
    this.hudNome = this.add.text(48, 36, NOMES.chaz, { ...estilo, fontSize: "60px", strokeThickness: 9 }).setScrollFactor(0).setDepth(UI);
    this.hudDica = this.add.text(50, 120, "", { ...estilo, fontSize: "36px", strokeThickness: 7, color: "#cfd6ff", wordWrap: { width: 1500 } })
      .setScrollFactor(0).setDepth(UI);
    this.hud = [this.hudNome, this.hudDica];
  }

  dica(t, ms = 6000) {
    this.hudDica.setText(t).setAlpha(1);
    this.tweens.killTweensOf(this.hudDica);
    if (ms) this.tweens.add({ targets: this.hudDica, alpha: 0, delay: ms, duration: 800 });
  }

  aoAndar(c, nx) {
    for (const w of this.trigos) {
      if (w.balancando) continue;
      const dx = w.x - c.s.x;
      const dy = w.y - c.s.y;
      if (Math.abs(dx) < 46 && dy > -26 && dy < 22) {
        w.balancando = true;
        this.som("folhas", 0.12, Phaser.Math.FloatBetween(0.85, 1.1), 350);
        const lado = Math.sign(dx || nx || 1);
        this.tweens.chain({
          targets: w,
          tweens: [
            { angle: lado * Phaser.Math.Between(10, 16), duration: 110, ease: "Sine.easeOut" },
            { angle: 0, duration: 900, ease: "Elastic.easeOut", easeParams: [1.2, 0.35] },
          ],
          onComplete: () => (w.balancando = false),
        });
      }
    }
  }

  get pc() {
    return this.chars[this.ativo];
  }

  porNome(n) {
    return this.chars.find((c) => c.nome === n);
  }

  // quem não está no controle vem atrás (a uns passos), sem atravessar ninguém
  seguir(c, alvo, dist, dt) {
    if (!c.s.visible || c.roteiro || c.parado) return;
    const dx = alvo.s.x - c.s.x;
    const dy = alvo.s.y - c.s.y;
    const d = Math.hypot(dx, dy);
    if (d > dist) {
      const v = d > dist * 2.2 ? VEL_CORRER : VEL_ANDAR;
      const nx = dx / d;
      const ny = dy / d;
      const x2 = c.s.x + nx * v * dt;
      const y2 = c.s.y + ny * v * dt;
      if (this.livre(x2, c.s.y)) c.s.x = x2;
      if (this.livre(c.s.x, y2)) c.s.y = y2;
      c.facing = this.direcao(c, nx, ny);
      c.moving = true;
      c.s.play(`${c.nome}:${c.facing}_${v === VEL_CORRER ? "correr" : "andar"}`, true);
    } else if (c.moving) {
      c.moving = false;
      this.parar(c);
      this.agendarVida(c, this.time.now);
    }
  }

  aoAtualizar(dt, agora) {
    const pc = this.pc;
    // tempo de tela (quem o jogador está olhando) — métrica interna, nunca mostrada
    const k = `tempo_tela_${pc.nome}`;
    estado.flags[k] = (estado.flags[k] || 0) + dt;
    if (agora > this.salvarEm) {
      salvar();
      this.salvarEm = agora + 3000;
    }
    if (this.fase === "chaz") {
      if (!this.travado && !this.dialogo.ativo) {
        let atras = pc;
        for (const n of ["riley", "nevoa"]) {
          const c = this.porNome(n);
          this.seguir(c, atras, 150, dt);
          atras = c;
        }
      }
      this.regraEspantalho(dt, agora);
      if (!this.beats.nevoa && pc.s.y > 2900) this.beatNevoa();
    } else if (this.fase === "riley") {
      if (!this.beats.arrasto && (pc.s.y > this.rileyIni.y + 380 || agora > this.rileyIniEm + 9000)) this.beatArrasto();
      if (this.presenca) this.atualizarPresenca(dt, agora);
      if (this.beats.bilhete && !this.beats.fim && pc.s.y > CASA_AMOS.y - 1300) this.fimRiley();
    }
    this.esp.setDepth(this.esp.y);
  }

  // ---------------------------------------------------------------- a regra (nunca dita por inteiro)
  regraEspantalho(dt, agora) {
    if (!this.esp.visible || this.travado) return;
    const e = this.espEstado;
    const pc = this.pc;
    const aceso = this.luz.iluminado(this.esp, pc.s.x, pc.s.y - 70);
    if (aceso) {
      e.visto = true;
      e.moveu = false;
      e.apagouEm = agora;
      estado.flags.olhou_espantalho_s = (estado.flags.olhou_espantalho_s || 0) + dt;
      return;
    }
    if (!e.visto || e.moveu || agora - e.apagouEm < 900) return;
    // a luz saiu dele: ele está mais perto (nunca dentro da luz, nunca colado)
    const dx = pc.s.x - this.esp.x;
    const dy = pc.s.y - this.esp.y;
    const d = Math.hypot(dx, dy);
    const novo = Math.max(330, d * 0.62);
    const lateral = Phaser.Math.Between(-160, 160);
    const nx = pc.s.x - (dx / d) * novo + (-dy / d) * lateral;
    const ny = pc.s.y - (dy / d) * novo + (dx / d) * lateral;
    if (this.luz.iluminado({ x: nx, y: ny }, pc.s.x, pc.s.y - 70)) return; // espera a luz sair de onde ele vai
    e.moveu = true;
    e.passos++;
    this.esp.setPosition(Phaser.Math.Clamp(nx, 160, TRIGAL_W - 160), Phaser.Math.Clamp(ny, 300, TRIGAL_H - 200));
    this.som("folhas", 0.22, 0.6);
    if (e.passos === 1) this.primeiroPasso();
    else if (novo <= 340) this.pertoDemais();
  }

  async primeiroPasso() {
    this.travado = true;
    await this.esperar(500);
    await this.dizer([
      ["riley", "...CHAZ. ELE NÃO TAVA ALI."],
      ["chaz", "TAVA LONGE. EU VI. TAVA LONGE."],
      ["nevoa", "...NÃO TIRA A LUZ DELE."],
    ]);
    this.travado = false;
  }

  async pertoDemais() {
    const e = this.espEstado;
    e.sustos++;
    this.travado = true;
    this.cameras.main.shake(320, 0.006);
    this.som("batida_vidro_2", 0.4, 0.5);
    await this.esperar(300);
    await this.dizer([["riley", e.sustos === 1 ? "CHAZ. ANDA. AGORA." : "NÃO OLHA PRA TRÁS. ANDA."]]);
    // ele "volta" pro escuro mais longe (no capítulo 1 ninguém morre aqui: é pra aprender a regra)
    const pc = this.pc;
    this.esp.setPosition(Phaser.Math.Clamp(pc.s.x + Phaser.Math.Between(-900, 900), 160, TRIGAL_W - 160), Math.max(300, pc.s.y - 1100));
    e.visto = false;
    this.travado = false;
  }

  // ---------------------------------------------------------------- o Névoa e o gerador (escolha C)
  async beatNevoa() {
    this.beats.nevoa = true;
    this.travado = true;
    const pc = this.pc;
    const nevoa = this.porNome("nevoa");
    const riley = this.porNome("riley");
    pc.moving = false;
    this.parar(pc);
    await this.dizer([
      ["nevoa", "...A CASA DO SEU AMOS TEM GERADOR. EU SEI LIGAR."],
      ["riley", "COMO VOCÊ SABE?"],
      ["nevoa", "...EU SEI."],
    ]);
    // ele entra no trigo, pro lado do gerador, e some do alcance da luz
    nevoa.parado = true;
    const vai = this.andarAte(nevoa, nevoa.s.x + 520, nevoa.s.y + 380);
    await this.esperar(900);
    await this.dizer([
      ["riley", "NÉVOA. NÉVOA, VOLTA AQUI."],
      {
        id: "seguir_nevoa", quem: "chaz", tempo: 7,
        opcoes: [
          { texto: "SEGUIR O NÉVOA", flag: "seguiu_nevoa", depois: [["chaz", "FICA AQUI, RILEY. EU JÁ VOLTO!"], ["riley", "CHAZ, VOCÊ TÁ LEVANDO A ÚNICA LUZ—"]] },
          { texto: "FICAR COM A RILEY", flag: "ficou_riley", depois: [["chaz", "ELE CONHECE O CAMINHO. A GENTE VAI JUNTO."], ["riley", "...TÁ."]] },
        ],
        silencio: [["riley", "...ELE JÁ FOI."]],
        flagSilencio: "hesitou_nevoa",
      },
    ]);
    await vai;
    nevoa.s.setVisible(false);
    if (estado.flags.hesitou_nevoa) marcar("ficou_riley");
    if (estado.flags.seguiu_nevoa) {
      // o Chaz corre atrás do Névoa e leva a luz junto: a Riley fica no escuro
      this.andarAte(pc, pc.s.x + 560, pc.s.y + 420, true);
      await this.esperar(1100);
    } else {
      // a Riley vira pra olhar a coisa no trigal. Quando volta, o Chaz não está mais ali.
      this.virar(riley, "costas");
      this.som("folhas", 0.3, 0.7);
      await this.esperar(1400);
    }
    pc.s.setVisible(false);
    await this.trocarParaRiley();
  }

  // ---------------------------------------------------------------- troca de perspectiva -> Riley
  async trocarParaRiley() {
    const cam = this.cameras.main;
    cam.fadeOut(600, 0, 0, 0);
    await this.esperar(700);
    const riley = this.porNome("riley");
    this.ativo = this.chars.indexOf(riley);
    this.jogaveis = [riley];
    riley.parado = false;
    cam.startFollow(riley.s, true, 0.12, 0.12);
    this.luz.isqueiro = true;
    this.esp.setVisible(false);
    this.hudNome.setText(NOMES.riley);
    // cartela da troca: o nome de quem você agora é
    const W = this.scale.width;
    const t = this.add.text(W / 2, 540, "RILEY", { fontFamily: '"Caveat Brush", sans-serif', fontSize: "120px", color: "#7d001a", stroke: "#000", strokeThickness: 10 })
      .setOrigin(0.5).setScrollFactor(0).setDepth(UI + 2).setAlpha(0);
    this.tweens.add({ targets: t, alpha: 1, duration: 500, hold: 1200, yoyo: true, onComplete: () => t.destroy() });
    await this.esperar(2200);
    cam.fadeIn(900, 0, 0, 0);
    this.fase = "riley";
    this.rileyIni = { x: riley.s.x, y: riley.s.y };
    this.rileyIniEm = this.time.now + 4000;
    this.virar(riley, "frente");
    await this.esperar(500);
    await this.dizer([
      ["riley", "...CHAZ?"],
      ["riley", "CHAZ. NÃO TEM GRAÇA."],
      ["riley", "(o celular foi junto. Só sobrou o isqueiro.)"],
    ]);
    this.travado = false;
    this.dica("Sem lanterna: o isqueiro só ilumina perto. Continue descendo.");
  }

  // ---------------------------------------------------------------- algo arrasta palha (esconder)
  async beatArrasto() {
    this.beats.arrasto = true;
    const r = this.pc;
    this.som("folhas", 0.5, 0.45);
    await this.dizer([["riley", "(alguma coisa tá arrastando palha. Ali.)"]]);
    this.dica(this.sys.game.device.input.touch ? "SEGURE ESCONDER. Prenda a respiração." : "SEGURE C pra se esconder e prender a respiração.", 9000);
    // a presença passa pela frente dela, a uns 220 px, devagar, da esquerda pra direita
    this.presenca = { x: r.s.x - 900, y: r.s.y + 220, vx: 150, viu: false, inicio: this.time.now, somEm: 0, escondida: true };
  }

  atualizarPresenca(dt, agora) {
    const p = this.presenca;
    const r = this.pc;
    p.x += p.vx * dt;
    if (agora > p.somEm) {
      // arrasto: folha + papel, mais alto quanto mais perto
      const d = Math.hypot(p.x - r.s.x, p.y - r.s.y);
      const vol = Phaser.Math.Clamp(1 - d / 1100, 0.05, 0.6);
      this.som(Phaser.Utils.Array.GetRandom(["folhas", "papel_1", "papel_3"]), vol, 0.5);
      p.somEm = agora + 380;
      if (d < 330 && !r.prendendo && !p.viu) this.foiVista();
      if (d < 330 && r.prendendo) p.prendeu = true;
    }
    // rastro escuro no chão por onde passou
    if (!p.ultimo || p.x - p.ultimo > 70) {
      this.add.ellipse(p.x, p.y + Phaser.Math.Between(-10, 10), Phaser.Math.Between(40, 70), 16, 0x1c0609, 0.85).setDepth(-1e5);
      p.ultimo = p.x;
    }
    if (p.x > r.s.x + 700) {
      // passou. O rastro continua até um fardo de palha, mais pra baixo
      this.presenca = null;
      if (p.prendeu && !p.viu) marcar("riley_prendeu_respiracao");
      this.colocarFardo(p.x + 60, p.y + 520);
    }
  }

  async foiVista() {
    const p = this.presenca;
    p.viu = true;
    marcar("riley_foi_vista");
    const r = this.pc;
    // por um instante, na beira da luz do isqueiro: ele
    this.esp.setVisible(true).setPosition(r.s.x + 150, r.s.y + 30).setAlpha(0.9);
    this.cameras.main.shake(260, 0.008);
    this.som("batida_vidro_2", 0.5, 0.45);
    await this.esperar(260);
    this.esp.setVisible(false).setAlpha(1);
    this.travado = true;
    await this.dizer([["riley", "...!"]]);
    this.travado = false;
  }

  colocarFardo(x, y) {
    x = Phaser.Math.Clamp(x, 300, TRIGAL_W - 300);
    // trilha do fim do arrasto até o fardo
    const ini = { x: x - 60, y: y - 520 };
    for (let i = 1; i <= 7; i++) {
      this.add.ellipse(ini.x + (x - ini.x) * (i / 8) + Phaser.Math.Between(-20, 20), ini.y + (y - ini.y) * (i / 8), 50, 16, 0x1c0609, 0.85).setDepth(-1e5);
    }
    this.fardo = this.add.image(x, y, "fardo").setOrigin(0.5, 1).setScale(1.2).setTint(0x9a96a8).setDepth(y);
    this.interativo({ id: "fardo", x, y: y - 70, raio: 190, ativo: () => !this.beats.bilhete, acao: () => this.abrirFardo() });
    this.dica("Um rastro escuro... siga.", 5000);
  }

  // ---------------------------------------------------------------- o bilhete (escolha D)
  async abrirFardo() {
    this.beats.bilhete = true;
    this.travado = true;
    const c = this.cine;
    await this.dizer([["riley", "(tem um papel enfiado na palha.)"]]);
    await c.abrir(() => {
      c.objeto("bilhete", {
        tinta: "#6b5844",
        texto: "TODA NOITE EU TRANCO A PORTA DO MENINO POR FORA.\n\nONTEM EU ESQUECI.\n\nQUE DEUS ME PERDOE PELO QUE EU PENSO QUANDO ELE VOLTA COM TERRA NAS MÃOS.",
      });
      c.camera({ z: 1.0 });
      c.camera({ z: 1.06, ms: 9000 });
    });
    await c.esperar(4500);
    await c.falar([
      {
        id: "bilhete", quem: "riley",
        opcoes: [
          { texto: "GUARDAR O BILHETE", flag: "riley_guardou_bilhete", depois: [["riley", "(no bolso. Junto com o isqueiro.)"]] },
          { texto: "LARGAR ALI", flag: "riley_largou_bilhete", depois: [["riley", "(não é da minha conta. Não é.)"]] },
        ],
      },
    ], { fora: { riley: "esquerda" } });
    await c.fechar({ fade: 500 });
    this.travado = false;
    this.dica("A casa do seu Amos é lá embaixo.", 5000);
  }

  async fimRiley() {
    this.beats.fim = true;
    this.travado = true;
    await this.dizer([["riley", "(a porta da casa tá aberta.)"]]);
    const cam = this.cameras.main;
    cam.fadeOut(900, 0, 0, 0);
    await this.esperar(1000);
    salvar();
    this.scene.start("Cozinha");
  }
}

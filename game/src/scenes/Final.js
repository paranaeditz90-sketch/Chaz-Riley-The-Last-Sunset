import Phaser from "phaser";
import { CenaJogo, irPara, tocarAmbiente, tocarMusica } from "../base.js";
import { Cinema } from "../cinema.js";
import { estado, marcar, marcarMeta } from "../estado.js";

// Capítulo 1, beat 6: a varanda. Convergência e 3 finais (decididos pelas escolhas C, D e E):
//   C "Sem luz"  : o Chaz seguiu o Névoa e ninguém ligou o gerador
//   B "A porta"  : o Névoa trancou a porta (e o Chaz não foi atrás dele)
//   A "Três"     : o resto (luz ligada, ou ninguém trancou)
// O Chaz sobrevive sempre no capítulo 1. Última imagem de todos os finais: a janela da casa do Chaz.

const NOITE_FINAL = 0x5a6290;
const QUENTE_FINAL = 0xe0c098;

export function qualFinal(f) {
  if (f.seguiu_nevoa && !f.luz_varanda) return "C";
  if (f.nevoa_trancou) return "B";
  return "A";
}

export default class Final extends CenaJogo {
  constructor() {
    super("Final");
  }

  config() {
    return { personagens: [{ nome: "chaz", x: -400, y: 900 }], controla: ["chaz"], esconder: false, cameraFixa: { x: 960, y: 540 } };
  }

  aoEntrar() {
    this.chars[0].s.setVisible(false);
    this.travado = true;
    this.cine = new Cinema(this);
    tocarAmbiente(this, "grilos_loop", 0.0, 10);
    this.time.delayedCall(200, () => this.roteiro());
  }

  async roteiro() {
    const f = estado.flags;
    const fim = qualFinal(f);
    marcar("final_cap1", fim);
    marcar("status_chaz", "vivo");
    marcar("status_riley", fim === "B" ? "desaparecido" : "vivo");
    marcar("status_nevoa", fim === "C" ? "desaparecido" : "vivo");
    const c = this.cine;
    c.expAtual = { chaz: "susto", riley: "tristeza", nevoa: "nervoso" };
    if (fim === "A") await this.finalA(c, f);
    else if (fim === "B") await this.finalB(c, f);
    else await this.finalC(c, f);
    await this.janela(c);
    await c.fechar({ fade: 1200 });
    irPara(this, "Fluxo", {}, 200);
  }

  // ---------------------------------------------------------------- A: "Três"
  async finalA(c, f) {
    tocarMusica(this, "musica_noite", 0.18, 3000);
    await c.abrir(() => {
      c.fundo(f.luz_varanda ? "cine_fazenda_luz" : "cine_fazenda_noite");
      c.entrar("chaz", null, { x: 0.28 });
      c.entrar("nevoa", null, { x: 0.52 });
      c.entrar("riley", null, { x: 0.76 });
      c.tingir(f.luz_varanda ? QUENTE_FINAL : NOITE_FINAL);
      c.camera({ z: 1.0, fx: 0.5, fy: 0.55 });
      c.camera({ z: 1.06, ms: 16000 });
    }, { fade: 1200 });
    await c.esperar(800);
    await c.falar([
      ["chaz", "...TÁ TODO MUNDO AQUI. TÁ TODO MUNDO AQUI.", "tristeza"],
      ...(f.seguiu_nevoa
        ? [["riley", "VOCÊ LEVOU A ÚNICA LUZ, CHAZ.", "raiva"], ["chaz", "EU PERDI ELE NO TRIGO. DESCULPA. DESCULPA.", "tristeza"]]
        : [["riley", "VOCÊ SUMIU, CHAZ. EU VIREI E VOCÊ TINHA SUMIDO.", "raiva"], ["chaz", "EU NÃO SUMI. EU TAVA DO SEU LADO.", "susto"]]),
      ["nevoa", "...O SEU AMOS TÁ NO QUARTO.", "choro"],
      ["nevoa", "NÃO ENTRA LÁ.", "encolhido"],
      ...(f.riley_guardou_bilhete ? [["riley", "(o bilhete pesa no bolso. Ainda não.)", "defensiva"]] : []),
      ["chaz", "TRANCA A PORTA. A GENTE ESPERA O SOL AQUI DENTRO.", "explicando"],
    ]);
    this.som("porta_abre", 0.4, 1.3);
    await c.esperar(900);
    // pela janela: o trigal. O espantalho não está mais lá.
    c.corte(() => {
      c.fundo("cine_morro_noite");
      c.camera({ z: 1.0, fx: 0.6, fy: 0.75 });
      c.camera({ z: 1.3, ms: 6000, ease: "Cubic.easeIn" });
    });
    await c.esperar(2400);
    await c.falar([["riley", "...CHAZ. ELE NÃO TÁ MAIS LÁ."]], { fora: { riley: "direita" } });
    await c.esperar(1200);
    // o celular: o vídeo de 0:47 agora tem um segundo de imagem
    c.corte(() => {
      c.fundo("cine_fazenda_noite");
      c.objeto("celular", { tela: "video", audio: "♪ hm... hm-hm... ♪\n\n(1 quadro recuperado: trigo, de noite)", ms: 6000, ate: 0.04 });
      c.camera({ z: 1.0 });
    });
    await c.esperar(3000);
    await c.falar([["chaz", "...ISSO É O TRIGAL. DE NOITE.", null], ["chaz", "O SOL APAGOU FAZ MEIA HORA. COMO EU GRAVEI ISSO ANTES?"]], { fora: { chaz: "esquerda" } });
  }

  // ---------------------------------------------------------------- B: "A porta"
  async finalB(c, f) {
    tocarMusica(this, null, 0, 200);
    await c.abrir(() => {
      c.fundo("cine_cozinha");
      c.entrar("nevoa", "encolhido", { x: 0.5, escala: 1.1 });
      c.tingir(0x7078a4);
      c.camera({ z: 1.05, fx: 0.5, fy: 0.6 });
      c.camera({ z: 1.15, ms: 14000 });
    }, { fade: 1200 });
    const bater = async (n) => {
      for (let i = 0; i < n; i++) {
        this.som(`batida_vidro_${i % 3}`, 0.6, 0.55);
        c.tremer(0.002, 80);
        await c.esperar(320);
      }
    };
    await c.esperar(800);
    await bater(3);
    await c.falar([["riley", "NÉVOA! ABRE! SOU EU!"]], { fora: { riley: "direita" } });
    await bater(4);
    await c.falar([
      ["riley", "NÉVOA, TEM ALGUMA COISA AQUI FORA. ABRE A PORTA."],
      ["nevoa", "(...não. Não, se eu abrir...)", "choro"],
    ], { fora: { riley: "direita" } });
    await bater(2);
    // e para.
    await c.esperar(4000);
    await c.falar([["nevoa", "...RILEY?", "susto"]]);
    await c.esperar(2500);
    // o Chaz chega pelos fundos
    c.corte(() => {
      c.fundo("cine_cozinha");
      c.entrar("chaz", "tristeza", { x: 0.3 });
      c.entrar("nevoa", "choro", { x: 0.66 });
      c.tingir(0x7078a4);
      c.camera({ z: 1.0, fx: 0.5, fy: 0.55 });
    });
    await c.falar([
      ["chaz", "NÉVOA! A PORTA DOS FUNDOS TAVA... CADÊ A RILEY?", "susto"],
      ["nevoa", "...LÁ FORA.", "choro"],
    ]);
    this.som("porta_abre", 0.5, 0.9);
    // abrem a porta: no capacho, só palha
    c.corte(() => {
      c.fundo("cine_fazenda_noite");
      const g = this.add.graphics().setScrollFactor(0);
      const rnd = new Phaser.Math.RandomDataGenerator(["capacho"]);
      g.fillStyle(0x3a2a22);
      g.fillRect(c.px(0.38), c.H * 0.82, 480, 90);
      for (let i = 0; i < 60; i++) {
        g.lineStyle(5, 0xb0904c);
        const x = c.px(0.4) + rnd.between(0, 420);
        const y = c.H * 0.84 + rnd.between(0, 60);
        const a = rnd.realInRange(0, Math.PI);
        g.lineBetween(x, y, x + Math.cos(a) * 40, y + Math.sin(a) * 12);
      }
      c.camFundo.add(g);
      c.camera({ z: 1.0, fx: 0.5, fy: 0.7 });
      c.camera({ z: 1.25, fy: 0.82, ms: 7000 });
    });
    await c.esperar(3500);
    await c.falar([["chaz", "...RILEY?"], ["chaz", "RILEY!"]], { fora: { chaz: "esquerda" } });
    await c.esperar(1500);
  }

  // ---------------------------------------------------------------- C: "Sem luz"
  async finalC(c, f) {
    tocarMusica(this, null, 0, 200);
    await c.abrir(() => {
      c.fundo("cine_fazenda_noite");
      c.entrar("chaz", null, { x: 0.28 });
      c.entrar("nevoa", null, { x: 0.52 });
      c.entrar("riley", null, { x: 0.76 });
      c.tingir(0x8a90b4);
      c.camera({ z: 1.0, fx: 0.5, fy: 0.55 });
      c.camera({ z: 1.06, ms: 16000 });
    }, { fade: 1200 });
    await c.esperar(700);
    await c.falar([
      ["chaz", "EU TE PERDI NO TRIGO, NÉVOA. EU CORRI ATRÁS E VOCÊ TINHA SUMIDO.", "tristeza"],
      ["nevoa", "...EU ACORDEI LÁ DENTRO. NA COZINHA.", "nervoso"],
      ["riley", "COMO ASSIM, ACORDOU?", "irritacao"],
      ["nevoa", "...O SEU AMOS—", "choro"],
      ["chaz", "...A BATERIA. NÃO, NÃO, NÃO. UM POR CENTO.", "susto"],
    ]);
    // apaga tudo: 5 segundos de tela preta, com som
    const preto = this.add.rectangle(0, 0, this.scale.width * 3, this.scale.height * 3, 0x000000).setOrigin(0).setScrollFactor(0).setDepth(9.8e6);
    for (let i = 0; i < 10; i++) {
      this.time.delayedCall(i * 480, () => this.som(Phaser.Utils.Array.GetRandom(["folhas", "papel_2"]), 0.25 + i * 0.03, 0.5));
    }
    this.time.delayedCall(2600, () => this.som("passo_grama_2", 0.4, 0.8));
    await c.esperar(5000);
    // o isqueiro da Riley
    this.som("papel_1", 0.4, 1.6);
    c.corte(() => {
      c.fundo("cine_fazenda_noite");
      c.entrar("chaz", "susto", { x: 0.3 });
      c.entrar("riley", "tristeza", { x: 0.72 });
      c.tingir(QUENTE_FINAL);
      c.camera({ z: 1.08, fx: 0.5, fy: 0.55 });
    });
    preto.destroy();
    await c.falar([
      ["riley", "...NÉVOA?", "tristeza"],
      ["chaz", "NÉVOA!", "susto"],
    ]);
    // pegadas: saindo da varanda, indo pro trigal. Pro espantalho.
    c.corte(() => {
      c.fundo("cine_morro_noite");
      const g = this.add.graphics().setScrollFactor(0);
      g.fillStyle(0x0b0608, 0.9);
      for (let i = 0; i < 9; i++) {
        const t = i / 8;
        const x = c.px(0.3 + t * 0.32) + (i % 2 ? 22 : -22);
        const y = c.H * (0.98 - t * 0.14);
        g.fillEllipse(x, y, 46 * (1 - t * 0.6), 18 * (1 - t * 0.6));
      }
      c.camFundo.add(g);
      const e = this.add.image(c.px(0.62), c.H * 0.84, "espantalho").setOrigin(0.5, 1).setScale(0.36).setTint(0x5a5e78).setScrollFactor(0);
      c.camFundo.add(e);
      c.camera({ z: 1.0, fx: 0.45, fy: 0.85 });
      c.camera({ z: 1.3, fx: 0.62, fy: 0.78, ms: 7000, ease: "Sine.easeIn" });
    });
    await c.esperar(5000);
  }

  // ---------------------------------------------------------------- todos: a janela da casa do Chaz
  async janela(c) {
    tocarMusica(this, null, 0, 1500);
    tocarAmbiente(this, "vento_loop", 0.1, 2000);
    c.corte(() => {
      c.fundo("cine_janela_andy");
      c.camera({ z: 1.0, fx: 0.5, fy: 0.5 });
      c.camera({ z: 1.12, ms: 8000 });
    });
    await c.esperar(6500);
  }
}

// ---------------------------------------------------------------- fluxograma (estilo Detroit)
// Mostra o caminho desta partida e o que já foi descoberto em todas as partidas (porcentagem).
const NOS = [
  { id: "carta", rotulo: "A carta", ops: ["Guardar de volta", "Levar no bolso"] },
  { id: "guitarra", rotulo: "A guitarra", ops: ["Amanhã. Juro.", "Tá bem cuidada", "(silêncio)"] },
  { id: "tom", rotulo: "A janela", ops: ["Piada", "Meia verdade", "Esconder o caderno", "(silêncio)"] },
  { id: "bolso", rotulo: "O bolso", ops: ["Mentir", "Depois eu mostro", "(silêncio)"] },
  { id: "acordar_nevoa", rotulo: "Acordar o Névoa", ops: ["Chamar baixinho", "Mexer na orelha", "(silêncio)"] },
  { id: "novidade", rotulo: "A novidade", ops: ["Contar metade", "Desconversar", "(silêncio)"] },
  { id: "cachecol", rotulo: "O cachecol", ops: ["Pra Riley", "Pro Névoa", "(ficar com ele)"] },
  { id: "seguir_nevoa", rotulo: "O gerador", ops: ["Seguir o Névoa", "Ficar com a Riley", "(silêncio)"] },
  { id: "bilhete", rotulo: "O bilhete", ops: ["Guardar", "Largar"] },
  { id: "porta_luz", rotulo: "A porta", ops: ["Trancar", "Ligar a luz", "(silêncio)"] },
  { id: "final", rotulo: "Final", ops: ["A — Três", "B — A porta", "C — Sem luz"] },
];

export class Fluxo extends Phaser.Scene {
  constructor() {
    super("Fluxo");
  }

  create() {
    const W = this.scale.width;
    const H = this.scale.height;
    this.cameras.main.setBackgroundColor("#0b0a10");
    this.cameras.main.fadeIn(800, 0, 0, 0);
    // o que foi escolhido nesta partida (última escolha de cada id) e o que já foi descoberto em todas
    const agora = {};
    for (const e of estado.escolhas) agora[e.id] = e.opcao;
    const fim = estado.flags.final_cap1;
    if (fim) agora.final = { A: 0, B: 1, C: 2 }[fim];
    const desc = Object.assign({}, estado.meta.descobertos || {});
    for (const [id, op] of Object.entries(agora)) {
      const no = NOS.find((n) => n.id === id);
      if (!no) continue;
      const i = op === "silencio" ? no.ops.length - 1 : op;
      desc[`${id}:${i}`] = true;
    }
    marcarMeta("descobertos", desc);
    marcarMeta("cap1_concluido", true);
    const total = NOS.reduce((s, n) => s + n.ops.length, 0);
    const achados = Object.keys(desc).length;

    const fonte = '"Patrick Hand", sans-serif';
    this.add.text(W / 2, 70, "CAPÍTULO 1 — O ÚLTIMO PÔR DO SOL", { fontFamily: fonte, fontSize: "54px", color: "#fff3d6" }).setOrigin(0.5);
    this.add.text(W / 2, 128, `${Math.round((achados / total) * 100)}% dos caminhos descobertos`, { fontFamily: fonte, fontSize: "34px", color: "#b9ad9c" }).setOrigin(0.5);
    // grade: uma coluna por escolha, de cima pra baixo as opções
    const n = NOS.length;
    const passo = Math.min(170, (W - 120) / n);
    const x0 = W / 2 - (passo * (n - 1)) / 2;
    const g = this.add.graphics();
    let antes = null;
    NOS.forEach((no, k) => {
      const x = x0 + k * passo;
      this.add.text(x, 220, no.rotulo, { fontFamily: fonte, fontSize: "30px", color: "#cfc6b4", align: "center", wordWrap: { width: passo - 6 } }).setOrigin(0.5, 0);
      no.ops.forEach((op, i) => {
        const y = 350 + i * 165;
        const escolhido = agora[no.id] !== undefined && (agora[no.id] === "silencio" ? no.ops.length - 1 : agora[no.id]) === i;
        const visto = desc[`${no.id}:${i}`];
        g.fillStyle(escolhido ? 0xe8b04a : visto ? 0x4a4458 : 0x1d1b24);
        g.lineStyle(3, escolhido ? 0xffe2a0 : 0x5a5468);
        g.fillCircle(x, y, 26);
        g.strokeCircle(x, y, 26);
        this.add.text(x, y + 34, visto ? op : "???", { fontFamily: fonte, fontSize: "25px", color: escolhido ? "#ffe2a0" : visto ? "#9a92a8" : "#4a4656", align: "center", wordWrap: { width: passo - 6 } }).setOrigin(0.5, 0);
        if (escolhido) {
          if (antes) {
            g.lineStyle(5, 0xe8b04a, 0.8);
            g.lineBetween(antes.x + 26, antes.y, x - 26, y);
          }
          antes = { x, y };
        }
      });
    });
    const dica = this.add.text(W / 2, H - 70, "toque pra voltar ao título", { fontFamily: fonte, fontSize: "32px", color: "#8f8798" }).setOrigin(0.5).setAlpha(0);
    this.tweens.add({ targets: dica, alpha: 1, delay: 2500, duration: 800 });
    this.time.delayedCall(2500, () => {
      const sair = () => irPara(this, "Titulo");
      this.input.once("pointerdown", sair);
      this.input.keyboard.once("keydown", sair);
    });
  }
}

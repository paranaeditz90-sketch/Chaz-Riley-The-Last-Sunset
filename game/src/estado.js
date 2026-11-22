// Memória do jogo: escolhas e flags. "Este jogo se lembra das suas escolhas."
// Fica no aparelho (localStorage). Se o navegador não deixar salvar, o jogo continua sem salvar.
// - flags/escolhas: da partida atual (NOVO JOGO apaga)
// - meta: o que vale entre partidas (ex.: já viu a abertura, então pode pular)
// - checkpoint: começo da última cena jogada, com as flags daquele momento (CONTINUAR volta pra lá)
const CHAVE = "the_last_sunset_v1";

export const estado = { flags: {}, escolhas: [], meta: {}, checkpoint: null };

export function carregar() {
  try {
    const s = JSON.parse(localStorage.getItem(CHAVE) || "null");
    if (s && typeof s === "object") {
      estado.flags = s.flags || {};
      estado.escolhas = s.escolhas || [];
      estado.meta = s.meta || {};
      estado.checkpoint = s.checkpoint || null;
      // salvamento antigo (v0.1): "viu_abertura" ficava junto das flags da partida
      if (estado.flags.viu_abertura) {
        estado.meta.viu_abertura = true;
        delete estado.flags.viu_abertura;
      }
    }
  } catch (e) {
    /* sem armazenamento: segue sem salvar */
  }
  return estado;
}

export function salvar() {
  try {
    localStorage.setItem(CHAVE, JSON.stringify(estado));
  } catch (e) {
    /* idem */
  }
}

export function marcar(flag, valor = true) {
  estado.flags[flag] = valor;
  salvar();
}

export function marcarMeta(chave, valor = true) {
  estado.meta[chave] = valor;
  salvar();
}

export function registrarEscolha(id, opcao) {
  estado.escolhas.push({ id, opcao, quando: Date.now() });
  salvar();
}

export function novoJogo() {
  estado.flags = {};
  estado.escolhas = [];
  estado.checkpoint = null;
  salvar();
}

export function pontoDeSalvamento(cena) {
  estado.checkpoint = { cena, flags: JSON.parse(JSON.stringify(estado.flags)), escolhas: estado.escolhas.length, quando: Date.now() };
  salvar();
}

export function temSalvamento() {
  return !!(estado.checkpoint && estado.checkpoint.cena);
}

// volta pro começo da cena salva, com as flags e escolhas de quando ela começou
export function continuar() {
  const cp = estado.checkpoint;
  estado.flags = JSON.parse(JSON.stringify(cp.flags || {}));
  estado.escolhas = estado.escolhas.slice(0, cp.escolhas || 0);
  salvar();
  return cp.cena;
}

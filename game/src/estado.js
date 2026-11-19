// Memória do jogo: escolhas e flags. "Este jogo se lembra das suas escolhas."
// Fica no aparelho (localStorage). Se o navegador não deixar salvar, o jogo continua sem salvar.
const CHAVE = "the_last_sunset_v1";

export const estado = { flags: {}, escolhas: [] };

export function carregar() {
  try {
    const s = JSON.parse(localStorage.getItem(CHAVE) || "null");
    if (s && typeof s === "object") Object.assign(estado, { flags: s.flags || {}, escolhas: s.escolhas || [] });
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

export function registrarEscolha(id, opcao) {
  estado.escolhas.push({ id, opcao, quando: Date.now() });
  salvar();
}

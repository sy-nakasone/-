/**
 * 固定の対応表（ユーザー指定）
 * - ドラえもん：大吉
 * - のびた：中吉
 * - しずか：吉
 * - スネ夫：小吉
 * - ジャイアン：凶
 * - 先生：大凶
 */
const OMIKUJI = [
  { character: "ドラえもん", fortune: "大吉" },
  { character: "のびた", fortune: "中吉" },
  { character: "しずか", fortune: "吉" },
  { character: "スネ夫", fortune: "小吉" },
  { character: "ジャイアン", fortune: "凶" },
  { character: "先生", fortune: "大凶" },
];

function pickRandom(items) {
  if (!Array.isArray(items) || items.length === 0) return null;
  const idx = Math.floor(Math.random() * items.length);
  return items[idx];
}

function renderMappingList(listEl) {
  listEl.innerHTML = "";
  for (const item of OMIKUJI) {
    const li = document.createElement("li");
    li.textContent = `${item.character}：${item.fortune}`;
    listEl.appendChild(li);
  }
}

function setResult({ character, fortune }) {
  const fortuneEl = document.getElementById("fortune");
  const characterEl = document.getElementById("character");
  const hintEl = document.getElementById("hint");

  fortuneEl.textContent = fortune;
  characterEl.textContent = character;
  hintEl.textContent = "もう一度引くこともできます。";
}

function resetResult() {
  const fortuneEl = document.getElementById("fortune");
  const characterEl = document.getElementById("character");
  const hintEl = document.getElementById("hint");

  fortuneEl.textContent = "—";
  characterEl.textContent = "—";
  hintEl.textContent = "「おみくじを引く」を押してください。";
}

function main() {
  const drawButton = document.getElementById("drawButton");
  const resetButton = document.getElementById("resetButton");
  const mappingEl = document.getElementById("mapping");

  renderMappingList(mappingEl);

  drawButton.addEventListener("click", () => {
    const result = pickRandom(OMIKUJI);
    if (!result) return;
    setResult(result);
  });

  resetButton.addEventListener("click", () => {
    resetResult();
  });
}

main();

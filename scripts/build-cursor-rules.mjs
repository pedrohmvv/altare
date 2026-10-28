// Gera .cursor/rules/altare-*.mdc a partir de .claude/skills/*/SKILL.md (AGENTS.md §5).
// A skill é a fonte: o Cursor recebe o mesmo `description` (decide quando aplicar a regra) e um ponteiro para o SKILL.md.
// Uso: node scripts/build-cursor-rules.mjs [--check]   (--check falha se houver arquivo desatualizado, sem escrever)
import { readdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const skillsDir = join(root, ".claude", "skills");
const rulesDir = join(root, ".cursor", "rules");

// Skills que também anexam sozinhas ao abrir arquivos correspondentes. As demais só entram pelo `description`.
const globs = {
  "altare-frontend": ["apps/web/src/**/*.ts", "apps/web/src/**/*.tsx"],
  "altare-design": ["apps/web/src/**/*.tsx", "apps/web/src/**/*.css", "docs/design/**"],
  "altare-conteudo-copy": ["apps/web/src/**/copy.ts"],
  "altare-testes-qa": ["apps/web/src/**/*.test.ts", "apps/web/src/**/*.test.tsx"],
  "altare-monorepo": ["Makefile", "package.json", "pnpm-workspace.yaml"],
  "altare-devops": [".github/**", "Dockerfile"],
  "altare-docs-vivas": ["docs/**"],
};

function readDescription(skill, text) {
  const front = text.match(/^---\n([\s\S]*?)\n---/);
  const folded = front?.[1].match(/^description:\s*>-?\n((?:[ \t]+.*\n?)+)/m);
  if (!folded) throw new Error(`${skill}: SKILL.md sem description em bloco dobrado`);
  return folded[1].split("\n").map((l) => l.trim()).filter(Boolean).join(" ");
}

function render(skill, description) {
  const lines = [
    "---",
    `description: ${JSON.stringify(description)}`,
    ...(globs[skill] ? [`globs: ${globs[skill].join(",")}`] : []),
    "alwaysApply: false",
    "---",
    "",
    `<!-- Gerado por scripts/build-cursor-rules.mjs a partir de .claude/skills/${skill}/SKILL.md. Não edite aqui. -->`,
    "",
    `Antes de agir, leia [SKILL.md](mdc:.claude/skills/${skill}/SKILL.md) e siga o que ele manda.`,
    "As regras de projeto e a precedência estão em [AGENTS.md](mdc:AGENTS.md) (§5).",
    "",
  ];
  return lines.join("\n");
}

const check = process.argv.includes("--check");
const skills = readdirSync(skillsDir).filter((s) => s.startsWith("altare-")).sort();
const stale = [];

for (const skill of skills) {
  const text = readFileSync(join(skillsDir, skill, "SKILL.md"), "utf8");
  const content = render(skill, readDescription(skill, text));
  const target = join(rulesDir, `${skill}.mdc`);
  if (existsSync(target) && readFileSync(target, "utf8") === content) continue;
  stale.push(`${skill}.mdc`);
  if (!check) writeFileSync(target, content);
}

if (check && stale.length > 0) {
  console.error(`Regras do Cursor desatualizadas (rode \`make cursor-rules\`): ${stale.join(", ")}`);
  process.exit(1);
}
console.log(check ? "Regras do Cursor em dia." : `${skills.length} regras conferidas, ${stale.length} escritas.`);

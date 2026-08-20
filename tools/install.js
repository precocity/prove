#!/usr/bin/env node
/**
 * PROVE installer — zero-dependency (Node 18+, stdlib only).
 *
 * Interactive:      npx prove-method install        (or: node tools/install.js)
 * Non-interactive:  node tools/install.js --dir /path/to/project \
 *                     --tools copilot,claude,cursor,agents --agents all --yes
 */
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const readline = require("node:readline/promises");

const SRC = path.join(__dirname, "..", "src");

const TOOLS = {
  copilot: "GitHub Copilot (.github/instructions/prove.instructions.md)",
  claude: "Claude Code (CLAUDE.md)",
  cursor: "Cursor (.cursor/rules/prove.mdc)",
  agents: "Generic AGENTS.md",
};

const AGENTS = ["orchestrator", "discovery", "drafter", "evidence", "refiner", "council", "tester", "tracker"];
const CORE_AGENTS = new Set(["orchestrator"]);

// ---------------------------------------------------------------- CLI args
function parseArgs(argv) {
  const args = { dir: null, tools: null, agents: null, yes: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "install") continue; // npx prove-method install
    else if (a === "--dir") args.dir = argv[++i];
    else if (a === "--tools") args.tools = argv[++i];
    else if (a === "--agents") args.agents = argv[++i];
    else if (a === "--yes" || a === "-y") args.yes = true;
    else if (a === "--help" || a === "-h") {
      console.log("Usage: prove-method [install] [--dir DIR] [--tools t1,t2] [--agents all|a1,a2] [--yes]");
      console.log("Tools: " + Object.keys(TOOLS).join(", "));
      console.log("Agents: " + AGENTS.join(", "));
      process.exit(0);
    } else {
      console.error("Unknown argument: " + a);
      process.exit(1);
    }
  }
  return args;
}

// ---------------------------------------------------------------- prompts
async function ask(rl, question, fallback) {
  const answer = (await rl.question(`${question}${fallback ? ` [${fallback}]` : ""}: `)).trim();
  return answer || fallback || "";
}

async function multiSelect(rl, title, options, defaults) {
  console.log(`\n${title}`);
  options.forEach((opt, i) => console.log(`  ${i + 1}. ${opt.label}`));
  const raw = await ask(rl, "Enter numbers (comma-separated) or 'all'", "all");
  if (raw.toLowerCase() === "all") return options.map((o) => o.value);
  const picked = new Set(
    raw.split(",").map((s) => parseInt(s.trim(), 10)).filter((n) => n >= 1 && n <= options.length)
  );
  const values = options.filter((_, i) => picked.has(i + 1)).map((o) => o.value);
  return values.length ? values : defaults;
}

// ---------------------------------------------------------------- glue text
function glueBody(relRunner) {
  return [
    "This project uses the PROVE method (Propose, Run, Observe, Verify, Enable)",
    "for developing expert-reviewed logic artifacts without review/serving skew.",
    "",
    "- Start every session with `python " + relRunner + " status` to see in-flight artifacts.",
    "- Principles (P1-P5): `.prove/docs/PRINCIPLES.md` — enforce them.",
    "- Lifecycle and gates: `.prove/docs/LIFECYCLE.md`.",
    "- Forbidden moves: `.prove/docs/ANTI-PATTERNS.md` — refuse them, including",
    "  your own impulse to write a standalone detector or scan unbounded.",
    "- Agent personas: `.prove/agents/` — adopt the persona matching the task.",
    "- If `prove.config.toml` is full of TBDs, offer to run the onboarding",
    "  interview in `.prove/docs/ONBOARDING.md`.",
  ].join("\n");
}

const BEGIN = "<!-- PROVE:BEGIN -->";
const END = "<!-- PROVE:END -->";

function writeWithMarkers(filePath, block, header) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  const wrapped = `${BEGIN}\n${block}\n${END}`;
  if (fs.existsSync(filePath)) {
    let text = fs.readFileSync(filePath, "utf8");
    if (text.includes(BEGIN) && text.includes(END)) {
      const re = new RegExp(`${BEGIN}[\\s\\S]*?${END}`);
      text = text.replace(re, wrapped);
    } else {
      text = text.trimEnd() + "\n\n" + wrapped + "\n";
    }
    fs.writeFileSync(filePath, text);
  } else {
    fs.writeFileSync(filePath, (header ? header + "\n\n" : "") + wrapped + "\n");
  }
}

function writeGlue(tool, dir, body) {
  switch (tool) {
    case "copilot":
      writeWithMarkers(
        path.join(dir, ".github", "instructions", "prove.instructions.md"),
        body,
        "---\napplyTo: '**'\n---\n\n# PROVE Method"
      );
      return ".github/instructions/prove.instructions.md";
    case "claude":
      writeWithMarkers(path.join(dir, "CLAUDE.md"), "## PROVE Method\n\n" + body, "# CLAUDE.md");
      return "CLAUDE.md";
    case "cursor":
      writeWithMarkers(
        path.join(dir, ".cursor", "rules", "prove.mdc"),
        body,
        "---\ndescription: PROVE method rails\nalwaysApply: true\n---\n\n# PROVE Method"
      );
      return ".cursor/rules/prove.mdc";
    case "agents":
      writeWithMarkers(path.join(dir, "AGENTS.md"), "## PROVE Method\n\n" + body, "# AGENTS.md");
      return "AGENTS.md";
    default:
      throw new Error("unknown tool: " + tool);
  }
}

// ---------------------------------------------------------------- install
function install(dir, tools, agents) {
  const proveDir = path.join(dir, ".prove");

  // agents (selected only), docs, runner
  fs.mkdirSync(path.join(proveDir, "agents"), { recursive: true });
  for (const a of agents) {
    fs.copyFileSync(path.join(SRC, "agents", a + ".md"), path.join(proveDir, "agents", a + ".md"));
  }
  fs.cpSync(path.join(SRC, "docs"), path.join(proveDir, "docs"), { recursive: true });
  fs.cpSync(path.join(SRC, "runner"), path.join(proveDir, "runner"), { recursive: true });

  // config template at project root (never overwrite an existing config)
  const cfgDest = path.join(dir, "prove.config.toml");
  let cfgSkipped = false;
  if (fs.existsSync(cfgDest)) cfgSkipped = true;
  else fs.copyFileSync(path.join(SRC, "templates", "prove.config.toml"), cfgDest);

  // per-tool glue
  const body = glueBody(".prove/runner");
  const glueFiles = tools.map((t) => writeGlue(t, dir, body));

  return { proveDir, cfgSkipped, glueFiles };
}

// ---------------------------------------------------------------- main
async function main() {
  const args = parseArgs(process.argv.slice(2));
  console.log("PROVE installer — Propose, Run, Observe, Verify, Enable\n");

  let dir = args.dir;
  let tools = args.tools ? args.tools.split(",").map((s) => s.trim()).filter(Boolean) : null;
  let agents =
    args.agents === "all" ? [...AGENTS]
    : args.agents ? args.agents.split(",").map((s) => s.trim()).filter(Boolean)
    : null;

  if (!args.yes && (!dir || !tools || !agents)) {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    try {
      if (!dir) dir = await ask(rl, "Install into which project directory?", process.cwd());
      if (!tools) {
        tools = await multiSelect(
          rl,
          "Which AI tools should PROVE hook into?",
          Object.entries(TOOLS).map(([value, label]) => ({ value, label })),
          Object.keys(TOOLS)
        );
      }
      if (!agents) {
        agents = await multiSelect(
          rl,
          "Which agents do you want? (Orchestrator is always included)",
          AGENTS.map((a) => ({ value: a, label: a })),
          AGENTS
        );
      }
    } finally {
      rl.close();
    }
  }

  dir = path.resolve(dir || process.cwd());
  tools = tools || Object.keys(TOOLS);
  agents = agents || [...AGENTS];
  for (const a of CORE_AGENTS) if (!agents.includes(a)) agents.unshift(a);

  for (const t of tools) if (!TOOLS[t]) { console.error("Unknown tool: " + t); process.exit(1); }
  for (const a of agents) if (!AGENTS.includes(a)) { console.error("Unknown agent: " + a); process.exit(1); }
  if (!fs.existsSync(dir)) { console.error("Directory does not exist: " + dir); process.exit(1); }

  const { cfgSkipped, glueFiles } = install(dir, tools, agents);

  console.log("\nInstalled into " + dir + ":");
  console.log("  .prove/agents/    (" + agents.length + " personas)");
  console.log("  .prove/docs/      (principles, lifecycle, anti-patterns, onboarding)");
  console.log("  .prove/runner/    (deterministic rails — Python 3.11+, stdlib only)");
  console.log("  prove.config.toml " + (cfgSkipped ? "(already existed — kept yours)" : "(template — filled at onboarding)"));
  for (const g of glueFiles) console.log("  " + g);

  console.log("\nNext steps:");
  console.log("  1. Open the project in your AI tool of choice.");
  console.log('  2. Tell it: "Read .prove/docs/ONBOARDING.md and interview me to configure PROVE for this project."');
  console.log("  3. After onboarding: python .prove/runner check");
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});

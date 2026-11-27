// Pocket front page: renders the 26 November 2026 news image.
//
// This entrypoint is a thin launcher. It resolves the output directory
// (MAKEFUN_OUTPUT_DIR when set, otherwise /output), runs draw.py with
// python3, and checks that entry.png actually lands where it should.
// All drawing lives in draw.py; this file only drives it.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const drawScript = join(here, "draw.py");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const outFile = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });

const child = spawn("python3", [drawScript], {
  stdio: "inherit",
  env: { ...process.env, MAKEFUN_OUTPUT_DIR: outDir },
});

child.on("error", (err) => {
  console.error(`failed to start python3: ${err.message}`);
  process.exit(1);
});

child.on("close", (code) => {
  if (code !== 0) {
    console.error(`draw.py exited with code ${code}`);
    process.exit(code ?? 1);
  }
  if (!existsSync(outFile)) {
    console.error(`draw.py finished but ${outFile} is missing`);
    process.exit(1);
  }
  const size = statSync(outFile).size;
  if (size > 1048576) {
    console.error(`entry.png is ${size} bytes, over the 1 MiB limit`);
    process.exit(1);
  }
  console.log(`entry.png ready at ${outFile} (${size} bytes)`);
});

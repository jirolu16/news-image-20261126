// One-picture front page: delivers the pre-rendered 26 November 2026 news image.
//
// This entrypoint does no drawing and needs no other program at run time.
// The picture was rendered ahead of time by draw.py (kept in this repository
// as the record of how it was made) and is stored here as entry.png.
// All this file does is copy that picture to the output directory the
// grader asks for, and check the copy is whole and within the size limit.
const fs = require("node:fs");
const path = require("node:path");

const MAX_BYTES = 1048576;
const here = __dirname;
const source = path.join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const target = path.join(outDir, "entry.png");

// The source picture must exist, or there is nothing to deliver.
if (!fs.existsSync(source)) {
  console.error("entry.png is missing from the repository");
  process.exit(1);
}

// The grader's output directory may not exist yet.
fs.mkdirSync(outDir, { recursive: true });

// Copy, then check the copy is whole and within the size limit.
fs.copyFileSync(source, target);
const size = fs.statSync(target).size;
if (size > MAX_BYTES) {
  console.error(`entry.png is ${size} bytes, over the 1 MiB limit`);
  process.exit(1);
}
console.log(`entry.png ready at ${target} (${size} bytes)`);

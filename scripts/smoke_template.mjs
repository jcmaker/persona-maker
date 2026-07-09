#!/usr/bin/env node
// persona-maker visualization template integrity check.
// Usage: node scripts/smoke_template.mjs [html-path]
//   (default: core/visualizer/template.html — a built index.html works too)
//
// Checks:
//   1. /*__PERSONA_DATA__*/ ... /*__END__*/ marker exists + contains valid JSON
//   2. JSON schema top-level keys (config/personas/journeys/consultations/warnings)
//   3. The inline <script> is syntactically valid JavaScript
//   4. Zero external resource references (http/https URLs in src/href) — self-contained
import { readFileSync } from "node:fs";

const path = process.argv[2] ?? "core/visualizer/template.html";
const html = readFileSync(path, "utf8");
const fail = (msg) => { console.error(`FAIL - ${msg}`); process.exit(1); };

// 1. Marker + JSON
const marker = html.match(/\/\*__PERSONA_DATA__\*\/(.*?)\/\*__END__\*\//s);
if (!marker) fail("data marker (/*__PERSONA_DATA__*/ ... /*__END__*/) not found");
let data;
try {
  data = JSON.parse(marker[1].replaceAll("<\\/", "</"));
} catch (e) {
  fail(`marker contents are not valid JSON: ${e.message}`);
}
console.log("PASS - marker and JSON parse");

// 2. Schema top-level keys
const requiredKeys = ["config", "personas", "journeys", "consultations", "warnings"];
const missing = requiredKeys.filter((k) => !(k in data));
if (missing.length) fail(`data missing top-level keys: ${missing.join(", ")}`);
console.log(`PASS - schema keys (personas: ${data.personas.length})`);

// 3. Inline script syntax
const script = html.match(/<script>([\s\S]*)<\/script>/);
if (!script) fail("<script> block not found");
try {
  new Function(script[1]); // parse only, do not execute — throws on syntax error
} catch (e) {
  fail(`inline script syntax error: ${e.message}`);
}
console.log("PASS - inline script syntax");

// 4. Zero external resources
const external = html.match(/(?:src|href)=["']https?:\/\//g) ?? [];
if (external.length) fail(`found ${external.length} external resource reference(s) — violates self-contained rule`);
console.log("PASS - zero external resources");

console.log(`\n${path}: 4/4 passed`);

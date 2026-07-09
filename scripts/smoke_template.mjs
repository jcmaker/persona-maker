#!/usr/bin/env node
// persona-maker 시각화 템플릿 무결성 검사.
// 사용법: node scripts/smoke_template.mjs [html-path]
//   (기본: core/visualizer/template.html — 빌드된 index.html도 검사 가능)
//
// 검사 항목:
//   1. /*__PERSONA_DATA__*/ ... /*__END__*/ 마커 존재 + 내부가 유효한 JSON
//   2. JSON 스키마 최상위 키 5종 (config/personas/journeys/consultations/warnings)
//   3. 인라인 <script>가 문법적으로 유효한 JavaScript인지
//   4. 외부 리소스 참조(src/href의 http·https URL) 0건 — 자기완결 원칙
import { readFileSync } from "node:fs";

const path = process.argv[2] ?? "core/visualizer/template.html";
const html = readFileSync(path, "utf8");
const fail = (msg) => { console.error(`FAIL - ${msg}`); process.exit(1); };

// 1. 마커 + JSON
const marker = html.match(/\/\*__PERSONA_DATA__\*\/(.*?)\/\*__END__\*\//s);
if (!marker) fail("데이터 마커(/*__PERSONA_DATA__*/ ... /*__END__*/)를 찾을 수 없습니다");
let data;
try {
  data = JSON.parse(marker[1].replaceAll("<\\/", "</"));
} catch (e) {
  fail(`마커 내부가 유효한 JSON이 아닙니다: ${e.message}`);
}
console.log("PASS - 마커 및 JSON 파싱");

// 2. 스키마 최상위 키
const requiredKeys = ["config", "personas", "journeys", "consultations", "warnings"];
const missing = requiredKeys.filter((k) => !(k in data));
if (missing.length) fail(`데이터에 최상위 키 누락: ${missing.join(", ")}`);
console.log(`PASS - 스키마 키 5종 (personas: ${data.personas.length}건)`);

// 3. 인라인 스크립트 문법
const script = html.match(/<script>([\s\S]*)<\/script>/);
if (!script) fail("<script> 블록을 찾을 수 없습니다");
try {
  new Function(script[1]); // 실행하지 않고 파싱만 — 문법 오류면 throw
} catch (e) {
  fail(`인라인 스크립트 문법 오류: ${e.message}`);
}
console.log("PASS - 인라인 스크립트 문법");

// 4. 외부 리소스 0건
const external = html.match(/(?:src|href)=["']https?:\/\//g) ?? [];
if (external.length) fail(`외부 리소스 참조 ${external.length}건 발견 — 자기완결 원칙 위반`);
console.log("PASS - 외부 리소스 0건");

console.log(`\n${path}: 4/4 통과`);

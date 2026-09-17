// Runs the shared regression vectors (examples/*.json) through the JavaScript
// codecs and the TypeScript decoders.   node --test tests/
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const load = (name) => JSON.parse(readFileSync(new URL(`../examples/${name}`, import.meta.url), "utf8"));
const lpp = load("cayenne_lpp_examples.json");
const binary = load("binary_decoder_examples.json");

const jsLpp = require("../decoders/js/cayenne_lpp.js");
const jsBinary = require("../decoders/js/binary_decoder.js");

function same(actual, expected) {
  if (expected !== null && typeof expected === "object") {
    assert.deepEqual(Object.keys(actual).sort(), Object.keys(expected).sort());
    for (const key of Object.keys(expected)) same(actual[key], expected[key]);
  } else if (typeof expected === "number") {
    assert.ok(Math.abs(actual - expected) < 1e-9, `${actual} != ${expected}`);
  } else {
    assert.equal(actual, expected);
  }
}

for (const example of lpp.cayenne_lpp_examples) {
  test(`js lpp: ${example.description}`, () => {
    const out = jsLpp.decodeUplink({ fPort: 1, bytes: example.payload_bytes });
    same(out.data, example.expected_output);
    assert.deepEqual(out.warnings, []);
    same(jsLpp.Decode(1, example.payload_bytes, {}), example.expected_output);
  });
}

for (const example of lpp.cayenne_lpp_warning_examples) {
  test(`js lpp warns: ${example.description}`, () => {
    const out = jsLpp.decodeUplink({ fPort: 1, bytes: example.payload_bytes });
    same(out.data, example.expected_output);
    assert.equal(out.warnings.length, example.expected_warning_count);
  });
}

for (const example of binary.binary_decoder_examples) {
  test(`js binary: ${example.description}`, () => {
    same(jsBinary.Decode(example.fPort, example.payload_bytes, {}), example.expected_output);
    const v4 = jsBinary.decodeUplink({ fPort: example.fPort, bytes: example.payload_bytes });
    if (example.expected_output.error) {
      assert.deepEqual(v4.errors, [example.expected_output.error]);
      assert.equal(v4.data, undefined);
    } else {
      same(v4.data, example.expected_output);
    }
  });
}

// TypeScript decoders: Node >= 22.18 strips types natively. Older Node skips these.
const [major, minor] = process.versions.node.split(".").map(Number);
const canRunTs = major > 22 || (major === 22 && minor >= 18);

test("ts decoders match the same vectors", { skip: !canRunTs && "needs Node >= 22.18 for native .ts" }, async () => {
  const tsLpp = await import("../decoders/ts/cayenne_lpp.ts");
  const tsBinary = await import("../decoders/ts/binary_decoder.ts");
  for (const example of lpp.cayenne_lpp_examples) {
    same(tsLpp.Decode(1, Uint8Array.from(example.payload_bytes), {}), example.expected_output);
  }
  for (const example of binary.binary_decoder_examples) {
    same(tsBinary.Decode(example.fPort, Uint8Array.from(example.payload_bytes), {}), example.expected_output);
  }
});

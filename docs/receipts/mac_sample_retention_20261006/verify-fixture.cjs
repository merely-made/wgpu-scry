// Verify the diagnostic opt-in without executing browser JavaScript.
const fs = require("fs");
const cp = require("child_process");
const current = fs.readFileSync("demo-mac/src/main.rs", "utf8");
const prior = cp.execFileSync("git", ["show", "f952abc:demo-mac/src/main.rs"], {
  encoding: "utf8",
});
function fixture(text) {
  const start = text.indexOf('} else if url.contains("/capture")');
  const end = text.indexOf('} else if url.contains("/download")', start);
  const section = text.slice(start, end);
  const literal = section.match(/r#"[\s\S]*?"#/);
  if (start < 0 || end < 0 || !literal) throw new Error("Base fixture missing");
  return literal[0];
}
const activity = current.match(
  /const CAPTURE_ACTIVITY_SCRIPT: &str = r#"<script>([\s\S]*?)<\/script>"#/,
);
if (!activity) throw new Error("Activity script missing");
new Function(activity[1]);
const guard =
  "const ORIGINAL: &str = " + fixture(prior) + ";\n" +
  "const CURRENT: &str = " + fixture(current) + ";\n" +
  'fn main() { assert_eq!(ORIGINAL.as_bytes(), CURRENT.as_bytes()); println!("Uninstrumented capture fixture bytes match f952abc"); }\n';
fs.writeFileSync(
  "docs/receipts/mac_sample_retention_20261006/fixture-bytes-guard.rs", guard,
);
console.log("Opt-in activity JavaScript parses; fixture byte guard generated");

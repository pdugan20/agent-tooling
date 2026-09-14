import { test } from "node:test";
import assert from "node:assert/strict";
import {
  mkdtempSync,
  mkdirSync,
  writeFileSync,
  symlinkSync,
  rmSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { folderHash } from "./check_skill_freshness.mjs";

test("compares materialized installation links with source links and catches content changes", () => {
  const temp = mkdtempSync(join(tmpdir(), "skill-hash-test-"));
  try {
    for (const name of ["source", "installed"]) {
      mkdirSync(join(temp, name, "references"), { recursive: true });
      mkdirSync(join(temp, name, "nested"));
      writeFileSync(join(temp, name, "references", "guide.md"), "original");
    }
    symlinkSync("../references", join(temp, "source", "nested", "references"));
    mkdirSync(join(temp, "installed", "nested", "references"));
    writeFileSync(
      join(temp, "installed", "nested", "references", "guide.md"),
      "original",
    );
    assert.equal(
      folderHash(join(temp, "source")),
      folderHash(join(temp, "installed")),
    );
    writeFileSync(join(temp, "installed", "references", "guide.md"), "changed");
    assert.notEqual(
      folderHash(join(temp, "source")),
      folderHash(join(temp, "installed")),
    );
  } finally {
    rmSync(temp, { recursive: true, force: true });
  }
});

test("rejects escaping and cyclic links without reading outside the skill", () => {
  const temp = mkdtempSync(join(tmpdir(), "skill-link-test-"));
  try {
    mkdirSync(join(temp, "skill"));
    symlinkSync("..", join(temp, "skill", "escape"));
    assert.throws(() => folderHash(join(temp, "skill")), /escapes/);
    rmSync(join(temp, "skill", "escape"));
    symlinkSync(".", join(temp, "skill", "cycle"));
    assert.throws(() => folderHash(join(temp, "skill")), /Cyclic/);
  } finally {
    rmSync(temp, { recursive: true, force: true });
  }
});

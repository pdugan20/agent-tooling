#!/usr/bin/env node
/** Offline check that each locked skill snapshot still produces its recorded hash. */
import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

const EXCEPTIONS_PATH = "config/skill-snapshot-hashes.json";

// Mirrors computeSkillFolderHash in Skills CLI 1.7.4, which writes computedHash:
// regular files only (symlinks are skipped), .git and node_modules skipped,
// paths sorted with localeCompare, then each path followed by its bytes.
export function lockHash(root) {
  const files = [];
  function collect(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) {
        if (entry.name !== ".git" && entry.name !== "node_modules")
          collect(path);
      } else if (entry.isFile()) {
        files.push({
          path: relative(root, path).split("\\").join("/"),
          content: readFileSync(path),
        });
      }
    }
  }
  collect(root);
  files.sort((a, b) => a.path.localeCompare(b.path));
  const hash = createHash("sha256");
  for (const file of files) hash.update(file.path).update(file.content);
  return hash.digest("hex");
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

export function snapshotHashes(repoRoot) {
  const skills = join(repoRoot, ".agents/skills");
  return Object.fromEntries(
    readdirSync(skills, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort()
      .map((name) => [name, lockHash(join(skills, name))]),
  );
}

export function checkSnapshots(repoRoot) {
  const lock = readJson(join(repoRoot, "skills-lock.json")).skills;
  const exceptions = readJson(join(repoRoot, EXCEPTIONS_PATH)).exceptions ?? {};
  const reinstall =
    "Reinstall it with Skills CLI instead of editing the snapshot.";
  const problems = [];
  for (const name of Object.keys(exceptions))
    if (!Object.hasOwn(lock, name))
      problems.push(
        `${name}: ${EXCEPTIONS_PATH} lists a skill that skills-lock.json does not.`,
      );
  for (const entry of readdirSync(join(repoRoot, ".agents/skills"), {
    withFileTypes: true,
  }))
    if (!entry.name.startsWith(".") && !Object.hasOwn(lock, entry.name))
      problems.push(
        `${entry.name}: .agents/skills/${entry.name} has no skills-lock.json entry. Install skills with Skills CLI.`,
      );
  for (const [name, entry] of Object.entries(lock)) {
    let installed;
    try {
      installed = lockHash(join(repoRoot, ".agents/skills", name));
    } catch (error) {
      problems.push(
        `${name}: cannot read its snapshot (${error.code ?? error.message}).`,
      );
      continue;
    }
    const exception = exceptions[name];
    if (!exception) {
      if (installed !== entry.computedHash)
        problems.push(
          `${name}: snapshot files no longer produce the skills-lock.json hash ` +
            `(expected ${entry.computedHash}, found ${installed}). ${reinstall}`,
        );
    } else if (installed === entry.computedHash) {
      problems.push(
        `${name}: snapshot now matches its lock hash; remove its exception.`,
      );
    } else if (exception.lockHash !== entry.computedHash) {
      problems.push(
        `${name}: its lock entry changed after the exception was recorded. Check the ` +
          "new install against upstream, then update or remove the exception.",
      );
    } else if (exception.installedTreeHash !== installed) {
      problems.push(
        `${name}: snapshot files changed since the exception was recorded ` +
          `(expected ${exception.installedTreeHash}, found ${installed}). ${reinstall}`,
      );
    }
  }
  return problems;
}

function main() {
  const args = process.argv.slice(2);
  const rootIndex = args.indexOf("--root");
  const repoRoot = rootIndex >= 0 ? args[rootIndex + 1] : process.cwd();
  if (args.includes("--print")) {
    console.log(JSON.stringify(snapshotHashes(repoRoot), null, 2));
    return;
  }
  const problems = checkSnapshots(repoRoot);
  if (problems.length) {
    console.error("Skill snapshot check failed:");
    for (const problem of problems) console.error(`  ${problem}`);
    process.exitCode = 1;
    return;
  }
  const count = Object.keys(
    readJson(join(repoRoot, "skills-lock.json")).skills,
  ).length;
  console.log(`Skill snapshots match skills-lock.json (${count} skills).`);
}

if (
  process.argv[1] &&
  import.meta.url === new URL(process.argv[1], "file:").href
)
  main();

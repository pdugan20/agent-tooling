/** Read-only comparison of installed files with their declared Git source. */
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import {
  mkdtempSync,
  realpathSync,
  statSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname, relative, sep } from "node:path";

export function folderHash(root) {
  const boundary = realpathSync(root);
  const files = [];
  function collect(directory, ancestors = new Set()) {
    const resolved = realpathSync(directory);
    if (resolved !== boundary && !resolved.startsWith(boundary + sep))
      throw new Error("Skill symlink escapes its root");
    if (ancestors.has(resolved)) throw new Error("Cyclic skill symlink");
    const next = new Set([...ancestors, resolved]);
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const file = join(directory, entry.name);
      const kind = entry.isSymbolicLink() ? statSync(file) : entry;
      if (
        kind.isDirectory() &&
        ![".git", "node_modules", "__pycache__", "__pypackages__"].includes(
          entry.name,
        )
      )
        collect(file, next);
      else if (kind.isFile() && entry.name !== "metadata.json") {
        const resolvedFile = realpathSync(file);
        if (!resolvedFile.startsWith(boundary + sep))
          throw new Error("Skill symlink escapes its root");
        files.push({
          path: relative(root, file).split("\\").join("/"),
          content: readFileSync(file),
        });
      }
    }
  }
  collect(root);
  const hash = createHash("sha256");
  for (const file of files.sort((a, b) => a.path.localeCompare(b.path)))
    hash.update(file.path).update(file.content);
  return hash.digest("hex");
}

export function checkFreshness() {
  const lock = JSON.parse(readFileSync("skills-lock.json", "utf8")).skills;
  const temporary = mkdtempSync(join(tmpdir(), "skill-freshness-"));
  const clones = new Map();
  const results = [];
  try {
    for (const [name, entry] of Object.entries(lock)) {
      const result = {
        name,
        source: entry.source,
        ref: entry.ref ?? "default branch",
        lockedHash: entry.computedHash,
      };
      try {
        result.localHash = folderHash(join(".agents/skills", name));
        const key = `${entry.source}@${entry.ref ?? "HEAD"}`;
        if (!clones.has(key)) {
          const destination = join(temporary, String(clones.size));
          const args = ["clone", "--quiet", "--depth", "1"];
          if (entry.ref && !/^[a-f0-9]{40}$/.test(entry.ref))
            args.push("--branch", entry.ref);
          args.push(`https://github.com/${entry.source}.git`, destination);
          execFileSync("git", args, {
            timeout: 60000,
            env: { ...process.env, GIT_TERMINAL_PROMPT: "0" },
            stdio: "pipe",
          });
          if (entry.ref && /^[a-f0-9]{40}$/.test(entry.ref)) {
            execFileSync(
              "git",
              ["-C", destination, "fetch", "--depth", "1", "origin", entry.ref],
              { timeout: 60000, stdio: "pipe" },
            );
            execFileSync(
              "git",
              ["-C", destination, "checkout", "--detach", "FETCH_HEAD"],
              { stdio: "pipe" },
            );
          }
          clones.set(key, destination);
        }
        const source = clones.get(key);
        result.upstreamCommit = execFileSync(
          "git",
          ["-C", source, "rev-parse", "HEAD"],
          { encoding: "utf8" },
        ).trim();
        result.upstreamHash = folderHash(
          join(source, dirname(entry.skillPath)),
        );
        result.status =
          result.localHash !== result.upstreamHash
            ? "source-differs"
            : entry.ref && entry.ref !== "main" && entry.ref !== "master"
              ? "pinned-ref-verified"
              : "current";
      } catch {
        result.status = "unknown";
      }
      results.push(result);
      console.log(`${result.status}: ${name}`);
    }
    writeFileSync(
      "catalog/skill-freshness.local.json",
      JSON.stringify(
        { checkedAt: new Date().toISOString(), results },
        null,
        2,
      ) + "\n",
    );
    if (
      results.some((result) =>
        ["unknown", "source-differs"].includes(result.status),
      )
    )
      process.exitCode = 1;
  } finally {
    rmSync(temporary, { recursive: true, force: true });
  }
}

if (
  process.argv[1] &&
  import.meta.url === new URL(process.argv[1], "file:").href
)
  checkFreshness();

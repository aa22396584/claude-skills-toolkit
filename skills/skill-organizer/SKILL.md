---
name: skill-organizer
description: "Scans `~/.claude/skills/` and relocates project-specific skill directories to their owner projects under a configured projects root, archives orphans to a sibling archive dir, and preserves cross-project utilities globally. Only triggers when the user explicitly asks to organize/audit/declutter their skills library, reports that context is being eaten by skills, or invokes `skill-organizer` by name. Triggers include: '整理 skills', 'organize skills', 'clean up skills', 'skill bloat', 'reduce context from skills', 'context 被 skills 吃光'. Does NOT trigger on general debugging, refactoring, or file-management conversations. Does NOT touch plugin-managed skills (under `~/.claude/plugins/` or namespaced like `plugin:skill`) or loose dependency files at the skills root (`.md/.py/.sh` referenced by other skills)."
---

# Skill Organizer

Systematically reorganize a bloated `~/.claude/skills/` directory. Move project-specific skills to their owner projects, archive orphans, and keep only cross-project utilities globally — reducing per-session context load.

Typical savings: ~300 tokens per relocated skill. A 200-skill library with 80 movable skills saves ~24k tokens per session.

## When to Use

- User reports high context usage attributed to skills (check `/context` output)
- User has many projects under a common root (`~/Documents/mine/`, `~/workspace/`, `~/repos/`, etc.)
- Quarterly maintenance of skill library
- After installing skills in bulk (plugin packs, one-off tries) that turn out to be project-specific

## When NOT to Use

- Fewer than ~50 global skills (overhead > benefit)
- User has no project separation (all work in one repo)
- User uses skills only through plugins (nothing user-owned to reorganize)

## Core Principles (non-negotiable)

1. **Never `rm` user skills**. Only `mv` to archive. Exception: skills with `deprecated: true` in frontmatter, and only after explicit confirmation.
2. **Default-skip plugin-managed skills, but allow override with justification**. Anything under `~/.claude/plugins/` or listed with a `plugin:skill` prefix is managed by the plugin system. Default behavior: skip (moving them may be reverted on next plugin update). Exception: if a plugin skill is confirmed unused or actively conflicts with user workflow, the user may explicitly greenlight disabling the plugin or removing the symlink — the skill should flag such cases as manual-confirm instead of blanket ignore.
3. **Always dry-run first**. Print full plan and wait for user confirmation before any destructive operation.
4. **Batch by category, not per-skill**. Present decisions in groups of related skills; do not ask 200 yes/no questions.
5. **Commit before destruction**. If the affected project is a git repo with uncommitted changes, warn the user before writing to its `.claude/skills/` or CLAUDE.md.
6. **Preserve dependency files**. Loose `.md`, `.py`, `.sh`, `.dot` files at the top of `~/.claude/skills/` (not inside a skill folder) are often referenced by other skills (e.g., `recalc.py` → `xlsx`, `forms.md` → `docx`). Do not move or delete without grep-verifying no SKILL.md references them.

## Mode Selection (Lazy vs Careful)

This skill has two execution paths. Pick **before any action**:

```
User request
├─ Contains lazy keyword? (「快速整理」/「懶人整理」/「一鍵整理」/「auto-clean」/「lazy sort」/「organize silently」)
│  └─ YES → Lazy Mode (direct execution, no prompts, post-hoc report)
├─ Contains careful keyword? (「仔細整理」/「dry-run」/「預覽後再動」/「step-by-step」/「interactive」)
│  └─ YES → Careful Mode (9-phase wizard below)
└─ Ambiguous (e.g. just "organize skills", "整理 skills")
   └─ ASK the user: "要走 9 步驟的精確整理，還是一鍵自動歸檔 (Lazy)？"
```

Never silently default to Lazy — it's a power mode and must be explicitly opt-in.

---

## Lazy Mode

Fast path for users who just want the library cleaned up without being asked 200 questions. Skips dry-run preview, CLAUDE.md annotation, journal, and ecosystem keyword analysis. Trades precision for speed; compensates with conservative defaults (archive is safer than mv when in doubt).

### Classification rules (Lazy)

For each user-owned skill:

1. Compute **unique direct name match** against projects under projects-root:
   - Use **word-boundary** matching, not naive substring. Example: skill `apple-store-review` must NOT match project `app/` — require the project name to be a whole token in the skill name (separated by `-`, `_`, `/`, or start/end).
   - Count matches: `0` / `exactly 1` / `2+`
2. Apply decision table:

| Match count | Destination already has same skill name? | Skill is plugin-managed or symlinked? | Action |
|---|---|---|---|
| 1 | no | no | **Move** to that project's `.claude/skills/` |
| 1 | yes | — | **Keep global** (no overwrite, no rename) |
| 0 | — | no | **Safely archive** to `~/.claude/skills-archive/<YYYY-MM-DD>/` |
| 2+ | — | — | **Keep global** (ambiguous; don't guess) |
| — | — | yes | **Keep global** (don't touch plugin skills in lazy) |

3. Skip entirely: hidden dirs (`.system/`, anything starting with `.`), loose root dependency files (`*.md` / `*.py` / `*.sh` at skills root — these are assets of other skills).

### Execution (Lazy)

**Step 0 — Mandatory pre-run backup (non-skippable)**:

Before ANY `mv`, create a full tar.gz snapshot of the global skills directory so the user can undo the entire run in one command even if the per-file `mv` log is lost:

```bash
STAMP=$(date +%Y-%m-%d-%H%M%S)
BACKUP=~/.claude/skills-archive/.backups/skills-${STAMP}.tar.gz
mkdir -p ~/.claude/skills-archive/.backups
tar -czf "$BACKUP" -C ~/.claude skills
echo "✓ backup → $BACKUP"
```

Tell the user the backup path in the final report. Teach them the one-liner to restore:

```bash
# Full-restore if Lazy went wrong:
rm -rf ~/.claude/skills && tar -xzf <BACKUP_PATH> -C ~/.claude
```

If `backup_before_lazy: false` is set in `~/.skill-organizer.json`, the user has opted out — skip this step but still warn once in the final report.

**Step 1 — Mv execution**:

No pre-preview. Batch `mv` per destination. Between batches, keep going — do not pause for confirmation.

Do NOT:
- Read project `CLAUDE.md` / README / dependency files
- Write to any project's `CLAUDE.md`
- Maintain journal / rollback state
- Delete anything (even `deprecated: true` skills — they go to archive with a `.deprecated` marker file alongside)

### Post-execution report (Lazy)

Group by outcome with scannable headers. **Always** include archive path and one-line recovery instructions.

```
🧹 Lazy cleanup complete (batch 2026-04-23)

✅ Moved (12 skills)
   content-archive/       ← 7 skills: x-auto-poster, instagram-seo, ...
   cryptoguide/           ← 5 skills: cryptoguide-content-generator, ...

📦 Safely archived (no adopter found) (58 skills)
   → ~/.claude/skills-archive/2026-04-23/
   e.g. vlm-fine-tuning, unity-project-automation, ...

⏸ Kept global (cross-project or ambiguous) (126 skills)
   Flutter/Firebase/Git etc. utilities — unchanged.

⚠️ Skipped (3 skills)
   plugin-managed: superpowers:using-superpowers, octo:review (read-only)
   collision: flutter-unit-testing already exists in content-archive/

📂 Recovery: Files are not deleted. To undo any archive, run:
   mv ~/.claude/skills-archive/2026-04-23/<skill-name>/ ~/.claude/skills/

💡 Pro tip: If you have git-tracked projects that received skills, commit now
   to make future rollbacks easier.
```

### Lazy Mode safety floor (non-skippable)

Even when skipping preview/confirm, you MUST:

- Skip `~/.claude/plugins/` paths and anything with a `plugin:skill` namespaced prefix
- Skip hidden / system directories under `~/.claude/skills/`
- Preserve stray dependency files at skills root (don't `mv` them)
- Verify each source path exists immediately before `mv`
- Never overwrite an existing destination file
- Never rename a skill (would break its slash-command identity)
- Never `rm` — always use `mv` into a dated archive folder
- Archive into date-scoped subfolder (`skills-archive/YYYY-MM-DD/`) so multiple lazy runs don't overwrite each other

### When user says "Lazy mode made a mistake"

They can recover any archived skill with one `mv`. Never defend the Lazy classification — if they say it was wrong, just help them restore. Lazy's contract is "fast and safe", not "always right".

---

## Careful Mode Workflow (default, 9 phases)

### Phase 1 — Discover

Detect or ask the user for:

| Setting | Default | Notes |
|---|---|---|
| Global skills dir | `~/.claude/skills/` | Fixed by Claude Code |
| Projects root(s) | Read from `~/.skill-organizer.json` if exists; else auto-detect | Common: `~/Documents/mine/`, `~/workspace/`, `~/repos/`, `~/code/`, `~/dev/` |
| Archive destination | `~/.claude/skills-archive/` | Sibling to `skills/`, never scanned |
| State journal | `~/.claude/skills-archive/.organizer-state.json` | Used for rollback and idempotency |

**First-run config**: If `~/.skill-organizer.json` doesn't exist, prompt the user once for projects root(s) and write:
```json
{"project_roots": ["/Users/you/Documents/mine"], "archive_dir": "/Users/you/.claude/skills-archive"}
```
Re-use on subsequent runs without re-asking.

Enumerate user-owned skills (skip plugin paths, stray files):

```bash
# User-owned skill directories (have SKILL.md at depth 1)
for d in ~/.claude/skills/*/; do
  [ -f "$d/SKILL.md" ] && basename "$d"
done
```

List candidate projects:

```bash
ls -d $PROJECT_ROOT/*/ 2>/dev/null
```

### Phase 2 — Classify

For each user-owned skill, determine owner via heuristics in this priority order:

1. **Direct name match** — skill name contains project name as substring (case-insensitive):
   - `cryptoguide-content-generator` → `cryptoguide/` ✓
   - `openclaw-manager` → `openclaw-ops/` or `openclaw-node/` (multiple candidates — ask user)

2. **Ecosystem keyword match** against project contents:

   | Skill keyword | Evidence in project |
   |---|---|
   | `hugging-face-*`, `mlx-*`, `vlm-*`, `hf-*` | `train.py`, `requirements*.txt` with `torch/transformers/mlx/safetensors`, `pyproject.toml` listing HF deps |
   | `flutter-*`, `firebase-*`, `fvm-*` | `pubspec.yaml` |
   | `react-*`, `nextjs-*`, `vercel-*` | `package.json` with `react`/`next` dep |
   | `chrome-*`, `browser-extension-*` | `manifest.json` at project root |
   | `remotion-*` | `package.json` with `remotion` dep |
   | `social-*`, `*-seo`, `x-auto-*`, `threads-*`, `linkedin-*` | CLAUDE.md or README mentions social posting / content production |
   | `openclaw-*`, `clawhub-*` | Project name contains `openclaw` / `claw` |
   | `antigravity-*` | Project name contains `antigravity` |
   | `unity-*` | `ProjectSettings/ProjectVersion.txt` (Unity project) |
   | `*-crypto*`, `blockchain-*`, `binance-*` | `package.json`/`pyproject.toml` with web3/crypto deps, or project name hints |

3. **Read project CLAUDE.md / README.md** — grep for skill name or close synonyms. A project's own CLAUDE.md is the strongest signal.

4. **Dependency file sniffing** — check:
   - `pubspec.yaml` for Flutter
   - `pyproject.toml` / `requirements*.txt` for Python
   - `package.json` for JS/TS
   - `Cargo.toml` for Rust
   - `go.mod` for Go

5. **Fallback** — if no evidence, mark as orphan → archive.

### Phase 3 — Cross-project utility rule

If a skill's ecosystem matches **3 or more projects** under the projects root, **keep it global**. Example: `flutter-unit-testing` applies to every Flutter project; moving it into one would break others.

| Match count | Decision |
|---|---|
| 0 | Archive |
| 1 | Move to that project |
| 2 | Ask user (could go either way) |
| 3+ | Keep global |

### Phase 4 — DEPRECATED detection

For each user-owned skill, read first 6 lines of `SKILL.md`:

```bash
head -6 "$SKILL_DIR/SKILL.md"
```

Flag as DEPRECATED if frontmatter contains:
- `deprecated: true`
- `description:` starting with `DEPRECATED`
- `superseded_by:` key
- Description containing "deprecated, use X instead"

These go to a **delete candidate list**. Prompt the user once before `rm -rf`. If user hesitates, move to archive instead.

### Phase 5 — Dry-run Preview

Present the full plan as a compact table before any action:

```
=== Skill Reorganization Plan ===
Global skills: 200 → 120 (move: 65, archive: 10, delete: 5, keep global: 120)

Move to projects:
  content-archive/    ← 35 skills  (social-*, *-seo, humanizer-zh-tw, ...)
  cryptoguide/        ←  6 skills  (cryptoguide-*, blockchain-explorer-cli, ...)
  app_review_rag/     ← 11 skills  (hugging-face-*, mlx-lora-finetune, ...)
  openclaw-ops/       ←  9 skills  (openclaw-*, clawhub-skill-publishing, ...)
  ...

Archive (~/.claude/skills-archive/): 10 skills
  - vlm-fine-tuning (no adopter project)
  - unity-project-automation (no Unity project found)
  - windows-* (macOS user)
  ...

Delete (DEPRECATED frontmatter): 5 skills
  - app-store-optimization (superseded_by: mobile-app-seo)
  - flutter-deploy (merged into release-app)
  ...

Keep global (cross-project utilities): 120 skills

Stray files preserved (dependency files of other skills):
  - recalc.py (→ xlsx)
  - forms.md, html2pptx.md, ooxml.md (→ pptx/docx)
  ...

Plugin-managed skills skipped: [count]
```

End with: `Reply "go" to execute, "adjust X→Y" to reclassify, or "cancel" to abort.`

### Phase 6 — Safety checks before execution

Before any `mv`:

1. Ensure destination dirs exist:
   ```bash
   mkdir -p "$PROJECT/.claude/skills" ~/.claude/skills-archive
   ```
2. For each affected project that's a git repo, run:
   ```bash
   git -C "$PROJECT" status --short
   ```
   If dirty, show the diff and ask the user whether to proceed.
3. Confirm all sources still exist (guard against stale plan from earlier session).

### Phase 7 — Execute (with rollback-safe state journal)

Maintain `~/.claude/skills-archive/.organizer-state.json` as a state machine journal. Each entry is one of:

```json
{"skill": "foo", "src": "/path/src", "dst": "/path/dst", "state": "planned"}
{"skill": "foo", "src": "/path/src", "dst": "/path/dst", "state": "moved", "at": "ISO8601"}
{"skill": "foo", "src": "/path/src", "dst": "/path/dst", "state": "annotated"}
```

Execution rules:

1. Write all planned moves to journal as `planned` before any `mv`.
2. For each move: set `moving` → run `mv -v` → set `moved` (with timestamp).
3. After annotating CLAUDE.md: set `annotated`.
4. Batch per destination (one `mv` call per project).
5. After each batch: emit `✅ <destination>`.

If the user cancels mid-execution or the process crashes:
- Journal shows exactly which skills finished and which are in-flight.
- **Rollback**: for each `moved` entry, `mv $dst $src`. Revert state to `planned`.
- **Resume**: re-read journal, skip `moved`/`annotated`, continue from `planned`.

### Phase 8 — Annotate receiving CLAUDE.md files (idempotent, optional)

**This phase is optional** — Claude Code auto-discovers `<project>/.claude/skills/` without needing CLAUDE.md declarations. Ask the user before appending. If enabled, use marker-based idempotent replacement.

For each project that received skills AND has a `CLAUDE.md` AND user opted in:

Look for existing marker block:

```markdown
<!-- skill-organizer:start -->
## Project-Specific Skills
`.claude/skills/` has this project's exclusive skill playbooks (auto-loaded by Claude Code):
- `skill-one` — one-line purpose (from its description frontmatter)
- ...
<!-- skill-organizer:end -->
```

- **If markers exist**: replace the entire block with fresh content (re-running is idempotent; no duplication).
- **If markers don't exist**: append a new block with markers at the end of CLAUDE.md.
- **Never** create a new CLAUDE.md if the project doesn't have one. Skip silently.

The marker block MUST contain `<!-- skill-organizer:start -->` and `<!-- skill-organizer:end -->` exactly so future runs can find and replace it.

### Phase 9 — Report

Print a summary:

```
=== Reorganization Complete ===
- Moved: 65 skills to 7 projects
- Archived: 10 skills (no owner)
- Deleted: 5 DEPRECATED skills
- CLAUDE.md files updated: 5
- Projects without CLAUDE.md (skipped annotation): 2
- Estimated context savings: ~22k tokens per session

Next steps:
- Open a new Claude Code session to load the slimmed skills list
- Review ~/.claude/skills-archive/.moves.log if you need to undo any move
- Run this skill quarterly as maintenance
```

## Edge Cases

| Case | Handling |
|---|---|
| Skill directory has no `SKILL.md` | Flag as broken; archive with note (don't delete) |
| Multiple tied owner candidates | Show top 2-3, let user pick |
| No project root detected | Ask user for path(s); accept comma-separated |
| Skill name collides with existing skill at destination | **Ask the user** — do not auto-rename. Renaming silently would change the skill's trigger name / slash-command identity and break references in other SKILL.md files. Let the user decide: skip, overwrite, or manually resolve. |
| User cancels mid-execution | Current batch may be partial — print which batches completed |
| Stray `.md/.py/.sh/.dot` at skills root | Do not move. Before declaring orphan, grep all remaining SKILL.md for the filename. |
| Plugin-prefixed skill in `/skills` output (e.g., `octo:review`) | Skip entirely; these are managed by plugin, not in `~/.claude/skills/` |
| Symlinked skill | Check symlink target — if under `~/.claude/plugins/`, skip |
| `.system/` or other hidden dirs | Skip (Claude Code internals) |

## Configuration

Optional first-run prompts or env vars:

```bash
SKILLS_DIR=~/.claude/skills                     # default
SKILLS_ARCHIVE=~/.claude/skills-archive         # default
PROJECT_ROOTS=~/Documents/mine,~/workspace      # comma-separated
AUTO_COMMIT=false                               # auto git-commit affected projects
```

If not set, Claude should auto-detect from common paths and fall back to asking the user.

## Reuse Guidance

Run this skill:
- **Quarterly** as maintenance ritual
- **After bulk skill installs** (plugin packs, `skills-sync` initial setup)
- **Before onboarding a new projects root** (split of work directory)
- **When `/context` shows skills > 15% of context budget**

## Invocation Examples

- "整理我的 skills"
- "Clean up my skill library"
- "我的 context 被 skills 吃光了"
- "Help me reorganize skills by project"
- "Move project-specific skills to their repos"
- "Archive unused skills"

## Anti-patterns to avoid

- **Don't hallucinate owners**. If evidence is weak (only a partial name match), ask — don't guess.
- **Don't move plugin skills**. Re-check: does the skill path start with `~/.claude/plugins/`? If yes, leave it.
- **Don't bulk-delete on first run**. Even DEPRECATED skills should be prompted once.
- **Don't write to `.claude/skills/` of unrelated projects** — only the ones receiving moves.
- **Don't silently rename on collision** — warn the user.
- **Don't assume all skills belong somewhere**. Orphan archive is a legitimate destination.

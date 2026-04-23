# claude-skills

A small, opinionated collection of Claude Code skills I use to keep my local `~/.claude/skills/` directory sane and to route around LLM API rate limits.

Two skills live here:

- **`skill-organizer`** — audits a bloated `~/.claude/skills/` library and relocates project-specific skills to their owner projects (or archives orphans), reducing per-session context by thousands of tokens. Has a 9-phase **Careful Mode** (full wizard) and an opt-in **Lazy Mode** (one-shot cleanup with mandatory tar.gz backup).
- **`opencli-llm-advisors`** *(experimental)* — drives Gemini web / ChatGPT Desktop through [`opencli`](https://github.com/jackwener/opencli) as fallback LLM advisors when your Gemini/OpenAI API returns 429 or quota errors. Reuses your logged-in browser / app session, no tokens spent.

---

## Install

These are Claude Code [Agent Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) — a skill is just a folder containing a `SKILL.md` under `~/.claude/skills/`.

**Requires** Claude Code with Agent Skills support (2026-02 or newer). See [Compatibility](#compatibility) for full matrix.

```bash
# Clone anywhere
git clone https://github.com/iml1s/claude-skills.git
cd claude-skills

# Symlink the skills you want into Claude Code's global skills dir
ln -s "$(pwd)/skills/skill-organizer" ~/.claude/skills/skill-organizer
ln -s "$(pwd)/skills/opencli-llm-advisors" ~/.claude/skills/opencli-llm-advisors

# Next Claude Code session will auto-discover them via their SKILL.md descriptions.
```

(Prefer copying over symlinking? Swap `ln -s` for `cp -r`.)

### First-run config for `skill-organizer`

Copy the example config to your home:

```bash
cp examples/.skill-organizer.example.json ~/.skill-organizer.json
$EDITOR ~/.skill-organizer.json   # set project_roots to your own paths
```

Or skip this — the skill will ask on first run and write the file for you.

---

## `skill-organizer` — Two modes

| Mode | When to use | What it does |
|---|---|---|
| **Careful** (default) | First time running, unfamiliar skill library, or you want to review every decision | 9 phases: discover → classify → cross-project check → DEPRECATED detect → dry-run preview → safety check → execute with journal → optional CLAUDE.md annotation → report. Pauses for your `go` before any `mv`. |
| **Lazy** (opt-in) | Quarterly maintenance, library you trust, "just do it" | Only moves skills with a **unique direct name match** to a project. Everything else → dated archive. Pre-run **tar.gz snapshot** of the entire skills dir so a full rollback is one command. No prompts, no CLAUDE.md writes. |

Trigger Careful with: `整理 skills`, `organize skills`, `step-by-step organize`, `dry-run`.
Trigger Lazy with: `快速整理`, `懶人整理`, `一鍵整理`, `auto-clean`, `lazy sort`, `organize silently`.
Ambiguous requests make the skill ASK which mode you want.

### Safety properties (both modes)

- **Never `rm`** user skills. Always `mv` to archive.
- **Never** touch plugin-managed skills (`~/.claude/plugins/...` or `plugin:skill` prefixed).
- **Word-boundary name matching** — `app` will NOT match `apple-skill`.
- **Dated archive subfolders** — multiple runs don't overwrite each other.
- **Full rollback from one tar.gz** (Lazy Mode only, on by default).

---

## `opencli-llm-advisors` — Experimental

> ⚠️ This skill automates vendor chat UIs. Read the [skill file](skills/opencli-llm-advisors/SKILL.md) top note before using. Web UI changes may break it; heavy use may flag your account.

Covers:

- `opencli gemini ask` on a specific Google account (`/u/N` navigation pattern)
- Clicking the in-page model picker to select Gemini Pro (highest free tier)
- Driving ChatGPT Desktop natively via `opencli chatgpt-app`
- Using as a drop-in replacement for `omc ask gemini` when the API 429s

**Prerequisite**: install [opencli](https://github.com/jackwener/opencli) first and get its browser bridge running (`opencli doctor`).

---

## Troubleshooting

**`skill-organizer` moved a skill to the wrong project**
Lazy Mode's final report shows the archive path. Run `mv ~/.claude/skills-archive/YYYY-MM-DD/<name>/ ~/.claude/skills/` to restore. Or blast the whole run back with the pre-run tar.gz (path shown in report).

**`skill-organizer` says "keep global" but I want to force-move**
Use Careful Mode — in dry-run preview, type `adjust <skill>→<project>` to reclassify before running.

**`opencli gemini ask` returns garbage or hangs**
Selectors may be stale. Run `opencli doctor`, ensure the Browser Bridge extension is loaded, and check the target account has a Gemini tab open on `/u/N/app`. If still broken, it's an [opencli](https://github.com/jackwener/opencli) issue — file there.

**`opencli chatgpt-app send` does nothing**
Check `opencli chatgpt-app status`. The native app must be running and focused. AppleScript automation permission needs to be granted to your terminal in macOS System Settings.

**Claude Code doesn't auto-trigger the skill**
Open `/context` to confirm the skill is loaded. If loaded but not triggering, the skill's `description` frontmatter may not match your phrasing — edit it to add more trigger keywords.

---

## Compatibility

- **Platform**: macOS primary target (tested there). Linux *should* work for `skill-organizer`; `opencli-llm-advisors` may not (ChatGPT Desktop is macOS-only).
- **Claude Code**: any version that supports Agent Skills (2026-02 onwards).
- **opencli**: `^1.7.x` for `opencli-llm-advisors` recipes.
- **Shell**: zsh or bash; examples use POSIX-compatible syntax.

---

## Contributing

Bug reports and PRs welcome. Open an issue with:

- Which skill
- Claude Code / opencli version
- What you ran vs what you expected
- Any relevant output from the post-run report

For proposing new trigger keywords or heuristics, include a concrete example of the missed match.

---

## License

[MIT](./LICENSE) — do what you want, keep the notice.

## Related

- [anthropics/skills](https://github.com/anthropics/skills) — official reference skills
- [jackwener/opencli](https://github.com/jackwener/opencli) — browser/desktop-app CLI bridge this repo depends on
- [Agent Skills docs](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

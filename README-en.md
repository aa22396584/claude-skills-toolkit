# claude-skills

A two-skill toolkit for Claude Code power users. Best used together:

| Skill | What it does | Use when |
|---|---|---|
| **skill-organizer** | Cleans `~/.claude/skills/` — moves project-specific skills back to their owner repos, archives orphans, keeps only cross-project utilities global | Skills eating too much context, sessions running slow |
| **opencli-llm-advisors** | Drives Gemini/ChatGPT via browser as a fallback when API quotas are exhausted | Gemini/ChatGPT API hits 429, want to use free Pro model |

**Best together**: `skill-organizer` trims context → `opencli-llm-advisors` runs faster and cheaper.

---

## Install (pick what you need)

```bash
git clone https://github.com/aa22396584/claude-skills-toolkit.git ~/claude-skills-toolkit
cd ~/claude-skills-toolkit

# Install both
ln -s "$(pwd)/skills/skill-organizer" ~/.claude/skills/skill-organizer
ln -s "$(pwd)/skills/opencli-llm-advisors" ~/.claude/skills/opencli-llm-advisors

# Or just one
ln -s "$(pwd)/skills/skill-organizer" ~/.claude/skills/skill-organizer
```

Restart Claude Code and it will auto-discover skills by reading their descriptions. Trigger keywords are in each skill's documentation.

### First-run config (optional for skill-organizer)

To customize project root detection, copy the example config:

```bash
cp examples/.skill-organizer.example.json ~/.skill-organizer.json
$EDITOR ~/.skill-organizer.json   # set your projects_root
```

You can skip this — the skill will ask on first run and write the file for you.

---

## Getting Started

### Step 1: Tidy up existing skills (recommended first)

Session is slow or context near limit? Run:

```
整理 skills
```

This triggers **Careful Mode** — 9 phases with full preview → confirm → execute. You'll see the full classification plan before anything moves. Reply `go` to proceed.

After tidying, every new session loads faster with a slimmer skills list.

### Step 2: Set up opencli-llm-advisors (optional)

When you want an AI advisor but API quota is full:

```
用 Gemini 問問看這個架構
```

This auto-opens Gemini in browser, clicks the Pro model, and returns the answer.

**Requires [opencli](https://github.com/jackwener/opencli)** installed first (`brew install opencli` or `pip install opencli`).

---

## Decision Flow: Which one to use

```
Your situation
│
├─ Claude Code session is slow, context maxed out
│   └─ → skill-organizer (tidy skills)
│
├─ Want a second opinion but Gemini/ChatGPT API hits 429
│   └─ → opencli-llm-advisors (browser-driven)
│
├─ Both problems at once (common)
│   └─ → Run skill-organizer first, then opencli-llm-advisors
│
└─ Not sure
    └─ → Run skill-organizer first, decide after
```

---

## skill-organizer: Mode Comparison

| Situation | Mode | Trigger keywords |
|---|---|---|
| First time, want to see every decision | **Careful** (default) | `整理 skills`, `organize skills`, `dry-run` |
| Already used it, want speed + safety | **Lazy** | `快速整理`, `懶人整理`, `一鍵整理`, `lazy sort` |
| Ambiguous | — | Asks which mode you want |

**Careful Mode** runs 9 phases by default: Discover → Classify → Cross-project check → DEPRECATED detect → Dry-run preview → Safety check → Execute → CLAUDE.md annotation → Report. Pauses for your `go` before any changes.

**Lazy Mode** trades precision for speed — conservative defaults (archives when uncertain), mandatory tar.gz backup before any move.

### Lazy Mode Safety Floor

Even when skipping all prompts, Lazy guarantees:
- Never deletes skills (everything goes to archive)
- Never touches plugin-managed skills (`~/.claude/plugins/`)
- Always creates a tar.gz backup before running — one command to restore:

```bash
# Restore if Lazy moved something wrong:
rm -rf ~/.claude/skills && tar -xzf ~/.claude/skills-archive/.backups/skills-YYYY-MM-DD-HHMMSS.tar.gz -C ~/.claude
```

---

## opencli-llm-advisors: When to use

| Situation | How to use |
|---|---|
| Gemini API hits 429 | `用 Gemini 問問看架構設計` → browser opens, selects Pro model, returns answer |
| Want 3.1 Pro but API only has Fast | Same as above — browser version is always Pro |
| Have ChatGPT Plus Desktop | `用 ChatGPT 問問看` → drives macOS Desktop app |
| Compare Claude + Gemini answers | Use Claude normally, then `opencli-llm-advisors` for Gemini side |

> ⚠️ **Experimental**: Web UIs can break when Google/OpenAI change their DOM. When that happens, update the [opencli adapter](https://github.com/jackwener/opencli), not this skill.

---

## FAQ

**Q: Can I install just one?**
A: Yes. They are completely independent. Just `skill-organizer` if you only want to tidy; just `opencli-llm-advisors` if you only want API fallback.

**Q: Do I need to restart Claude Code after organizing?**
A: No. New sessions auto-load the slimmed skills list.

**Q: Why does this need account switching?**
A: `opencli` binds to the active browser tab. Open `https://gemini.google.com/u/1/app` to use a second Google account. Default is `/u/0`.

**Q: Lazy Mode moved a skill to the wrong project**
A: Restore from the archive path in the report: `mv ~/.claude/skills-archive/YYYY-MM-DD/<skill>/ ~/.claude/skills/`

---

## File Structure

```
claude-skills-toolkit/
├── skills/
│   ├── skill-organizer/              # skills tidying tool
│   │   └── SKILL.md
│   └── opencli-llm-advisors/         # API fallback via browser
│       └── SKILL.md
├── examples/
│   └── .skill-organizer.example.json  # example config
└── README.md        (Chinese / 中文)
└── README-en.md    (English / 英文)
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `skill-organizer` moved a skill to wrong project | Restore from archive, re-run Careful Mode and use `adjust` in preview |
| `opencli gemini ask` hits 429 | That's exactly what this skill handles — it switches to browser path automatically |
| `opencli gemini ask` returns garbage or times out | Selectors may be stale; run `opencli doctor` to verify Browser Bridge |
| Claude Code doesn't auto-trigger skill | Open `/context` to check it's loaded, or invoke directly: `整理 skills` |
| ChatGPT Desktop does nothing | Verify app is running, `opencli chatgpt-app status` detects it, terminal has AppleScript automation permission |

---

## Links

- [opencli](https://github.com/jackwener/opencli) — browser/desktop CLI bridge
- [Official Agent Skills docs](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- MIT License

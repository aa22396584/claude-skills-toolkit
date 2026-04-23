---
name: opencli-llm-advisors
description: "Use opencli to drive LLM chat apps (Gemini web, ChatGPT Desktop) as external advisors — bypasses API 429/quota by using the user's logged-in browser/desktop-app session. Triggers when: Gemini CLI returns 429 or capacity-exhausted, user wants a CCG advisor and API is unavailable, user wants to use their ChatGPT Plus subscription instead of API, or user says 'ask Gemini/ChatGPT via opencli'. Covers `/u/N` account switching, clicking the in-page mode picker to select highest-tier model (Gemini Pro 3.1), ChatGPT Desktop native control, and common failure modes. Does NOT apply for: normal API calls that work, image generation (use `opencli chatgpt image` directly), or headless/CI workflows."
---

# OpenCLI as LLM Advisor Bridge

> ⚠️ **Experimental / unofficial**. This skill automates vendor web UIs (Gemini, ChatGPT) via `opencli`'s browser bridge. It is inherently fragile:
> - **Upstream UI changes** may break the DOM selectors overnight. When that happens, the adapter inside opencli needs updating — not this skill.
> - **Terms of Service**: automating chat UIs may violate provider ToS. Use for personal productivity only; avoid high-volume scraping.
> - **Account safety**: excessive automation can get accounts flagged. Keep per-minute rates low.
>
> Use only as a fallback when the official API path is unavailable. If your API quota works, use that instead.

When the official API path fails (429, quota, auth), or when the user wants a higher-tier model than their API key allows, `opencli` can drive the **web UI or desktop app** of the LLM instead — reusing your logged-in browser / installed app session. No tokens consumed on the API side, no rate limits against free tiers.

Complements the official OpenCLI skills (`opencli-usage`, `opencli-browser`, `opencli-adapter-author`). Those cover generic opencli capabilities. This skill covers **how we specifically use it as an LLM advisor** in this user's environment.

## When to Use

- `gemini-cli` (API path) returned 429 / `MODEL_CAPACITY_EXHAUSTED` / auth issue
- CCG flow (`/oh-my-claudecode:ccg`) needs a Gemini response but API is down
- User explicitly wants Gemini 3.1 Pro or GPT-5.2 Thinking via their Plus subscription
- Want to cross-validate a Claude answer with a different frontier model, no budget
- `ask-gemini` / `ask-codex` helpers failed; need fallback

## When NOT to Use

- Normal programmatic calls in working CI (opencli needs a GUI Chrome session)
- Image generation → use `opencli chatgpt image` / `opencli gemini image` directly (these are already simple)
- When headless / no GUI available
- When the user's own browser Chrome window is not logged into the target service

## User's Environment (specific to this setup)

| Service | Preferred account | Notes |
|---|---|---|
| Gemini web | Your preferred Google account — use `/u/N` where N is the account index (`/u/0` is the default-logged-in account, `/u/1` is the second, etc.) | Always navigate to the correct `/u/N/app` URL before calling `opencli gemini` |
| ChatGPT Desktop | Native macOS app | Use `opencli chatgpt-app` — native, not web |
| Chrome profile | Default profile | opencli uses whichever profile's browser is connected via the Browser Bridge extension |

## Recipe 1 — Gemini 3.1 Pro (free-tier highest)

**Goal**: Send a prompt to Gemini with the highest-tier free model (Pro / 3.1 Pro), not the default Fast mode.

```bash
# 1. Navigate to the right account (/u/1) AND open new chat
opencli browser open "https://gemini.google.com/u/1/app"
sleep 2

# 2. Find the mode picker button (labeled "Fast" or current mode)
opencli browser find --css "bard-mode-switcher button, [aria-label='Open mode picker']"
# Note the ref number from output — likely around 29 after page loads

# 3. Click to open mode picker, then list options
opencli browser click <ref>
sleep 1
opencli browser find --css "[role=menuitem], button[role=menuitemradio]" --text-max 200

# 4. Click the "Pro" menu item (text: "Pro  Advanced math and code with 3.1 Pro")
opencli browser click <pro-ref>

# 5. Now send the prompt — adapter will use the Pro model
opencli gemini ask "your prompt here" --timeout 120
```

**Why click instead of CLI flag**: `opencli gemini ask` has no `--model` flag. Mode is set via UI state, persists for the session.

**Timeout**: Pro mode "thinks" — set `--timeout 120` or higher. Default 60s will cut Pro mid-reasoning.

## Recipe 2 — ChatGPT Desktop as advisor

**Goal**: Ask ChatGPT Desktop (native macOS app) for a second opinion. Uses Plus subscription, zero API spend.

```bash
# Pre-flight: ensure ChatGPT Desktop is running
opencli chatgpt-app status
# If not running: launch ChatGPT.app via Spotlight or `open -a "ChatGPT"`

# 1. Open a new chat
opencli chatgpt-app new

# 2. (Optional) Switch model to thinking mode for harder questions
opencli chatgpt-app model thinking   # or: 5.2-thinking / 5.2-instant

# 3. Send the prompt
opencli chatgpt-app send "your prompt here"

# 4. Wait for the response (no built-in wait — poll read)
sleep 15
opencli chatgpt-app read
# If still generating, sleep longer and read again
```

**Gotcha**: `chatgpt-app read` returns the last visible message. If ChatGPT is still streaming, you may get partial text. Poll until content stops growing.

## Recipe 3 — Account switching (general pattern)

OpenCLI has **no** `--account` flag. It uses whatever session is active in the current browser tab.

To use a non-default Google account (e.g., `/u/1` instead of `/u/0`):

```bash
# Always pre-navigate to the /u/N variant of the URL
opencli browser open "https://gemini.google.com/u/1/app"
# Then run the normal adapter command — it operates on whatever tab is active
opencli gemini ask "..."
```

Same pattern for any Google-authenticated site.

## Recipe 4 — CCG (Claude-Codex-Gemini) via opencli fallback

When `omc ask gemini` fails with 429, the original `/oh-my-claudecode:ccg` flow can still complete by substituting opencli for the Gemini leg:

```bash
# Codex leg (API path, usually fine)
omc ask codex "<codex prompt>"

# Gemini leg via opencli (no API, no 429)
opencli browser open "https://gemini.google.com/u/1/app"
# ... select Pro per Recipe 1 ...
opencli gemini ask "<gemini prompt>" --timeout 120 > /tmp/gemini-response.md

# Claude synthesizes both as usual
```

## Failure Modes & Workarounds

| Symptom | Likely cause | Fix |
|---|---|---|
| `opencli gemini ask` hangs or times out at 60s | Pro mode thinking longer | Add `--timeout 120` or `--timeout 180` |
| Wrong Google account replies | Active tab is on `/u/0`, not `/u/1` | Always `browser open` the `/u/N` URL first |
| Mode picker button ref not 29 | Page layout changed or lazy load | Re-run `browser find --css "bard-mode-switcher button"` to get fresh ref |
| "Upgrade" shown instead of Pro option | Free-tier quota for Pro used up that day | Switch to Thinking mode (still high-tier) or use `chatgpt-app` instead |
| ChatGPT Desktop returns partial message | Still streaming | Sleep longer, re-`read` until stable |
| `opencli chatgpt-app send` but nothing happens | App not focused / not running | Check `chatgpt-app status`; focus window manually if needed |
| Adapter targets wrong tab | opencli binds to the "site workspace" tab, not the one you have open | Use `opencli browser open` to seed the correct URL into the site workspace first |

## Model Tier Reference (as of 2026-04)

**Gemini web (via `opencli gemini ask`)**:
- Fast (default) — low-effort answers
- Thinking — medium, good for most advisor queries
- **Pro (3.1 Pro)** — highest free-tier, use for architecture/review tasks
- Upgrade — paid, skip unless user has Gemini Advanced

**ChatGPT Desktop (`opencli chatgpt-app model <mode>`)**:
- `auto` — ChatGPT picks
- `instant` / `5.2-instant` — fast
- `thinking` / `5.2-thinking` — higher reasoning, recommended for advisor role

## Integration with Existing Skills

| Task | Skill to use |
|---|---|
| First-time setup / CLI install questions | `opencli-usage` |
| Writing a new adapter for a new site | `opencli-adapter-author` |
| Fixing a broken built-in adapter | `opencli-autofix` |
| Low-level browser primitives | `opencli-browser` |
| **Using an LLM as advisor/fallback (this skill)** | `opencli-llm-advisors` |

## Anti-patterns

- **Don't use opencli when the API path works**. API is faster, scriptable, idempotent. opencli is a fallback, not a default.
- **Don't leave chat history accumulating in the browser**. Gemini/ChatGPT web context can bleed between calls. Always `browser open .../app` fresh or `chatgpt-app new` before a new advisor query.
- **Don't assume the model persists**. If the user restarts the browser, mode resets to Fast / default. Re-run the mode picker flow.
- **Don't send sensitive prompts through the chat UI** without thinking about it — these go through the web service with regular chat-history retention, unlike opaque API calls.
- **Don't wait forever**. If Pro mode takes > 3 min, something's wrong — abort, retry with smaller prompt.

## Quick one-liner wrappers

Add to `~/.zshrc` for fast access:

```zsh
# Gemini Pro on account /u/1
ask-gemini-pro() {
  opencli browser open "https://gemini.google.com/u/1/app" > /dev/null
  opencli gemini ask "$@" --timeout 180
}

# ChatGPT Desktop with thinking mode
ask-gpt-think() {
  opencli chatgpt-app new > /dev/null
  opencli chatgpt-app model thinking > /dev/null
  opencli chatgpt-app send "$@"
  sleep 20
  opencli chatgpt-app read
}
```

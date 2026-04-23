# claude-skills

A two-skill toolkit for Claude Code power users:

| Skill | What it does | Use when |
|---|---|---|
| **skill-organizer** | 清理 `~/.claude/skills/` 目錄，把專屬專案的 skill 搬回該專案，全域只留跨專案工具 | skills 太多吃 context、session 變慢 |
| **opencli-llm-advisors** | API 額度用完時，用瀏覽器驅動 Gemini/ChatGPT 當 fallback | Gemini/ChatGPT API 噴 429、想用免費的 Pro 模型 |

**一起用最有效**：`skill-organizer` 減少 context 負載 → 讓 `opencli-llm-advisors` 跑更快、、省更多 tokens。

---

## 安裝（選你要的）

```bash
git clone https://github.com/ImL1s/claude-skills.git ~/claude-skills
cd ~/claude-skills

# 兩個都裝
ln -s "$(pwd)/skills/skill-organizer" ~/.claude/skills/skill-organizer
ln -s "$(pwd)/skills/opencli-llm-advisors" ~/.claude/skills/opencli-llm-advisors

# 或只裝其中一個
ln -s "$(pwd)/skills/skill-organizer" ~/.claude/skills/skill-organizer
```

只要裝完重開 Claude Code session 就會自動吃到。

---

## 新手起手式

### 第一步：整理現有 skills（推薦先做）

Session 變慢、context 快滿了？先整理：

```
整理 skills
```

→ 走 **Careful Mode**（9 步驟預覽 → 確認 → 執行），你會看到所有 skills 的分類計畫，按 `go` 才真的動。

整理完後每次新 session context 變輕，skill 載入更快。

### 第二步：設定 `opencli-llm-advisors`（可選）

當你想用 AI advisor 但 API 額度滿了：

```
用 Gemini 問問看這個架構
```

→ 會自動用瀏覽器開啟 Gemini，點選 Pro 模型，回傳答案給你。

**需要先裝 [opencli](https://github.com/jackwener/opencli)**（`brew install opencli` 或 `pip install opencli`）。

---

## 決策流程：什麼時候用哪個

```
你的情境
│
├─ Claude Code session 變慢、context 爆了
│   └─ → skill-organizer（整理 skills）
│
├─ 想問 AI 第二意見，但 Gemini/ChatGPT API 噴 429
│   └─ → opencli-llm-advisors（瀏覽器驅動）
│
├─ 兩種情境都有（常見）
│   └─ → 先用 skill-organizer，再用 opencli-llm-advisors
│
└─ 不確定
    └─ → 先跑 skill-organizer，整理完再說
```

---

## skill-organizer 模式對照

| 情境 | 模式 | 觸發關鍵字 |
|---|---|---|
| 第一次整理，想看清楚每一步 | **Careful**（預設） | `整理 skills`、`organize skills`、`dry-run` |
| 已經用過一次，想要快又安全 | **Lazy** | `快速整理`、`懶人整理`、`一鍵整理`、`lazy sort` |
| 不確定 | — | 兩個都不是 → 會問你要哪個 |

**Lazy 的代價**：它保守搬家（不確定就 archive），適合季度清理。Careful 讓你每步都核准，適合第一次跑。

### Lazy 的 Safety Floor

即使跳過所有確認，Lazy 仍保證：
- 不會刪 skill（全部進 archive）
- 不動 plugin-managed skills（`~/.claude/plugins/`）
- 每次執行前自動打 tar.gz 備份，出事一行指令還原

```bash
# 萬一 Lazy 整理錯了，這樣救回來：
rm -rf ~/.claude/skills && tar -xzf ~/.claude/skills-archive/.backups/skills-YYYY-MM-DD-HHMMSS.tar.gz -C ~/.claude
```

---

## opencli-llm-advisors 什麼情境用

| 情境 | 怎麼用 |
|---|---|
| Gemini API 噴 429 | `用 Gemini 問問看架構設計` → 自動用瀏覽器跑 Pro 模型 |
| 想用 3.1 Pro 但 API 只有 Fast | 同上，瀏覽器版是 Pro |
| ChatGPT Desktop 有 Plus 訂閱 | `用 ChatGPT 問問看` → 驅動桌面 App |
| 想比較 Claude + Gemini 兩個答案 | 先用 Claude，再用 `opencli-llm-advisors` 拿 Gemini 的 |

**注意**：這是實驗性的。Web UI 可能因為 Google/OpenAI 改版而失效，那時去更新 [opencli adapter](https://github.com/jackwener/opencli) 不是這個 skill。

---

## 常見問題

**Q: 只裝一個可以嗎？**
A: 可以。兩個完全獨立，想只整理 skills 就只裝 `skill-organizer`；想省 API 額度就只裝 `opencli-llm-advisors`。

**Q: 整理完 skill 要重開 Claude Code 嗎？**
A: 不用重開。新 session 自動吃到新的 slimmed skills 清單。

**Q: `opencli-llm-advisors` 為什麼需要帳號切換？**
A: `opencli` 綁定瀏覽器目前的 tab。開 `https://gemini.google.com/u/1/app` 才能用第二個 Google 帳號。預設 `/u/0` 是主要帳號。

**Q: Lazy Mode 把 skill 搬到錯的專案了**
A: 從報告裡的 archive path 還原：`mv ~/.claude/skills-archive/YYYY-MM-DD/<skill>/ ~/.claude/skills/`

---

## 檔案結構

```
claude-skills/
├── skills/
│   ├── skill-organizer/          # skills 整理工具
│   │   └── SKILL.md
│   └── opencli-llm-advisors/     # API fallback 瀏覽器驅動
│       └── SKILL.md
├── examples/
│   └── .skill-organizer.example.json  # 範例設定檔
└── README.md
```

---

## 疑難排解

| 問題 | 解法 |
|---|---|
| `skill-organizer` 把 skill 搬到錯誤的專案 | 用 Lazy 的 archive 復原，下次跑 Careful Mode 並在預覽階段用 `adjust` 指令修正 |
| `opencli gemini ask` 噴 429 | 這正是這個 skill 要處理的 — 它會自動改走瀏覽器路徑，不走 API |
| `opencli gemini ask` 回 garbage 或超時 | selectors 可能過時，跑 `opencli doctor` 確認 Browser Bridge 正常 |
| Claude Code 沒自動觸發 skill | 開 `/context` 確認有載入。或直接叫用：`整理 skills` |
| ChatGPT Desktop 沒反應 | 確認 App 在跑、`opencli chatgpt-app status` 有認到、終端機有 AppleScript 自動化權限 |

---

## 關於

- [opencli](https://github.com/jackwener/opencli) — 瀏覽器/桌面 App CLI 橋接工具
- [官方 Agent Skills 文档](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- MIT License

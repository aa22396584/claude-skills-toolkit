# Flutter Fleet Audit Skills

一套以 `SKILL.md` 封裝、證據優先的 Flutter 多專案稽核技能。它會先發現所有 Flutter repository，蒐集可重現的 facts，再分別進行效能、架構、測試、安全／發佈稽核，最後輸出跨專案矩陣、共通問題與 30/60/90 天路線圖。

## 包含技能

| Skill | 用途 |
|---|---|
| `flutter-fleet-audit` | 主控：發現專案、批次稽核、保存進度、產出總報告 |
| `flutter-performance-audit` | UI/Raster、layout、圖片、CPU、啟動、Platform View、app size |
| `flutter-architecture-audit` | 模組邊界、狀態、資料流、生命週期、平台整合與依賴治理 |
| `flutter-test-audit` | Unit、Widget、Golden、Integration、migration 與 flaky test 缺口 |
| `flutter-security-release-audit` | Secrets、權限、儲存、WebView、網路、簽章與 release 設定 |
| `flutter-portfolio-synthesis` | 跨專案排序、共通模式、共用 package／lint／CI 候選 |

## 核心規則

- 預設只讀，不執行 `dart fix --apply`、`flutter pub upgrade`、格式化、codegen 或發佈。
- source pattern 只能標成 `static_candidate`；可重現才是 `reproduced`；有 trace／benchmark／memory／size 數據才是 `measured`。
- 每個 finding 都必須有 repository-relative 檔案與行號、命令結果、測試、trace 或量測證據。
- 不輸出 token、keystore 密碼、private key 或包含認證資訊的 URL。
- 大量 repo 預設每五個保存一次 manifest，可在中斷後續跑。

## Gemini CLI 安裝

安裝主控技能：

```bash
gemini skills install https://github.com/ImL1s/claude-skills-toolkit.git \
  --path skills/flutter-fleet-audit \
  --scope user \
  --consent
```

安裝其餘技能：

```bash
for skill in \
  flutter-performance-audit \
  flutter-architecture-audit \
  flutter-test-audit \
  flutter-security-release-audit \
  flutter-portfolio-synthesis
do
  gemini skills install https://github.com/ImL1s/claude-skills-toolkit.git \
    --path "skills/$skill" \
    --scope user \
    --consent
done
```

也可將各技能目錄連結到 `~/.agents/skills/`、`~/.gemini/skills/`，或專案內的 `.agents/skills/`、`.gemini/skills/`。

## 起手提示

```text
使用 flutter-fleet-audit 掃描 ~/workspace 與 ~/Documents/mine 裡所有 Flutter 專案。
採 read-only standard audit，不修改程式碼；每五個專案保存一次進度。
效能 finding 必須區分 static_candidate、reproduced、measured，無量測不得宣稱掉幀。
最後輸出專案矩陣、前 20 個高價值問題、共通模式、共用 package／lint／CI 候選，
以及 30/60/90 天路線圖。
```

## 直接使用腳本

```bash
python3 skills/flutter-fleet-audit/scripts/discover_flutter_projects.py \
  ~/workspace ~/Documents/mine \
  --output audit/inventory.json

python3 skills/flutter-fleet-audit/scripts/collect_project_facts.py \
  /path/to/flutter-project \
  --output audit/project-facts.json

python3 skills/flutter-fleet-audit/scripts/validate_audit.py \
  audit/project-audit.json

python3 skills/flutter-fleet-audit/scripts/aggregate_audits.py \
  audit/ \
  --output audit/portfolio-report.md
```

腳本只依賴 Python 標準函式庫，對被掃描的 Flutter repository 維持只讀。

## 測試

```bash
python3 -m unittest tests/test_flutter_fleet_audit_scripts.py -v
```

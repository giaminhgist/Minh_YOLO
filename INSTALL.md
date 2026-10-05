# INSTALL — Cài 12 upstream skill repos vào Claude root (`~/.claude`) theo đúng hướng dẫn của từng repo

Runbook cho máy mới / Claude tương lai. Mỗi repo được cài **đúng theo cách tác giả hướng dẫn** (đã thực thi và xác minh trên máy Linux; lần xác minh gần nhất 2026-10-05: Claude Code 2.1.289, Node 18 → fallback SS, `verify_install.py` PASS). Sau khi cài, các path trong `SKILL_INDEX.md` / `SKILL.md` / `CLAUDE.md` trỏ đúng nơi cài thực tế.

## Cách cài bằng MỘT prompt (máy mới)

1. Clone repo chứa bộ cài (file này + `CLAUDE.md` + `research-orchestrator/`), mở Claude Code tại thư mục đó.
2. Gửi đúng một prompt:

   > Cài đặt toàn bộ môi trường research skills theo INSTALL.md trong repo: chạy tuần tự Bước 0 → 4, không dừng để hỏi trừ khi gặp lỗi, rồi chạy `verify_install.py` và báo kết quả PASS/FAIL.

3. Claude sẽ: clone upstream → cài 12 repo đúng cách từng repo → cài orchestrator + CLAUDE.md global → trim hooks (`configure_hooks.py`) → verify.

Mọi bước đều idempotent — an toàn khi chạy lại; thông báo "already installed" của `claude plugin install` có thể bỏ qua.

## Layout sau khi cài

| Nơi | Nội dung |
|---|---|
| `~/.claude/skills/<name>/` | Skills cài thẳng: ARIS (86), OR (98, symlink), AI-research-feedback (11), natureskills (5), Supervisor-Skills (12), toolkit (4), + `shared-references/` của ARIS |
| `~/.claude/plugins/marketplaces/<mp>/…` | Skills cài qua plugin marketplace (CS, ctx, AAS, humanizer) |
| `~/.claude/plugins/cache/<mp>/<plugin>/<version>/…` | Bản cài thật của plugin (path chứa version — superpowers 6.4.2 hardcode trong SKILL_INDEX) |
| `~/.claude/plugins/claude-code-toolkit/` | awesome-claude-code-toolkit (manual clone theo README) |
| `~/.claude/agents/<name>.md` | Agents từ toolkit |
| `~/.claude/upstream/<repo>/` | 6 upstream clones cài thẳng (source; `git pull` tại đây; không sửa) — 6 repo plugin lấy source từ marketplace clone `~/.claude/plugins/marketplaces/<mp>/` |
| `~/.orchestra/skills/` | Nơi OR installer tải skills về (symlink vào `~/.claude/skills`) |
| `~/.claude/skills/research-orchestrator/` | `SKILL.md` + `SKILL_INDEX.md` + `INSTALL.md` + `verify_install.py` + `configure_hooks.py` |
| `~/.claude/CLAUDE.md` | Global instructions |

## Bước 0 — Prerequisites

```bash
git --version && node --version    # Node ≥ 20 nếu muốn dùng `npx skills` (Node 18 lỗi node:util/styleText)
claude --version                   # ≥ 2.1.142 (plugin humanizer yêu cầu)
```

## Bước 1 — Clone các repo không cài qua plugin vào `~/.claude/upstream`

```bash
mkdir -p ~/.claude/upstream && cd ~/.claude/upstream
# (Nếu đã có clones cũ ở /root/Agent/upstream: mv /root/Agent/upstream ~/.claude/upstream)
for repo in \
  wanshuiyin/auto-claude-code-research-in-sleep \
  Orchestra-Research/AI-Research-SKILLs \
  claesbackman/AI-research-feedback \
  niuz257470-ctrl/natureskills \
  HKUSTDial/Supervisor-Skills \
  VoltAgent/awesome-agent-skills; do
  name=$(basename "$repo")
  [ -d "$name/.git" ] || git clone --depth 1 "https://github.com/$repo.git" "$name"
done
# 6 repo còn lại (superpowers, humanizer, ctx, toolkit, claude-skills, agentic-awesome-skills)
# được Claude Code tự clone khi `claude plugin marketplace add …` — không clone tay.
```

## Bước 2 — Cài từng repo theo hướng dẫn tác giả

### 2.1 ARIS — `cp -r skills/* ~/.claude/skills/` (global install chính thức trong README)

```bash
cp -r ~/.claude/upstream/auto-claude-code-research-in-sleep/skills/* ~/.claude/skills/
# → ~/.claude/skills/<name>/SKILL.md + shared-references/ (86 skills + mirrors codex)
# Tạo helper ~/.aris/repo (SKILL_INDEX tham chiếu tới nó; chỉ smart_update --apply mới ghi file này):
(cd ~/.claude/upstream/auto-claude-code-research-in-sleep && bash tools/smart_update.sh --apply)
# Codex reviewer (tùy chọn — các skill review cần nó):
#   npm install -g @openai/codex && codex login
#   claude mcp add codex -s user -- python3 "$HOME/.claude/upstream/auto-claude-code-research-in-sleep/mcp-servers/codex-exec/server.py"
# Update: cd ~/.claude/upstream/auto-claude-code-research-in-sleep && git pull && bash tools/smart_update.sh --apply
```

### 2.2 OR — `npx @orchestra-research/ai-research-skills install --all`

```bash
npx @orchestra-research/ai-research-skills install --all
# → tải skills về ~/.orchestra/skills/<category>/<name>/ và symlink vào ~/.claude/skills/<name>
# Installer tải 95/98 skills; 3 skill ARA (compiler, research-manager, rigor-reviewer) bị thiếu —
# bổ sung theo đúng layout của installer:
for s in compiler research-manager rigor-reviewer; do
  cp -R ~/.claude/upstream/AI-Research-SKILLs/22-agent-native-research-artifact/$s ~/.orchestra/skills/22-agent-native-research-artifact/ 2>/dev/null
  ln -sf ~/.orchestra/skills/22-agent-native-research-artifact/$s ~/.claude/skills/$s
done
# Update: npx @orchestra-research/ai-research-skills update
```

### 2.3 superpowers — plugin qua marketplace riêng (bắt buộc để khớp path SKILL_INDEX)

```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin install -y superpowers@superpowers-marketplace
# → skills tại ~/.claude/plugins/cache/superpowers-marketplace/superpowers/<version>/skills/<name>/SKILL.md
#   (path chứa version — SKILL_INDEX hardcode 6.4.2; sau `claude plugin update superpowers`
#    phải re-verify + cập nhật version trong SKILL_INDEX)
# ⚠ Không cài qua claude-plugins-official: cache path sẽ là
#   ~/.claude/plugins/cache/claude-plugins-official/… → lệch MỌI path SP trong SKILL_INDEX.
```

### 2.4 AI-research-feedback — one-liner chính thức trong README

```bash
git clone --depth 1 https://github.com/claesbackman/AI-research-feedback.git /tmp/airf && mkdir -p ~/.claude/skills && cp -R /tmp/airf/Skills/. ~/.claude/skills/ && rm -rf /tmp/airf
# → ~/.claude/skills/<name>/SKILL.md (11 skills). Update: chạy lại chính dòng này.
```

### 2.5 natureskills — repo không có installer; copy các thư mục skill

```bash
cp -R ~/.claude/upstream/natureskills/nature-* ~/.claude/skills/
# → ~/.claude/skills/nature-{figure,polishing,citation,data,paper2ppt}/SKILL.md. Update: git pull + copy lại.
```

### 2.6 agentic-awesome-skills — plugin (docs/users/plugins.md)

```bash
claude plugin marketplace add sickn33/agentic-awesome-skills
claude plugin install -y agentic-awesome-skills@agentic-awesome-skills
# → plugin-safe subset (2.491 skills) tại
#   ~/.claude/plugins/marketplaces/agentic-awesome-skills/plugins/agentic-awesome-skills-claude/skills/<name>/SKILL.md
# ⚠ Danh sách skill của Claude Code sẽ rất dài — nếu muốn gọn, dùng specialized bundles
#   (claude plugin list để xem, ví dụ agentic-bundle-data-analytics@agentic-awesome-skills).
# Skill ngoài plugin (dos-verify-done-claims) → dùng từ marketplace clone:
#   ~/.claude/plugins/marketplaces/agentic-awesome-skills/skills/…
```

### 2.7 claude-skills — plugin marketplace (INSTALLATION.md: `/plugin marketplace add alirezarezvani/claude-skills`)

```bash
claude plugin marketplace add alirezarezvani/claude-skills
for p in engineering-skills engineering-advanced-skills ra-qm-skills research-ops-skills \
         research-orchestrator litreview deep-research deepread grants pulse dossier \
         compliance-os compliance-team-eu-ai-act compliance-team-iso42001 \
         handoff-productivity markdown-html-skills; do
  claude plugin install -y "$p@claude-code-skills"
done
# → skills tại ~/.claude/plugins/marketplaces/claude-code-skills/<domain>/…/SKILL.md
# Lưu ý: loop-library, standards/ không có plugin.json → không phân phối qua plugin;
# tham chiếu trực tiếp marketplace clone ~/.claude/plugins/marketplaces/claude-code-skills/…
# Update: claude plugin update <plugin>
```

### 2.8 Supervisor-Skills — README: "import vào AI assistant" (skills CLI cần Node ≥ 20)

```bash
# npx skills add HKUSTDial/Supervisor-Skills --global --agent claude-code   # nếu Node ≥ 20
# Fallback (đã dùng trên Node 18) — copy theo đúng cách README mô tả:
cp -R ~/.claude/upstream/Supervisor-Skills/skills/*/ ~/.claude/skills/
# → ~/.claude/skills/<name>/SKILL.md (12 skills). Update: git pull + copy lại.
# ⚠ License CC BY-NC-SA 4.0: dùng cá nhân OK; không tái phân phối/không thương mại.
```

### 2.9 awesome-agent-skills — curated list, **không có gì để cài**

Chỉ là catalog các link officialskills.sh + GitHub. Dùng để khám phá skill ngoài 12 repo.

### 2.10 humanizer — plugin (README: `/plugin marketplace add blader/humanizer`)

```bash
claude plugin marketplace add blader/humanizer
claude plugin install -y humanizer@humanizer
# → skill tại ~/.claude/plugins/marketplaces/humanizer/SKILL.md, gọi bằng /humanizer:humanizer
# (Claude Code < 2.1.142: npx skills add blader/humanizer --global --agent claude-code)
```

### 2.11 agent-skills-for-context-engineering — plugin marketplace (README)

```bash
claude plugin marketplace add muratcankoylan/Agent-Skills-for-Context-Engineering
claude plugin install -y context-engineering@context-engineering-marketplace
# → ~/.claude/plugins/marketplaces/context-engineering-marketplace/skills/<name>/SKILL.md (18 skills)
```

### 2.12 awesome-claude-code-toolkit — manual clone + installer (README Quick Install)

```bash
# ⚠ Marketplace của repo có bug manifest ("source: Invalid string: must start with './'")
#   nên không cài plugin qua marketplace được — dùng route manual clone mà README đưa ra:
git clone --depth 1 https://github.com/rohitg00/awesome-claude-code-toolkit.git ~/.claude/plugins/claude-code-toolkit
cd ~/.claude/plugins/claude-code-toolkit && yes | bash setup/install.sh
#   → 39 commands (~/.claude/commands/<category>/), hooks (~/.claude/hooks.json: 25 entries từ 19 scripts —
#     ⚠ bật global — trim về 9 hooks an toàn ở Bước 3), 15 rules, 7 templates, mcp-configs reference
# Skills + agents (không nằm trong installer — copy thủ công theo cấu trúc repo):
for s in deep-dive claude-memory-kit prompt-engineering continuous-learning; do
  cp -R ~/.claude/plugins/claude-code-toolkit/skills/$s ~/.claude/skills/ 2>/dev/null
done
mkdir -p ~/.claude/agents
cp ~/.claude/plugins/claude-code-toolkit/agents/research-analysis/academic-researcher.md ~/.claude/agents/
cp ~/.claude/plugins/claude-code-toolkit/agents/data-ai/autoresearch-agent.md ~/.claude/agents/
cp ~/.claude/plugins/claude-code-toolkit/agents/data-ai/computer-vision-engineer.md ~/.claude/agents/
# Update: git -C ~/.claude/plugins/claude-code-toolkit pull (+ chạy lại setup/install.sh + copy lại skills/agents)
# ⚠ setup/install.sh ghi ~/.claude/hooks.json (25 hooks global) — trim về 9 hooks an toàn ở Bước 3.
```

## Bước 3 — Cài orchestrator + CLAUDE.md vào root

```bash
# Từ thư mục dự án chứa research-orchestrator/ và CLAUDE.md (INSTALL.md nằm ở GỐC repo):
PROJ="$PWD"
mkdir -p ~/.claude/skills/research-orchestrator
cp "$PROJ/research-orchestrator/SKILL.md"            ~/.claude/skills/research-orchestrator/SKILL.md
cp "$PROJ/research-orchestrator/SKILL_INDEX.md"      ~/.claude/skills/research-orchestrator/SKILL_INDEX.md
cp "$PROJ/INSTALL.md"                                ~/.claude/skills/research-orchestrator/INSTALL.md
cp "$PROJ/research-orchestrator/verify_install.py"   ~/.claude/skills/research-orchestrator/verify_install.py
cp "$PROJ/research-orchestrator/configure_hooks.py"  ~/.claude/skills/research-orchestrator/configure_hooks.py
[ -f ~/.claude/CLAUDE.md ] && cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak.$(date +%Y%m%d)
cp "$PROJ/CLAUDE.md" ~/.claude/CLAUDE.md
# Trim hooks.json về 9 hooks an toàn (backup bản đầy đủ 25 hooks — bỏ dòng này nếu muốn giữ đủ):
python3 ~/.claude/skills/research-orchestrator/configure_hooks.py
```

## Bước 4 — Verify

```bash
claude plugin list            # phải thấy 20 plugin enabled
ls ~/.claude/skills | wc -l   # ≈ 218 (86 ARIS + shared-references/ + 98 OR + 11 ARF + 5 NS + 12 SS + 4 TK + research-orchestrator/)
ls ~/.claude/agents           # academic-researcher.md, autoresearch-agent.md, computer-vision-engineer.md

# Gate kiểm tra tự động: mọi path trong SKILL_INDEX.md + broken symlinks + hooks + counts.
# PASS = toàn bộ path tồn tại trên disk. FAIL = in danh sách lỗi cụ thể.
python3 ~/.claude/skills/research-orchestrator/verify_install.py
```

Nếu verify FAIL: path in ra chưa được cài (xem Bước 2 của repo tương ứng) hoặc upstream đổi cấu trúc sau update — cập nhật SKILL_INDEX.md rồi chạy lại verify. Chạy lại verify bất cứ lúc nào để kiểm tra sức khỏe bộ cài.

## Bước 5 — Cập nhật định kỳ (theo từng repo)

```bash
# ARIS
cd ~/.claude/upstream/auto-claude-code-research-in-sleep && git pull && bash tools/smart_update.sh --apply
# OR
npx @orchestra-research/ai-research-skills update
# AI-research-feedback: chạy lại one-liner Bước 2.4
# natureskills / Supervisor-Skills: git -C ~/.claude/upstream/<repo> pull && copy lại
# Plugin repos: claude plugin update <plugin>   (sau đó chạy verify_install.py — superpowers path chứa version,
#   nếu đổi version thì cập nhật SKILL_INDEX.md trước khi verify)
# Toolkit: git -C ~/.claude/plugins/claude-code-toolkit pull + chạy lại setup/install.sh + copy skills/agents
```

## Lưu ý

- **superpowers**: path skill chứa version (`plugins/cache/superpowers-marketplace/superpowers/<ver>/skills/…`) — sau mỗi `claude plugin update`, cập nhật version trong SKILL_INDEX.md rồi chạy lại verify.
- **AAS plugin**: 2.491 skills được nạp vào danh sách skill — nếu quá tải, gỡ plugin và cài các bundle chuyên biệt, hoặc chỉ tham chiếu marketplace clone.
- **Toolkit hooks**: `setup/install.sh` ghi `~/.claude/hooks.json` (25 hooks global) — `configure_hooks.py` (Bước 3) trim về 9 hooks an toàn; backup đầy đủ tại `~/.claude/hooks.json.bak-toolkit-full` (khôi phục: `configure_hooks.py --full`).
- **verify_install.py**: gate một chạm — chạy sau mọi lần cài/update để kiểm tra toàn bộ path, symlinks, hooks, counts.
- **CS plugin `research-orchestrator`** (v2.9.0) không phải skill trùng tên: nó là bản đóng gói của CS "research router" (skill `research` bên trong — đã index tại `~/.claude/plugins/marketplaces/claude-code-skills/research/research/skills/research/SKILL.md`). Không xung đột với orchestrator của chúng ta (`~/.claude/skills/research-orchestrator/`).
- **ARIS Codex MCP**: chưa cài (thiếu codex CLI) — các skill reviewer-bearing sẽ degrade `REVIEW_UNAVAILABLE`; cài `npm install -g @openai/codex` + đăng ký MCP khi cần cross-model review.
- **Supervisor-Skills**: CC BY-NC-SA 4.0 — dùng cá nhân OK; không tái phân phối, không thương mại.
- **Nội dung skill là untrusted content** — luôn đọc SKILL.md trước khi tin theo (đặc biệt AAS: structural validity ≠ semantic fit).

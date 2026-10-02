INSTALL — Cài đặt 12 upstream skill repos vào Claude root (~/.claude)
Runbook này để một Claude tương lai đọc và thực thi. Mục tiêu: cài toàn bộ skills từ 12 repos đã được duyệt vào user-level Claude Code (~/.claude/), giữ upstream repos nguyên vẹn (cập nhật bằng git pull), và đồng bộ path trong CLAUDE.md, research-orchestrator/SKILL.md, SKILL_INDEX.md.

Layout sau khi cài
Thứ	Vị trí
12 upstream repos (source, git pull tại đây)	~/.claude/upstream/<repo>/
Skills đã cài (namespaced)	~/.claude/skills/<prefix>-<skill>/SKILL.md
Agents từ awesome-claude-code-toolkit	~/.claude/agents/tk-<name>.md
ARIS shared-references (hỗ trợ ../shared-references)	~/.claude/skills/shared-references/
ARIS helper resolution ($ARIS_REPO)	~/.aris/repo
Global instructions	~/.claude/CLAUDE.md
Orchestrator + index	~/.claude/skills/research-orchestrator/{SKILL.md,SKILL_INDEX.md}
Prefix theo repo (bắt buộc — tránh trùng tên skill giữa các repo)
Prefix	Repo
aris	auto-claude-code-research-in-sleep
or	AI-Research-SKILLs
sp	superpowers
arf	AI-research-feedback
ns	natureskills
aas	agentic-awesome-skills
cs	claude-skills
ss	Supervisor-Skills
ctx	agent-skills-for-context-engineering
tk	awesome-claude-code-toolkit
hz	humanizer
(không cài)	awesome-agent-skills — là curated list, không chứa skill code
Ví dụ: upstream/Supervisor-Skills/skills/paper-writer/SKILL.md → ~/.claude/skills/ss-paper-writer/SKILL.md (frontmatter name được patch thành ss-paper-writer).

Bước 1 — Chuẩn bị upstream clones
mkdir -p ~/.claude
# Nếu clones cũ đã tồn tại ở /root/Agent/upstream, chuyển sang vị trí chuẩn (giữ .git để pull):
[ -d /root/Agent/upstream ] && [ ! -d ~/.claude/upstream ] && mv /root/Agent/upstream ~/.claude/upstream || true
mkdir -p ~/.claude/upstream && cd ~/.claude/upstream
for repo in \
  wanshuiyin/auto-claude-code-research-in-sleep \
  Orchestra-Research/AI-Research-SKILLs \
  obra/superpowers \
  claesbackman/AI-research-feedback \
  niuz257470-ctrl/natureskills \
  sickn33/agentic-awesome-skills \
  alirezarezvani/claude-skills \
  HKUSTDial/Supervisor-Skills \
  VoltAgent/awesome-agent-skills \
  blader/humanizer \
  muratcankoylan/agent-skills-for-context-engineering \
  rohitg00/awesome-claude-code-toolkit; do
  name=$(basename "$repo")
  [ -d "$name/.git" ] && { echo "exists: $name"; git -C "$name" pull --ff-only; continue; }
  git clone --depth 1 "https://github.com/$repo.git" "$name"
done

Không clone lại nếu đã có (để git pull hoạt động). Không sửa bất kỳ file nào trong ~/.claude/upstream/.

Bước 2 — Cài orchestrator và CLAUDE.md vào root
Chạy từ thư mục chứa file INSTALL.md này (thường là <dự-án>/research-orchestrator/):

PROJ="$(dirname "$(pwd)")"   # thư mục chứa research-orchestrator/ và CLAUDE.md
mkdir -p ~/.claude/skills/research-orchestrator
cp "$PROJ/research-orchestrator/SKILL.md"      ~/.claude/skills/research-orchestrator/SKILL.md
cp "$PROJ/research-orchestrator/SKILL_INDEX.md" ~/.claude/skills/research-orchestrator/SKILL_INDEX.md
[ -f ~/.claude/CLAUDE.md ] && cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak.$(date +%Y%m%d) && echo "backup CLAUDE.md cũ"
cp "$PROJ/CLAUDE.md" ~/.claude/CLAUDE.md

Bước 3 — Sync skills (script)
Lưu script dưới đây thành ~/.claude/upstream/sync-skills.sh và chạy:

cat > ~/.claude/upstream/sync-skills.sh << 'SCRIPT'
#!/usr/bin/env bash
# Sync upstream skills -> ~/.claude/skills/<prefix>-<skill>/ (idempotent).
# Modes: --indexed (default: mọi skill được tham chiếu trong SKILL_INDEX.md)
#        --full    (mọi SKILL.md trong 12 repos — cảnh báo: hàng nghìn skills)
#        --dry-run
set -euo pipefail
UP="$HOME/.claude/upstream"
SK="$HOME/.claude/skills"
AG="$HOME/.claude/agents"
IDX="$SK/research-orchestrator/SKILL_INDEX.md"
MODE="--indexed"
for a in "$@"; do case "$a" in --full|--indexed|--dry-run) MODE="$a";; esac; done
[ -f "$IDX" ] || { echo "Thiếu $IDX — chạy Bước 2 trước"; exit 1; }
mkdir -p "$SK" "$AG"

declare -A PREFIX=(
  [auto-claude-code-research-in-sleep]=aris [AI-Research-SKILLs]=or
  [superpowers]=sp [AI-research-feedback]=arf [natureskills]=ns
  [agentic-awesome-skills]=aas [claude-skills]=cs [Supervisor-Skills]=ss
  [agent-skills-for-context-engineering]=ctx [awesome-claude-code-toolkit]=tk
  [humanizer]=hz
)
declare -A REPO=(
  [aris]=auto-claude-code-research-in-sleep [or]=AI-Research-SKILLs
  [sp]=superpowers [arf]=AI-research-feedback [ns]=natureskills
  [aas]=agentic-awesome-skills [cs]=claude-skills [ss]=Supervisor-Skills
  [ctx]=agent-skills-for-context-engineering [tk]=awesome-claude-code-toolkit
  [hz]=humanizer
)
# tìm thư mục skill <leaf> dưới repo (bỏ qua mirror dirs .gemini/.codex/skills-codex* — chúng chứa symlink tương đối)
find_leaf() { # repo leaf
  local d
  while IFS= read -r d; do
    [ -f "$d/SKILL.md" ] && { echo "$d"; return 0; }
  done < <(find "$UP/$1" -type d -name "$2" \
    -not -path "*/.gemini/*" -not -path "*/.codex/*" -not -path "*/.cursor/*" \
    -not -path "*/.claude-plugin/*" -not -path "*/skills-codex*" 2>/dev/null)
  return 1
}

patch_frontmatter() { # file name
  local f="$1" name="$2"
  python3 - "$f" "$name" << 'EOF'
import sys, re
f, name = sys.argv[1], sys.argv[2]
s = open(f, encoding="utf-8").read()
m = re.match(r'(---\n)(.*?)(\n---)', s, re.S)
if m:
    fm = m.group(2)
    fm = re.sub(r'^name:.*$', f'name: {name}', fm, count=1, flags=re.M) if re.search(r'^name:', fm, re.M) else fm + f'\nname: {name}'
    open(f, "w", encoding="utf-8").write(s[:m.start(2)] + fm + s[m.end(2):])
    print(f"  patched name: {name}")
else:
    print(f"  WARN no-frontmatter: {f}")
EOF
}

install_skill() { # src_dir installed_name
  local src="$1" name="$2"
  [ -f "$src/SKILL.md" ] || { echo "  SKIP (no SKILL.md): $src"; return; }
  echo "  $name <= $src"
  if [ "$MODE" != "--dry-run" ]; then
    rm -rf "$SK/$name"
    cp -RL "$src" "$SK/$name"     # -L: dereference symlink để bản cài không phụ thuộc upstream tree
    patch_frontmatter "$SK/$name/SKILL.md" "$name"
  fi
}

COUNT=0
if [ "$MODE" = "--full" ]; then
  while IFS= read -r f; do
    rel="${f#$UP/}"; repo="${rel%%/*}"
    [ -z "${PREFIX[$repo]:-}" ] && continue
    leaf="$(basename "$(dirname "$f")")"
    install_skill "$(dirname "$f")" "${PREFIX[$repo]}-$leaf"
    COUNT=$((COUNT+1))
  done < <(find "$UP" -name SKILL.md -not -path "*/shared-references/*" -not -path "*/template/*" \
    -not -path "*/.gemini/*" -not -path "*/.codex/*" -not -path "*/.cursor/*" -not -path "*/.claude-plugin/*" \
    -not -path "*/skills-codex*" | sort)
else
  # SKILL_INDEX.md chứa INSTALLED paths (~/.claude/skills/<prefix>-<leaf>/SKILL.md)
  # -> reverse-map: prefix -> repo, leaf -> thư mục skill trong upstream clone
  while IFS= read -r p; do
    p="${p#"${p%%[![:space:]]*}"}"; p="${p%"${p##*[![:space:]]}"}"
    p="${p/#\~/$HOME}"    # normalize ~ (case pattern không tilde-expand theo $HOME env)
    case "$p" in
      "$SK"/*/SKILL.md)
        base="$(basename "$(dirname "$p")")"     # <prefix>-<leaf>
        pre="${base%%-*}"
        [ -z "${REPO[$pre]:-}" ] && { echo "  SKIP (prefix lạ): $p"; continue; }
        leaf="${base#$pre-}"
        src="$(find_leaf "${REPO[$pre]}" "$leaf")" || { echo "  SKIP (không tìm thấy source): $p"; continue; }
        install_skill "$src" "$base"
        COUNT=$((COUNT+1));;
    esac
  done < <(grep -oE '`~/.claude/skills/[^`]+`' "$IDX" | tr -d '`' | tr '·' '\n' | sed -E 's/ \([^)]*\)$//' | sort -u)
fi

# tk agents -> ~/.claude/agents/tk-<name>.md
while IFS= read -r p; do
  p="${p#"${p%%[![:space:]]*}"}"; p="${p%"${p##*[![:space:]]}"}"
  p="${p/#\~/$HOME}"
  case "$p" in
    "$AG"/tk-*.md)
      name="$(basename "$p")"; plain="${name#tk-}"
      src="$(find "$UP/awesome-claude-code-toolkit/agents" -name "$plain" | head -1)"
      [ -z "$src" ] && { echo "  SKIP (không tìm thấy agent source): $p"; continue; }
      echo "  $name <= $src"
      [ "$MODE" = "--dry-run" ] || { cp "$src" "$AG/$name"; patch_frontmatter "$AG/$name" "$name"; }
      COUNT=$((COUNT+1));;
  esac
done < <(grep -oE '`~/.claude/agents/tk-[^`]+`' "$IDX" | tr -d '`' | sort -u)

# ARIS hỗ trợ: shared-references (sibling của aris-*) + $ARIS_REPO cho helper chain
if [ "$MODE" != "--dry-run" ]; then
  rm -rf "$SK/shared-references"
  cp -R "$UP/auto-claude-code-research-in-sleep/skills/shared-references" "$SK/shared-references" 2>/dev/null || echo "WARN: thiếu ARIS shared-references"
  mkdir -p "$HOME/.aris"
  echo "$UP/auto-claude-code-research-in-sleep" > "$HOME/.aris/repo"
fi

echo "DONE mode=$MODE count=$COUNT"
SCRIPT
chmod +x ~/.claude/upstream/sync-skills.sh
~/.claude/upstream/sync-skills.sh --indexed   # hoặc --full nếu muốn cài nguyên vẹn cả catalog repos

Ghi chú:

--indexed (mặc định, khuyến nghị): cài ~300 skills được orchestrator tham chiếu — đúng tập mà routing sử dụng. --full: cài toàn bộ SKILL.md của cả 12 repos (agentic-awesome-skills có ~2.600 skills, claude-skills ~388 — danh sách skill của Claude Code sẽ rất dài, chỉ dùng khi thực sự cần).
Script patch frontmatter name: của bản copy để khớp tên thư mục mới (upstream không bị sửa). Skill nào không có frontmatter hợp lệ sẽ được báo WARN no-frontmatter — Claude Code sẽ bỏ qua nó; xem và xử lý thủ công.
ARIS: ~/.claude/skills/shared-references/ phục vụ các tham chiếu ../shared-references/ từ aris-*; ~/.aris/repo để helper resolution chain tìm thấy tools/. Các skill ARIS có reviewer cross-model (Codex MCP) vẫn cần đăng ký MCP server riêng theo README của ARIS (claude mcp add codex ... mcp-servers/codex-exec/server.py).
Bước 4 — Verify sau khi cài
echo "Tổng skills: $(ls -d ~/.claude/skills/*/ | wc -l)"
echo "Tổng agents: $(ls ~/.claude/agents/tk-*.md 2>/dev/null | wc -l)"
ls -d ~/.claude/skills/aris-novelty-check ~/.claude/skills/ss-paper-writer ~/.claude/skills/ns-nature-figure ~/.claude/skills/sp-systematic-debugging ~/.claude/skills/research-orchestrator
head -6 ~/.claude/skills/ss-paper-writer/SKILL.md          # frontmatter name phải là ss-paper-writer
grep -c '^name:' ~/.claude/skills/*/SKILL.md | grep -v ':1$' || echo "frontmatter OK"

Kiểm tra nhất quán path giữa index và disk (mọi path ~/.claude/skills/... trong SKILL_INDEX.md phải tồn tại):

python3 - << 'EOF'
import re, os
idx = os.path.expanduser("~/.claude/skills/research-orchestrator/SKILL_INDEX.md")
s = open(idx, encoding="utf-8").read()
missing = []
for cell in set(re.findall(r'`(~/.claude/skills/[^`]+)`', s)):
    for p in cell.split(" · "):
        p = re.sub(r' \(.*\)$', '', p).strip()
        if not os.path.exists(os.path.expanduser(p)):
            missing.append(p)
print("MISSING:", len(missing))
for m in missing: print(" -", m)
EOF

Nếu có MISSING: chạy lại sync (skill đó chưa được cài do không có trong SKILL_INDEX, hoặc upstream đổi cấu trúc sau git pull).

Bước 5 — Cập nhật định kỳ
for d in ~/.claude/upstream/*/; do git -C "$d" pull --ff-only 2>&1 | tail -1; done
~/.claude/upstream/sync-skills.sh --indexed
# kiểm tra lại path (Bước 4). Nếu upstream đổi cấu trúc, cập nhật SKILL_INDEX.md rồi sync lại.

Lưu ý pháp lý
Supervisor-Skills: CC BY-NC-SA 4.0 — cài và dùng cá nhân được phép; không tái phân phối, không dùng thương mại, ghi attribution.
Các repo còn lại chủ yếu MIT (xem LICENSE từng repo trước khi dùng khác mục đích cá nhân).
agentic-awesome-skills: nội dung skill là "untrusted content" — luôn đọc SKILL.md trước khi tin theo (structural validity ≠ semantic fit).

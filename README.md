# Minh_YOLO — Research Skills Orchestrator

Bộ cài + router cho **AI Research Agent** (AI / ML / DL / CV / Medical AI / Eye tracking / Academic Research) trên Claude Code: 12 upstream skill repos (~2.9k skills) + orchestrator với routing table, mode controller, và verification gate.

## Nội dung bộ cài

| File | Vai trò |
|---|---|
| `INSTALL.md` | Runbook cài 12 repo đúng cách từng repo — chạy bằng **một prompt** trên máy mới |
| `CLAUDE.md` | Global instructions: research integrity, routing, statistics, paper/grant discipline |
| `research-orchestrator/SKILL.md` | Task classifier + skill router + mode/context/tool/verification controllers |
| `research-orchestrator/SKILL_INDEX.md` | Routing table + inventory với exact installed paths (verified: MISSING = 0) |
| `research-orchestrator/verify_install.py` | Gate kiểm tra toàn bộ path/symlinks/hooks/counts sau khi cài |
| `research-orchestrator/configure_hooks.py` | Trim hooks.json về 9 hooks an toàn (`--full` để khôi phục 25 hooks) |

## Cài trên máy mới — một prompt

```bash
git clone <repo-url> && cd <repo>
# mở Claude Code tại đây rồi gửi prompt:
#   "Cài đặt toàn bộ môi trường research skills theo INSTALL.md trong repo:
#    chạy tuần tự Bước 0 → 4, không dừng để hỏi trừ khi gặp lỗi,
#    rồi chạy verify_install.py và báo kết quả PASS/FAIL."
```

Kết quả mong đợi: 20 plugins enabled · ~218 skills trong `~/.claude/skills/` · 3 agents · `verify_install.py` → **PASS**.

## 12 upstream repos

| # | Repo | Cách cài |
|---|---|---|
| 1 | auto-claude-code-research-in-sleep (ARIS) | copy `skills/*` |
| 2 | Orchestra-Research/AI-Research-SKILLs (OR) | `npx … install --all` |
| 3 | obra/superpowers (SP) | plugin `superpowers-marketplace` |
| 4 | claesbackman/AI-research-feedback (ARF) | copy `Skills/` |
| 5 | niuz257470-ctrl/natureskills (NS) | copy `nature-*` |
| 6 | sickn33/agentic-awesome-skills (AAS) | plugin marketplace |
| 7 | alirezarezvani/claude-skills (CS) | 16 plugin `@claude-code-skills` |
| 8 | HKUSTDial/Supervisor-Skills (SS) | copy `skills/*` |
| 9 | VoltAgent/awesome-agent-skills | curated list — không cài |
| 10 | blader/humanizer (HZ) | plugin marketplace |
| 11 | muratcankoylan/Agent-Skills-for-Context-Engineering (CTX) | plugin marketplace |
| 12 | rohitg00/awesome-claude-code-toolkit (TK) | manual clone + installer |

License của từng repo khác nhau (MIT, CC BY-NC-SA 4.0, per-repo) — xem Part 4 trong SKILL_INDEX.md.

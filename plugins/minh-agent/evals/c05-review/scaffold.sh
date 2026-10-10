#!/bin/bash
set -euo pipefail
git init -q .
cat > calc.py <<'PYEOF'
def divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b


def discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValueError("percent out of range")
    return price * (1 - percent / 100)
PYEOF
git add calc.py
git -c user.email=eval@example.com -c user.name=eval commit -qm "base: calculator"
cat > calc.py <<'PYEOF'
def divide(a, b):
    return a / b  # removed the zero guard


def discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValueError("percent out of range")
    return price * (1 + percent / 100)  # BUG: adds instead of subtracts


def total(items):
    return sum(item["price"] for item in items)  # BUG: KeyError on missing keys, no default
PYEOF
git add calc.py
git -c user.email=eval@example.com -c user.name=eval commit -qm "refactor discount logic"

#!/bin/bash
set -euo pipefail
git init -q .
printf 'def add(a, b):\n    return a + b\n' > add.py
git add add.py
git -c user.email=eval@example.com -c user.name=eval commit -qm "add helper"
# materialize the diff so the review can run without shell access
git show --stat HEAD > commit_info.txt
printf 'def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a + b  # copy-paste bug: adds instead of subtracts\n' > add.py
git add add.py
git -c user.email=eval@example.com -c user.name=eval commit -qm "add subtract helper"
git diff HEAD~1 HEAD > diff.txt

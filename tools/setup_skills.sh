#!/usr/bin/env bash
# Reclona as skills de terceiros (fora do git) nos commits exatos usados no projeto.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .claude/skills
clone() { [ -d ".claude/skills/$2" ] || git clone -q "https://github.com/$1.git" ".claude/skills/$2"; git -C ".claude/skills/$2" checkout -q "$3"; }
clone Gamezxz/pixel-art-studio pixel-art-studio f8c246635c4621a6c2b427833149afdc3dc3c719
clone mankidev/codixel         codixel          604a9dcbcc4e386bc48188b5f7f49099f5d04db7
clone bradautomates/claude-video claude-video   03ceb42f7fa2c4439aca01752118044baabffb8f
echo "skills ok"

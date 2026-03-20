#!/usr/bin/env bash
set -euo pipefail

# Validate that all depends: entries in SKILL.md frontmatter resolve to existing skill directories.
# Exit 0 if all deps are valid, exit 1 if any are missing.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/../skills" && pwd)"

errors=0
checked=0
skills_count=0

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  skill_md="$skill_dir/SKILL.md"

  if [[ ! -f "$skill_md" ]]; then
    echo "WARN: $skill_name has no SKILL.md"
    continue
  fi

  skills_count=$((skills_count + 1))

  # Extract depends line from frontmatter (between first two ---)
  depends_line=$(awk '/^---$/{n++; next} n==1 && /^depends:/{print; exit}' "$skill_md")

  if [[ -z "$depends_line" ]]; then
    continue
  fi

  # Parse depends: [dep1, dep2, dep3] -> individual deps
  deps=$(echo "$depends_line" | sed 's/depends:\s*\[//; s/\]//; s/,/ /g' | tr -s ' ')

  for dep in $deps; do
    dep=$(echo "$dep" | xargs) # trim whitespace
    if [[ -z "$dep" ]]; then
      continue
    fi
    checked=$((checked + 1))
    if [[ ! -d "$SKILLS_DIR/$dep" ]]; then
      echo "ERROR: $skill_name depends on '$dep' but skills/$dep/ does not exist"
      errors=$((errors + 1))
    fi
  done
done

echo ""
echo "Validated $skills_count skills, checked $checked dependency references."

if [[ $errors -gt 0 ]]; then
  echo "FAILED: $errors unresolved dependencies."
  exit 1
else
  echo "PASSED: All dependencies resolve."
  exit 0
fi

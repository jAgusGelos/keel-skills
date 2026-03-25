# keel-skills — Developer Instructions

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: <skill-name>
   description: |
     <trigger description>
   version: 1.0.0
   category: <reasoning|persistence|development|devops|content|meta>
   depends: [<dep1>, <dep2>]
   ---
   ```

2. If the skill invokes other skills, add those to `depends:` and document the invocation in the SKILL.md body.

3. Update `skills/keel-orchestration/SKILL.md` if the skill participates in cross-invocation chains.

4. Run `./scripts/validate-deps.sh` to verify all dependencies resolve.

## Importing Skills from Other Repos

When copying skills from external repos (e.g., Sentinel's `.claude/skills/`), they often lack the
`version`, `category`, and `depends` fields required by CI. **Always** check and add missing
frontmatter fields before committing. The CI pipeline (`Validate Plugin`) will reject any SKILL.md
missing `name`, `description`, `version`, or `category`.

Quick checklist after importing:
- [ ] `version:` present (use `1.0.0` for new imports)
- [ ] `category:` present (one of: reasoning, persistence, development, devops, content, meta)
- [ ] `depends:` present (list skills it invokes, or `[]` if none)

## Cross-Invocation Rules

Skills should invoke other skills rather than reimplementing overlapping logic. The full routing table lives in `skills/keel-orchestration/SKILL.md`.

## Validation

```bash
./scripts/validate-deps.sh          # Verify all depends resolve
claude plugin validate ./            # Validate plugin structure
claude --plugin-dir ./               # Test locally
```

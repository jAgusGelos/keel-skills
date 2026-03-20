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

## Cross-Invocation Rules

Skills should invoke other skills rather than reimplementing overlapping logic. The full routing table lives in `skills/keel-orchestration/SKILL.md`.

## Validation

```bash
./scripts/validate-deps.sh          # Verify all depends resolve
claude plugin validate ./            # Validate plugin structure
claude --plugin-dir ./               # Test locally
```

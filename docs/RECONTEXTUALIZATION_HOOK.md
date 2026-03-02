# Installing Re-Contextualization Enforcement Hook

## One-Time Setup

Run these commands once to activate the enforcement system:

```bash
# Make hook executable
chmod +x .git-hooks/enforce-recontextualization

# Install as pre-commit hook
cd .git/hooks
ln -sf ../../.git-hooks/enforce-recontextualization pre-commit
cd ../..

# Verify installation
ls -la .git/hooks/pre-commit
```

You should see:
```
.git/hooks/pre-commit -> ../../.git-hooks/enforce-recontextualization
```

## How It Works

1. **On main branch:** Hook does nothing (allows commits)

2. **On feature branch (feat/PX-TXX-*):**
   - Extracts task ID (e.g., P1-T09)
   - Checks for `docs/recontextualization/recontextualization-P1-T09.md`
   - Blocks commit if file missing or incomplete
   - Validates checklist has actual content (not just template)

3. **Required workflow:**
   ```bash
   # After PR merge, pull main
   git checkout main
   git pull origin main

   # Create checklist BEFORE creating feature branch
   cp .git-hooks/checklist-template.md docs/recontextualization/recontextualization-P1-T09.md

   # Fill out checklist with EVIDENCE from previous PR
   # (Review commits, run tests, check coverage, verify criteria)

   # Commit checklist FIRST
   git add docs/recontextualization/recontextualization-P1-T09.md
   git commit -m "chore: complete re-contextualization for P1-T09"

   # NOW create feature branch
   git checkout -b feat/P1-T09-base-html-template

   # Hook will now allow commits on this branch
   ```

## What Gets Checked

- ✅ Checklist file exists for current task
- ✅ Checklist is committed (not just created)
- ✅ Checklist has fewer than 3 unchecked boxes
- ✅ Checklist has fewer than 2 blank fields (marked `___`)

## Bypass (Emergency Only)

```bash
# ONLY use if hook is genuinely broken
git commit --no-verify -m "..."

# This bypasses ALL pre-commit hooks including security scans
# Use ONLY when hook itself has a bug
```

## Testing the Hook

```bash
# Should succeed (main branch)
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test: hook allows main commits"
git reset HEAD~1
rm test.txt

# Should FAIL (feature branch without checklist)
git checkout -b feat/P1-T99-test
echo "test" > test.txt
git add test.txt
git commit -m "test: should be blocked"
# Expected: ❌ BLOCKED: Missing re-contextualization checklist

# Cleanup
git checkout main
git branch -D feat/P1-T99-test
```

## Uninstalling (Not Recommended)

```bash
rm .git/hooks/pre-commit
```

---

**This hook enforces the AUTONOMOUS_DEVELOPMENT_PROMPT.md Phase 0 protocol.**
**It cannot be bypassed without `--no-verify`, which violates CONSTITUTION.md.**

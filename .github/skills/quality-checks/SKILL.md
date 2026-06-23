---
name: quality-checks
description: Handles all test, lint, and quality-check execution for this project — running backend unit tests, Playwright E2E tests, and ESLint; debugging failures; verifying code changes; and validating readiness before commits, pushes, or merges. Use this skill instead of running test, lint, or verification commands (such as run-server-tests.sh, run-e2e-tests.sh, or run-lint.sh) directly.
allowed-tools:
  - shell
---

# Quality Checks

## Quick Reference

| Test Suite | Command | When to Use |
|------------|---------|-------------|
| Backend unit tests | `./scripts/run-server-tests.sh` | After any Python/API change |
| Frontend E2E tests | `./scripts/run-e2e-tests.sh` | After any UI/frontend change |
| Frontend lint | `./scripts/run-lint.sh` | After any TypeScript/Svelte/Astro change |

**Always use the provided scripts** — they handle environment setup, virtual environments, and proper configuration automatically.

---

## Running the Verification Suite

### Backend Unit Tests

```bash
./scripts/run-server-tests.sh
```

- Activates the Python virtual environment
- Runs `python3 -m unittest discover` against `server/tests/`
- Covers Flask routes, SQLAlchemy models, and API responses

### Frontend E2E Tests

```bash
./scripts/run-e2e-tests.sh
```

- Starts the Flask backend (port 5100) and Astro dev server (port 4321)
- Runs all Playwright specs in `client/e2e-tests/`
- Covers home page, game listing/detail pages, accessibility, and API proxy

### Frontend Lint

```bash
./scripts/run-lint.sh
```

- Runs ESLint on all TypeScript, Astro, and Svelte files in `client/`
- Must pass with zero errors before committing

---

## Debugging & Troubleshooting

### Environment / Setup Failures

**Symptom**: `ModuleNotFoundError`, `command not found`, or missing packages.

```bash
# Re-run the full setup (installs Python venv + Node deps)
./scripts/setup-env.sh
```

- Ensure Python 3.11+ is available: `python3 --version`
- Ensure Node 18+ is available: `node --version`
- If `venv` is missing: `python3 -m venv venv && source venv/bin/activate && pip install -r server/requirements.txt`

---

### Port Conflicts

**Symptom**: `Address already in use` on port 5100 or 4321.

```bash
# Find and kill the occupying process
lsof -ti :5100 | xargs kill -9
lsof -ti :4321 | xargs kill -9
```

Then re-run the failing script.

---

### Python / Backend Test Failures

**Symptom**: Test errors or assertion failures in `run-server-tests.sh`.

1. **Read the full traceback** — the first frame usually identifies the root cause.
2. **In-memory database**: Tests use `sqlite:///:memory:` — schema is recreated per test class via `setUp`/`tearDown`. If a model change isn't reflected, ensure `db.create_all()` is called in `setUp`.
3. **Missing fixtures**: Each test class seeds its own data via `_seed_test_data()`. If a test expects data that isn't seeded, add it there.
4. **Import errors**: Verify the model or blueprint is registered in `server/app.py`.
5. **Type errors**: All Python functions require type hints — check `mypy`-style annotations.

Run a single test class for faster iteration:

```bash
source venv/bin/activate && cd server && python3 -m unittest tests.test_games -v
```

---

### Playwright / E2E Test Failures

**Symptom**: Test timeouts, element not found, or screenshot mismatches.

1. **Browser not installed**: Run `cd client && npx playwright install --with-deps chromium` to install browser binaries.
2. **Servers not running**: The E2E script starts servers automatically, but if running tests manually, start both servers first (`./scripts/start-app.sh`).
3. **Locator changed**: If a `data-testid` was renamed or removed, update the spec to match the new attribute.
4. **Flaky test**: If a test fails intermittently, look for hard-coded waits or race conditions. Replace them with auto-retrying web-first assertions (see [playwright.instructions.md](../../instructions/playwright.instructions.md)). **Never use `waitForTimeout`.**
5. **Aria snapshot mismatch**: Re-generate the snapshot with `npx playwright test --update-snapshots`.

Run a single spec for faster iteration:

```bash
cd client && npx playwright test e2e-tests/games.spec.ts
```

---

### Lint Failures

**Symptom**: ESLint errors from `run-lint.sh`.

1. **Auto-fix safe issues**: `cd client && npm run lint -- --fix`
2. **Svelte 4 legacy syntax**: Replace `on:click` with `onclick`, `export let` with `$props()`, `$:` with `$derived`/`$effect`.
3. **TypeScript type errors**: Add missing type annotations or correct incorrect types.
4. **Remaining errors after `--fix`**: Must be resolved manually — do not suppress with `eslint-disable` without justification.

---

### Local vs CI Divergence

**Symptom**: Tests pass locally but fail in CI (or vice versa).

- **Node version mismatch**: Verify `.nvmrc` or `package.json` `engines` field; CI uses Node 20.
- **Python version mismatch**: CI uses Python 3.11. Check `server/requirements.txt` for version-pinned packages.
- **Missing environment variables**: CI sets `API_SERVER_URL`. Locally, defaults to `http://localhost:5100`.
- **Database state**: CI always starts with a clean database. Locally, stale `data/*.db` files can cause conflicts — delete them and restart.

---

## Verification Policy

### Tests Must Pass Before Commit/Merge

- All existing tests must pass before committing changes
- Never skip or disable tests without explicit justification
- Broken tests block merges — fix them, don't ignore them
- Run the full test suite, not just tests for changed code
- New functionality must ship with appropriate test coverage

> [!NOTE]
> This skill covers **running, verifying, and debugging** tests. For **how to author** test code — structure, fixtures, naming, locators, and quality standards — follow the instructions files, which are the single source of truth:
> - Backend (`server/tests/test_*.py`): [unit-tests.instructions.md](../../instructions/unit-tests.instructions.md)
> - Frontend E2E (`client/e2e-tests/*.spec.ts`): [playwright.instructions.md](../../instructions/playwright.instructions.md)

---

## Pre-Commit Checklist

1. Run backend tests: `./scripts/run-server-tests.sh`
2. Run lint (if any frontend files changed): `./scripts/run-lint.sh`
3. Run E2E tests (if UI changed): `./scripts/run-e2e-tests.sh`
4. Verify new functionality has appropriate test coverage
5. Confirm no tests were broken, skipped, or disabled

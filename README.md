# Tailspin Toys

Tailspin Toys is a crowdfunding platform for games with a developer theme. The project is a website for a fictional game crowd-funding company, with a [Flask](https://flask.palletsprojects.com/en/stable/) backend using [SQLAlchemy](https://www.sqlalchemy.org/) and [Astro](https://astro.build/) frontend using [Svelte](https://svelte.dev/) for dynamic pages.

## Getting started

Install dependencies (Python venv, npm packages, Playwright Chromium) once with the setup script. It is idempotent and only installs what is missing or stale, so it is safe to re-run any time:

```bash
./scripts/setup-env.sh
```

Pass `--force` to reinstall everything, or `--with-system-deps` to also install Playwright's OS-level dependencies (Linux only; may require sudo). Use `--scope <server|client|app|e2e|all>` to limit the install to a subset of dependencies (for example `--scope server` installs only the Python venv).

## Launch the site

```bash
./scripts/start-app.sh
```

Then navigate to the [website](http://localhost:4321) to see the site!

## Running tests

```bash
./scripts/run-server-tests.sh   # Flask unit tests
./scripts/run-e2e-tests.sh      # Playwright end-to-end tests
```

Each runner verifies its prerequisites and exits with a remediation message if anything is missing — it will never silently install dependencies on your behalf. Run `./scripts/setup-env.sh` when prompted.

## Linting

The frontend uses ESLint to enforce code quality across TypeScript, Astro, and Svelte files. Run it with:

```bash
./scripts/run-lint.sh
```

ESLint is also run automatically in CI on pull requests to `main`.

## Admin catalog management

Administrators can add, edit, and archive games from the browser at [/admin](http://localhost:4321/admin), reachable from the **Admin sign in** entry in the header menu. The admin area covers:

- Creating a game with a title, description, optional 0–5 star rating, and a publisher and category picked from existing records
- Editing any field of an existing game
- Archiving a game, which hides it from the public catalog while keeping the record
- Restoring an archived game via the **Show archived games** toggle

### Authentication

Admin access is protected by a single shared password held in the session cookie. Two environment variables configure it:

| Variable | Purpose | Development fallback |
| --- | --- | --- |
| `ADMIN_PASSWORD` | Password required to sign in at `/admin` | `tailspin-admin` |
| `FLASK_SECRET_KEY` | Signs the admin session cookie | `dev-only-insecure-secret-key` |

Both fall back to development-only defaults so a fresh clone runs without configuration, and the server logs a warning when it does. **Set both variables before deploying.**

```bash
export ADMIN_PASSWORD='choose-a-strong-password'
export FLASK_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
./scripts/start-app.sh
```

### Admin API endpoints

All write endpoints require an authenticated session and return `401` otherwise.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/login` | Sign in with `{"password": "..."}` |
| `POST` | `/api/logout` | End the admin session |
| `GET` | `/api/session` | Report `{"authenticated": bool}` |
| `POST` | `/api/games` | Create a game |
| `PUT` | `/api/games/<id>` | Update a game |
| `DELETE` | `/api/games/<id>` | Archive a game (soft delete) |
| `POST` | `/api/games/<id>/restore` | Restore an archived game |
| `GET` | `/api/games?includeArchived=true` | List games including archived ones |
| `GET` | `/api/publishers` | List publishers (public, used by admin dropdowns) |
| `GET` | `/api/categories` | List categories (public, used by admin dropdowns) |

### Database schema updates

The project has no migration framework — tables are created by `db.create_all()`, which never alters an existing table. `server/utils/migrations.py` fills that gap: `ensure_schema()` runs at startup and adds any missing columns (such as the `is_archived` flag behind archiving) to databases created before the column existed. It is idempotent, so existing `data/tailspin-toys.db` files are upgraded in place rather than needing to be deleted.

When adding a column to a model, add the matching `ALTER TABLE` statement to `_ADDED_COLUMNS` in that file.

## Copilot Agents & Skills

This project ships two Copilot customizations to assist with quality assurance:

### PR Readiness Agent

The **PR Readiness** agent (`.github/agents/pr-readiness.md`) is a pre-PR quality gate. Invoke it before opening a pull request to:

- Verify all acceptance criteria have been implemented
- Audit test coverage and fill any gaps
- Run the full verification suite (unit tests, lint, E2E tests)
- Manually validate the feature in the browser via Playwright MCP (required for every run)
- Produce a go/no-go report

### quality-checks Skill

The **quality-checks** skill (`.github/skills/quality-checks/SKILL.md`) wraps the project's test and lint scripts with a detailed debugging and troubleshooting runbook. Use it via `/quality-checks` when:

- Running tests or lint for the first time after setup
- Diagnosing test failures (environment issues, port conflicts, flaky tests, CI divergence)
- Validating readiness before commits, pushes, or merges

## License 

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) for the full terms.

## Maintainers 

You can find the list of maintainers in [CODEOWNERS](./.github/CODEOWNERS).

## Support

This project is provided as-is, and may be updated over time. If you have questions, please open an issue.

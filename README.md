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

## Copilot Agents & Skills

This project ships two Copilot customizations to assist with quality assurance:

### PR Readiness Agent

The **PR Readiness** agent (`.github/agents/pr-readiness.md`) is a pre-PR quality gate. Invoke it before opening a pull request to:

- Verify all acceptance criteria have been implemented
- Audit test coverage and fill any gaps
- Run the full verification suite (unit tests, lint, E2E tests)
- Validate UI changes in the browser via Playwright MCP
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

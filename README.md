# Tailspin Toys

Tailspin Toys is a crowdfunding platform for games with a developer theme. The project is a website for a fictional game crowd-funding company, with a [Flask](https://flask.palletsprojects.com/en/stable/) backend using [SQLAlchemy](https://www.sqlalchemy.org/) and [Astro](https://astro.build/) frontend using [Svelte](https://svelte.dev/) for dynamic pages.

## Launch the site

A script file has been created to launch the site. You can run it by:

```bash
./scripts/start-app.sh
```

Then navigate to the [website](http://localhost:4321) to see the site!

## Linting

The frontend uses ESLint to enforce code quality across TypeScript, Astro, and Svelte files. Run it with:

```bash
./scripts/run-lint.sh
```

ESLint is also run automatically in CI on pull requests to `main`.

## Copilot Agents & Skills

This project ships two Copilot customizations to assist with quality assurance:

### QA Reviewer Agent

The **QA Reviewer** (`.github/agents/qa-reviewer.md`) is a pre-PR quality gate. Invoke it before opening a pull request to:

- Verify all acceptance criteria have been implemented
- Audit test coverage and fill any gaps
- Run the full verification suite (unit tests, lint, E2E tests)
- Validate UI changes in the browser via Playwright MCP
- Produce a go/no-go report

### test-runner Skill

The **test-runner** skill (`.github/skills/test-runner/SKILL.md`) wraps the project's test scripts with a detailed debugging and troubleshooting runbook. Use it via `/test-runner` when:

- Running tests for the first time after setup
- Diagnosing test failures (environment issues, port conflicts, flaky tests, CI divergence)
- Writing new backend or frontend tests following project conventions

## License 

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) for the full terms.

## Maintainers 

You can find the list of maintainers in [CODEOWNERS](./.github/CODEOWNERS).

## Support

This project is provided as-is, and may be updated over time. If you have questions, please open an issue.

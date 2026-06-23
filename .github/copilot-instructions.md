# Tailspin Toys Crowd Funding Development Guidelines

This is a crowdfunding platform for games with a developer theme. The application uses a Flask backend API with SQLAlchemy ORM for database interactions, and an Astro/Svelte frontend with Tailwind CSS for styling. Please follow these guidelines when contributing:

## Agent notes

- Explore the project before beginning code generation
- Create todo lists for long operations
  - Before each step in a todo list, reread the instructions to ensure you always have the right directions
- Always use instructions files when available, reviewing before generating code
- Do not generate summary markdown files upon completion of a task
- Always use absolute paths when running scripts and BASH commands
- **NEVER commit or push to main automatically unless explicitly instructed to do so**

## Code standards

### Required Before Each Commit

#### Testing guidelines

- **Always run tests and lint through the `quality-checks` skill — never invoke `run-server-tests.sh`, `run-e2e-tests.sh`, or `run-lint.sh` directly.** The skill wraps environment setup, ordering, and troubleshooting. (Starting the app for manual validation is not a quality check — call `scripts/start-app.sh` directly for that.)
- Run Python tests to ensure backend functionality, and Playwright tests to ensure e2e and frontend functionality
- Run ESLint to check frontend code quality before committing
- Review the existing tests to ensure we're not duplicating efforts
- Test code should be of the same quality as the rest of the project, and follow DRY principles
- For frontend changes, verify the build in the `client` directory (`npm run build`) directly, and run the end-to-end tests through the `quality-checks` skill, to ensure everything works correctly
- When making API changes, update and run the corresponding tests to ensure everything works correctly

#### Project guidelines

- When updating models, ensure database migrations are included if needed
- When adding new functionality, make sure you update the README
- Make sure all guidance in the Copilot Instructions file is updated with any relevant changes, including to project structure and scripts, and programming guidance

### Code formatting requirements

- When writing Python, you must use type hints for return values and function parameters.
- Frontend code (TypeScript, Astro, Svelte) must pass ESLint checks (`scripts/run-lint.sh`)

### Python and Flask Patterns

- Use SQLAlchemy models for database interactions
- Use Flask blueprints for organizing routes
- Follow RESTful API design principles

### Svelte and Astro Patterns

- **Svelte 5 Components**: Use runes-based reactivity (`$state`, `$derived`, `$effect`, `$props`) - see `svelte.instructions.md`
- **Astro Pages**: Use Astro for routing, layouts, and static content - see `astro.instructions.md`
- Create reusable Svelte components when functionality is used in multiple places
- Use `client:load` directive when embedding Svelte in Astro pages for SSR hydration

### Styling

- Use Tailwind CSS utility classes exclusively - see `style.instructions.md`
- Dark theme colors: slate palette (`bg-slate-800`, `text-slate-100`, etc.)
- Rounded corners and modern UI patterns
- Follow modern UI/UX principles with clean, accessible interfaces

### GitHub Actions workflows

- Follow good security practices
- Make sure to explicitly set the workflow permissions
- Add comments to document what tasks are being performed

## Scripts

- **Skills take precedence over scripts.** Before invoking any script directly, check whether a skill covers the task. If one does, load and follow that skill — it may wrap the script with required setup, ordering, or troubleshooting steps.
- Helper scripts live in the `scripts` folder. Use provided scripts rather than relying on a hard-coded list.
- Only fall back to calling a script directly when no skill applies.
- Always prefer an existing script over performing the operation manually.
- `scripts/setup-env.sh` is the single canonical installer for Python, Node, and Playwright browser dependencies. It is idempotent (uses sha256 markers) and supports `--check [scope]`, `--force`, and `--with-system-deps`. Runner scripts (`start-app.sh`, `run-server-tests.sh`, `run-e2e-tests.sh`) call `setup-env.sh --check` to validate prerequisites and exit with a remediation message when anything is missing — they do not install anything themselves.

## Repository Structure

- `server/`: Flask backend code
  - `models/`: SQLAlchemy ORM models
  - `routes/`: API endpoints organized by resource
  - `tests/`: Unit tests for the API
  - `utils/`: Utility functions and helpers
- `client/`: Astro/Svelte frontend code
  - `src/components/`: Reusable Svelte components
  - `src/layouts/`: Astro layout templates
  - `src/pages/`: Astro page routes
    - `src/pages/api/`: Streaming API proxy (catch-all endpoint)
  - `src/styles/`: CSS and Tailwind configuration
  - `src/types/`: TypeScript interfaces (Game, Publisher, Category)
  - `src/config/`: Centralized API configuration
  - `e2e-tests/`: Playwright E2E tests (home, games, accessibility, api-proxy)
- `scripts/`: Development and deployment scripts
- `data/`: Database files
- `README.md`: Project documentation

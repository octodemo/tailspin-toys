# Contributing to Tailspin Toys

[fork]: https://github.com/octodemo/tailspin-toys/fork
[pr]: https://github.com/octodemo/tailspin-toys/compare
[code-of-conduct]: CODE_OF_CONDUCT.md

Thank you for your interest in contributing to Tailspin Toys! Your help is essential for making this crowdfunding platform the best it can be for game creators and backers alike.

Contributions to this project are [released](https://help.github.com/articles/github-terms-of-service/#6-contributions-under-repository-license) to the public under the [project's open source license](LICENSE).

Please note that this project is released with a [Contributor Code of Conduct][code-of-conduct]. By participating in this project you agree to abide by its terms.

## Getting Started

### Prerequisites

Before you can run and test the application locally, you'll need to install:

- **Python 3.10+** - [Download](https://www.python.org/downloads/) | [Homebrew](https://formulae.brew.sh/formula/python@3.11)
- **Node.js 18+** - [Download](https://nodejs.org/) | [Homebrew](https://formulae.brew.sh/formula/node)
- **Git** - [Download](https://git-scm.com/downloads) | [Homebrew](https://formulae.brew.sh/formula/git)

### Setting Up Your Development Environment

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/tailspin-toys.git
   cd tailspin-toys
   ```

2. Run the setup script to install all dependencies:
   ```bash
   ./scripts/setup-env.sh
   ```

3. Start the development servers:
   ```bash
   ./scripts/start-app.sh
   ```

4. Open your browser to [http://localhost:4321](http://localhost:4321)

## Project Structure

- `server/` - Flask backend API with SQLAlchemy ORM
- `client/` - Astro frontend with Svelte components
- `scripts/` - Development and deployment scripts
- `data/` - SQLite database files

## Making Changes

### Backend (Flask/Python)

- Follow RESTful API design principles
- Use type hints for all function parameters and return values
- Add or update tests in `server/tests/` for any API changes
- Run tests before submitting: `./scripts/run-server-tests.sh`

### Frontend (Astro/Svelte)

- Use Svelte 5 runes syntax (`$state`, `$props`, `$derived`)
- Follow the dark theme using Tailwind CSS utility classes
- Add `data-testid` attributes to interactive elements for testing
- Run E2E tests before submitting: `./scripts/run-e2e-tests.sh`

## Submitting a Pull Request

1. Create a new branch from `main` for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the coding standards above

3. Run the test suites to ensure nothing is broken:
   ```bash
   ./scripts/run-server-tests.sh
   ./scripts/run-e2e-tests.sh
   ```

4. Commit your changes with a clear, descriptive message:
   ```bash
   git commit -m "Add feature: brief description of changes"
   ```

5. Push to your fork and [submit a pull request][pr]

6. Wait for your pull request to be reviewed and merged

### Pull Request Guidelines

- Keep your changes focused. If you have multiple unrelated changes, submit them as separate pull requests.
- Write clear commit messages that explain *what* and *why*.
- Update documentation if your changes affect how the application works.
- Ensure all tests pass before requesting a review.
- Be responsive to feedback and ready to make adjustments.

## Reporting Issues

Found a bug or have a feature request? Please [open an issue](https://github.com/octodemo/tailspin-toys/issues/new) with:

- A clear, descriptive title
- Steps to reproduce (for bugs)
- Expected vs. actual behavior
- Screenshots if applicable
- Your environment details (OS, browser, Node/Python versions)

## Resources

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [Using Pull Requests](https://help.github.com/articles/about-pull-requests/)
- [Writing Good Commit Messages](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
- [GitHub Help](https://help.github.com)
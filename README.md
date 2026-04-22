# Tailspin Toys

Tailspin Toys is a crowdfunding platform for games with a developer theme. The project is a website for a fictional game crowd-funding company, with a [Flask](https://flask.palletsprojects.com/en/stable/) backend using [SQLAlchemy](https://www.sqlalchemy.org/) and [Astro](https://astro.build/) frontend using [Svelte](https://svelte.dev/) for dynamic pages.

## Launch the site

A script file has been created to launch the site. You can run it by:

```bash
./scripts/start-app.sh
```

Then navigate to the [website](http://localhost:4321) to see the site!

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/games` | List games (paginated). Supports `page`, `pageSize`, `category`, and `publisher` query params. |
| GET | `/api/games/<id>` | Get a single game by ID |
| GET | `/api/categories` | List all categories with game counts |
| GET | `/api/publishers` | List all publishers with game counts |

### Filtering

The games listing supports filtering by category and/or publisher using their IDs:

```
GET /api/games?category=1&publisher=2&page=1&pageSize=9
```

## Linting

The frontend uses ESLint to enforce code quality across TypeScript, Astro, and Svelte files. Run it with:

```bash
./scripts/run-lint.sh
```

ESLint is also run automatically in CI on pull requests to `main`.

## License 

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) for the full terms.

## Maintainers 

You can find the list of maintainers in [CODEOWNERS](./.github/CODEOWNERS).

## Support

This project is provided as-is, and may be updated over time. If you have questions, please open an issue.

# Tailspin Toys

Tailspin Toys is a crowdfunding platform for games with a developer theme. The project is a website for a fictional game crowd-funding company, with a [Spring Boot](https://spring.io/projects/spring-boot) backend using [Spring Data JPA](https://spring.io/projects/spring-data-jpa) and an [Astro](https://astro.build/) frontend using [Svelte](https://svelte.dev/) for dynamic pages.

## Prerequisites

- **Java 17+** – [Download Temurin](https://adoptium.net/)
- **Node.js 18+** – [Download](https://nodejs.org/)
- **Gradle** – bundled via the Gradle wrapper (`./gradlew`)

## Launch the site

```bash
./scripts/start-app.sh
```

Then navigate to the [website](http://localhost:4321) to see the site!

## Running tests

### Backend (Spring Boot)

```bash
./scripts/run-server-tests.sh
```

### Frontend (Playwright E2E)

```bash
./scripts/run-e2e-tests.sh
```

## Project structure

- `server-java/` – Spring Boot backend API (Java 17, Gradle)
- `client/` – Astro/Svelte frontend
- `scripts/` – Development automation scripts

## License 

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) for the full terms.

## Maintainers 

You can find the list of maintainers in [CODEOWNERS](./.github/CODEOWNERS).

## Support

This project is provided as-is, and may be updated over time. If you have questions, please open an issue.

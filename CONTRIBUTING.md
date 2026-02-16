# Contributing to Quantlix

Thanks for your interest in contributing.

## How to contribute

1. **Fork** the repository
2. **Create a branch** — `git checkout -b feature/your-feature` or `fix/your-fix`
3. **Make changes** — follow existing code style
4. **Test** — run the API and tests locally
5. **Commit** — use clear, descriptive messages
6. **Push** and open a **Pull Request**

## Development setup

```bash
# Start services
docker compose up -d

# API (with reload)
docker compose exec api uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Portal
cd portal && npm install && npm run dev

# CLI
pip install -e .
```

## Code style

- **Python**: Black-compatible, type hints where helpful
- **TypeScript/React**: Prettier, existing patterns in the codebase

## Pull request guidelines

- Keep PRs focused — one feature or fix per PR
- Add tests for new behavior when practical
- Update docs if you change user-facing behavior

## Questions?

Open an issue for bugs, feature requests, or questions.

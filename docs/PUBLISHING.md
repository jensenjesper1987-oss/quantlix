# Publishing Quantlix to PyPI

## Prerequisites

1. **PyPI account** — Create at [pypi.org/account/register](https://pypi.org/account/register/)
2. **API token** — Create at [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/) (scope: entire account or project `quantlix`)
3. **TestPyPI** (optional) — Test first at [test.pypi.org](https://test.pypi.org/)

## Check name availability

```bash
# quantlix might be taken; if so, use quantlix-cli or similar
curl -s https://pypi.org/pypi/quantlix/json | head -5
# 404 = available
```

## Build and publish

```bash
# 1. Install build tools
pip install build twine

# 2. Build the package
python -m build

# 3. Upload to TestPyPI (test first)
twine upload --repository testpypi dist/*

# 4. Upload to PyPI (production)
twine upload dist/*
```

When prompted, use your PyPI username and the API token as the password.

## Environment variables for CI

For GitHub Actions or other CI:

```
TWINE_USERNAME=__token__
TWINE_PASSWORD=pypi-xxxxxxxx  # Your API token
```

## After publishing

Users can install with:

```bash
pip install quantlix
```

For full stack (API, orchestrator) when running the server locally:

```bash
pip install quantlix[full]
```

## Version bumps

Before each release, update `version` in `pyproject.toml`, then rebuild and upload:

```bash
# Edit pyproject.toml: version = "0.1.1"
python -m build
twine upload dist/*
```

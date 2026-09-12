# Contributing to django-statsd

Contributions are welcome. This guide covers the development workflow.

## Quick start

1. Clone and install:

   ```bash
   git clone https://github.com/WoLpH/django-statsd.git
   cd django-statsd
   uv sync --all-extras
   ```

2. Install the git hooks:

   ```bash
   lefthook install
   ```

3. Run the tests:

   ```bash
   uv run pytest
   ```

4. Lint and format:

   ```bash
   uv run ruff check django_statsd tests
   uv run ruff format django_statsd tests
   ```

5. Type-check:

   ```bash
   uv run ty check django_statsd
   ```

## Development workflow

### Prerequisites

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) (package manager)
- [lefthook](https://github.com/evilmartians/lefthook) (git hooks)

### Running the full test suite

```bash
uv run pytest
```

That runs every test with coverage reporting against a minimal Django
project in `tests/`. To run a subset:

```bash
uv run pytest tests/test_middleware.py -x
```

### Running the matrix

tox owns the support matrix, so a local `tox` run is the same one CI
drives. tox-uv provisions any Python you do not have installed.

```bash
tox                  # everything: matrix, lint, type checkers, docs, coverage
tox -e lint          # ruff check and format check
tox -e py313-django61  # a single cell
```

The coverage environment combines the data from every cell and fails
under 100%, so a single cell on its own will report gaps.

### Pre-commit hooks

Lefthook runs these checks in parallel on every commit:

- `ruff check` for linting
- `ruff format` for formatting, which restages what it fixes
- `ty check` for type errors

If a hook fails, fix the issue and commit again.

### Code style

- **Formatter**: ruff, 79-character lines
- **Quotes**: single quotes for all strings, docstrings included
- **Docstrings**: Google style (`Args:`, `Returns:`, `Raises:`)
- **Type hints**: required on every function and method

Four type checkers run in CI, all in strict mode: mypy with
django-stubs, basedpyright, pyrefly and ty. A change has to satisfy all
four.

### Building the documentation

```bash
uv sync --extra docs
uv run sphinx-build -W -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` to preview. The `-W` flag turns
warnings into errors, which is what CI does too.

## Pull request guidelines

1. New functionality needs tests. Coverage is enforced at 100%.
2. Every CI check has to pass: tests, lint, all four type checkers, docs.
3. The change should work on Python 3.10 through 3.14 and Django 5.2,
   6.0 and 6.1.

## Reporting bugs

File issues at <https://github.com/WoLpH/django-statsd/issues>.

Include:

- Your OS, Python version and Django version
- The relevant `STATSD_*` settings and your `MIDDLEWARE` order
- Steps to reproduce
- Expected against actual behaviour

For security issues, follow [SECURITY.md](SECURITY.md) instead of the
public tracker.

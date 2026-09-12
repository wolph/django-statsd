"""Extract and run the code samples in README.md and docs/.

A documentation sample is the first thing a reader copies, so it is
executed like any other test instead of being trusted to stay current.
"""

from __future__ import annotations

import inspect
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from re import (
    Pattern,
    compile as re_compile,
)
from typing import Any, Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
README_PATH: Final[Path] = PROJECT_ROOT / 'README.md'
DOCS_ROOT: Final[Path] = PROJECT_ROOT / 'docs'

#: Only these two languages are executed. Anything else in a fence is
#: left alone.
SUPPORTED_LANGUAGES: Final[frozenset[str]] = frozenset({'bash', 'python'})

#: `pip install django-statsd` has to become an install of this checkout,
#: otherwise the sample would test whatever is currently on PyPI.
INSTALL_REWRITES: Final[dict[str, str]] = {
    'pip install django-statsd': '.',
}

#: Settings whose entries are dotted paths the samples claim exist.
DOTTED_PATH_SETTINGS: Final[frozenset[str]] = frozenset(
    {'INSTALLED_APPS', 'MIDDLEWARE'}
)

MARKDOWN_FENCE: Final[Pattern[str]] = re_compile(
    r'^```(?P<language>[a-zA-Z0-9_+-]*)\s*$'
)
RST_DIRECTIVE: Final[Pattern[str]] = re_compile(
    r'^\.\.\s+code-block::\s*(?P<language>[a-zA-Z0-9_+-]+)\s*$'
)


@dataclass(frozen=True)
class CodeSample:
    """One fenced or directive-introduced code block."""

    source_path: Path
    language: str
    body: str
    block_index: int
    start_line: int

    @property
    def display_path(self) -> str:
        return self.source_path.relative_to(PROJECT_ROOT).as_posix()

    @property
    def location(self) -> str:
        """A `path:line` label, used as the compiled filename."""
        return f'{self.display_path}:{self.start_line}'


def iter_doc_sources() -> tuple[Path, ...]:
    """Every documentation file whose samples are executed."""
    docs = sorted(
        path for path in DOCS_ROOT.rglob('*.rst') if '_build' not in path.parts
    )
    return (README_PATH, *docs)


def extract_samples(path: Path) -> tuple[CodeSample, ...]:
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.md':
        return _extract_markdown(path, text)
    return _extract_rst(path, text)


def runnable_samples(path: Path) -> tuple[CodeSample, ...]:
    return tuple(
        sample
        for sample in extract_samples(path)
        if sample.language in SUPPORTED_LANGUAGES
    )


def _extract_markdown(path: Path, text: str) -> tuple[CodeSample, ...]:
    samples: list[CodeSample] = []
    lines = text.splitlines()
    line_no = 0
    while line_no < len(lines):
        match = MARKDOWN_FENCE.match(lines[line_no])
        if match is None:
            line_no += 1
            continue

        start = line_no + 1
        end = start
        while end < len(lines) and not lines[end].startswith('```'):
            end += 1

        samples.append(
            CodeSample(
                source_path=path,
                language=match.group('language').lower(),
                body='\n'.join(lines[start:end]) + '\n',
                block_index=len(samples),
                start_line=start + 1,
            )
        )
        line_no = end + 1

    return tuple(samples)


def _extract_rst(path: Path, text: str) -> tuple[CodeSample, ...]:
    samples: list[CodeSample] = []
    lines = text.splitlines()
    line_no = 0
    while line_no < len(lines):
        line = lines[line_no]
        match = RST_DIRECTIVE.match(line.strip())
        if match is None:
            line_no += 1
            continue

        indent = len(line) - len(line.lstrip())
        start = _skip_blank_lines(lines, line_no + 1)
        end = _rst_block_end(lines, start, indent)
        samples.append(
            CodeSample(
                source_path=path,
                language=match.group('language').lower(),
                body=textwrap.dedent('\n'.join(lines[start:end])) + '\n',
                block_index=len(samples),
                start_line=start + 1,
            )
        )
        line_no = end

    return tuple(samples)


def _skip_blank_lines(lines: list[str], start: int) -> int:
    index = start
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index


def _rst_block_end(lines: list[str], start: int, indent: int) -> int:
    end = start
    for index in range(start, len(lines)):
        line = lines[index]
        if not line.strip():
            continue
        if len(line) - len(line.lstrip()) <= indent:
            return end
        end = index + 1
    return end


def execute_python_sample(
    sample: CodeSample, namespace: dict[str, Any]
) -> dict[str, Any]:
    """Run one python sample, returning the names it bound."""
    before = set(namespace)
    code = compile(sample.body, sample.location, 'exec')
    exec(code, namespace)
    return {name: namespace[name] for name in set(namespace) - before}


def call_sample_functions(
    defined: dict[str, Any], request: Any
) -> tuple[str, ...]:
    """Call every function a sample defined.

    A sample that only defines a view proves nothing until the view runs,
    so anything taking no arguments or a single `request` is called.
    """
    called: list[str] = []
    for name, value in sorted(defined.items()):
        if not inspect.isfunction(value):
            continue

        parameters = list(inspect.signature(value).parameters)
        if parameters == ['request']:
            value(request)
        elif not parameters:
            value()
        else:
            continue

        called.append(name)

    return tuple(called)


def resolve_dotted(path: str) -> Any:
    """Import a dotted path, module or attribute."""
    try:
        return import_module(path)
    except ImportError:
        module_path, _, attribute = path.rpartition('.')
        module = import_module(module_path)
        if not hasattr(module, attribute):
            raise AssertionError(
                f'{path} is documented but {module_path} has no '
                f'attribute {attribute}'
            ) from None
        return getattr(module, attribute)


def validate_dotted_paths(defined: dict[str, Any]) -> tuple[str, ...]:
    """Import every dotted path an INSTALLED_APPS/MIDDLEWARE sample lists."""
    checked: list[str] = []
    for name in sorted(DOTTED_PATH_SETTINGS & set(defined)):
        for entry in defined[name]:
            resolve_dotted(entry)
            checked.append(entry)

    return tuple(checked)


def validate_statsd_settings(defined: dict[str, Any]) -> tuple[str, ...]:
    """Check every documented STATSD_* name is one the package reads."""
    from django_statsd import settings as statsd_settings

    checked: list[str] = []
    for name in sorted(defined):
        if not name.startswith('STATSD_'):
            continue
        if not hasattr(statsd_settings, name):
            raise AssertionError(
                f'{name} is documented but django_statsd.settings does '
                f'not define it'
            )
        checked.append(name)

    return tuple(checked)


def install_target(command: str) -> str | None:
    """Return the install spec a documented command should really use."""
    return INSTALL_REWRITES.get(command.strip())


class InstallSandboxCache:
    """Build each documented install once and reuse it."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._installed: dict[str, Path] = {}

    def install(self, target: str) -> Path:
        cached = self._installed.get(target)
        if cached is not None:
            return cached

        env_dir = self._root / f'venv-{len(self._installed)}'
        uv = _uv_binary()
        _run([uv, 'venv', '--python', sys.executable, str(env_dir)])
        python = _venv_python(env_dir)
        _run([uv, 'pip', 'install', '--python', str(python), target])
        self._installed[target] = python
        return python


def execute_bash_sample(
    sample: CodeSample, install_cache: InstallSandboxCache
) -> tuple[str, ...]:
    """Run the install commands a bash sample documents."""
    executed: list[str] = []
    for line in sample.body.splitlines():
        command = line.strip()
        if not command or command.startswith('#'):
            continue

        target = install_target(command)
        if target is None:
            raise AssertionError(
                f'{sample.location}: no rule for documented command '
                f'{command!r}'
            )

        python = install_cache.install(target)
        _run([str(python), '-c', _INSTALL_CHECK])
        executed.append(command)

    return tuple(executed)


_INSTALL_CHECK: Final[str] = (
    "from importlib import metadata; print(metadata.version('django-statsd'))"
)


def _uv_binary() -> str:
    uv = shutil.which('uv')
    if uv is None:
        raise AssertionError(
            'uv is needed to build the documentation sandboxes. Run '
            'these tests with `tox -e docs-examples`.'
        )
    return uv


def _venv_python(env_dir: Path) -> Path:
    if sys.platform == 'win32':
        return env_dir / 'Scripts' / 'python.exe'
    return env_dir / 'bin' / 'python'


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        capture_output=True,
        check=False,
        cwd=PROJECT_ROOT,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f'{" ".join(command)} failed with {result.returncode}\n'
            f'stdout:\n{result.stdout}\nstderr:\n{result.stderr}'
        )
    return result

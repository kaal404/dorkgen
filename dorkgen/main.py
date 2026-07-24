"""Process entry point: ``python -m dorkgen`` / the ``dorkgen`` console script."""
from __future__ import annotations

import sys

from . import ui
from .cli import run_interactive, run_noninteractive


def main() -> None:
    argv = sys.argv[1:]
    if argv:
        # Any arguments -> non-interactive scripting mode (`dorkgen generate ...`).
        sys.exit(run_noninteractive(argv))

    try:
        run_interactive()
    except Exception as exc:  # pragma: no cover - top-level safety net
        ui.err_console.print(f"[red]Error: {exc}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()

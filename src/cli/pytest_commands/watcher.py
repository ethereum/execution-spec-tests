"""File watcher implementation for --watch flag functionality."""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict

from rich.console import Console


class FileWatcher:
    """Simple file watcher that re-runs the fill command on changes."""

    def __init__(self, console=None):
        """Initialize the file watcher."""
        self.console = console or Console(highlight=False)

    def run_with_watch(self, args):
        """Watch for file changes and re-run fill command."""
        file_mtimes: Dict[Path, float] = {}

        def get_file_mtimes():
            """Get current modification times of all test files."""
            mtimes = {}
            tests_dir = Path("tests")
            if tests_dir.exists():
                for py_file in tests_dir.rglob("*.py"):
                    try:
                        mtimes[py_file] = py_file.stat().st_mtime
                    except (OSError, FileNotFoundError):
                        pass
            return mtimes

        def run_fill():
            """Run fill command without --watch flag."""
            clean_args = [arg for arg in args if arg != "--watch"]
            cmd = ["uv", "run", "fill"] + clean_args
            result = subprocess.run(cmd)

            if result.returncode == 0:
                self.console.print("[green]✓ Fill completed[/green]")
            else:
                self.console.print(f"[red]✗ Fill failed (exit {result.returncode})[/red]")

        # Setup
        self.console.print("[blue]Starting watch mode...[/blue]")
        file_mtimes = get_file_mtimes()

        # Initial run
        self.console.print("[green]Running initial fill...[/green]")
        run_fill()

        file_count = len(file_mtimes)
        self.console.print(f"[blue]Watching {file_count} files. Press Ctrl+C to stop.[/blue]")

        # Watch loop
        try:
            while True:
                time.sleep(0.5)
                current_mtimes = get_file_mtimes()

                if current_mtimes != file_mtimes:
                    os.system("clear" if os.name != "nt" else "cls")
                    self.console.print("[yellow]File changes detected, re-running...[/yellow]\n")
                    run_fill()
                    file_mtimes = current_mtimes
                    self.console.print("\n[blue]Watching for changes...[/blue]")

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Watch mode stopped.[/yellow]")

"""Launch both the FastAPI backend and the Streamlit frontend.

Usage (from the slowburn directory):
    python run_ui.py

Or start them individually (after activating .venv):
    .venv\\Scripts\\activate
    uvicorn api.main:app --reload --port 8000
    streamlit run ui/app.py --server.port 8501
"""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent


def _venv_python() -> Path:
    """Return the Python executable inside the project .venv, falling back to sys.executable."""
    candidates = [
        ROOT / ".venv" / "Scripts" / "python.exe",   # Windows
        ROOT / ".venv" / "bin" / "python",             # Linux/Mac
    ]
    for p in candidates:
        if p.exists():
            return p
    return Path(sys.executable)


def main() -> None:
    python = _venv_python()

    print("=" * 60)
    print("  SlowBurn UI Launcher")
    print(f"  Python: {python}")
    print("=" * 60)

    api_proc = subprocess.Popen(
        [
            str(python), "-m", "uvicorn",
            "api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ],
        cwd=ROOT,
    )
    print("  FastAPI  ->  http://localhost:8000")
    print("  API docs ->  http://localhost:8000/docs")
    time.sleep(2)

    ui_proc = subprocess.Popen(
        [
            str(python), "-m", "streamlit",
            "run", str(ROOT / "ui" / "app.py"),
            "--server.port", "8501",
            "--server.headless", "false",
        ],
        cwd=ROOT,
    )
    print("  Streamlit -> http://localhost:8501")
    print("=" * 60)
    print("  Press Ctrl+C to stop both servers.")
    print("=" * 60)

    try:
        api_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        api_proc.terminate()
        ui_proc.terminate()
        api_proc.wait()
        ui_proc.wait()
        print("Done.")


if __name__ == "__main__":
    main()

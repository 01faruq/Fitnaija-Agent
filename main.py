"""FitNaija+ CLI entrypoint."""

import sys
import subprocess


def main():
    """Launch the FitNaija+ Streamlit application."""
    cmd = ["streamlit", "run", "app.py"] + sys.argv[1:]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()

"""
Setup virtual environment and install dependencies.
"""

import venv

if __name__ == "__main__":
    venv.create('.env', with_pip=True)
    
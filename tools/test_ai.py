"""Run native MCP integration tests against a selected CMake configuration."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='Release')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
build = root / 'build'
candidates = [build / args.config / 'sharpnesslauncher.exe', build / 'sharpnesslauncher.exe',
              build / args.config / 'sharpnesslauncher', build / 'sharpnesslauncher',
              build / args.config / 'SharpnessLauncher.app/Contents/MacOS/sharpnesslauncher',
              build / 'SharpnessLauncher.app/Contents/MacOS/sharpnesslauncher']
executable = next((path for path in candidates if path.is_file()), None)
if executable is None:
    raise SystemExit('No built Sharpness executable found; compile the selected configuration first.')
os.environ['SHARPNESS_EXE'] = str(executable)
raise SystemExit(subprocess.call([sys.executable, '-m', 'unittest', 'discover', '-s', str(root / 'tests/ai'), '-v']))

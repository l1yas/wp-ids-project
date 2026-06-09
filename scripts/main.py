import subprocess

subprocess.Popen([
    "xfce4-terminal",
    "--hold",
    "-e",
    "python3 detection.py"
])

subprocess.Popen([
    "xfce4-terminal",
    "--hold",
    "-e",
    "python3 dashboard.py"
])

print("IDS Started")

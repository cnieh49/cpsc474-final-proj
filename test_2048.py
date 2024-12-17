import subprocess

for i in range(1, 8):
    subprocess.run(["python3", "game2048.py", "10", str(i)])
    print("------------------------")

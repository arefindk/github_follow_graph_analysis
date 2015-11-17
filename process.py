import subprocess
import sys

if len(sys.argv) > 1:
	programPath = "python"
	scriptPath = sys.argv[1]

	proc = subprocess.Popen([programPath,scriptPath])
	pid = proc.pid
	exitcode = proc.wait()
	print pid

	while not exitcode == 0:
		proc = subprocess.Popen([programPath,scriptPath])
		pid = proc.pid
		exitcode = proc.wait()
		print pid
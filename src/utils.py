import subprocess

# Print an error and exit
def eprint(*args, exit=True, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    if exit:
    	sys.exit(1)

def run(command, error, output=False):
	res = subprocess.run(command, shell=True ,check=True, text=True, capture_output=output)
	if res.returncode != 0:
		eprint(error)
	return str(res.stdout)
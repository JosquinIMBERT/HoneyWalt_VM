import subprocess, sys
from os.path import abspath, dirname, exists, join

# Print an error and exit
def eprint(*args, exit=True, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    if exit:
    	sys.exit(1)

# Get the path to the root of the application
def get_root_path():
	path = abspath(dirname(__file__))
	return "/".join(path.split("/")[:-1])

def run(command, error, output=False):
	res = subprocess.run(command, shell=True ,check=True, text=True, capture_output=output)
	if res.returncode != 0:
		eprint(error)
	return str(res.stdout)

# get the path to a file in the application
def to_root_path(path):
	root_path = get_root_path()
	return join(root_path, path)
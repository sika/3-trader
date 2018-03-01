from pdb import set_trace as BP
import psutil
import os

for proc in psutil.process_iter():
	try:
		# BP()
		pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
	except psutil.NoSuchProcess:
		pass
	else:
	    print(pinfo)
# pgrp = os.getpgrp()
# BP()
# print(pgrp)
# print(os.getpid())

var = 7
while True:
	try:
		BP()
		if os.getpgid(var):
			print(var, 'exist!')
		else:
			print(var, 'does NOT exist!')
	except OSError:
	    print ("ERROR:")

BP()
pass
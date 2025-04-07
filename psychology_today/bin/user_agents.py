import random

def load_user_agents(uafile="psychology_today/bin/user_agents.txt"):
	"""
	uafile : string
		path to text file of user agents, one per line
	"""
	uas = []
	with open(uafile, "r") as uaf:
	   for ua in uaf.readlines():
		   if ua:
			   uas.append(ua.strip())
	random.shuffle(uas)
	return uas

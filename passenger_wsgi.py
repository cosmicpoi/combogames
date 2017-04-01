# import sys, os
# INTERP = os.path.join(os.environ['HOME'], 'combinatoric.games', 'bin', 'python')
# if sys.executable != INTERP:
# 	os.execl(INTERP, INTERP, *sys.argv)
# sys.path.append(os.getcwd())

from app import MyApp as application

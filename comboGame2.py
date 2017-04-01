import copy

def mex(alist):
	current = 0
	mylist = sorted(alist)

	for i in range(len(mylist)):
		if mylist[i]==current:
			current+=1
		if mylist[i]>current:
			return current
	return current

def arrayToString(anarray):
	newstr = ""
	for i in range(len(anarray)-1):
		newstr = newstr + str(anarray[i])+" "
	return newstr+str(anarray[len(anarray)-1])

def getGameKey(agame):
	key = ""
	for i in range(len(agame[0])-1):
		key = key + arrayToString(agame[0][i])+","
	return key + arrayToString(agame[0][len(agame[0])-1])+"|"+arrayToString(agame[1])


class ComboGame(object):
	def __init__(self, newgame):
		self.game = newgame		

	def __str__(self):
		return str(self.game)

	def mexMoves(self):
		self.getPossibleMoves()

		mexlist = []
		for move in self.possiblemoves:
			move.setConns(self.cursor, self.conn)
			mexlist.append(move.getNimValue())
		return mex(mexlist)

	def getNimValue(self):
		'''return sequences defined first, then run through the remaining moves'''
		return mexMoves()

	def setConns(self, acursor, aconn):
		self.conn = aconn
		self.cursor = acursor

class HubSpoke(ComboGame):
	#def __init__ #gonna have to ignore isomorphism for now
	def __str__(self):
		return str(self.game)
	def getNimValue(self):
		self.cursor.execute("SELECT * from NimValues WHERE Game = \""+getGameKey(self.game)+"\";")
		data = self.cursor.fetchone()

		if not (data is None):
			return data[1]

		newnimvalue = self.mexMoves()

		self.cursor.execute("INSERT into NimValues VALUES (\""+getGameKey(self.game)+"\", "+str(newnimvalue)+");")
		self.conn.commit()

		return newnimvalue

	#each game has [adjacency array, values]
	def getPossibleMoves(self):
		moves = []

		# for each leaf...
		for node in range( len(self.game[0]) ):
			if sum(self.game[0][node]) == 1: #then it's a leaf
				for value in range( self.game[1][node]-1 ): #0.... x-2
					newgame = copy.deepcopy(self.game)
					newgame[1][node] = value + 1
					moves.append(HubSpoke(newgame))
				newgame = copy.deepcopy(self.game)
				newgame[0].pop(node)
				newgame[1].pop(node)
				for newrow in newgame[0]:
					newrow.pop(node)
				moves.append(HubSpoke(newgame))

		self.possiblemoves = moves

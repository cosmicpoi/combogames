import copy
from flaskext.mysql import MySQL

#mex of a list: returns the minimum value not in the list
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


#GalesNim class: should probably make a combogame class that implements this
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
		self.cursor.execute("SELECT * from HubSpoke WHERE Game = \""+getGameKey(self.game)+"\";")
		data = self.cursor.fetchone()

		if(len(self.game[1])==1):
			return self.game[1][0]

		if not (data is None):
			return data[1]

		newnimvalue = self.mexMoves()

		self.cursor.execute("INSERT into HubSpoke VALUES (\""+getGameKey(self.game)+"\", "+str(newnimvalue)+");")
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


class GalesNim(ComboGame):
	def __init__(self, newgame):
		super(GalesNim, self).__init__(sorted(newgame)) #isomorphic under ordering

	def getNimValue(self):
		#for speedup, consider loading the whole db into memory each startup
		self.cursor.execute("SELECT * from NimValues WHERE Game = \""+arrayToString(self.game)+"\";")
		data = self.cursor.fetchone()

		if not (data is None):
			return data[1]

		if len(self.game) == 1:
			return 0

		newnimvalue = self.mexMoves()

		self.cursor.execute("INSERT into NimValues VALUES (\""+arrayToString(self.game)+"\", "+str(newnimvalue)+");")
		self.conn.commit()

		return newnimvalue


	def getPossibleMoves(self):
		moves = []

		index=0
		# for number in self.game:
		for index in range(len(self.game)):
			number = self.game[index]

			#for optimization, sort each list first, and also skip duplicate #s (so 2, 2 only has to run half as much)
			for value in [number-i-1 for i in range(number-1)]: #x can go to x-1, x-2 ... 1
				newlist = copy.deepcopy(self.game)
				newlist[index] = value
				moves.append(GalesNim(newlist))

			newlist = copy.deepcopy(self.game) #deep copy is slow, but otherwise you get pointer errors
			newlist.pop(index) #i think this is a little faster than remove()?
			# newlist.remove(number)
			moves.append(GalesNim(newlist))

			index+=1

		self.possiblemoves = moves

def getGameKey(agame):
	key = ""
	for i in range(len(agame[0])-1):
		key = key + arrayToString(agame[0][i])+","
	return key + arrayToString(agame[0][len(agame[0])-1])+"|"+arrayToString(agame[1])


from flask import Flask, render_template, jsonify, request
from comboGame import *
MyApp = Flask(__name__)

MyApp.config['MYSQL_DATABASE_USER'] = 'combogames'
MyApp.config['MYSQL_DATABASE_PASSWORD'] = 'GalesNim'
MyApp.config['MYSQL_DATABASE_DB'] = 'combogames'
MyApp.config['MYSQL_DATABASE_HOST'] = 'mysql.combinatoric.games'

def arrayToString(anarray):
	newstr = ""
	for i in range(len(anarray)-1):
		newstr = newstr + str(anarray[i])+" "
	return newstr+str(anarray[len(anarray)-1])

def stringToArray(astring):
	return [int(segment) for segment in astring.split(" ")]

@MyApp.route("/")
def form():
	return render_template('index.html')

@MyApp.route("/index2")
def form2():
	return render_template('index2.html')

@MyApp.route("/parser.js")
def form3():
	return render_template('parser.js')

# @MyApp.route("/clean_up")
# def clean_up():
# 	mysql = MySQL()
# 	mysql.init_app(MyApp)
# 	conn = mysql.connect()
# 	cursor = conn.cursor()

# 	cursor.execute("select * from NimValues;")
# 	data = cursor.fetchall()
# 	# print data[0][0]
# 	for row in data:
# 		numbers = stringToArray(row[0])
# 		sortednumbers = sorted(numbers)
# 		if (numbers != sortednumbers):
# 			print "found" + row[0]
# 			cursor.execute("delete from NimValues where Game='"+row[0]+"';")

# 	conn.commit();

# 	return jsonify(value = data[0])


@MyApp.route("/_search_val")
def search_val():
	mysql = MySQL()
	mysql.init_app(MyApp)
	conn = mysql.connect()
	cursor = conn.cursor()

	qstring = "select * from NimValues where Game REGEXP '^([0-9] ){"+str(request.args.get('count', 0, type=int)-1)+"}([0-9]+)$' AND Value = "+str(request.args.get('value', 0, type=int))+";";

	cursor.execute(qstring)
	data = cursor.fetchall()

	return jsonify(result = data);



@MyApp.route("/_fill_val")
def fill_val():
	#write a function to query the database for a certain game and returns the value, returns -1 for dne
	#now we can iterate through the list of unique symbols

	mysql = MySQL()
	mysql.init_app(MyApp)
	conn = mysql.connect()
	cursor = conn.cursor()

	key = request.args.get('key', 0, type=str)
	nimval = request.args.get('value', 0, type=int)
	symbolcount = request.args.get('count', 0, type=int)

	solutions = []
	class LoopObj(object):
		def __init__(self):
			self.solutions = []
		def setConns(self, curs, cnx):
			self.cursor = curs
			self.conn = cnx
		def loop(self, args, count, continuing, checkval):
			docontinue=continuing
			iterator = 1
			while docontinue:
				args[count] = iterator

				if count < symbolcount-1:
					docontinue = self.loop(args, count+1, docontinue, checkval)
					return docontinue

				if count==symbolcount-1: #each args inside here is a valid string
					game = key + " " + str(arrayToString(args))
					game = arrayToString(sorted(stringToArray(game)))

					cursor.execute("select * from NimValues where Game='"+game+"'")
					data = cursor.fetchone()

					if (data is None):
						docontinue = False
						return docontinue

					if(data[1]==checkval):
						self.solutions.append(game)
						
				iterator+=1

				
	initargs = []
	for i in range(symbolcount):
		initargs.append(1)

	aloop = LoopObj()
	aloop.setConns(cursor, conn)
	randombool = aloop.loop(initargs, 0, True, nimval)
	retsolns = aloop.solutions
	print len(retsolns)

	return jsonify(result= retsolns)
# def fill_val():
# 	mysql = MySQL()
# 	mysql.init_app(MyApp)
# 	conn = mysql.connect()
# 	cursor = conn.cursor()

# 	qstring = "select * from NimValues where Game REGEXP '"+str(request.args.get('expression', 0, type=str))+"' AND Value = "+str(request.args.get('value', 0, type=int))+";";
# 	print qstring

# 	cursor.execute(qstring)
# 	data = cursor.fetchall()

# 	return jsonify(result = data, result2 = qstring);

@MyApp.route("/_check_val")
def check_val():
	mysql = MySQL()
	mysql.init_app(MyApp)
	conn = mysql.connect()
	cursor = conn.cursor()

	qstring = arrayToString(sorted(stringToArray(request.args.get('game', 0, type=str))))

	cursor.execute("SELECT * from NimValues WHERE Game = \""+qstring+"\";")
	data = cursor.fetchone()

	if not (data is None):
		return jsonify(result = data[1], 
			verified="theorem is "+str(request.args.get('check', 0, type=int)==data[1]))
	else:
		return jsonify(result = "no entry in db", verified = "theorem is False")
	


def keyToGame(astring):
	newgame = [[],[]]
	halves = astring.split("|")
	newgame[1] = stringToArray(halves[1])
	rows = halves[0].split(",")

	for row in rows:
		newgame[0].append(stringToArray(row))

	return newgame	


@MyApp.route('/_hub_spoke')
def hub_spoke():
	mysql = MySQL()

	mysql.init_app(MyApp)
	conn = mysql.connect()
	cursor = conn.cursor()

	spokegame = HubSpoke( keyToGame(request.args.get('game', 0, type=str)))
	spokegame.setConns(cursor, conn)

	thenimvalue = spokegame.getNimValue()

	# print thenimvalue
	# print spokegame.game
	# for move in spokegame.possiblemoves:
	# 	print move

	conn.close
	cursor.close

	return jsonify(result = thenimvalue)

@MyApp.route('/_gales_nim') #this is the nim form
def gales_nim():
	mysql = MySQL()

	mysql.init_app(MyApp)
	conn = mysql.connect()
	cursor = conn.cursor()

	game = GalesNim(stringToArray(request.args.get('game', 0, type=str)))
	game.setConns(cursor, conn) #this is the faulty line

	thenimvalue = game.getNimValue()

	conn.close()
	cursor.close()
	return jsonify(result = thenimvalue)

if __name__ == "__main__":
	MyApp.run()

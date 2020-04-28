from time import *

	#inicjalizacja pakietu
class Packet:
	def __init__(self, data=None):
		if data:
			self.payload = data
			self.decode()
		else:
			self.payload = {
				"Operacja": None,
				"Odpowiedz": "None",
				"Zawartosc": "None",
				"Identyfikator": -1,
				"Czas": -1,
				"IDPakietu": -1,
				"Status": "0"
			}

#sekcja parsera
	def parse(self, data):
		get_key = False
		get_value = False
		keys = []
		values = []
		buff = ''

		for ch in data:
			if ch == '<':
				get_key, get_value = True, False
				if buff: values.append(buff)
				buff = ''
			elif ch == '>':
				get_key, get_value = False, True
				if buff: keys.append(buff)
				buff = ''
			else: buff += ch

		dict_list = {}
		for key, value in zip(keys, values):
			dict_list[key] = value
		return dict_list

	def compress(self):
		compressed = ''
		for key in self.payload:
			compressed += str(key)
			compressed += '>'
			compressed += str(self.payload[key])
			compressed += '<'
		return compressed

#funkcje dodawania do pakietu
	def addOperation(self, operation):
		self.payload["Operacja"] = operation

	def addResponse(self, resp):
		self.payload["Odpowiedz"] = resp

	def addSessionId(self, Id):
		self.payload["Identyfikator"] = Id

	def addTimestamp(self):
		self.payload["Czas"] = int(time())

	def addId(self, ID):
		self.payload["IDPakietu"] = ID

	def addContent(self, content):
		self.payload["Zawartosc"] = content

	def addStatus(self, status):
		self.payload["Status"] = status

#gety z pakietu
	def getOperation(self):
		return self.payload["Operacja"]

	def getResponse(self):
		return self.payload["Odpowiedz"]

	def getSessionId(self):
		return self.payload["Identyfikator"]

	def getTimestamp(self):
		return int(self.payload["Czas"])

	def getId(self):
		return int(self.payload["IDPakietu"])

	def getContent(self):
		return self.payload["Zawartosc"]

	def getStatus(self):
		return self.payload["Status"]

# kodowanie, dekodowanie pakietu do wysylu
	def decode(self):
		self.payload = self.parse( self.payload.decode('utf-8') )
		#print(self.payload)

	def encode(self):
		self.payload = self.compress().encode()
		#print(self.payload)

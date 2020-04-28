import threading
import os

from time import *
from random import randint
from hashlib import md5
from packet import *
from socket import *


#klasa klienta
class Client:
	def __init__(self, address, port):
		self.soc_out = socket(AF_INET, SOCK_DGRAM)
		self.soc_in = socket(AF_INET, SOCK_DGRAM)
		self.port_out = port
		self.port_in = port + 1
		self.address = address

		self.soc_in.bind(('192.168.0.12', self.port_in))

	def recv(self, size):
		data, addr = self.soc_in.recvfrom(size)
		if addr[0] == self.address: return data
		else: return None

	def send(self, data):
		self.soc_out.sendto(data, (self.address, self.port_out))

	def close(self):
		pass

class Server:
	#socket UDP
	_soc = socket(AF_INET, SOCK_DGRAM)

	def __init__(self):
		# liczba polaczen, maksymalne wartosci
		self.conn = 0
		self.MAX_CONN = 4
		self.MAX_DATA = 2**10
		self.MAX_ROOMS = 5
		self.clients = []
		self.rooms = []
		self.magicNumber = 0

		#zwroc pokoj sesji
	def AddRoom(self, ID):
		R = {
			"Id": ID,
			"MaxPlayers": 2,
			"CurrPlayers": 0,
			"Players": [],
			"Room_num": randint(1,20)
		}
		return R

		#zwroc zainicjowanego klienta po stronie serwera
	def AddClient(self, soc, addr):
		C = {
			"Socket": soc,
			"Address": addr,
			"IsConnected": True,
			"Session": str(md5(os.urandom(4)).hexdigest())[0:4],
			"InitNumber": -1,
			"MagicNumber": -1,
			"Chances": -1,
			"Room": -1,
			"Id": 1,
			"Ch_flag": 0
		}
		return C

		#zabij klienta
	def KillClient(self, cl):
		room = cl["Room"]
		cl["Socket"].close()
		cl["IsConnected"] = False
		# Kick player from room
		if not room < 0:
			self.rooms[room]["CurrPlayers"] -= 1
			self.rooms[room]["Players"].remove(cl)
		self.conn -= 1


	def SendGameStartReq(self, client):
		packet = Packet()
		packet.addOperation( "NumberGuess" )
		packet.addSessionId( client["Session"] )
		packet.addId( client["Id"] )
		packet.addStatus( "908" )
		packet.addContent( str(client["Chances"]))
		packet.addTimestamp()
		packet.encode()

		F = open("server.log", "a")
		F.write( packet.payload.decode('utf-8')+'\n' )
		F.close()

		client["Socket"].send( packet.payload )

	#-----------------Handle-Requests-------------------------

	#obsluga pakietu startowego klienta
	def HandleServerHello(self, number, cl):
		error = 0
		if number.isdigit():
			number = int(number)
			if number % 2: error = 2
			else: cl["InitNumber"] = number
		else: error = 1

		packet = Packet()
		packet.addOperation( "RoomChoice" )
		if error == 1:
			packet.addContent( "None" )
			packet.addStatus("905")
		elif error == 2:
			packet.addContent( "None" )
			packet.addStatus("906")
		else:
			packet.addContent("None")
			packet.addStatus("907")

		packet.addSessionId( cl["Session"] )
		packet.addId( cl["Id"] )
		packet.addTimestamp()
		packet.encode()


		F = open("server.log", "a")
		F.write( packet.payload.decode('utf-8')+'\n' )
		F.close()

		cl["Socket"].send( packet.payload )
		if error: self.KillClient(cl)

	#obsluga numeru pokoju przeslana przez klienta
	def HandleRoomChoice(self, number, cl):
		error = 0
		room_full = False
		packet = Packet()
		packet.addOperation( "GameWait" )
		packet.addSessionId( cl["Session"] )
		packet.addId( cl["Id"] )

		#ustawienie numeru bledu w zaleznosci od warunku
		if number.isdigit():
			number = int(number)
			if number > self.MAX_ROOMS - 1 or number < 0:
				error = 3
			else:
				if self.rooms[number]["CurrPlayers"] == 2 : error = 2
				if self.rooms[number]["CurrPlayers"] < self.rooms[number]["MaxPlayers"] and number < self.MAX_ROOMS:
					cl["Room"] = number
					self.rooms[number]["Players"].append(cl)
					self.rooms[number]["CurrPlayers"] += 1

					if self.rooms[number]["CurrPlayers"] == self.rooms[number]["MaxPlayers"]: room_full = True

		else: error = 1

		#sprawdzenie czy sesja jest polaczona i mozna rozpoaczac zgadywanie
		if room_full:
			chances = 0
			mgn = randint(1,20)
			for player in self.rooms[number]["Players"]: chances += player["InitNumber"]
			chances //= self.rooms[number]["MaxPlayers"]

			for player in self.rooms[number]["Players"]:
				if player["Ch_flag"] == 0:
					player["Chances"] = chances
					player["Ch_flag"] = 1
				player["MagicNumber"] = self.rooms[number]["Room_num"]
				self.SendGameStartReq(player)
			return

		#wystepujace bledy
		if error == 0:
			packet.addContent("None")
			packet.addStatus("901")
		elif error == 1:
			packet.addContent("None")
			packet.addStatus("902")
		elif error == 2:
			packet.addContent("None")
			packet.addStatus("903")
		elif error == 3:
			packet.addContent("None")
			packet.addStatus("904")

		packet.addTimestamp()
		packet.encode()

		F = open("server.log", "a")
		F.write( packet.payload.decode('utf-8')+'\n' )
		F.close()

		cl["Socket"].send( packet.payload )
		if error: self.KillClient(cl)

	#obsluga pakietu ze zgadywana liczba
	def HandleGuessNum(self, number, cl):
		error = 0
		packet = Packet()
		packet.addOperation( "NumberGuess" )
		packet.addSessionId( cl["Session"] )
		packet.addId( cl["Id"] )

		if number.isdigit():
			number = int(number)
			guess = True if number == cl["MagicNumber"] else False
		else: error = 1
		cl["Chances"] -= 1

		if guess == True:
			packet.addContent( "None" )
			packet.addStatus("999")
			error = 2
		elif cl["Chances"] < 1:
			packet.addStatus("998")
			packet.addContent( "None" )
			error = 2
		elif error == 1:
			packet.addStatus( "997" )
			packet.addContent("None")
		else:
			packet.addStatus("990")
			packet.addContent( str(cl["Chances"]) )

		packet.addTimestamp()
		packet.encode()

		F = open("server.log", "a")
		F.write( packet.payload.decode('utf-8')+'\n' )
		F.close()

		cl["Socket"].send( packet.payload )
		if error: self.KillClient(cl)

		#odeslanie pakietu potwierdzajacego
	def HandleResponse(self, cl, packet):
		resp_p = Packet()
		resp_p.addOperation( packet.getOperation() )
		resp_p.addContent( packet.getContent() )
		resp_p.addResponse("ACK")
		resp_p.addSessionId( packet.getSessionId() )
		resp_p.addId( packet.getId() )
		resp_p.addTimestamp()
		packet.addStatus("0")
		resp_p.encode()

		F = open("server.log", "a")
		F.write( resp_p.payload.decode('utf-8')+'\n' )
		F.close()

		cl["Socket"].send(resp_p.payload)

	# Client dedicated loop
	def HandleClient(self, Cl):
		while Cl["IsConnected"]:
			#obsluga istniejacych polaczen
			try:
				packet = Packet( Cl["Socket"].recv(1024) )
				data = packet.getContent()

				#Respond with ACK packet
				if packet.getResponse() == "None":
					self.HandleResponse(Cl, packet)

				if packet.getOperation() == "NumberGuess" and packet.getResponse() == "None":
					Cl["Id"] = packet.getId() + 1
					self.HandleGuessNum(data, Cl)
				elif packet.getOperation() == "HelloServer" and packet.getResponse() == "None":
					Cl["Id"] = packet.getId() + 1
					self.HandleServerHello(data, Cl)
				elif packet.getOperation() == "RoomChoice" and packet.getResponse() == "None":
					Cl["Id"] = packet.getId() + 1
					self.HandleRoomChoice(data, Cl)
				else:
					continue

			#zamknij polaczenie w przypadku bledu
			except:
				print("Connection timeout from: {0}".format(Cl["Address"]))
				self.KillClient(Cl)
				self.conn -= 1
				return

		print("Connection finished with: {0}".format(Cl["Address"]))


	#obsluga nowych polaczen
	def HandleNewConnections(self):
		while True:
			if self.conn == self.MAX_CONN:
				continue
			data, addr = Server._soc.recvfrom(1024)
			init_p = Packet(data)
			address = addr[0]
			port = addr[1]

			porcisko = int(init_p.getContent())
			cl = Client(address, porcisko)

			_client = self.AddClient(cl, addr)
			print('Server receieved new connection from: ', _client["Address"])

			#przygotowanie pakietu powitalnego
			packet = Packet()
			packet.addOperation( "HelloClient" )
			packet.addSessionId( _client["Session"] )
			packet.addId( _client["Id"] )
			packet.addContent( "None")
			packet.addStatus("900")
			packet.addTimestamp()
			packet.encode()

			F = open("server.log", "a")
			F.write( packet.payload.decode('utf-8')+'\n' )
			F.close()

			_client["Socket"].send(packet.payload)

			#tworzenie nowego watku dla kazdego klienta
			clientHandle_thread = threading.Thread(target=self.HandleClient, args=(_client,))
			clientHandle_thread.start()
			self.conn += 1


	#start dzialania serwera
	def Start(self):
		print('Server is up and waiting for connections...')
		Server._soc.bind(('192.168.0.12', 31337))

		for _ in range(self.MAX_ROOMS): self.rooms.append( self.AddRoom(_) )
		newConnection_thread = threading.Thread(target=self.HandleNewConnections)
		newConnection_thread.start()

if __name__ == '__main__':
	S = Server()
	S.Start()

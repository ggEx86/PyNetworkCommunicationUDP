import sys
from time import *
from random import randint
from packet import *
from socket import *

#zmienne globalne po stronie klienta
SERVER_IP = '127.0.0.1'
SERVER_PORT = 31337
MY_PORT = -1

	#zwracanie podanej liczby
def getNumber():
	data = input(">> ")
	while not data.isdigit():
		print("Not a number error!")
		data = input(">> ")
	return int(data)

	#lista komunikatow po stronie klienta
def HandleCom(status, content):
	C_list = {
		"0": "None",
		"900": "Let's start with even number!",
		"901": "Joined room, now wait for other players...",
		"902": "Sorry, number is not a digit.",
		"903": "Sorry, room is too busy right now.",
		"904": "Sorry, wrong room number.",
		"905": "Error: Initial value is not type of int!",
		"906": "Error: Initial value is not even!",
		"907": "Ok, now choose your room:\n Room 0:\n Room 1:\n Room 2:\n Room 3:\n",
		"908": "Everybody is ready send me your guess. Your chances: {0}".format(content),
		"990": "Wrong number! Remaining chances: {0}".format(content),
		"997": "Not a number!",
		"998": "No more chances! You lost.",
		"999": "Good number! Congratulations."
	}
	return C_list[status]

class Client:
	#inicjalizacja klienta
	def __init__(self):
		self.port = randint(10000, 20000)
		self.soc_out = socket(AF_INET, SOCK_DGRAM)
		self.soc_in = socket(AF_INET, SOCK_DGRAM)
		self.SessionId = -1
		self.Id = -1

	#wyslanie pakietu rozpoczynajacego z podana liczba klienta
	def SendHelloReq(self, number):
		packet = Packet()
		packet.addOperation("HelloServer")
		packet.addContent( number )
		packet.addSessionId( self.SessionId )
		packet.addId( self.Id )
		packet.addTimestamp()
		packet.addStatus("0")
		packet.encode()

		F = open("client.log", "a")
		F.write( packet.payload.decode('utf-8')+'\n' )
		F.close()

		self.soc_out.sendto(packet.payload, (SERVER_IP, MY_PORT))

	#wyslanie pakietu ze zgadywaną liczba
	def SendNumGuessReq(self, number):
		packet = Packet()
		packet.addOperation("NumberGuess")
		packet.addContent( number )
		packet.addSessionId( self.SessionId )
		packet.addId( self.Id )
		packet.addTimestamp()
		packet.addStatus("0")
		packet.encode()

		F = open("client.log", "a")
		F.write( packet.payload.decode('utf-8')+'\n' )
		F.close()

		self.soc_out.sendto(packet.payload, (SERVER_IP, MY_PORT))

	# wyslanie zapytania o polaczenie sie z pokojem o podanym numerze
	def SendRoomChoice(self, number):
		packet = Packet()
		packet.addOperation("RoomChoice")
		packet.addContent( number )
		packet.addSessionId( self.SessionId )
		packet.addId( self.Id )
		packet.addTimestamp()
		packet.addStatus("0")
		packet.encode()

		F = open("client.log", "a")
		F.write( packet.payload.decode('utf-8')+'\n' )
		F.close()

		self.soc_out.sendto(packet.payload, (SERVER_IP, MY_PORT))

		#polaczenie sie z serwerem
	def ConnectToServer(self):
		try:
			packet = Packet()
			packet.addOperation("ConnInit")
			packet.addContent( self.port )
			packet.addSessionId("None")
			packet.addId("None")
			packet.addTimestamp()
			packet.addStatus("0")
			packet.encode()

			#_port = str(self.port).encode()
			#self.soc_out.sendto(_port, (SERVER_IP, SERVER_PORT))
			self.soc_out.sendto(packet.payload, (SERVER_IP, SERVER_PORT))
			return True
		except:
			print("Can not connect to the server!")
			sys.exit()


			#odeslanie odpowiedzi
	def HandleResponse(self, packet):
		resp_p = Packet()
		resp_p.addOperation( packet.getOperation() )
		resp_p.addContent( packet.getContent() )
		resp_p.addResponse("ACK")
		resp_p.addSessionId( packet.getSessionId() )
		resp_p.addId( packet.getId() )
		resp_p.addTimestamp()
		resp_p.addStatus( packet.getStatus() )
		resp_p.encode()

		F = open("client.log", "a")
		F.write( resp_p.payload.decode('utf-8')+'\n' )
		F.close()

		self.soc_out.sendto(resp_p.payload, (SERVER_IP, MY_PORT))


if __name__ == '__main__':
	# Init client object
	C = Client()
	C.soc_in.bind(('', C.port))
	MY_PORT = C.port + 1
	connection = C.ConnectToServer()
	_option = 'None'
	ACK_flag = 0

	while connection:
		# Get response packet
		packet = Packet( C.soc_in.recv(1024) )
		p_data = HandleCom(packet.getStatus(), packet.getContent())
		stat_n = packet.getStatus()
		C.Id = packet.getId() + 1
		needResponse = True

		#określanie czy wymagana jest odpowiedz na pakiet
		if packet.getResponse() == "ACK":
			ACK_flag = 1
		else:
			ACK_flag = 0

		#Handle respone packet if resp != acks
		if packet.getResponse() == "None":
			C.HandleResponse(packet)

		# Get packet section
		if ACK_flag == 0:
			if packet.getOperation() == "HelloClient":
				_option = "HelloServer"
				C.SessionId = packet.getSessionId()
				print("Current session's ID:" + packet.getSessionId())
				print( p_data )
			elif packet.getOperation() == "NumberGuess":
				_option = "NumberGuess"
				print( p_data )
				# Exit on error response
				if ("999" in stat_n or
					"998" in stat_n or
					"997" in stat_n or
					"906" in stat_n or
					"905" in stat_n):
					sys.exit()
			elif packet.getOperation() == "RoomChoice":
				_option = "RoomChoice"
				print( p_data )
				if ("905" in stat_n or
					"906" in stat_n or
					"999" in stat_n or
					"998" in stat_n or
					"904" in stat_n): sys.exit()
			elif packet.getOperation() == "GameWait":
				_option = "Wait"
				needResponse = False
				print( p_data )
				if ("905" in stat_n or
					"903" in stat_n or
					"902" in stat_n): sys.exit()
			else:
				print("Unknown operation occured:", packet.getOperation())
				sys.exit()

			if needResponse: data = getNumber()
			# Send response section
			if _option == "HelloServer":
				C.SendHelloReq( data )
			elif _option == "NumberGuess":
				C.SendNumGuessReq( data )
			elif _option == "RoomChoice":
				C.SendRoomChoice( data )
			elif _option == "Wait":
				continue
			else:
				break

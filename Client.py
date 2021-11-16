import socket, select, string, sys, time
import pickle
import readline

def prompt():
	sys.stdout.write('->')
	sys.stdout.flush()

if __name__ == '__main__':
	
	if(len(sys.argv) < 3):
		print('Usage: python Client.py hostname port')
		sys.exit()

	host = sys.argv[1]
	port = int(sys.argv[2])

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)

	try:
		s.connect((host, port))
		s.send(pickle.dumps('Client'))
	except:
		print('Unable to connect')
		sys.exit()

	print('Connected to database.')
	# prompt()

	while 1:
		msg = input("Enter your command: \n Usage: read key / write local_port key value \n")
		msg_ = msg.split(' ')
		# check value input
		if msg_[0] == 'read' or msg_[0] == 'write':
			if s.send(pickle.dumps(msg)):
				print('Message sent to database!')
				time.sleep(0.5)

		else:
			print('Invalid input, try again!')
			time.sleep(0.5)

		# socket_list = [sys.stdin, s]

		if msg_[0] == 'read':
			read_sockets, write_sockets, error_sockets = select.select([s], [], [])

			for sock in read_sockets:
				if sock == s:
					# new add
					# data = sock.recv(4096).decode('utf8')
					data = pickle.loads(sock.recv(4096))
					print(msg_[1], 'is', data)
					print('\n')
					time.sleep(1)
					if not data:
						print('\n Disconnected from chat server')
						sys.exit()
					else:
						pass
					#sys.stdout.write(data)
					#prompt()

		# 	else:
		# 		msg = input("Enter your command: ")
		# 		# msg = sys.stdin.readline()
		# 		if s.send(msg.encode('utf8')):
		# 			print('success')
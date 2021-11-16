import socket, select, string, sys, time
import pickle

def broadcast_data(sock, message):
	for socket in CONNECTION_LIST:
		if socket != server_socket and socket != sock:
			try:
				socket.send(message.encode('utf8'))
			except:
				socket.close()
				CONNECTION_LIST.remove(socket)

def broadcast_database(message):
	try:
		time.sleep(1)
		# CONNECTION_LIST[1].send(repr(message).encode('utf8'))
		CONNECTION_LIST[1].send(pickle.dumps(message))
		print('Message sent to middle area')
	except:
		print('Cannot send message')

	if len(CONNECTION_LIST) > 2:
		try:
			time.sleep(30)
			# CONNECTION_LIST[2].send(repr(message).encode('utf8'))
			CONNECTION_LIST[2].send(pickle.dumps(message))
			print('Message sent to west coast')
		except:
			print('Cannot send message')

def dependency_check(message):
	if message == []:
		return True
	# new add
	for m in message:
		database = int(m[2])
		if DATABASE_TIME[database] < int(m[1]):
			return False
	return True

def commit(message):
	data = message.split(' ')
	if data[0] == 'write':
		DICTIONARY[data[2]] = {'From': data[1], 'Value': data[3]}
		DATABASE_TIME[int(data[1])] += 1


if __name__ == '__main__':
	
	CONNECTION_LIST = []
	PENDING = []
	DEPENDENCY = {}
	DICTIONARY = {}
	RECV_BUFFER = 4096
	PORT = 5000

	DATABASE_TIME = {}
	DATABASE_TIME[5000] = 0
	DATABASE_TIME[5001] = 0
	DATABASE_TIME[5002] = 0

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(('0.0.0.0', PORT))
	server_socket.listen(10)

	CONNECTION_LIST.append(server_socket)
	

	print('Database server started on port', PORT)

	while 1:
		
		read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])

		for sock in read_sockets:
			if sock == server_socket:
				sockfd, addr = server_socket.accept()
				CONNECTION_LIST.append(sockfd)

				print('Client (%s, %s) connected' % addr)

				# broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)

			else:
				try:
					print('Receiving data...', sock.getpeername()[1])
					# data = sock.recv(RECV_BUFFER).decode('utf8')
					data = pickle.loads(sock.recv(RECV_BUFFER))
					if data:
						if data[0] == 'D':
							msg = data.split(' ')
							print('Database %i joined.' % int(msg[1]))
							print('Send broadcast')
							broadcast_database('Hello from 5000, east coast')
						elif sock == CONNECTION_LIST[1] or sock == CONNECTION_LIST[2]:
							print('Message from other Databse: ', data)
							if data[0] != 'H':
								print('Doing dependency check')
								if dependency_check(data[0]):
									print('Dependency check pass, update database')
									commit(data[1])
									DATABASE_TIME[5000] += 1
									print('Now database is:')
									print(DICTIONARY)
									while PENDING != []:
										print('Try to commit pending message')
										dep, cmt = PENDING[0][0], PENDING[0][1]
										print(dep)
										print(cmt)
										if dependency_check(dep):
											print('Pending message dependency pass, update database and time')
											commit(cmt)
											DATABASE_TIME[5000] += 1
											print('Now database is:')
											print(DICTIONARY)
											# new add
											print('Time is:')
											print(DATABASE_TIME)
											PENDING.pop(0)
										else:
											print('Pending message dependency fail, do not commit')
											break
								else:
									print('Dependency check fail, hold message')
									# TODO: add this message to pending, each time commit, try to get pending message
									PENDING.append([data[0], data[1]])
									print('Pending message is:')
									print(PENDING)

						else:
							# first time client join
							client = sock.getpeername()[1]
							if data == 'Client':
								print('Create dependency for Client ', client)
								DEPENDENCY[client] = []
							else:
								print('Message receive from ', client, ': ', data)
								print('Prepare current dependency')
								cur_dep = DEPENDENCY[client]

								message = data.split(' ')
								if message[0] == 'write':
									print('Write operation, update dependency, time and dictionary')
									# Update dependency, time and dictionary
									DATABASE_TIME[5000] += 1
									DICTIONARY[message[2]] = {'From': message[1], 'Value': message[3]}
									# new add
									DEPENDENCY[client] = [[message[2], DATABASE_TIME[5000], 5000]]
									broadcast_message = [cur_dep, data]
									print('Send broadcast message to other Database')
									broadcast_database(broadcast_message)

								elif message[0] == 'read':
									print('Read operation, update dependency')
									# TODO: how to update read dependency
									# new add
									msg_time = DATABASE_TIME[int(DICTIONARY[message[1]]['From'])]
									DEPENDENCY[client].append([message[1], msg_time, DICTIONARY[message[1]]['From']])
									read_data = DICTIONARY[message[1]]['Value']
									# new add
									# sock.send(read_data.encode('utf8'))
									sock.send(pickle.dumps(read_data))
									print("Message sent back to client")
					else:
						print('Client', sock.getpeername()[1], 'disconnected!')
						sock.close()
						CONNECTION_LIST.remove(sock)
					# sock.send(b'Database has received data\n')
					# for later usage
					# if data:
					# 	broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)

				except:
					# broadcast_data(sock, "Client (%s, %s) is offline" % addr)
					print("Client (%s, %s) is offline" % addr)
					sock.close()
					CONNECTION_LIST.remove(sock)
					continue

	server_socket.close()
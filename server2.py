from socket import *
import pickle
from transactions import Transaction
from message import Message
from user import User

# Users
UserA = User("A", "A", 10, [])
UserB = User("B", "B", 10, [])
UserC = User("C", "C", 10, [])
UserD = User("D", "D", 10, [])

# Users Dictionary
users = { "A": UserA, "B": UserB, "C": UserC, "D": UserD}

# Server Transaction List (Comfirmed Only)
transactions = []

# UDP Server Setup
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print ('The server is ready to receive')

# Will handle any authentication requests
def authentication_handler(credentials, clientAddress):
	print ("Recived an Authentication Request from Client " + str(clientAddress))
	# attempt to authenticate client
	username = credentials.data.username
	password = credentials.data.password
	if (users.get(username) == None):
		isValidCredentials = False
	else:
		isValidCredentials = (users.get(username).username == username) and (users.get(username).password == password)
	# send client response based on authentication success or failure
	if (not isValidCredentials):
		# print to server
		print ("Failed to Authenticate client: " + str(clientAddress))
	if (isValidCredentials):
		# print to server
		print ("Authentication Successful! Client: " + str(clientAddress) + ", User: " + credentials.data.username)
		
  	# send client authentication value in Message
	isAuthenticated = Message("server", "auth", isValidCredentials)
	isAuthenticated = pickle.dumps(isAuthenticated)
	serverSocket.sendto(isAuthenticated, clientAddress)
 
	return isValidCredentials

def updateClientUser():
	# update balance and transactions
	client_message, clientAddress = serverSocket.recvfrom(2048)    
	updatedClient = pickle.loads(client_message)
	updatedClient.balance = users[updatedClient.username].balance
	updatedClient.transactions = users[updatedClient.username].transactions
	 
  	# send updated client value in Message
	clientUser = Message("server", "update", updatedClient)
	clientUser = pickle.dumps(clientUser)
	serverSocket.sendto(clientUser, clientAddress)

	print ("Client User Data has been updated!")

def menu2(menu2_option, clientAddress):
	# handle menu2 option
	option = menu2_option.data[0]
	username = menu2_option.username

	if (option == "1"):
		# print server message
		print("Client: " + str(clientAddress) + " User " + username + " sent a transaction request.")
		# process transaction request from client
		temp_transaction = menu2_option.data[1]
		# print temp_transaction data to server
		print ("Transactions Data Recived: \n" + str(temp_transaction))

		isVaildTransaction = False

		# check client balance for sufficent funds
		# if client balance is less than the transfer amount then transaction is rejected
		if (users[username].balance < temp_transaction.transfer_amount):
			print ("User " + username + " transaction request failed. Insufficient Balance.")
			temp_transaction.status = 3
			users[username].transactions.append(temp_transaction)
			serverSocket.sendto(pickle.dumps(Message("server", "tx", isVaildTransaction)), clientAddress)
		# if client balance is equal to transfer amount or less than transfer amount
		# then the transaction request is vaild
		if (users[username].balance >= temp_transaction.transfer_amount):
			# print to server that the transaction is vaild
			print ("Vaild Transaction Request. Updating Balances.")

			# update Payer balance
			users[username].balance -= temp_transaction.transfer_amount

			# update Payee1 balance
			users[temp_transaction.payee1].balance += temp_transaction.received_amount_payee1

			# update Payee2 balance
			if (temp_transaction.payee2 != "0"):
				users[temp_transaction.payee2].balance += temp_transaction.received_amount_payee2

			# Update Temp Transaction Status from Temp (1) to Comfirmed (2)
			temp_transaction.status = 2

			# Update Server Transaction List
			transactions.append(temp_transaction)

			# Update client transactions
			users[username].transactions.append(temp_transaction)

			# Update Payee1 transactions
			users[temp_transaction.payee1].transactions.append(temp_transaction)

			# Update Payee2 transactions
			if (temp_transaction.payee2 != "0"):
				users[temp_transaction.payee2].transactions.append(temp_transaction)

			print ("User " + username + " transaction request succsessful!")

			# update transaction vaild value
			isVaildTransaction = True
			serverSocket.sendto(pickle.dumps(Message("server", "tx", isVaildTransaction)), clientAddress)

			# Update Client's balance and transactions
			updateClientUser()
	if (option == "2"):
		# print server message
		print("Client: " + str(clientAddress) + " User " + username + " has view their data.")
		updateClientUser()
	if (option == "3"):
		# print server message
		print("Client: " + str(clientAddress) + " User " + username + " has logged out.")

while True:
	client_message, clientAddress = serverSocket.recvfrom(2048)
	client_message = pickle.loads(client_message)
	# check message type
	if (client_message.type == "auth"):
		isAuthenticated =  authentication_handler(client_message, clientAddress)
		# Update user balance and transactions list if authenticated
		if (isAuthenticated):
			updateClientUser()
	
	if (client_message.type == "menu2"):
		# Menu 2 loop
		menu2(client_message, clientAddress)

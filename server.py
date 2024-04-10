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

# Users List
users = [UserA, UserB, UserC, UserD]

# Dictionaries
userIndex = {
	"A": 0,
	"B": 1,
	"C": 2,
	"D": 3
}

# Comfirmed Transactions (TX) List
transactions = []

# UDP Server Setup
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print ('The server is ready to receive')

def authenticate():
	# Authentication flag to either let user access server or login to server
	isAuthenticated = False
	
	# Authentication Loop
	while not isAuthenticated:
		# Recive username as message form client user
		username_message, clientAddress = serverSocket.recvfrom(2048)
		 
		# Recive password as message form client user
		password_message, clientAddress = serverSocket.recvfrom(2048)
		print ("Recived an Authentication Request from User " + username_message.decode())
		
		# Authenticate User
		for index, user in enumerate(users):
			if user.username == username_message.decode() and user.password == password_message.decode():
				isAuthenticated = True
		
		# If Authentication Failed
		if not isAuthenticated:
			serverSocket.sendto("False".encode(), clientAddress)
			serverSocket.sendto("Authentication Failed. :(".encode(), clientAddress)
			print ("Failed to Authenticate User " + username_message.decode())
			authentication_menu_option_message, clientAddress = serverSocket.recvfrom(2048)
			authentication_menu_option_message = authentication_menu_option_message.decode()
			if (authentication_menu_option_message == "1"):
				print ("Recived an Authentication Request from User " + username_message.decode())
			if (authentication_menu_option_message == "2"):
				print ("User " + username_message.decode() + " has quit program.")
				break;
		# If Authentication was successful
		if isAuthenticated:
			serverSocket.sendto("True".encode(), clientAddress)
			serverSocket.sendto(("Authentication Successful!\nCurrent Balance: " + str(users[userIndex[username_message.decode()]].balance) + " BTC").encode(), clientAddress)
			serverSocket.sendto(str(users[userIndex[username_message.decode()]].balance).encode(), clientAddress)
			user_transactions = pickle.dumps(users[userIndex[username_message.decode()]].transactions)
			serverSocket.sendto(user_transactions, clientAddress)
			print ("User " + username_message.decode() + " is Authenticated!")
			break
	return username_message.decode()

def menu(username):
# Authenticated User Options Loop
	while 1:
		options_message, clientAddress = serverSocket.recvfrom(2048)
		option = options_message.decode()
		
		# Handle Transaction requests
		if (option == "Authentication"):
			username = authenticate()
			menu(username)
			break
		if (option == "1"):
			print("User " + username + " sent a transaction request.")
			temp_transaction, clientAddress = serverSocket.recvfrom(2048)
			temp_transaction = pickle.loads(temp_transaction)
			print ("Transactions Data Recived: \n" + str(temp_transaction))
			
			# Check if User has a sufficent balance
			# Transfer amount cannot excede balance
			# If balance is sufficent then update Payer, Payee1 (and Payee2) Balance
			# In users list
			
			if (users[userIndex[username]].balance < temp_transaction.transfer_amount):
				print ("User " + username + " transaction request failed. Insufficient Balance.")
				serverSocket.sendto("False".encode(), clientAddress)
			if (users[userIndex[username]].balance >= temp_transaction.transfer_amount):
				print ("Updating Balances.")
				# Update Payer Balance
				users[userIndex[username]].balance -= temp_transaction.transfer_amount
				# Update Payee1 Balance
				users[userIndex[temp_transaction.payee1]].balance += temp_transaction.received_amount_payee1
				# Update Payee2
				if (temp_transaction.payee2 != "0"):
					users[userIndex[temp_transaction.payee2]].balance += temp_transaction.received_amount_payee2
				
				# Update Temp Transaction Status from Temp (1) to Comfirmed (2)
				temp_transaction.status = 2
				# Add Transaction to comfired transactions list
				transactions.append(temp_transaction)
				# Add Transaction to Payer Transactions List
				users[userIndex[username]].transactions.append(temp_transaction)
				# Add Transaction to Payee1 Transactions List
				users[userIndex[temp_transaction.payee1]].transactions.append(temp_transaction)
				# Add Transaction to Payee2 Transactions List
				if (temp_transaction.payee2 != "0"):
					users[userIndex[temp_transaction.payee2]].transactions.append(temp_transaction)
				
				print ("User " + username + " transaction request succsessful!")
				serverSocket.sendto("True".encode(), clientAddress)
				# Send client updated balance
				serverSocket.sendto(str(users[userIndex[username]].balance).encode(), clientAddress)
			
		# Handle Transactions List requests
		if (option == "2"):
			print ("User " + username + " has requested transactions list.")
			user_transactions = pickle.dumps(users[userIndex[username]].transactions)
			serverSocket.sendto(user_transactions, clientAddress)
			serverSocket.sendto(str(users[userIndex[username]].balance).encode(), clientAddress)
		# Handle User Logout
		if (option == "3"):
			
			print ("User " + username + " has logged out.")
			break;

#Program Loop
while 1:
	whichLoop_message, clientAddress = serverSocket.recvfrom(2048)
	if (whichLoop_message.decode() == "Authentication"):
		username = authenticate()
  
	if (whichLoop_message.decode() == "Menu"):
		menu(username)
	
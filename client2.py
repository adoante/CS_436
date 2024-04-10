from socket import *
import pickle
from transactions import Transaction
from message import Message
from user import User

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

client = User("0", "0", 0, [])

transactionID = {
	"A": 100, 
	"B": 200, 
	"C": 300, 
	"D": 400
}

def authenticate():
	# ask user for username and password
	username = input("Enter Username: ")
	password = input("Enter Password: ")
	# Set client username and password
	client.username = username
	client.password = password
	
	# create message for server
	credentials = Message(username, "auth", client)
	credentials = pickle.dumps(credentials)
	# send server message
	clientSocket.sendto(credentials, (serverName, serverPort))
	# receive authentication response from server
	server_message, serverAddress = clientSocket.recvfrom(2048)
	# print server response
	server_message = pickle.loads(server_message)
	isAuthenticated = server_message.data
	if (isAuthenticated):
		print ("Authentication Successful!")
		return True
	else:
		print ("Authentication Failed!")
		return False

def updateClient():
	clientUser = Message(client.username, "update", client)
	clientUser = pickle.dumps(clientUser)
	# send server message
	clientSocket.sendto(clientUser, (serverName, serverPort))
	# receive server message with updated user balance and transactions
	server_message, serverAddress = clientSocket.recvfrom(2048)
	# check server message type
	server_message = pickle.loads(server_message)
	if (server_message.type == "update"):
		client.balance = server_message.data.balance
		client.transactions = server_message.data.transactions
	else:
		print ("Invalide Message Type: " + server_message.type + ". Expected 'update'.")
		return False
	
	print ("User Data has been updated!")
	return True

# authentication loop
while True:
	# request Server for authentication
	# is the user authenticated by the sever
	isAuthenticated = authenticate()
	# exit authentication loop if authentication was successful
	if (isAuthenticated):
		break
	# if authentication failed ask user to try again or quit
	else:
		# Menu 1
		print ("(1) Try Again \n(2) Quit")
		tryAgainQuit = input("Enter Number: ")
		# Handle Menu 1 Response
		if (tryAgainQuit == "1"):
			continue
		# if user quits break out of program loop
		elif (tryAgainQuit == "2"):
			# notifiy server that client has quit
			quit()

# client was authenticated successfully
# set client balance and client transactions list based on server values
if (updateClient()):
	print ("Current Balance: " + str(client.balance)  + " BTC")
	print ("id | payer | transfer amount | payee1 | payee1 amount | payee2 | payee2 amount | status |")
	for tx in client.transactions:
			print (str(tx.id) + " | " + tx.payer + " | " + str(tx.transfer_amount) + " | " + tx.payee1  + " | " + str(tx.received_amount_payee1) + " | " + tx.payee2 + " | " + str(tx.received_amount_payee2) + " | " + str(tx.status) + " |")
else:
	quit()

# menu 2 loop

idCount = transactionID[client.username] - 1

while True:
	# Menu 2

	# ask user to pick an option from the menu using numbers
	print ("(1) Make a Transaction\n(2) Fetch and display the list of transactions\n(3) Quit the Program")
	print ("Current Balance: " + str(client.balance))
	menu2_option = input("Enter Number: ")

	# Handle Menu 2 Response
	if (menu2_option == "1"):
		# ask user for Transaction data
  
		# how much does the client want to transfer
		transfer_amount = int(input("How much to transfer?: "))

		# used to change the payee1 and payee2 options in the printed out text
		payee1Options = {
			"A": "1. B, 2. C, 3. D", 
			"B": "1. A, 2. C, 3. D", 
			"C": "1. A, 2. B, 3. D", 
			"D": "1. A, 2. B, 3. C"
		}

		payee2Options = {
			"AB": "1. C, 2. D",
			"AC": "1. B, 2. D",
			"AD": "1. B, 2. C",
		 	"BA": "1. C, 2. D",
			"BC": "1. A, 2. D",
			"BD": "1. A, 2. C",
		  	"CA": "1. B, 2. D",
			"CB": "1. A, 2. D",
			"CD": "1. A, 2. B",
		  	"DA": "1. B, 2. C",
			"DB": "1. A, 2. C",
			"DC": "1. A, 2. B",
		}

		# who will be payee1 the option will not include the client user
		payee1 = input("Who will be Payee1? " + payee1Options[client.username] + ": ")
		# how much will payee1 recieve from the transfer amount
		received_amount_payee1 = int(input("How much will Payee1 receive?: "))

		# initially there is no payee2
		payee2 = "0"
		received_amount_payee2 = 0

		# if the amount payee1 will receive is greater than the transfer amount
		# then the client is asked to enter again
		# if it is equal then there is no payee2 and countine program
		# if the amount payee1 will receive is less than the transfer amount
		# then there is a payee2 and prompt client for payee2 data
		while 1:
			if (received_amount_payee1 > transfer_amount):
				print("Transfer Amount: " + str(transfer_amount))
				print("Enter a number equal to or less than Transfer Amount.")
				received_amount_payee1 = int(input("How much will Payee1 receive?: "))
			if (received_amount_payee1 == transfer_amount):
				print ("Payee1 will receive: " + str(transfer_amount))
				break
			if (received_amount_payee1 < transfer_amount):
				payee2 = input("Who will be Payee2? " + payee2Options[client.username + payee1] + ": ")
				received_amount_payee2 = transfer_amount - received_amount_payee1
				print ("Payee2 will receive: " + str(received_amount_payee2))
				break

		# set the status of the transaction to temporary (1)
		status = 1

		# set the transaction id
		# if this is the first transaction then the id starts with A:100, B:200, C:300, D:400
		idCount = idCount + 1

		# create Transaction using data given by user
		temp_transaction = Transaction(idCount, client.username, transfer_amount, payee1, received_amount_payee1, status, payee2, received_amount_payee2)

		# create Message for server containing menu2_option and a Transaction
		menu2_message = Message(client.username, "menu2", (menu2_option, temp_transaction))
		menu2_message = pickle.dumps(menu2_message)
		# send server message
		clientSocket.sendto(menu2_message, (serverName, serverPort))

		# recieve server messsage to update client data
		server_message, clientAddress = clientSocket.recvfrom(2048)
		isVaildTransaction = pickle.loads(server_message)
		if (isVaildTransaction.data):
			updateClient()
			print ("Transaction was Successful!")
		else:
			print ("Transaction Failed!")
			print ("Current Balance: " + str(client.balance))

	elif (menu2_option == "2"):
		# create Message for server
		menu2_message = Message(client.username, "menu2", (menu2_option, None))
		menu2_message = pickle.dumps(menu2_message)
		# send server message
		clientSocket.sendto(menu2_message, (serverName, serverPort))
		updateClient()
		print ("Current Balance: " + str(client.balance)  + " BTC")
		print ("id | payer | transfer amount | payee1 | payee1 amount | payee2 | payee2 amount | status |")
		for tx in client.transactions:
	  		print (str(tx.id) + " | " + tx.payer + " | " + str(tx.transfer_amount) + " | " + tx.payee1  + " | " + str(tx.received_amount_payee1) + " | " + tx.payee2 + " | " + str(tx.received_amount_payee2) + " | " + str(tx.status) + " |")
	elif (menu2_option == "3"):
		# create Message for server
		menu2_message = Message(client.username, "menu2", (menu2_option, None))
		menu2_message = pickle.dumps(menu2_message)
		# send server message
		clientSocket.sendto(menu2_message, (serverName, serverPort))
		break
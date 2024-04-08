from socket import *
import pickle
from transactions import Transaction

transactions = []
username = "0"
balance = 0

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)

#  Authentication Flag to let user access server or prompt user to try again
isAuthenticated = "False"

# Authentication Loop
while isAuthenticated == "False":
	
	# Send Username to Server for Authentication
	username_message = input("Enter Username: ")
	username = username_message
	clientSocket.sendto(username_message.encode(),(serverName, serverPort))
	if (username_message == "quit"):
		break

	# Send Password to Server for Authentication
	password_message = input("Enter Password: ")
	clientSocket.sendto(password_message.encode(),(serverName, serverPort))
	if (password_message == "quit"):
		break
 
	# Get isAuthenticated Value From Server
	isAuthenticated_message, serverAddress = clientSocket.recvfrom(2048)
	isAuthenticated = isAuthenticated_message.decode()
 
	# Set Balance
	if (isAuthenticated == "True"):
		server_balance, serverAddress = clientSocket.recvfrom(2048)
		balance = int(server_balance.decode())
  
 	# Print authentication message to User
	authentication_message, serverAddress = clientSocket.recvfrom(2048)
	print (authentication_message.decode())

# Dictionaries
transactionID = {
	"A": 100, 
	"B": 200, 
	"C": 300, 
	"D": 400
}

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

# Program Loop
while isAuthenticated == "True":
	print ("(1) Make a Transaction\n(2) Fetch and display the list of transactions\n(3) Quit the Program")
	menu_option = input("Enter Number: ")
	clientSocket.sendto(menu_option.encode(),(serverName, serverPort))
	
	if (menu_option == "1"):
		id = 0
		transfer_amount = int(input("How much to transfer?: "))
		payee1 = input("Who will be Payee1? " + payee1Options[username] + ": ")
		received_amount_payee1 = int(input("How much will Payee1 receive?: "))
		payee2 = "0"
		received_amount_payee2 = 0
		while 1:
			if (received_amount_payee1 > transfer_amount):
				print("Transfer Amount: " + str(transfer_amount))
				print("Enter a number equal to or less than Transfer Amount.")
				received_amount_payee1 = int(input("How much will Payee1 receive?: "))
			if (received_amount_payee1 == transfer_amount):
				print ("Payee1 will receive: " + str(transfer_amount))
				break
			if (received_amount_payee1 < transfer_amount):
				payee2 = input("Who will be Payee2? " + payee2Options[username + payee1] + ": ")
				received_amount_payee2 = transfer_amount - received_amount_payee1
				print ("Payee2 will receive: " + str(received_amount_payee2))
				break  
		status = 1
		if (len(transactions) == 0):
			id = transactionID[username]
		else:
			id = transactions[len(transactions) - 1].id + 1
		
		temp_transaction = Transaction(id, username, transfer_amount, payee1, received_amount_payee1, status, payee2, received_amount_payee2)
		transactions.append(temp_transaction)
		clientSocket.sendto(pickle.dumps(temp_transaction), (serverName, serverPort))
		print ("Transaction Request sent!")
  
		# Recieve Transaction Request Status
		isProcessed, serverAddress = clientSocket.recvfrom(2048)
		isProcessed = isProcessed.decode()
		if (isProcessed == "False"):
			# Update Transaction Status from Temp (1) to Rejected (3)
			transactions[len(transactions) - 1].status = 3
			print ("Transfer Request was rejected. Insufficent Balance.")
			print ("Current Balance: " + str(balance))
		if (isProcessed == "True"):
			# Update Transaction Status from Temp (1) to Comfired (3)
			transactions[len(transactions) - 1].status = 2
			print ("Transfer Request was comfired!")
			# Update client balance
			server_balance, serverAddress = clientSocket.recvfrom(2048)
			balance = int(server_balance.decode())
			print ("Current Balance: " + str(balance))
   
	if (menu_option == "2"):
		user_transactions, serverAddress = clientSocket.recvfrom(2048)
		current_balance, serverAddress = clientSocket.recvfrom(2048)
		print ("Current Balance: " + current_balance.decode() + " BTC")
		print ("Transactions List: \n" + str(pickle.loads(user_transactions)))
		
	if (menu_option == "3"):
		print ("Quiting Program")
		break

clientSocket.close()
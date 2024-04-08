from socket import *
import pickle
from transactions import Transaction

# Server User Class
class User:
    def __init__(self, username, password, balance, transactions):
        self.username = username
        self.password = password
        self.balance = balance
        self.transactions = transactions
           
def authenticate(username, password, users):
    for index, user in enumerate(users):
        if user.username == username and user.password == password:
            return True
    return False

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

# Program Loop

while 1:
    # Authentication flag to either let user access server or login to server
    isAuthenticated = False
    
    # Authentication Loop
    while not isAuthenticated:
        # Recive username as message form client user
        username_message, clientAddress = serverSocket.recvfrom(2048)
        
        if (username_message.decode() == "quit"): 
            print ("User has quit the client program.")
            break      
         
        # Recive password as message form client user
        password_message, clientAddress = serverSocket.recvfrom(2048)
        print ("Recived an Authentication Request from User " + username_message.decode())
        
        if (password_message.decode() == "quit"): 
            print ("User has quit the client program.")
            break
        
        # Authenticate User
        isAuthenticated = authenticate(username_message.decode(), password_message.decode(), users)
        
        # If Authentication Failed
        if not isAuthenticated:
            serverSocket.sendto("False".encode(), clientAddress)
            serverSocket.sendto("Authentication Failed. :(\nEnter Username and Password again.\nOr Quit Program (Enter 'quit').".encode(), clientAddress)
            print ("Failed to Authenticate User " + username_message.decode())
        
        # If Authentication was successful
        if isAuthenticated:
            serverSocket.sendto("True".encode(), clientAddress)
            serverSocket.sendto(str(users[userIndex[username_message.decode()]].balance).encode(), clientAddress)
            serverSocket.sendto(("Authentication Successful!\nCurrent Balance: " + str(users[userIndex[username_message.decode()]].balance) + " BTC").encode(), clientAddress)
            print ("User " + username_message.decode() + " is Authenticated!")
            break
    
    # Authenticated User Options Loop
    while isAuthenticated:
        options_message, clientAddress = serverSocket.recvfrom(2048)
        option = options_message.decode()
        
        # Handle Transaction requests
        if (option == "1"):
            print("User " + username_message.decode() + " sent a transaction request.")
            temp_transaction, clientAddress = serverSocket.recvfrom(2048)
            temp_transaction = pickle.loads(temp_transaction)
            print ("Transactions Data Recived: \n" + str(temp_transaction))
            
            # Check if User has a sufficent balance
            # Transfer amount cannot excede balance
            # If balance is sufficent then update Payer, Payee1 (and Payee2) Balance
            # In users list
            
            if (users[userIndex[username_message.decode()]].balance < temp_transaction.transfer_amount):
                print ("User " + username_message.decode() + " transaction request failed. Insufficient Balance.")
                serverSocket.sendto("False".encode(), clientAddress)
            if (users[userIndex[username_message.decode()]].balance >= temp_transaction.transfer_amount):
                print ("Updating Balances.")
                # Update Payer Balance
                users[userIndex[username_message.decode()]].balance -= temp_transaction.transfer_amount
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
                users[userIndex[username_message.decode()]].transactions.append(temp_transaction)
                # Add Transaction to Payee1 Transactions List
                users[userIndex[temp_transaction.payee1]].transactions.append(temp_transaction)
                # Add Transaction to Payee2 Transactions List
                if (temp_transaction.payee2 != "0"):
                    users[userIndex[temp_transaction.payee2]].transactions.append(temp_transaction)
                
                print ("User " + username_message.decode() + " transaction request succsessful!")
                serverSocket.sendto("True".encode(), clientAddress)
                # Send client updated balance
                serverSocket.sendto(str(users[userIndex[username_message.decode()]].balance).encode(), clientAddress)
            
        # Handle Transactions List requests
        if (option == "2"):
            print ("User " + username_message.decode() + " has requested transactions list.")
            user_transactions = pickle.dumps(users[userIndex[username_message.decode()]].transactions)
            serverSocket.sendto(user_transactions, clientAddress)
            serverSocket.sendto(str(users[userIndex[username_message.decode()]].balance).encode(), clientAddress)
        # Handle User Logout
        if (option == "3"):
            
            print ("User " + username_message.decode() + " has logged out.")
            break;
            

from socket import *
import pickle

# Server User Class
class User:
    def __init__(self, username, password, balance, transactions):
        self.username = username
        self.password = password
        self.balance = balance
        self.transactions = transactions
        
class Transaction:
    def __init__(self, id, payer, transfer_amount, payee1, received_amount_payee1, status, payee2=None, received_amount_payee2=0):
        self.id = id
        self.payer = payer
        self.transfer_amount = transfer_amount
        self.payee1 = payee1
        self.received_amount_payee1 = received_amount_payee1
        self.status = status
        self.payee2 = payee2
        self.received_amount_payee2 = received_amount_payee2
    
    def __str__(self):
        return (f"TX: id = '{self.id}', payer = '{self.payer}', transfer_amount = '{self.transfer_amount}', payee1 = '{self.payee1}', received_amount_payee1 = '{self.received_amount_payee1}', payee2 = '{self.payee2}', received_amount_payee2 = '{self.received_amount_payee2}', status = '{self.status}'")
    
    def __repr__(self):
        return (f"TX: id = '{self.id}', payer = '{self.payer}', transfer_amount = '{self.transfer_amount}', payee1 = '{self.payee1}', received_amount_payee1 = '{self.received_amount_payee1}', payee2 = '{self.payee2}', received_amount_payee2 = '{self.received_amount_payee2}', status = '{self.status}'")
    
def authenticate(username, password, users):
    for index, user in enumerate(users):
        if user.username == username and user.password == password:
            return True, users[index]
    return False, User("0","0", 0, [])

def storeTransactions(transactions, user):
    comfirmed_transactions = []
    for index, users in enumerate(transactions):
        if (transactions[index].payer == user and transactions[index].status == 2):
            comfirmed_transactions.append(transactions[index]) 

# Users
UserA = User("A", "A", 10, [])
UserB = User("B", "B", 10, [])
UserC = User("C", "C", 10, [])
UserD = User("D", "D", 10, [])

# Users List
users = [UserA, UserB, UserC, UserD]

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
    
    # Most Recent User on Server
    currentUser = User("0","0", 0, [])
    
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
        isAuthenticated, currentUser = authenticate(username_message.decode(), password_message.decode(), users)
        
        # If Authentication Failed
        if not isAuthenticated:
            serverSocket.sendto("Authentication Failed. :(\nEnter Username and Password again.\nOr Quit Program (Enter 'quit').".encode(), clientAddress)
            serverSocket.sendto("False".encode(), clientAddress)
            print ("Failed to Authenticate User " + username_message.decode())
        
        # If Authentication was successful
        if isAuthenticated:
            serverSocket.sendto(("Authentication Successful!\nCurrent Balance: " + str(currentUser.balance) + " BTC").encode(), clientAddress)
            serverSocket.sendto("True".encode(), clientAddress)
            print ("User " + username_message.decode() + " is Authenticated!")
            break
    
    # Authenticated User Options Loop
    while isAuthenticated:
        options_message, clientAddress = serverSocket.recvfrom(2048)
        option = options_message.decode()
        
        if (option == "1"):
            print("User " + currentUser.username + " sent a transaction request.")
        if (option == "2"):
            print ("User " + currentUser.username + " has requested transactions list.")
            user_transactions = pickle.dumps(currentUser.transactions)
            serverSocket.sendto(user_transactions, clientAddress)
            serverSocket.sendto(str(currentUser.balance).encode(), clientAddress)
        if (option == "3"):
            print ("User " + currentUser.username + " has logged out.")
            break;
            

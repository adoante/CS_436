# Server User Class
class User:
	def __init__(self, username, password, balance, transactions):
		self.username = username
		self.password = password
		self.balance = balance
		self.transactions = transactions
  
	def __str__(self):
		return (f"User: username = '{self.username}', password = '{self.password}', balance = '{self.balance}', transactions = '{self.transactions}'")

	def __repr__(self):
		return (f"User: username = '{self.username}', password = '{self.password}', balance = '{self.balance}', transactions = '{self.transactions}'")

	def __getstate__(self):
		return self.__dict__
	
	def __setsate__(self, d):
		self.__dict__ = d
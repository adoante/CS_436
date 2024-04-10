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
    
    def __getstate__(self):
        return self.__dict__
    
    def __setsate__(self, d):
        self.__dict__ = d
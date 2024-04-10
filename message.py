class Message:
    def __init__(self, username, type, data):
        self.username = username
        self.type = type
        self.data = data
    
    def __str__(self):
        return (f"Message: User = '{self.username}', Type = '{self.type}', Data = '{self.data}'")
    
    def __repr__(self):
        return (f"Message: User = '{self.username}', Type = '{self.type}', Data = '{self.data}'")  
    
    def __getstate__(self):
        return self.__dict__
    
    def __setsate__(self, d):
        self.__dict__ = d
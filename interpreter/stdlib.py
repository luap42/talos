import re

class Error:

    isError = True
    isConc = False

    def __init__(self, type, msg):
        self.msg = msg
        self.type = type
    
    def printMessage(self):
        print(" ERROR ")
        print("=======")
        print("During program execution")
        print("occured this error:")
        print("Type: "+self.type)
        print("Message: "+self.msg)
        print("HALT execution.")
        
class ConcreteWrapper:
    
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
        
    @staticmethod
    def froms(s):
        s_ = s
        s = s.split(".")
        if len(s) > 2 or not re.match("[0-9]+(\.[0-9]+)?", s_):
            return Error("InvalidNumberError", "CONCRETE Number may only contain one dot.")
        elif len(s) == 2:
            a = int(s[0])
            b = int(s[1])
            c = len(s[1])
        else:
            a = int(s_)
            b = c = 0
        return Token("CONCRETE", ConcreteWrapper(a, b, c))
        
    def __float__(self):
        return self.a + (self.b*(0.1**self.c))
        
    def add(self, other):
        a = self.a + other.a
        diff_c = abs(self.c-other.c)
        max_c = max(self.c, other.c)
        thisone = self.c == max_c
        if thisone:
            ob = other.b * 10**diff_c
            sb = self.b
        else:
            ob = other.b
            sb = self.b * 10**diff_c
        b = ob+sb
        
        return Token("CONCRETE", ConcreteWrapper(a, b, max_c))
        
    def sub(self, other):
        a = self.a - other.a
        diff_c = abs(self.c-other.c)
        max_c = max(self.c, other.c)
        thisone = self.c == max_c
        if thisone:
            ob = other.b * 10**diff_c
            sb = self.b
        else:
            ob = other.b
            sb = self.b * 10**diff_c
        b = sb-ob
        
        return Token("CONCRETE", ConcreteWrapper(a, b, max_c))
        
    def mul(self, other):
        return ConcreteWrapper.froms(str(float(self)*float(other)))
    def div(self, other):
        return ConcreteWrapper.froms(str(float(self)/float(other)))
        

class SymbolTable:
    
    def __init__(self):
        self.table = {}
        
    def __getitem__(self, i):
        return self.table[i]
        
    def __delitem__(self, i):
        del self.table[i]
        
    def __hasitem__(self, i):
        return i in self.table.keys()
        
    def __setitem__(self, i, v):
        self.table[i] = v
        
    def __repr__(self):
        return repr(self.table)
    
class Random:
    
    def __init__(self):
        self.x = 1
        
    def get(self):
        return self.x
    
    def next(self):
        self.x += 1

class Token:

    isError = False
    
    def __init__(self, type_, value=""):
        self.type = type_
        self.value = value
        
    def __repr__(self):
        value = self.value
        if self.type != "INSTANCE":
            return self.type + "("+str(value)+")"
        else:
            return self.type + "("+str(self.object)+")"
        
def open_file(fn):
    data = open(fn, "r").read()
    return data
    return data
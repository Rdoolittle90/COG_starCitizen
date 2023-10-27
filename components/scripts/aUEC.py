class aUEC:
    def __init__(self, value:float=0) -> None:
        self.value:float = value

    def __add__(self, other):
        if type(other) == aUEC:
            return aUEC(self.value + other.value)
        else:
            return aUEC(self.value + float(other))

    def __sub__(self, other):
        if type(other) == aUEC:
            return aUEC(self.value - other.value)
        else:
            return aUEC(self.value - float(other))

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other

    def __str__(self) -> str:
        return f"{format(int(self.value), ',')} aUEC"
    
    def __int__(self):
        return int(self.value)
   
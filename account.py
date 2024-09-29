


class Token:
    def __init__(self, address="", buy_price=0, current_price=0, percent=0, price_5min=0,value = 0,buy_time = 0):
        self.address = address
        self.buy_price = buy_price
        self.current_price = current_price
        self.percent = percent
        self.price_5min = price_5min
        self.buy_time = buy_time
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.address == other.address
        return False

    def __hash__(self):
        return hash(self.address)

class Account:
    def __init__(self, address="", tokens=None,balance = 0,favorite="No"):
        self.address = address
        self.tokens = tokens if tokens is not None else []
        self.balance = balance
        self.favorite = favorite

    def find_token(self, f_token):
        for token in self.tokens:
            if token == token:
                return token
        return None

    def have_token(self, token_address):
        for token in self.tokens:
            if token.address == token_address:
                return True
        return False

    def remove_token(self,r_token):
        if r_token.value <= 0:
            self.tokens.remove(r_token)
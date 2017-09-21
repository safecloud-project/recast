import gfshare

class ShamirDriver:

    def __init__(self, n_blocks, threshold):
        self.threshold = threshold
        self.n_blocks = n_blocks

    def encode(self, data):
        shares = gfshare.split( self.n_blocks, self.threshold, data)
        encoded = map(lambda (x, y): str(x)+"<-->"+y, shares)
        return encoded

    def decode(self, data):
        rec_data = map(lambda x: (int(x.split('<-->')[0]),x.split('<-->')[1]), data)
        return gfshare.combine(rec_data)

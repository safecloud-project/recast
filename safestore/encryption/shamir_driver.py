from secretsharing import PlaintextToHexSecretSharer


class ShamirDriver:

    def __init__(self, n_blocks, threshold):
        self.threshold = threshold
        self.n_blocks = n_blocks

    def encode(self, data):
        share = PlaintextToHexSecretSharer.split_secret
        return share(data, self.threshold, self.n_blocks)

    def decode(self, data):
        unshare = PlaintextToHexSecretSharer.recover_secret
        return unshare(data)

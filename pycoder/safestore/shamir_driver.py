from secretsharing import PlaintextToHexSecretSharer

class ShamirDriver:

    def __init__(self, n_blocks, threshold):
        self.threshold = threshold
        self.n_blocks = n_blocks

    def encode(self, data):
        share = PlaintextToHexSecretSharer.split_secret
        temp_data = data
        res_data = []
        while len(temp_data) > 100:
            aux_data = temp_data[:100]
            res_data.append(aux_data)
            temp_data = temp_data[100:]

        res_data.append(temp_data)
        secrets = []

        for div_data in res_data:
            secrets.append(share(div_data, self.threshold, self.n_blocks))
        return [item for sublist in secrets for item in sublist]

    def decode(self, data):
        unshare = PlaintextToHexSecretSharer.recover_secret

        blocks = []
        for i in range(0, len(data), 3):
            current_block = data[i:i + 3]
            blocks.append(unshare(current_block))

        return ''.join(blocks)

from bip_utils import Bip39SeedGenerator, Bip44Coins, Bip44, base58, Bip44Changes
from mnemonic import Mnemonic


class Wallet():
    def __init__(self, coin_type=Bip44Coins.SOLANA) -> None:
        self.coin_type = coin_type

    def create_solana_wallet(self):
        mnemo = Mnemonic('english')
        random_mnemonic = mnemo.generate(strength=128)
        mnemo.check(random_mnemonic)
        address, pk = self.get_address_pk(random_mnemonic, "")
        return random_mnemonic, address, pk

    def get_address_pk(self, mnemonic, password):
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate(password)
        if self.coin_type != Bip44Coins.SOLANA:
            bip44_mst_ctx = Bip44.FromSeed(seed_bytes, self.coin_type).DeriveDefaultPath()
            return bip44_mst_ctx.PublicKey().ToAddress(), bip44_mst_ctx.PrivateKey().Raw().ToHex()
        else:
            bip44_mst_ctx = Bip44.FromSeed(seed_bytes, self.coin_type)

            bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
            bip44_chg_ctx = bip44_acc_ctx.Change(
                Bip44Changes.CHAIN_EXT)
            priv_key_bytes = bip44_chg_ctx.PrivateKey().Raw().ToBytes()
            public_key_bytes = bip44_chg_ctx.PublicKey().RawCompressed().ToBytes()[1:]
            key_pair = priv_key_bytes + public_key_bytes

            return bip44_chg_ctx.PublicKey().ToAddress(), base58.Base58Encoder.Encode(key_pair)

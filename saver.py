import pandas as pd
from account import Account,Token

def read_accounts_excel(path):
    df = pd.read_excel(path)
    accounts_dict = {}
    for _, row in df.iterrows():
        account_address = row['Account Address']
        token = Token(
            address=row['Token Address'],
            buy_price=row['Buy Price'],
            current_price=row['Current Price'],
            percent=row['Percent'],
            price_5min=row['Price 5min']
        )

        if account_address in accounts_dict:
            accounts_dict[account_address].token.append(token)
        else:
            accounts_dict[account_address] = Account(account_address, [token])
    accounts = list(accounts_dict.values())
    return accounts

async def save_accounts_exel(accounts,path):
    data = []
    for account in accounts:
        for token in account.token:
            data.append({
                "Account Address": account.address,
                "Token Address": token.address,
                "Buy Price": token.buy_price,
                "Current Price": token.current_price,
                "Percent": token.percent,
                "Price 5min": token.price_5min
            })
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
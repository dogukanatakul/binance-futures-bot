from binance.client import Client

client = Client("SjlxXktwDHd1h7Nrg9HnAQM4oJ7R8tu9H7joAEJM9mPc79RWkj0qDMviby1wb7Zq", "KWyjvXX4lkMBtlwIj9R4BIJkpLgYcfwNfFIiSUemojroJaEgDLgGsnz7rfb4CHYG", {"timeout": 40})

print(client.get_account_status())


# print(client.get_account_api_permissions())
# {'ipRestrict': False, 'createTime': 1650271865000, 'tradingAuthorityExpirationTime': 1658016000000, 'enableReading': True, 'enableInternalTransfer': False, 'enableFutures': True, 'permitsUniversalTransfer': True, 'enableVanillaOptions': True, 'enableSpotAndMarginTrading': True, 'enableWithdrawals': False, 'enableMargin': False}

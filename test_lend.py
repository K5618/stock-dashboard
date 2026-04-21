import json

with open('twse_lend.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
bal, prev = 0, 0
for r in d.get('data', []):
    bal += int(str(r[12]).replace(',', ''))
    prev += int(str(r[8]).replace(',', ''))
print('TWSE sum shares:', bal)
print('TWSE bal (張):', bal // 1000)
print('TWSE change (張):', (bal - prev) // 1000)

try:
    with open('tpex_sbl.json', 'r', encoding='utf-8') as f:
        dtpex = json.load(f)
    tbal, tprev = 0, 0
    for r in dtpex:
        tbal += int(str(r.get('SecuritiesBorrowingBalanceOfTheMarketDay', 0)).replace(',', ''))
        tprev += int(str(r.get('SecuritiesBorrowingBalancePreviousDay', 0)).replace(',', ''))
    print('TPEX sum shares:', tbal)
    print('TPEX bal (張):', tbal // 1000)
    print('TPEX change (張):', (tbal - tprev) // 1000)
except Exception as e:
    print('TPEX Error', e)

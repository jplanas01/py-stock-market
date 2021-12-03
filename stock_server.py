from stocks import Transaction, TransType
from market import Market
from banker import Banker, StockOwner
import random

import pdb
b = Banker()
m = Market(b)
for i in range(20):
	b.add_person(10000, 50)

for i in range(1000):
	type = random.choice([TransType.BID, TransType.ASK])
	t = Transaction(type, int(random.gauss(50, 10)), random.randint(1, 100), random.randint(0, 20 - 1))
	m.add_order(t)
	m.fulfill_single()
print(sorted(m.bids_list.queue))
print(sorted(m.asks_list.queue))
print(' '.join([str(b.owners[x]) for x in b.owners]))

a = m.bids_list.queue[0]
owner_id = m.bids[a[1]].owner_id
print(m.bids[a[1]], b.owners[owner_id])
m.del_order(a[1])
print(m.bids[m.bids_list.queue[0][1]], b.owners[owner_id])
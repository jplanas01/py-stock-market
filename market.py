from stocks import Transaction, TransType
import queue
import heapq
import copy

class Market(object):
	"""Market implementation. It receives transaction objects and matches bids and
	asks to each other, filling the orders first by best price and second by age
	(oldest first).
	It is worth noting that bids are kept internally with a negative price, care is 
	taken to ensure the banker does not see this implementation detail.
	"""
	def __init__(self, banker):
		"""Create a new Market. banker should be a class implementing charge_pending,
		charge_proper, refund, can_ask, can_bid, and person_exists. The Market does
		not check whether a Transaction is valid (ie, enough money, enough stock, 
		owner exists, etc), this is delegated to the Banker. The Market assumes the 
		results from the Banker are valid.
		"""
		self.bids = {}
		self.asks = {}
		self.bids_list = queue.PriorityQueue()
		self.asks_list = queue.PriorityQueue()
		self.ids = -1
		self.banker = banker
	
	def _insert_new_item(self, items_list, items_map, item):
		"""Inserts a new transaction into the given queue and map, assigns ID"""
		self.ids += 1
		item.id = self.ids
		items_map[self.ids] = item
		
		items_list.put((item.price, item.id, item.quantity))
	
	def _readd_item(self, items_list, items_map, item):
		"""Re-adds a transaction to given queue and map without changing ID"""
		items_map[item.id] = item
		items_list.put((item.price, item.id, item.quantity))
	
	def readd_order(self, trans):
		"""Re-adds a Transaction object to the market. Used, for example, when an 
		order is partially fulfilled and the updated order needs to go back into 
		the market without changing its ID.
		"""
		if trans.type == TransType.ASK:
			self._readd_item(self.asks_list, self.asks, trans)
		elif trans.type == TransType.BID:
			# Bid price is kept negative within the market to ensure
			# proper order in the priority queue
			if trans.price > 0:
				trans.price = -1 * trans.price
			self._readd_item(self.bids_list, self.bids, trans)
	
	def add_order(self, trans):
		"""Adds a Transaction object to the market, checking with the Banker if the
		transaction is allowed (eg, the owner of the transaction has enough money for
		a bid)
		"""
		if not self.banker.person_exists(trans.owner_id):
			print('Invalid owner ID: {}'.format(trans.owner_id))

		if trans.type == TransType.ASK:
			if self.banker.can_ask(trans):
				self.banker.charge_pending(trans)
				self._insert_new_item(self.asks_list, self.asks, trans)
			else:
				print('Ask rejected:', trans, self.banker.owners[trans.owner_id])
		elif trans.type == TransType.BID:
			if self.banker.can_bid(trans):
				self.banker.charge_pending(trans)
				
				trans.price = -1 * trans.price
				self._insert_new_item(self.bids_list, self.bids, trans)
			else:
				print('Bid rejected:', trans, self.banker.owners[trans.owner_id])
	
	def del_order(self, order_id):
		"""Deletes the order with the specified ID from the market. Worth noting 
		that this is an O(n) operation due to needing to re-build the priority 
		queue and searching.
		"""
		if order_id in self.bids:
			item = self.bids.pop(order_id)
			hay = self.bids_list
		elif order_id in self.asks:
			item = self.asks.pop(order_id)
			hay = self.asks_list
		else:
			print('Order {} does not exist'.format(order_id))
			return
		
		target = (item.price, item.id, item.quantity)
		hay.queue.remove(target)
		heapq.heapify(hay.queue)
		
		if item.type == TransType.BID:
			item.price = -item.price
		self.banker.refund(item)
		print('Order {} removed'.format(order_id))

	
	def fulfill_single(self):
		"""Checks the current market and tries to fulfill the top bid and ask, if 
		possible. Returns true if a bid, an ask, or both were filled, false 
		otherwise. Ties in price are broken by lowest ID, which corresponds to 
		oldest order.
		"""
		if self.asks_list.empty() or self.bids_list.empty():
			return False
		low_ask = self.asks_list.queue[0]
		high_bid = self.bids_list.queue[0]
		
		# Check if highest bid price overlaps with lowest ask price
		# If so, go ahead and fulfill one or both orders.
		if (-high_bid[0]) >= low_ask[0]:
			bid_id = self.bids_list.get()[1]
			ask_id = self.asks_list.get()[1]
			bid = self.bids[bid_id]
			ask = self.asks[ask_id]
			
			# Create a copy of the bid/ask to pass to the Banker
			bid_tmp = copy.copy(bid)
			bid_tmp.price = -bid_tmp.price
			ask_tmp = copy.copy(ask)
			
			final_quant = 0
			if bid.id < ask.id:
				final_price = -bid.price
			else:
				final_price = ask.price
			
			if bid.quantity > ask.quantity:
				remaining = bid.quantity - ask.quantity
				bid.quantity = remaining
				self.readd_order(bid)
				
				final_quant = ask.quantity

				print("Ask ID {} fulfilled".format(ask.id))
			elif ask.quantity > bid.quantity:
				remaining = ask.quantity - bid.quantity
				ask.quantity = remaining
				self.readd_order(ask)
				
				final_quant = bid.quantity
				
				print("Bid ID {} fulfilled".format(bid.id))
			else:
				final_quant = bid.quantity
				print("Bid ID {}, ask ID {} both fulfilled".format(bid.id, ask.id))
			
			self.banker.charge_proper(bid_tmp, ask_tmp, final_price, final_quant)
			return True
		return False
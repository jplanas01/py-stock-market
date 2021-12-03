from stocks import TransType

class StockOwner(object):
	"""Class that represents a person with a balance of money and stocks, and
any stocks/money that are pending."""
	def __init__(self, money_balance, stock_balance):
		self.money = money_balance
		self.stocks = stock_balance
		self.pending_money = 0
		self.pending_stocks = 0
	
	def __str__(self):
		return '[money: {}, stocks: {}]'.format(self.money, self.stocks)

class Banker(object):
	"""Manages the bookkeeping behind each transaction and fulfillment of transaction. This includes moving money between accounts, moving stocks between accounts, charging
	for pending (ie, not fulfilled) transactions, and ensuring that orders added to the
	market have a valid owner and that the owner has enough capital to execute the
	order.
	"""
	def __init__(self):
		self.owners = {}
		self.ids = -1
	
	def add_person(self, money, stocks):
		"""Adds a new person with new ID and specified money and stock balance"""
		self.ids += 1
		own = StockOwner(money, stocks)
		self.owners[self.ids] = own
	
	def person_exists(self, owner_id):
		"""Returns true if there is an entry with specified ID in the owner list"""
		if owner_id in self.owners:
			return True
		return False
	
	def charge_pending(self, trans):
		"""When a Transaction is added to the market, charge the owner's account to
		prevent double-spending of funds and place it in a pending account.
		"""
		id = trans.owner_id
		if trans.type == TransType.ASK:
			self.owners[id].stocks -= trans.quantity
			self.owners[id].pending_stocks += trans.quantity
		elif trans.type == TransType.BID:
			cost = trans.quantity * trans.price
			self.owners[id].money -= cost
			self.owners[id].pending_money += cost
	
	def charge_proper(self, bid, ask, act_price, act_quant):
		"""Moves money/stock into owners' accounts after a transaction is fulfilled.
		If a bid is filled at less than it's original value, the savings are credited
		to the owner's account.
		"""
		bid_owner = self.owners[bid.owner_id]
		ask_owner = self.owners[ask.owner_id]
		
		bid_owner.pending_money -= bid.price * act_quant
		ask_owner.money += act_price * act_quant
		# If order filled at lower value than original bid, refund cash savings
		if act_price != bid.price:
			bid_owner.money += act_quant * (bid.price - act_price)
		
		ask_owner.pending_stocks -= act_quant
		bid_owner.stocks += act_quant
	
	def refund(self, order):
		"""Refunds an owner for a cancelled transaction by moving money/stock from
		the pending account to the actual account.
		"""
		owner = self.owners[order.owner_id]
		if order.type == TransType.BID:
			owner.pending_money -= order.price * order.quantity
			owner.money += order.price * order.quantity
		elif order.type == TransType.ASK:
			owner.pending_stocks -= order.quantity
			owner.stocks += order.quantity
	
	def can_ask(self, transaction):
		"""Returns true if an owner has enough stock to fill the order."""
		id = transaction.owner_id
		if self.owners[id].stocks >= transaction.quantity:
			return True
		return False
	
	def can_bid(self, transaction):
		"""Returns true if an owner has enough money to fill the order."""
		id = transaction.owner_id
		if self.owners[id].money >= transaction.price * transaction.quantity:
			return True
		return False
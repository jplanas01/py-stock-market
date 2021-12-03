from enum import Enum

class TransType(Enum):
	BID = 0
	ASK = 1

class Transaction(object):
	"""Represents a single bid or ask within the market. The transaction ID is assigned
	by the market if it is accepted.
	"""
	def __init__(self, type, price, quantity, owner_id):
		self.type = type
		self.price = price
		self.quantity = quantity
		self.id = -1
		self.owner_id = owner_id
	
	def __str__(self):
		return '[type: {}, price: {}, quantity: {}, id: {}, owner: {}]'.format(
			self.type, self.price, self.quantity, self.id, self.owner_id)
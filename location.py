import os
class Location(object):
	def __init__(self, path):
		self.path = path
		self.parent = os.path.dirname(self.path).split('/')[-1]#BUG ON HOME FOLDER
		try:
		    self.children = [d for d in os.listdir(self.path) if os.path.isdir("{}/{}".format(self.path, d)) and not d.startswith('.')]
		except:
		    self.children = []
		self.name = self.path.split('/')[-1]
		self.characters = []
		self.events = {} #key = event, value = switch
		self.inventory = []
		self.dream_stone = False
		self.dimensional_warp = False

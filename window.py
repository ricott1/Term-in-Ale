# -*- coding: utf-8 -*-
#known bug, if I write a line too long, when printed with printOnDisplayPad or printOnLogPad one character is cutted and not printed before going to the next line

import curses, threading, time, os, sys

class Window(object):
	def __init__(self):
				
		try:
			self.resolution = os.popen('xrandr | grep \'*\'').read().split()[0].split('x')
			
		except:
			self.resolution = ['1280','960']
		
		n = int(self.resolution[1])/20
		m = int(self.resolution[0])/10
		if m < 	110:
			print 'The current screen resolution is too low to play'
			sys.exit()	
		elif m < 150:
			print 'The current screen resolution is too low to have an optimal game experience'		
		#set screen to nxm
		print '\x1b[8;%d;%dt'%(n,m)
		time.sleep(2)
		self.screen = curses.initscr()
		#self.screen.keypad(1)
		curses.start_color()
		curses.mousemask(1)
		curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
		self.WIDTH, self.HEIGHT = m, n
		os.system('clear')
		os.system('setterm -cursor off')
		self.pastEntries = []
		self.pastEntriesIndex = 0
		self.buildEntryBox()
		self.entryBox.keypad(1)
		self.buildStatusBox()
		self.buildDisplay()
		
		self.resetMessage()
		self.printOnDisplayPad('Press esc to reset the screen if something gets weird')
	def reset(self):
		self.screen.erase()
		self.screen.refresh()
		#self.display.erase()
		self.display.box()
		#self.display.refresh()
		#self.entryBox.erase()
		self.entryBox.box()
		#self.entryBox.refresh()	
		#self.statusBox.erase()
		self.statusBox.box()
		#self.statusBox.refresh()
		self.refreshMenu()
	
	def buildStatusBox(self):
		statusBoxLines = int(0.3 * self.HEIGHT)
		statusBoxCols = int(0.99* self.WIDTH)
		begin_y = 1
		begin_x = 1	
			
		self.statusBox =  curses.newwin(statusBoxLines, statusBoxCols, begin_y, begin_x)
		self.statusBox.box()
		self.title = '%-17s %-10s %3s %-2s   %-3s   %-5s               %-30s'%('Name', 'Type', 'lv', 'HB', 'STP','Status', 'Action')
		
		length = statusBoxCols - len(self.title) - 20
		self.breath_bars_length = max(3, int(0.67 * length))
		self.stamina_bars_length = max(3, int(0.33 * length))
	def buildDisplay(self):
		lines = int(0.64 * self.HEIGHT)
		cols = int(0.58* self.WIDTH)
		begin_y = int(0.32 * self.HEIGHT)
		begin_x = 1 
		self.display =  curses.newwin(lines,cols, begin_y, begin_x)
		self.display.box()
		self.displayCurrentLine = 1
		self.displayPad = curses.newpad(9999,cols-2)
		self.diplayPadCurrentLine = 0
		self.diplayPadWritingLine = 0

	def buildEntryBox(self):
		lines = int(0.07 * self.HEIGHT)
		cols = int(0.58* self.WIDTH)
		begin_y = int(0.95 * self.HEIGHT)
		begin_x = 1
		self.entryBox =  curses.newwin(lines, cols, begin_y, begin_x)		
		self.entryBox.box()

	def refreshStatusBox(self, totalStatus):
		self.statusBox.erase()
		self.statusBox.box()
		self.statusBox.addstr(1,1, self.title)
		y, x = self.statusBox.getmaxyx()
		for l, status in enumerate(totalStatus[:y-3]):
			
			line = '%-17s %-10s %3s %-4s %-3s %-10s %-30s %-7s '%(status['name'], status['type'], status['level'], status['HB'], status['STP'],status['conditions'], 
				status['action'], status['stamina'])

			self.statusBox.addstr(l+2,1, line)
			position = len(line)+2
			self.statusBox.addstr(l+2,position, ' ' * (self.stamina_bars_length))
			max_stamina_bars = int(status['max_stamina_bars'] * self.stamina_bars_length) * '-'
			self.statusBox.addstr(l+2,position, max_stamina_bars)
			stamina_bars = int(status['stamina_bars'] * self.stamina_bars_length) * '|'
			self.statusBox.addstr(l+2,position, stamina_bars)
			
			position = len(line)+2 + self.stamina_bars_length + 1
			breathing_line = '%-10s'%status['breath']
			self.statusBox.addstr(l+2,position, breathing_line)

			breath_bars = int(status['breath_bars'] * self.breath_bars_length) * '|'
			
			if status['color'] == 'red':	
				self.statusBox.addstr(l+2,position + 10,breath_bars , curses.color_pair(2))
			elif  status['color'] == 'yellow':	
				self.statusBox.addstr(l+2,position + 10, breath_bars, curses.color_pair(1))
			else:	
				self.statusBox.addstr(l+2,position + 10, breath_bars)
			
		self.statusBox.refresh()	
	
	def refreshEntryBox(self):
		y, x = self.entryBox.getmaxyx()
		self.entryBox.erase()
		
		try:
			self.entryBox.addstr(1,1, u'%s'%self.tmpMessage[:x-2])
		except UnicodeEncodeError:
			pass
		self.entryBox.box()
		self.entryBox.refresh()
	
	def scrollDisplayUp(self):
		self.display.refresh()
		y, x = self.display.getmaxyx()	
		self.diplayPadCurrentLine = max(min(self.diplayPadCurrentLine - y ,self.diplayPadWritingLine), 0)
		firstLine = max(self.diplayPadCurrentLine - (y-2),0)
		upper, left = self.display.getbegyx()
		self.displayPad.refresh(firstLine,1, upper +1, left +1 , upper + y -2,left + x -2)
	def scrollDisplayDown(self):
		self.display.refresh()
		y, x = self.display.getmaxyx()	
		self.diplayPadCurrentLine = max(min(self.diplayPadCurrentLine + y +1,self.diplayPadWritingLine), 0)
		firstLine = max(self.diplayPadCurrentLine - (y-2),0)
		upper, left = self.display.getbegyx()
		self.displayPad.refresh(firstLine,1, upper +1, left +1 , upper + y -2,left + x -2)

	def printOnDisplayPad(self, text):
		y, x = self.display.getmaxyx()		
		self.display.refresh()
		text = u'%s'%text
		self.displayPad.addstr(self.diplayPadWritingLine,1, text)
		increment = int(len(text)/(x-3)) + 1	
		if self.diplayPadWritingLine - self.diplayPadCurrentLine < y - 2:
			firstLine = max(self.diplayPadCurrentLine - (y-3),0)
			upper, left = self.display.getbegyx()
			self.displayPad.refresh(firstLine,1, upper +1, left +1 , upper + y -2,left + x -2)
			self.diplayPadCurrentLine += increment
		self.diplayPadWritingLine += increment
		

	def insertNextEntry(self):
		self.pastEntriesIndex = min(max(self.pastEntriesIndex + 1, -len(self.pastEntries)), 0)
		if self.pastEntriesIndex < 0:
			self.tmpMessage = u'%s'%self.pastEntries[self.pastEntriesIndex]
		elif self.pastEntriesIndex == 0:
			self.tmpMessage = ''
		self.refreshEntryBox()
	def insertPreviousEntry(self):
		self.pastEntriesIndex = min(max(self.pastEntriesIndex - 1, -len(self.pastEntries)), 0)
		if self.pastEntriesIndex < 0:
			self.tmpMessage = u'%s'%self.pastEntries[self.pastEntriesIndex]
		elif self.pastEntriesIndex == 0:
			self.tmpMessage = ''
		self.refreshEntryBox()
	
	#I use threading so that the world goes on while the program waits for user input
	def resetMessage(self):
		self.message = ''
		self.tmpMessage = ''
		self.pastEntriesIndex = 0
		self.refreshEntryBox()
		self.thread = threading.Thread(target=self.readInput)
		self.thread.start()

	def readInput(self):
		self.message = ''
		self.tmpMessage = ''
		y, x = self.entryBox.getmaxyx()

		while True:
			m = self.entryBox.getch()
			if m == 27:#esc
					self.reset()
					break	
			if m == curses.KEY_LEFT:
				self.scrollDisplayUp()
				
			elif m == curses.KEY_RIGHT:
				self.scrollDisplayDown()
			
			elif m == curses.KEY_UP:
				self.insertPreviousEntry()
			elif m == curses.KEY_DOWN:
				self.insertNextEntry()
			elif m in (8, 127, curses.KEY_BACKSPACE):#backspace
				if len(self.tmpMessage) > 0:
					self.tmpMessage = self.tmpMessage[:-1]
					self.refreshEntryBox()
			elif m in (10, 13):#return
				break
				
			elif len(self.tmpMessage) < x-2:
				try:
					char = unichr(m)
					self.tmpMessage = self.tmpMessage + char#u'%s'%char
					time.sleep(0.02)
				except:
					pass
			
					
					
		self.message =str(self.tmpMessage)# u'%s'%self.tmpMessage
		if self.message.strip():
			self.pastEntries.append(self.message)
		if not self.message:
			
			self.resetMessage()
	

class MasterWindow(Window):
	def __init__(self):
		super(MasterWindow, self).__init__()
		self.buildLogBox()
		
	def buildLogBox(self):
		logLines = int(0.7 * self.HEIGHT)
		logCols = int(0.41* self.WIDTH)
		begin_y = int(0.32 * self.HEIGHT)
		begin_x = int(0.59* self.WIDTH) 
		self.logBox =  curses.newwin(logLines, logCols, begin_y, begin_x)		
		self.logBox.box()
		self.logPad = curses.newpad(9999,logCols-2)
		self.logPadCurrentLine = 0
		
	def printOnLogPad(self, text):
		self.logBox.refresh()
		y, x = self.logBox.getmaxyx()
		self.logPad.addstr(self.logPadCurrentLine ,1, text)
		firstLine = max(self.logPadCurrentLine - (y-3),0)
		upper, left = self.logBox.getbegyx()
		self.logPad.refresh(firstLine,1, upper + 1, left + 1, upper +y -2,left + x -2)
		increment = int(len(text)/(x-3)) + 1		
		self.logPadCurrentLine += increment
	def tabFocus(self):
		pass
	def reset(self):
		super(MasterWindow, self).reset()
		self.logBox.erase()
		self.logBox.box()
		self.logBox.refresh()
	
class PlayerWindow(Window):
	def __init__(self):
		super(PlayerWindow, self).__init__()
		self.buildSide()
		self.barMenu = []
		self.sideMenu = []
		self.buildMenu()
		self.focus = 'entry'
		self.activeMenu = None
		
		self.refreshMenu()
	def buildSide(self):
		lines = int(0.7 * self.HEIGHT) - 3
		cols = int(0.41* self.WIDTH)
		begin_y = int(0.32 * self.HEIGHT)
		begin_x = int(0.59* self.WIDTH)
		self.side =  curses.newwin(lines, cols, begin_y, begin_x)		
		self.side.box()

	def printOnSide(self, text, selectables = []):
		self.sideMenu = []
		self.side.erase()
		self.side.box()
		y, x = self.side.getmaxyx()
		a, b = self.side.getbegyx()
		for l,line in enumerate(text):
			try:
				self.side.addstr(l+1,1, line[:x-1])
				
			except:
				#self.side.addstr(l+1,1, str(e))
				pass
		pos = int(b + 2)
		for j, s in enumerate(selectables):
			if s['position'] == 'bottom':
				begin_y, begin_x = a + y - 4, pos
				Button(s['name'], s['command'], self.sideMenu, 3, len(s['name']) + 2, begin_y, begin_x)
				pos +=  int(len(s['name']) + 3)
			elif s['position'] == 'overwrite':
				for l,line in enumerate(text):
					if s['find'].lower() in line.lower():
						begin_y, begin_x =  a + l + 1, b + 1 + line.lower().find(s['find'].lower())
						Button(s['name'], s['command'], self.sideMenu, 1, len(s['name']) + 1, begin_y, begin_x, box = False)
						break
				else:
					begin_x, begin_y = int(a + y - 4), pos
					Button(s['name'], s['command'], self.sideMenu, 1, len(s['name']) + 1, begin_y, begin_x, box = False)
					pos +=  int(len(s['name']) + 1)
			elif s['position'] == 'side':
				for l,line in enumerate(text):
					if s['find'].lower() in line.lower():
						begin_y, begin_x =  a + l + 1, b + 1 + line.lower().find(s['find'].lower()) + 20
						Button(s['name'], s['command'], self.sideMenu, 1, len(s['name']) + 1, begin_y, begin_x, box = False)
						break
				else:
					begin_x, begin_y = int(a + y - 4), pos
					Button(s['name'], s['command'], self.sideMenu, 1, len(s['name']) + 1, begin_y, begin_x, box = False)
					pos +=  int(len(s['name']) + 1)
			else:
				begin_x, begin_y = int(a + y - 4), pos
				Button(s['name'], s['command'], self.sideMenu, 1, len(s['name']) + 1, begin_y, begin_x, box = False)
				pos +=  int(len(s['name']) + 1)
		self.side.refresh()
		self.refreshMenu()
	def reset(self):
		super(PlayerWindow, self).reset()
		self.side.erase()
		self.side.box()
		self.side.refresh()
	def buildMenu(self):
		lines = 3
		cols = int(0.41* self.WIDTH)
		n = 3#7
		columns = int((cols - 2. * n) / n)
		begin_y = int(0.95 * self.HEIGHT)
		begin_x = int(0.59* self.WIDTH)
		
		#self.actionButton = Button('A1', '-z1', self.barMenu, lines, int((cols - 2. * n) / n), begin_y, begin_x)
		#self.actionButton = Button('A2', '-z2', self.barMenu, lines, int((cols - 2. * n) / n), begin_y, begin_x + 1 * int((cols - 2. * n) / n) + 2)
		#self.actionButton = Button('A3', '-z3', self.barMenu, lines, int((cols - 2. * n) / n), begin_y, begin_x + 2 * int((cols - 2. * n) / n) + 2)
		#self.actionButton = Button('A4', '-z4', self.barMenu, lines, int((cols - 2. * n) / n), begin_y, begin_x + 3 * int((cols - 2. * n) / n) + 2)
		self.roomButton = Button('Room', '-r', self.barMenu, lines, columns, begin_y, begin_x + 0 * columns)
		self.sheetButton = Button('Sheet', '-s', self.barMenu, lines, columns, begin_y , begin_x + 1 * columns + 2)
		self.inventoryButton = Button('Inventory', '-i', self.barMenu, lines, columns, begin_y, begin_x + cols - columns)
		
	def refreshMenu(self):	
		for b in self.barMenu + self.sideMenu:
			if self.focus == b:
				b.select()
			else:
				b.deselect()
		
	def tabFocus(self):
		if self.focus == 'entry':
			self.activeMenu = self.barMenu
			self.focus = self.barMenu[0]
		elif self.focus != 'entry':
			self.activeMenu = None
			self.focus = 'entry'
			
		self.refreshMenu()
	def cycleFocus(self, direction):
		try:
			if direction == 'left':
				incr = -1
				index = (self.activeMenu.index(self.focus) + incr) % len(self.activeMenu)
			elif direction == 'right':
				incr = +1
				index = (self.activeMenu.index(self.focus) + incr) % len(self.activeMenu)
			elif direction == 'up':
				index = (self.activeMenu.index(self.focus))
				self.activeMenu = self.sideMenu
				index = index  % len(self.activeMenu)
			elif direction == 'down':	
				index = (self.activeMenu.index(self.focus))
				self.activeMenu = self.barMenu 
				index = index  % len(self.activeMenu)
			self.focus = self.activeMenu[index]
			self.refreshMenu()
		except:
			self.tabFocus()
	def readInput(self):
		self.message = ''
		self.tmpMessage = ''
		y, x = self.entryBox.getmaxyx()

		while True:
			m = self.entryBox.getch()
			if m == 27:#esc
					self.reset()
					break	
			elif m == 9:#tab
				self.tabFocus()
				self.tmpMessage = ''
				break
			elif m == curses.KEY_MOUSE:
				_, mx, my, _, _ = curses.getmouse()
				for b in self.barMenu + self.sideMenu:
					if b.isMouseInside(my,mx):
						b.select()
						self.tmpMessage = b.command
						break
				break
			elif self.focus == 'entry':
				if m == curses.KEY_LEFT:
					self.scrollDisplayUp()
				
				elif m == curses.KEY_RIGHT:
					self.scrollDisplayDown()
				
				elif m == curses.KEY_UP:
					self.insertPreviousEntry()
				elif m == curses.KEY_DOWN:
					self.insertNextEntry()
				elif m in (8, 127, curses.KEY_BACKSPACE):#backspace
					if len(self.tmpMessage) > 0:
						self.tmpMessage = self.tmpMessage[:-1]
						self.refreshEntryBox()
				elif m in (10, 13):#return
					break
					
				elif len(self.tmpMessage) < x-2:
					try:
						char = unichr(m)
						self.tmpMessage = self.tmpMessage + u'%s'%char
						time.sleep(0.02)
					except:
						pass
			elif self.focus != 'entry':
				if m == curses.KEY_UP:#arrow up
					self.cycleFocus('up')
				elif m == curses.KEY_DOWN:#arrow down
					self.cycleFocus('down')
				elif m == curses.KEY_LEFT:#arrow left
					self.cycleFocus('left')
				elif m == curses.KEY_RIGHT:#arrow right
					self.cycleFocus('right')
				elif m == 49:
					self.tmpMessage = '-z1'
					break
				elif m == 50:
					self.tmpMessage = '-z2'
					break
				elif m == 51:
					self.tmpMessage = '-z3'
					break
				elif m == 52:
					self.tmpMessage = '-z4'
					break
				elif m in (10, 13):#return
					for b in self.barMenu + self.sideMenu:
						if b.isSelected:	
							self.tmpMessage = b.command
							break
					break
				elif len(self.tmpMessage) < x-2:
					self.focus = 'entry'
					self.refreshMenu()
					try:
						char = unichr(m)
						self.tmpMessage =  self.tmpMessage + u'%s'%char
						time.sleep(0.02)
					except:
						pass
					
					
		self.message = u'%s'%self.tmpMessage
		if self.message.strip():
			self.pastEntries.append(self.message)
		if not self.message:
			
			self.resetMessage()
class Menu(object):
	def __init__(self):
		self.buttons = []
		self.index = 0
	def scroll(self, incr):
		self.index = (self.index + incr)%len(self.buttons)
class Button(object):
	def __init__(self, name, command, master, lines, cols, begin_y, begin_x, box = True):
		self.name = name
		self.command = command
		self.master = master
		self.master.append(self)
		self.win = curses.newwin(lines, cols, begin_y, begin_x)	
		self.box = box
		if self.box:	
			self.win.box()
			self.win.addstr(1,1, self.name)
		else:
			self.win.addstr(0,0, self.name)
		self.win.refresh()
		self.y, self.x = self.win.getmaxyx()
		self.deselect()
	def deselect(self):
		self.isSelected = False
		self.win.erase()
		if self.box:	
			self.win.box()
			self.win.addstr(1,1, self.name)
		else:
			self.win.addstr(0,0, self.name)
		self.win.refresh()
		
	def select(self):
		self.isSelected = True
		if self.box:	
			self.win.addstr(1,1, self.name, curses.A_STANDOUT)
		else:
			self.win.addstr(0,0, self.name, curses.A_STANDOUT)
		
		self.win.refresh()
	def isMouseInside(self,y,x):
		my, mx = self.win.getmaxyx()
		by, bx = self.win.getbegyx()
		if bx <= x <= bx + mx and by <= y <= by + my:
			return True
		return False
	

	
	

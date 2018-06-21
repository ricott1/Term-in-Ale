import character, ability, random, item

def loadVillain(name, level='auto'):
	fileName = 'villains/%s.bbb'%name.lower().strip()
	try:
		with open(fileName,'r') as villainData:
			villain = character.Villain()
			fullData = villainData.read().splitlines()
			abilities = []
			if level != 'auto':
				exp = (level-1)**2*1000
			for data in fullData:
				try:
					key, value = data.split(' - ', 1)[0].strip().upper(), data.split(' - ', 1)[1].strip()
				except:
					key, value ='',''
				if key == 'TYPE':
					villain.type = value[0].upper() + value[1:].lower()
				elif key == 'RANDOMNAMES':
					villain.randomNames = [n.strip() for n in value.split(',')]
				elif key == 'TARGET':
					villain.combatRules['target'] = value.lower()
				elif key == 'PRIORITY':
					villain.combatRules['priority'] = value.lower()
				elif key == 'ALIGNMENT':
					villain.combatRules['alignment'] = value.lower()
				elif key == 'LEVEL' and level == 'auto':
					lv = int(value)
					exp = (lv-1)**2*1000
				elif key == 'BTH':
					villain.baseBTH = int(value)
				elif key == 'HB':
					villain.baseHB = int(value)
				elif key == 'SKR':
					villain.baseSKR = float(value)
				elif key == 'VOP':
					villain.baseVOP = int(value)
				elif key == 'RTM':
					villain.baseRTM = int(value)
				elif key == 'STA':
					villain.baseSTA = int(value)
				elif key == 'ABILITY':
					ab = value.split()[0]
					lv = value.split()[1]
					abilities.append((ab,lv))
				elif key == 'BONUS':
					villain.levelBonus.append(value)
				elif key == 'IMAGE':
					pic = value.strip('Q')
					villain.picture.append(pic)
				elif key == 'DESCRIPTION':
					villain.description.append(value)
				elif key == 'INVENTORY':
					obj = item.loadItem(value)
					villain.addInventory(obj)
				elif key == 'HASPICTURE':
					villain.hasPicture = True
			
			villain.addExperience(exp) 
			if villain.hasPicture:
				villain.initializePicture()
			for obj in villain.inventory:
				villain.equip(obj)
			for ab,lv in abilities:
				if villain.level >= int(lv):
					villain.abilities[ab] = getattr(ability, ab)(villain)		
			villain.restore()
		return villain
	except:
		return False



if __name__=='__main__':
	import sys
	print loadVillain(sys.argv[1]).pickTarget

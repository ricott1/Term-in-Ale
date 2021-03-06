import random,os, math, time
import ability, race, job, world, strategy, mission, inventory
   
   
             
class Character(object):
    MAX_RECOIL = 100
    LONG_RECOIL = 75
    MED_RECOIL = 50
    SHORT_RECOIL = 25
    ACTION_TIME_DEFAULT = 5
    BREATH_DMG_MULTI = 1
    BREATH_DMG_NORM = 100.
    HP_DMG_MULTI = 0.2
    HP_DMG_NORM = 100.
    HB_DMG_MULTI = 0.2
    HB_DMG_NORM = 100.
    RECOIL_MULTI = 9. 
    RECOIL_NORM = 6.
    DREAM_MULTI = 0.25
    RTM_RANGE = 0.025
    LVUP_MULTI = 1000

    def __init__(self,data, job, race, strategies, protagonist = None, generation=0, auto_loot=True):
        self.id = data["id"]
        self.name = data["name"]
        self.protagonist = protagonist
        
        self.job = job
        self.race = race
        self.strategies = strategies
        self.strategies[self.job.strategy.name] = self.job.strategy
        self.strategy = self.job.strategy
        self.description = []
        self.generation = generation
        self.recoil = 10 + random.random() * 75
        
       
        
        self.level = 1
        self.exp = 0
        
        self.HB_damage = 0
        self.BTH_damage = 0
        self.HP_damage = 0
        self.bonus = {"AC" : 0, "HP" : 0, "BTH" : 0,  "HB" : 0, "RES" : 0, "STR" : 0, "DEX" : 0, "SPD" : 0, "MAG" : 0, "RTM" : 0}
        self.immunities = {"shock" : 0, "mute" : 0, "dream" :0, "death" : 0}
        self.inventory = []#data["inventory"]
        self.equipment = {}#data["equipment"] #key = type, value = object
        self.crafting = {}
        #base value is the bare character value, without objects
        self._BTH, self.BTH = data["BTH"], data["BTH"]
        
        
        self._HP, self.HP = data["HP"], data["HP"]
        self._STA, self.STA = data["HP"], data["HP"]
        self._HB, self.HB = data["HB"], data["HB"]
        
        self._RES, self.RES = data["RES"], data["RES"]
        self._STR, self.STR = data["STR"], data["STR"]
        
        self._DEX, self.DEX = data["DEX"], data["DEX"]
        self._SPD, self.SPD = data["SPD"], data["SPD"]
        
        self._MAG, self.MAG = data["MAG"], data["MAG"]
        self._RTM, self.RTM = data["RTM"], data["RTM"]
        
        self.acquiredTargets = []
        self.print_action = ""
        self.action_time = 0
        self._is_shocked = 0
        self._is_muted = 0
        self._is_dreaming = 0 
        self._is_dead = 0 
             
        self.is_shocked = 0
        self.is_muted = 0
        self.is_dreaming = 0 
        self.is_dead = 0
        
        
        self.on_rythm = 0
        self.is_catching_breath = 0
        
        self.abilities = {"offense" : ability.Attack()}#, "defense" , "recover", "special",'support"
        #attributes that print the ongoing action
        self.print_action = ""
        self.action_time = 0
        
        self.is_moving = 0
        self.master_location_path = None
        self.world = None
        self.location = None
        self.auto_loot = auto_loot
        self.fix_strategy = False
        
        self.restore()
        
     
    @property
    def BTH(self):
        bonus = sum([self.equipment[obj].bonus["BTH"] for obj in self.equipment])
        return max(0, int(round(self._BTH +  self.bonus["BTH"] + self.race.bonus["BTH"] + self.job.bonus["BTH"] + bonus - self.BTH_damage)))  
    @BTH.setter
    def BTH(self, value):
        self._BTH = int(round(value))            
    
    @property
    def max_BTH(self):
        bonus = sum([self.equipment[obj].bonus["BTH"] for obj in self.equipment])
        return max(0, int(round(self._BTH +  self.bonus["BTH"] + self.race.bonus["BTH"] + self.job.bonus["BTH"] + bonus)))
        
    
    
    @property
    def HP(self):
        bonus = sum([self.equipment[obj].bonus["HP"] for obj in self.equipment])
        return max(0, int(round(self._HP +  self.bonus["HP"] + self.race.bonus["HP"] + self.job.bonus["HP"] + bonus - self.HP_damage)))  
    @HP.setter
    def HP(self, value):
        self._HP = int(round(value))
        
    @property
    def max_HP(self):
        bonus = sum([self.equipment[obj].bonus["HP"] for obj in self.equipment])
        return max(0, int(round(self._HP +  self.bonus["HP"] + self.race.bonus["HP"] + self.job.bonus["HP"] + bonus)))  
        
        
    @property
    def STA(self):
        return min(self.HP, max(0, self._STA))
    @STA.setter
    def STA(self, value):
        self._STA = min(self.HP, max(0, value))  
            
    @property
    def HB(self):
        bonus = sum([self.equipment[obj].bonus["HB"] for obj in self.equipment])
        return max(0, int(self._HB + self.bonus["HB"]  + self.race.bonus["HB"] + self.job.bonus["HB"] + bonus + self.HB_damage))
    @HB.setter
    def HB(self, value):
        self._HB = max(0, int(round(value)))
        
    @property
    def max_HB(self):
        bonus = sum([self.equipment[obj].bonus["HB"] for obj in self.equipment])
        return max(0, int(self._HB + self.bonus["HB"]  + self.race.bonus["HB"] + self.job.bonus["HB"] + bonus))
        
                  
    @property
    def STR(self):
        bonus = sum([self.equipment[obj].bonus["STR"] for obj in self.equipment])
        return max(1, int(self._STR + self.bonus["STR"] + self.race.bonus["STR"] + self.job.bonus["STR"] + bonus))
    @STR.setter
    def STR(self, value):
        self._STR = max(0, int(round(value)))
    @property
    def STRmod(self):
        return int((self.STR-10)/2)
    
               
    @property
    def SPD(self):
        bonus = sum([self.equipment[obj].bonus["SPD"] for obj in self.equipment])
        return max(1, int(self._SPD + self.bonus["SPD"] + self.race.bonus["SPD"] + self.job.bonus["SPD"] + bonus))
    @SPD.setter
    def SPD(self, value):
        self._SPD = max(0, int(round(value)))
    @property
    def SPDmod(self):
        return int((self.SPD-10)/2) 
                  
    @property
    def DEX(self):
        bonus = sum([self.equipment[obj].bonus["DEX"] for obj in self.equipment])
        return max(1, int(self._DEX + self.bonus["DEX"] + self.race.bonus["DEX"] + self.job.bonus["DEX"] + bonus))
    @DEX.setter
    def DEX(self, value):
        self._DEX = max(0, int(round(value)))
    @property
    def DEXmod(self):
        return int((self.DEX-10)/2)
                  
    @property
    def MAG(self):
        bonus = sum([self.equipment[obj].bonus["MAG"] for obj in self.equipment])
        if self.is_muted:
            return  max(1, int(bonus))
        else:        
            return max(1, int(self._MAG + self.bonus["MAG"] + self.race.bonus["MAG"] + self.job.bonus["MAG"] + bonus))
    @MAG.setter
    def MAG(self, value):
        self._MAG = max(0, int(round(value)))
    @property
    def MAGmod(self):
        return int((self.MAG-10)/2)
               
    @property
    def RES(self):
        bonus = sum([self.equipment[obj].bonus["RES"] for obj in self.equipment])
        if self.is_shocked:
            return  max(1, int(bonus))
        else:        
            return max(1, int(self._RES + self.bonus["RES"] + self.race.bonus["RES"] + self.job.bonus["RES"] + bonus))
    @RES.setter
    def RES(self, value):
        self._RES = max(0, int(round(value)))
    @property
    def RESmod(self):
        return int((self.RES-10)/2)
           
    @property
    def RTM(self):
        bonus = sum([self.equipment[obj].bonus["RTM"] for obj in self.equipment]) + self.race.bonus["RTM"] + self.job.bonus["RTM"]
        return max(1, int(self._RTM + self.bonus["RTM"] + bonus))
    @RTM.setter
    def RTM(self, value):
        self._RTM = max(0, int(round(value)))
    
    @property
    def AC(self):
        bonus = sum([self.equipment[obj].bonus["AC"] for obj in self.equipment])
        return 10 + self.DEXmod + bonus + self.race.bonus["AC"] + self.job.bonus["AC"]
    
    
    
    @property
    def recoil(self):
        return self._recoil
    @recoil.setter
    def recoil(self, value):
        self._recoil = min(self.MAX_RECOIL, max(0, value))
    
      
    @property
    def is_shocked(self):
        return self._is_shocked
    @is_shocked.setter
    def is_shocked(self, value):
        immunities = self.all_immunities()
        if value > 0:
            if immunities["shock"]:
                self._is_shocked = 0
            else:
                self._is_shocked = value
        else:
            self._is_shocked = 0
        
    @property
    def is_muted(self):
        return self._is_muted
    @is_muted.setter
    def is_muted(self, value):
        immunities = self.all_immunities()
        if value > 0:
            if immunities["mute"]:
                self._is_muted = 0
            else:
                self._is_muted = value
        else:
            self._is_muted = 0
  
    @property
    def is_dreaming(self):
        return self._is_dreaming
    @is_dreaming.setter
    def is_dreaming(self, value):
        immunities = self.all_immunities()
        if value > 0:
            if immunities["dream"]:
                self._is_dreaming = 0
            else:
                self._is_dreaming = value
        else:
            self._is_dreaming = 0   
              
    @property
    def is_dead(self):
        return self._is_dead
        
    @is_dead.setter
    def is_dead(self, value):
        immunities = self.all_immunities()
        if value > 0:
            if immunities["death"]:
                self._is_dead = 0
            else:
                self._is_dead = value
                self.HB_damage = -self.max_HB
                self.BTH_damage = self.max_BTH
                self.STA = 0
                self.HP_damage = self.max_HP
                self.is_catching_breath = 0
                self.recoil = self.MAX_RECOIL
                for i in self.inventory:
                    self.remove_inventory(i)
        else:
            self._is_dead = 0
            
                        
        #else:
        #    self.restore()

    def all_abilities(self):
        allAb = self.abilities.copy()
        
        obj_abilities = {}
        for obj in self.equipment:
            obj_abilities.update(self.equipment[obj].abilities)
        for (typ, ability) in obj_abilities.items() + self.race.abilities.items() + self.job.abilities.items():
            if typ in allAb:
                if ability.level > allAb[typ].level:
                    allAb[typ] = ability
            else:
                allAb[typ] = ability 
        
        return allAb
        
    def all_immunities(self):
    #when checking immunities should check all_immunities. fix this with update dictionaries
        allImm = self.immunities.copy()
        obj_immunities = {}
        for obj in self.equipment:
            obj_immunities.update(self.equipment[obj].immunities)
        allImm.update(obj_immunities)
        allImm.update(self.job.immunities)
        allImm.update(self.race.immunities)
        return allImm
        
    def update(self,DELTATIME):
        self.action_time -= DELTATIME
        if self.action_time <= 0:
            self.action_time = 0
            self.print_action = ""
        if self.HP <= 0 or self.max_BTH <= 0 or self.HB <= 0:
            self.is_dead = 1
        if self.is_dead:
            return
        abilities = self.all_abilities()    
        for a in abilities:
            abilities[a].on_update(DELTATIME, self)
        for eq in self.equipment:
            self.equipment[eq].on_update(DELTATIME, self)
        self.job.on_update(DELTATIME, self)
        self.race.on_update(DELTATIME, self)
        immunities = self.all_immunities()
        for i in immunities:
            if immunities[i]>0:
                immunities[i] = max(0, immunities[i] - DELTATIME ) 
                   
        self.recoil -= self.RECOIL_MULTI * DELTATIME * (1. + self.SPDmod/self.RECOIL_NORM)
        
        #BTH part
        if  self.is_catching_breath == 0 and self.BTH <= 0:
            self.is_catching_breath = self.time_to_catch_breath()
        elif self.is_catching_breath > 0:
            self.is_catching_breath -= DELTATIME * self.BREATH_DMG_MULTI * (1. + self.HB/self.BREATH_DMG_NORM)
            if self.is_catching_breath <= 0:
                self.catchBreath()
                self.is_catching_breath = 0
        else:
            self.BTH_damage += DELTATIME * self.BREATH_DMG_MULTI * (1. + self.HB/self.BREATH_DMG_NORM)
        
        #HP part     
        self.HP_damage = max(0, self.HP_damage - DELTATIME * self.HP_DMG_MULTI/ (1. + self.HB/self.HP_DMG_NORM))
        self.STA += DELTATIME       
        
        if self.is_dreaming > 0:
            self.HP_damage = max(0, self.HP_damage - self.DREAM_MULTI * DELTATIME * self.HP_DMG_MULTI/ (1. + self.HB/self.HP_DMG_NORM))
            self.BTH_damage -= self.DREAM_MULTI * DELTATIME * self.BREATH_DMG_MULTI * (1. + self.HB/self.BREATH_DMG_NORM)
            self.HB_damage = max(0, self.HB_damage - self.DREAM_MULTI * DELTATIME ) 
            self.recoil = self.MAX_RECOIL
            
        if self.is_shocked == 0:
            self.HB_damage = max(0, self.HB_damage - - DELTATIME * self.HB_DMG_MULTI/ (1. + self.HB/self.HB_DMG_NORM))
           
        #check rithm changing state
        for i in xrange(1, self.RTM + 1):
            if self.max_BTH*(1.*i/(self.RTM+1)  - self.RTM_RANGE) < self.BTH_damage < self.max_BTH*(1.*i/(self.RTM+1) + self.RTM_RANGE):
                self.on_rythm = 2
                break
            elif self.max_BTH*(1.*i/(self.RTM+1)  - 2 * self.RTM_RANGE) < self.BTH_damage < self.max_BTH*(1.*i/(self.RTM+1) + 2* self.RTM_RANGE):
                self.on_rythm = 1
                break
            
        else:
            self.on_rythm = 0
            
        #if no stamina gets shocked
        if self.STA < 0.1 * self.HP and self.is_shocked == 0:
            self.is_shocked += DELTATIME
        elif self.is_shocked > 0 and self.STA >= 0.1 * self.max_BTH:
            self.is_shocked = max(0,self.is_shocked - DELTATIME )            
        if self.is_muted >0:
            self.is_muted = max(0,self.is_muted - DELTATIME )
            
        if self.location.path != self.master_location_path and self.recoil == 0 and self.is_dreaming == 0:
            self.move()
            
        elif self.recoil == 0 and self.is_dreaming == 0:
            self.take_action()  
            
    def time_to_catch_breath(self):
        return self.max_BTH/2.15
        
    def catchBreath(self):
        self.BTH_damage = 0
        self.STA += 0.5*self.HP
           
    def restore(self):
        self.HB_damage = 0
        self.BTH_damage = 0
        self.HP_damage = 0
        for k in self.bonus:
            self.bonus[k] = max(self.bonus[k], 0)
        
        self.is_shocked = 0
        self.is_muted = 0
        self.is_dead = 0
        
        self.is_catching_breath = 0
        
    def add_experience(self, exp):
        self.exp += exp
        while self.exp>= self.level**2*1000:
            self.level_up()
          
    def level_up(self):
        self.job.level_up()
        self.level = self.job.level
        self.restore()
    
    def roll(self):
        return random.randint(1, 20) + self.job.proficiency
       
    def take_action(self):
        targets = self.strategy.pick_target(self, self.location.characters)
        all_abilities = self.all_abilities()
        if targets:
            abilities = {ab: all_abilities[ab] for ab in all_abilities if all_abilities[ab].is_legal(self)}
        else:
            abilities = {ab: all_abilities[ab] for ab in all_abilities if (not all_abilities[ab].has_target and all_abilities[ab].is_legal(self))}
            
        if abilities and targets:
            kind = self.strategy.pick_ability(abilities)
            if not abilities[kind].has_target:
                abilities[kind].use(self, False)
                
            elif abilities[kind].has_target == 'single':
                target = targets[0]
                abilities[kind].use(self, target)
                if target.is_dead:
                    self.add_experience(100 * target.level)
            elif abilities[kind].has_target == 'all':
                abilities[kind].use(self, targets)
                for target in targets:
                    if target.is_dead:
                        self.add_experience(100 * target.level)
                
        elif self.location.inventory and self.auto_loot:
            item = self.location.inventory[0]
            self.pick_up(item)
         
        elif abilities:
            kind = self.strategy.pick_ability(abilities)
            if not abilities[kind].has_target:
                abilities[kind].use(self, False) 
            
        
    def move(self):
        if self.is_dead == 0 and self.is_dreaming == 0 and self.recoil==0:
            self.recoil = self.MED_RECOIL 
            
            target_loc = self.master_location_path.split("/")
            my_loc = self.location.path.split("/")
            
            if len(target_loc) > len(my_loc):
                path = "/".join(target_loc[:len(my_loc) + 1])
            elif len(target_loc) < len(my_loc):
                path = "/".join(my_loc[:-1])
            else:
                path = "/".join(my_loc[:-1])
                
            self.location.characters.remove(self)
            self.location = self.get_location_from_path(path)
            self.location.characters.append(self)
            self.add_experience(100) 
               
    def get_location_from_path(self, path):
        for r in self.world.locations:
            if r.path == path:
                return r
                
        else:
            self.world.add_location(path)
            return self.get_location_from_path(path)
            
    def add_inventory(self, obj):
        self.location.inventory.remove(obj)
        obj.location = self
        self.inventory.append(obj)
        
    def remove_inventory(self, obj):
        obj.location = self.location
        obj.location.inventory.append(obj)
        self.unequip(obj)
        self.inventory.remove(obj)
            
    def equip(self, obj):
        if obj.type in self.equipment:
            self.equipment[obj.type].on_unequip(self)
        self.equipment[obj.type] = obj
        obj.on_equip(self)
        
    def unequip(self, obj):
        if obj.type in self.equipment and self.equipment[obj.type] == obj:
            self.equipment.pop(obj.type)
            obj.on_unequip(self)
    
    def pick_up(self, item):
        self.recoil += self.LONG_RECOIL
        self.add_inventory(item)
        self.print_action = "Picked up: {}".format(item.name)
        self.action_time = self.ACTION_TIME_DEFAULT       

    def drop(self, item):
        self.recoil += 5
        self.remove_inventory(item)
        self.print_action = "Dropped: {}".format(item.name)
        self.action_time = self.ACTION_TIME_DEFAULT
         
    def craft(self, item):
        self.recoil = self.MAX_RECOIL
        self.add_inventory(item)
        for i in self.craft[item]:
            self.remove_inventory(i)
        self.print_action = "Crafted: {}".format(item.name)
        self.action_time = self.ACTION_TIME_DEFAULT 
        
    def toggle_strategy(self):
        if not self.fix_strategy:
            keylist = sorted(self.strategies.keys())
            for i, k in enumerate(keylist):
                if k == self.strategy.name:
                    self.strategy = self.strategies[keylist[(i+1)%len(keylist)]]
                    break
           
class Villain(Character):
    pass
    
    
class Player(Character):
    def add_experience(self, exp):
        self.exp += exp
        while self.exp>= self.level**2*self.LVUP_MULTI:
            self.level_up()
        self.protagonist.data["jobs"][self.job.name] = self.exp    
    
    
            
class Protagonist(object):
    def __init__(self,data):
        self.id = data["id"]
        self.name = data["name"] 
        self.data = data
        self.players = []  
        self.worlds = []
        self.races = race.get_player_races()
        self.jobs = job.get_jobs()
        self.missions = mission.get_missions(self)
        if "jobs" not in self.data:
            self.data["jobs"] = {j.name : 0 for j in self.jobs}
        if "mission" not in self.data:
            self.data["mission"] = []
        self.mission = None
        #self.start_mission(self.mission)

        
        
    def generate(self, generation=0):
        path = os.getcwd()
        if generation > 0:
            path = self.players[generation-1].location.path
            
        if len(self.worlds) <= generation:
            w = world.World(generation=generation)
            self.worlds.append(w)
        pstrategies = strategy.get_strategies() 
        prace = random.sample(self.races, 1)[0]
        pjob = random.sample(self.jobs, 1)[0] 
        self.jobs.remove(pjob)
        player = Player(self.data, job=pjob, race=prace, strategies = pstrategies, protagonist = self, generation=generation)
        player.add_experience(self.data["jobs"][pjob.name])
        player.master_location_path = path
        player.world = self.worlds[generation]
        player.location = player.get_location_from_path(path)
        player.location.characters.append(player)    
        self.players.append(player)
    
    def update(self, path, DELTATIME):
        t = time.time()
        max_gen = max([p.world.generation for p in self.players])
        if self.mission != None:
            self.mission.on_update()
        for p in self.players:
            if path != p.master_location_path:
                p.master_location_path = path
        for l in set([p.location for p in self.players]):   
            for c in l.characters:
                c.update(DELTATIME * 2**(c.world.generation - max_gen) ) 
        log(time.time()-t)
    
    def dream(self):  
        for player in self.players[::-1]:
            if player.location.dream_stone and not player.is_dead and not player.is_dreaming: 
                if self.jobs:  
                    self.generate(generation=player.generation+1)
                    player.recoil = player.MAX_RECOIL
                    self.players[player.generation].is_dreaming = 1
                    player.location.dream_stone = False
                    break
           
    def warp(self):
        for player in self.players[::-1]:
            if player.location.dimensional_warp and player.generation>0 and not player.is_dead and not player.is_dreaming:   
                player.world = self.worlds[player.generation-1]
                player.location.characters.remove(player)
                player.location = self.players[player.generation-1].location
                player.location.characters.append(player)
                player.recoil = player.MAX_RECOIL
                self.players[player.generation-1].is_dreaming = 0
                player.location.dimensional_warp = False
                break
                
    def craft(self):
        for player in self.players[::-1]:
            for c in player.craft:
                if set(player.craft[c]) <= set(player.inventory):
                    player.craft(c)
                
    def switch(self,player1, player2):
        a, b = self.players.index(player1), self.players.index(player2)
        self.players[b], self.players[a] = self.players[a], self.players[b]
        
    def start_mission(self, mission):
        self.mission = mission  
        mission.on_start() 
        
def log(text):
    with open("log.tiac", "a") as f:
        f.write("{}: {}\n".format(time.time(), text))
   

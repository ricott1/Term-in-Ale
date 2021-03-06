from os import walk
import os
import location, character, random, uuid, item, race, job, inventory

base = os.getcwd()
RANDOM_NAMES = ("Gimmi", "Renny","Hop","Hip", "Cat", "Batman", "Yitterium", "Micha","Reynolds","Giangi","Paolino","Ventura","Mariachi","Favetti","Orleo","Bissaglia", "Fonzie","Alvarez","Selenio","Paul","Fedor","Gutierrez","Raul Bravo","Ricardo","Lopez","Figueroa","Beniamino", "Gino","Yasser","Gandalf","Komeini","Blasfy","Misfit","Pinto","Cucchi","Monty","Python","Fia Mei","Sean Penn","Pio Nono","Fau","Tella","Suarez","Hannibal","Maori")

class World(object):
    def __init__(self, base = base, generation=1):
        self.base = base
        self.generation = generation
        self.locations = []
        self.add_location(base)
    def add_location(self, path): 
        r = location.Location(path)
        
        if path == self.base:
            #r.inventory.append(inventory.FuryArmor(location = r))
            r.inventory.append(inventory.ChainArmor(location = r))
            r.inventory.append(inventory.LongSword(location = r))
            #r.inventory.append(inventory.GreatAxe(location = r))
           # r.inventory.append(inventory.BeltOfGiants(location = r))
            r.inventory.append(inventory.HelmOfContinency(location = r))
            r.inventory.append(inventory.JacksonHelm(location = r))
            r.inventory.append(inventory.JacksonBelt(location = r))
            r.inventory.append(inventory.JacksonBoots(location = r))
            r.dream_stone = True
            r.dimensional_warp = True
        else: #here everything should be folder dependent: monsters are file, depending on the type you get different monsters, maybe objects as well. size of files give monsters strength. should make more allies and passive monsters. 
            r.dream_stone = random.randint(0,1)
            r.dimensional_warp = random.randint(0,1)
            for i in xrange(random.randint(0,2)):
                v = self.quick_villain()
                v.location = r
                v.master_location_path = v.location.path
                v.world = self
                r.characters.append(v)
                
        self.locations.append(r)
        
    def quick_villain(self, r = 'random', j = 'random'):
        BTH, RES, MAG, SPD, DEX, STR = [sum(sorted([random.randint(1,6) for l in xrange(4)])[1:]) -2 for x in xrange(6)]
        HP = 4 + 2* random.randint(0,3)
        HB = 30 + random.randint(1, 30)
        RTM = random.randint(1,2)
        data = {"name" : random.sample(RANDOM_NAMES, 1)[0], "id" : uuid.uuid4(), "BTH" : BTH + 6,  "HB" : HB + 30, "RES" : RES, "MAG" : MAG, "HP" : HP + 4, "SPD" : SPD, "DEX" : DEX + 6, "STR" : STR + 6, 
        "RTM" : RTM}
        
        races = race.get_monster_races()
        all_races = race.get_races()
        if [rac for rac in all_races if rac.name == r]:
            prace = random.sample([rac for rac in all_races if rac.name == r], 1)[0]
        else:
            prace = random.sample(races, 1)[0]
        jobs = job.get_jobs()
        if [jo for jo in jobs if jo.name == j]:
            pjob = random.sample([jo for jo in jobs if jo.name == j], 1)[0]
        else:
            pjob = random.sample(jobs, 1)[0] 
        
        return character.Villain(data, job=pjob, race=prace, strategies = {}, generation=self.generation, auto_loot=False)   
             
if __name__ == "__main__":
    w = World()

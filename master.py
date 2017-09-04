import time, datetime, os, sys, uuid, random
import character, gui
import dill
import subprocess
path =  os.path.dirname(os.path.realpath(__file__))
RANDOM_NAMES = ("Gorbacioff", "Gundam", "Pesca", "Lukiko","Armando","Mariella","Formaggio","Pancrazio","Tancredi","Swallace","Faminy","Pertis","Pericles","Atheno","Mastella","Ciriaco")


GAME_SPEED = 1.5

def get_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

class Master(object):
    def __init__(self, ppid):
        self.ppid = ppid
        self.protagonist = None
        self.time = time.time()
        self.gui =  gui.GUI(self)
        
        
    def new_game(self):
        self.gui.to_create_screen()
                   
    def load_game(self, filename):
        with open("{}".format(filename), "r+") as f:
            data = dill.load(f)
          
        self.protagonist = character.Protagonist(data)
        self.protagonist.generate()
        self.start_game()
 
    def save_game(self):
        filename = "{}.tiac".format(self.protagonist.name + get_time())
        with open("{}/data/{}".format(path, filename), "w+") as f:
            dill.dump(self.protagonist.data, f)
       
    def quick_protagonist(self, generation=0):
        BTH, RES, MAG, SPD, DEX, STR = [sum(sorted([random.randint(1,6) for l in xrange(4)])[1:]) + generation for x in xrange(6)]
        HP = 6+ 2* random.randint(0,3)
        HB = 30 + random.randint(1, 30)
        RTM = random.randint(1,2)
        data = {"name" : random.sample(RANDOM_NAMES, 1)[0], "id" : uuid.uuid4(), "BTH" : BTH + 6, "HB" : HB, "RES" : RES, "MAG" : MAG, "HP" : HP, "SPD" : SPD, "DEX" : DEX + 6, "STR" : STR + 6, 
        "RTM" : RTM}
        protagonist = character.Protagonist(data)
        protagonist.generate()
        return protagonist
        
        
        
    def quick_game(self):
        self.protagonist = self.quick_protagonist()
        self.start_game()
        
    def create_player(self, name, chars):
        
        data = {"name" : name, "id" : uuid.uuid4(), "BTH" : chars["BTH"], "HB" : chars["HB"], "RES" : chars["RES"], "MAG" : chars["MAG"], "HP" : chars["HP"], 
        "SPD" : chars["SPD"], "DEX" : chars["DEX"], "STR" : chars["STR"], "RTM" : chars["RTM"]}
        
        self.protagonist = character.Protagonist(data)
        self.protagonist.generate()
        self.start_game()      
        
    def start_game(self):
        self.gui.to_game_screen()
        self.update()  
        
    def update(self, *args):
        DELTATIME =  time.time() - self.time
        self.time = time.time()
        try:
            #path = os.readlink("/proc/{}/cwd".format(self.ppid))
            process = subprocess.Popen(['pwdx', str(ppid)], stdout=subprocess.PIPE)
            path = process.communicate()[0].split()[-1]
        except:
            sys.exit()
        
        self.protagonist.update(path,  GAME_SPEED * DELTATIME)
        
        if os.path.exists(path+"/dream") and os.path.isfile(path+"/dream"):
            self.protagonist.dream()
            os.remove(path+"/dream")
                    
                
        if os.path.exists(path+"/warp") and os.path.isfile(path+"/warp"):
            self.protagonist.warp()
            os.remove(path+"/warp")
            
        self.gui.game_screen.update_screen(self.protagonist)
        self.gui.loop.set_alarm_in(sec=0.15, callback=self.update)
    
    def tire(self, index):
        self.protagonist.players[index].BTH_damage += 3
        self.protagonist.players[index].STA -= 3
        self.protagonist.players[index].HB_damage += 10
        self.protagonist.players[index].add_experience(1000)
        self.save_game()
    
    
if __name__ == "__main__":
    
    sys.stdout.write("\x1b]2;Term-in-Ale\x07")
    sys.stdout.write("\x1b[8;30;100t")
    ppid = sys.argv[1] 
    
    master = Master(ppid)   
    
    for filename in sorted(os.listdir(os.curdir)):
        if os.path.isfile(filename) and filename.endswith(".tiac"):
            try:
                master.load_game(filename)
                break
            except:
                continue
    
        
    master.gui.loop.run()
       
    
    #master.update()
     
    
   

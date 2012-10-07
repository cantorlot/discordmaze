import logger
import random
from const import MAXFEAR,PONYNAMES,GEMCOST,GROUND,DEBUG

class Grid(list):
    def __getitem__(self,index):
        try:
            return list.__getitem__(self,index[0])[index[1]]
        except:
            return list.__getitem__(self,index)

    def __setitem__(self,index,value):
        try:
            return list.__setitem__(list.__getitem__(self,index[0]),index[1],value)
        except:
            return list.__setitem__(self,index)

    def __repr__(self):
        return "\n".join(" ".join(repr(cell)[:2] for cell in row) for row in self)

class Block(object):
    def step(self,pony):
        """ Returns whether a pony should stop here. """
        return False

    def land(self,pony):
        pass

    def __repr__(self):
        return "..."

class Wall(Block):
    def __repr__(self):
        return "|||"

class SimpleBlock(Block):
    def __init__(self,attrib,diff):
        self.attrib = attrib
        self.diff = diff

    def land(self,pony):
        pony.__dict__[self.attrib] += self.diff
        logger.log(("land",pony.name,self.attrib,self.diff))

    def __repr__(self):
        #return self.attrib[0]+"+"*(self.diff>0)+str(self.diff)
        return self.attrib[0]+str(self.diff)

#Use the same instance for all blocks.
class TrapBlock(Block):
    def __init__(self,attrib,diff):
        self.attrib = attrib
        self.diff = diff
        self.active = True

    def step(self,pony):
        if not self.active: return False
        self.land(pony)
        return True

    def land(self,pony):
        if self.active:
            pony.__dict__[self.attrib] += self.diff
            self.active = False
            logger.log(("trigger","trap"))
        else:
            pony.__dict__[self.attrib] += 2*self.diff
            logger.log(("trigger","obvious trap"))

    def __repr__(self):
        if not self.active:
            return "tt"
        else:
            return "tt"

class RockslideBlock(Block):
    def __init__(self):
        self.active = True

    def step(self,pony):
        if self.active:
            self.trigger()
            self.active = False
        return False

    def land(self,pony):
        self.step(pony)

    def __repr__(self):
        return "Rf"

class BoulderBlock(Block):
    def __repr__(self):
        return "BB"

class EndBlock(Block):
    def step(self,pony):
        self.land(pony)
        return True

    def land(self,pony):
        self.arrive(pony)

    def __repr__(self):
        return "EE"

class Pony(object):
    def __init__(self,name,xy=(0,0)):
        self.name = name
        self.willpower = 0
        self.fear = 0
        self.routeloc = 0
        self.xy = xy
        self.arrived = False
        self.discorded = False
        #if self.name == "FS":
        #    self.fear += 1

    def checkfear(self):
        if self.fear < 0:
            logger.log("limit","fear",self.name)
            self.fear = 0
        if self.willpower < 0:
            logger.log("limit","willpower 0",self.name)
            self.willpower = 0
        if self.willpower > 3:
            logger.log("limit","willpower 3",self.name)
            pony.willpower = 3
        if DEBUG:
            return False
        else:
            return self.fear >= MAXFEAR

    def __repr__(self):
        return "N:%s F:%s W:%s L:%s xy:%s"%(self.name,self.fear,self.willpower,self.routeloc,self.xy)

class Game(object):
    def __init__(self,map,ponies,routexy={},routes=[],ponyxy=[]):
        self.gameover = False
        #logger.debug([(name,Pony(name)) for name in PONYNAMES])
        self.ponies = ponies
        logger.debug(self.ponies)
        self.routexy = routexy
        self.routes = routes#dict((name,[Block() for i in xrange(len(self.routexy[name]))]) for name in PONYNAMES)
        self.ponies["RA"].gems = 0
        self.timers = {}
        self.setupgame()
        self.nextturn()

    def setupgame(self):
        self.arrived = []
        for route in self.routes.values():
            route[-1].arrive = self.ponyarrive
        self.timers["global fear"] = 5
        self.timers["discord"] = 1
        self.timers["rarity gems"] = 1
        self.timers["flutter fear"] = 3+self.ponies["FS"].willpower            
        self.timers["pinkie song"] = 6-self.ponies["PP"].willpower            

        trapblock = TrapBlock("fear",1)
        self.routes["TS"][15] = trapblock
        self.routes["RA"][15] = trapblock
        self.routes["PP"][15] = trapblock
        rockslideblock = RockslideBlock()
        self.routes["RA"][-14] = rockslideblock
        rockslideblock.trigger = self.boulderfall

        grid = [[Wall() for cell in row] for row in map]
        self.grid = Grid(grid)
        for name in PONYNAMES:
            for i,xy in enumerate(self.routexy[name]):
                self.grid[xy] = self.routes[name][i]
        xy = self.routexy["AJ"][-1]
        self.grid[xy] = EndBlock()
        self.grid[xy].arrive = self.ponyarrive

    def maxdice(self):
        m = 3
        if not self.ponies["RD"].discorded:
            m += 1 + self.ponies["RD"].willpower
        if not self.ponies["AJ"].discorded:
            m += 1 + self.ponies["AJ"].willpower
        return m

    def nextturn(self):
        self.dice = random.randint(1,self.maxdice())
        logger.debug("new dice:",self.dice)

    def move(self,ponyname):
        pony = self.ponies[ponyname]
        if pony.arrived:
            logger.log("error","arrived",ponyname)
            return
        route = self.routes[ponyname]
        routexy = self.routexy[ponyname]
        for i in xrange(1,self.dice+1):
            if i == self.dice:
                logger.debug("landing",ponyname,routexy[pony.routeloc+i])
                route[pony.routeloc+i].land(pony)
                #Hack
                if not self.ponies["TS"].discorded and self.ponies["TS"].willpower >= 3:
                    if route[pony.routeloc+i].attrib == "willpower" and route[pony.routeloc+i].diff == 1:
                        logger.log("event","special","TS")
                        pony.willpower += 1
                pony.routeloc += i
                break
            logger.debug("moving",ponyname,routexy[pony.routeloc+i])
            if route[pony.routeloc+i].step(pony):
                pony.routeloc += i
                break
        pony.xy = routexy[pony.routeloc]
        logger.debug("routeloc",pony.routeloc,self.dice)
        self.endturn()
        if not self.gameover:
            self.nextturn()

    def endturn(self):
        for pony in self.ponies.values():
            if pony.checkfear():
                self.gameover = True
                return
        for tname in self.timers:
            self.timers[tname] -= 1
            if self.timers[tname] == 0:
                self.timereffect(tname)

    def timereffect(self,tname):
        logger.log("effect",tname)
        if tname == "global fear":
            logger.debug("Triggering global fear")
            for pony in self.ponies.values():
                if not pony.discorded:
                    pony.fear += 1
            self.timers["global fear"] = 5
        elif tname == "rarity gems":
            pony = self.ponies["RA"]
            if not pony.discorded:
                pony.gems += 1+pony.willpower
                self.timers[tname] = 1
        elif tname == "flutter fear":
            pony = self.ponies["FS"]
            if not pony.discorded:
                pony.fear += 1
                self.timers[tname] = 3+pony.willpower            
        elif tname == "pinkie song":
            pony = self.ponies["PP"]
            if not pony.discorded:
                for otherpony in self.ponies.values():
                    if not otherpony.discorded:
                        otherpony.fear -= 1
                self.timers[tname] = 6-pony.willpower
        elif tname == "discord":
            for pony in self.arrived:
                if pony.willpower > 0:
                    pony.willpower -= 1
                    logger.log("event","discord",pony.name)
                    if pony.willpower == 0:
                        pony.discorded = True
                        logger.log("event","discorded",pony.name)
                    break
            self.timers[tname] = 1

    def calm(self,ponyname):
        if self.ponies["RA"].gems >= GEMCOST:
            self.ponies["RA"].gems -= GEMCOST
            self.ponies[ponyname].fear -= 1
            self.ponies[ponyname].checkfear()
            logger.log(("calm",ponyname))
        else:
            logger.log(("error","not enough gems"))

    def parsecommand(self,s):
        command,param = s.split(" ")
        if command == "m":
            try:
                index = int(param)
                param = PONYNAMES[int(param)]
            except:
                pass
            self.move(param)
        elif command == "c":
            try:
                index = int(param)
                param = PONYNAMES[int(param)]
            except:
                pass
            self.calm(param)

    def ponyarrive(self,pony):
        logger.log("event","arrived",pony)
        pony.arrived = True
        self.arrived.append(pony)

    def boulderfall(self):
        pony = self.ponies["AJ"]
        if not pony.arrived and pony.routeloc < len(pony.routenoboulder)-5:
            logger.log("event","changeroute","AJ")
            self.grid[pony.routenoboulder[-6]] = BoulderBlock()
            self.routexy["AJ"] = pony.routewithboulder
            for i,xy in enumerate(self.routexy["AJ"]):
                self.grid[xy] = self.routes["AJ"][i]

    def __repr__(self):
        gridrepr = repr(self.grid).split("\n")
        for name in PONYNAMES:
            xy = self.ponies[name].xy
            row = list(gridrepr[xy[0]])
            row[3*xy[1]:3*xy[1]+len(name)] = name
            gridrepr[xy[0]] = "".join(row)
        gridpart = "\n".join(gridrepr)
        ponypart = repr(self.ponies)
        effectpart = repr(self.timers)
        statspart = "dice:"+repr(self.dice)+" gems:"+repr(self.ponies["RA"].gems)+" maxspeed:"+repr(self.maxdice())
        return "\n".join([gridpart,ponypart,effectpart,statspart])

def startend(mapstr):
    ponyxy = [[] for p in xrange(6)]
    for i,row in enumerate(mapstr):
        #Mane6
        for p in xrange(1,7):
            if str(p) in row:
                ponyxy[p-1].append((i,row.index(str(p))))
    return ponyxy

def bfs(map,xys,ajroute="b"):
    end,start = xys#[complex(*xy) for xy in xys]
    dirs = [(0,1),(0,-1),(1,0),(-1,0)]
    #GRIDHEIGHT = len(map)
    #GRIDWIDTH = len(map[0])
    queue = [(0,start)]
    visited = {start:True}
    i = 0 
    while i<len(queue):
        depth,xy = queue[i]#.pop(0)
        if xy == end:
            break
        i += 1
        #print depth,xy
        for dir in dirs:
            newxy = (xy[0]+dir[0],xy[1]+dir[1])#xy+dir
            #if 0<=newxy[0]<=GRIDWIDTH and 0<=newxy[1]<=GRIDHEIGHT and newxy not in visited and map[newxy[0]][newxy[1]] in GROUND:
            if newxy not in visited and map[newxy[0]][newxy[1]] in GROUND+ajroute:
                visited[newxy] = True
                queue.append((depth+1,newxy))
    return [dxy[1] for dxy in queue]

def genroute(length,pname):
    length -= 2 #reserved for start and end block
    route = [Block() for i in xrange(length)]
    cutoffs = [0,0.33,0.66,1]
    blockdistrib = [[("W +1",3),
                     ("F +1",3)],
                    [("F +1",2),
                     ("F +2",3),
                     ("F -1",2),
                     ("W -1",1)],
                    [("F +1",1),
                     ("F +2",5),
                     ("F -1",1),
                     ("W -1",2)]]
    if pname == "FS":
        blockdistrib[0] = [("W +1",3),
                           ("F +1",2),
                           ("F -2",2)]
    elif pname == "RA":
        blockdistrib[2] = [("G +10",3),
                           ("F +2",5),
                           ("W -1",2)]

    def parseblock(s):
        attrib,diff = s.split(" ")
        translate = {"W":"willpower","F":"fear","G":"gems"}
        return (translate[attrib],int(diff))
    for i in xrange(1,len(cutoffs)):
        indices = range(round(cutoffs[i-1]*length),
                        round(cutoffs[i]*length))
        logger.debug(indices)
        #slice = route[cutoffs[i-1]*length:cutoffs[i]*length]
        random.shuffle(indices)
        numblocks = 0
        for btype,bcount in blockdistrib[i-1]:
            for j in xrange(bcount):
                #print indices[numblocks],len(indices)
                route[indices[numblocks]] = SimpleBlock(*parseblock(btype))
                numblocks += 1
                if numblocks == len(indices):
                    break
            if numblocks == len(indices):
                break
    return [Block()] + route + [EndBlock()]

def printroute(route):
    print [(b.__dict__.get("attrib"," "),b.__dict__.get("diff",0)) for b in route]

if __name__=="__main__":
    map = open("map").read().split("\n")
    ponyxy = startend(map)
    routexy = dict((PONYNAMES[i],bfs(map,xy)) for i,xy in enumerate(ponyxy))
    ajroute1 = bfs(map,ponyxy[2],"b")
    ajroute2 = bfs(map,ponyxy[2],"a")
    #ajroute2 = ajroute1[:-1] + ajroute2[len(ajroute1)-1:]
    ponies = dict((name,Pony(name,ponyxy[i][1])) for i,name in enumerate(PONYNAMES))
    ponies["AJ"].routenoboulder = ajroute1
    ponies["AJ"].routewithboulder = ajroute2
    print len(ajroute1), len(ajroute2)
    routexy["AJ"] = ponies["AJ"].routewithboulder
    routes = dict([(name,genroute(len(routexy[name]),name))
                    for name in PONYNAMES])
    routexy["AJ"] = ponies["AJ"].routenoboulder
    g=Game(map,ponies,routexy,routes,ponyxy)
    #g.move(PONYNAMES[0])

from const import DEBUG, LONGPONYNAMES, LONGBLOCKNAMES, SHORTTOLONG, PONYNAMES, GEMCOST
import random
"""
def log(*s):
    for i in s:
        print i,
    print
"""

def debug(*s):
    if not DEBUG: return
    print "DEBUG:",
    for i in s:
        print i,
    print

def getflavtexts():
    rawflavtext = open("flavtext").read().split("===\n")
    flavtext = {}
    for pname in LONGPONYNAMES:
        flavtext[pname] = {}
        for bname in LONGBLOCKNAMES:
            flavtext[pname][bname] = []
    def parseflavtext(s):
        for pname in LONGPONYNAMES:
            if pname in s:
                for bname in LONGBLOCKNAMES:
                    if bname in s:
                        flavtext[pname][bname].append(s)
                        return
    map(parseflavtext,rawflavtext)
    return flavtext

flavtext = getflavtexts()

flavtext["<Pony>"]["trap 1"] = """<Pony> falls into a trap! When this trap triggers, other traps in the labyrinth are revealed.

Fear +1
"""
flavtext["<Pony>"]["trap 2"] = """<Pony> falls into a trap in plain sight. How clumsy.

Fear +2
"""
flavtext["<Pony>"]["win"] = """<Pony> is too scared to move. Discord dies of boredom. Literally. You've won. Game over."""
flavtext["<Pony>"]["lose"] = """As the last pony is turned from her element, the labyrinth begin to crumble. You lose.

Have the ponies bought Celestia enough time? Could she complete her plan while the ponies entertained him?
"""
flavtext["instruction"] = {}
flavtext["instruction"]["command"]="""
Type "i" to read the full introduction and instructions.
Type "m " followed by the name of a pony to move that pony.
Type "c " followed by the name of use gems to calm that pony.
Pony (shorthand) names are """+" ".join(PONYNAMES)
flavtext["instruction"]["full"] = open("instructions").read()

def log(*s):
    if s == ("event","changeroute","AJ"):
        print "Rarity scarcely avoids a rock slide! That rocks lands elsewhere in the labyrinth. They now block Applejack's path so she must find a way around them."
    elif s[:3] == ("event","special","TS"):
        print "Twilight boosts %s's Willpower by 1 more!" % SHORTTOLONG[s[3]]
    elif s[:3] == ("event","special","FS"):
        print "Fluttershy is scared but doesn't want to lose any more friends. Her Willpower increases by 1."
    elif s[:2] == ("event","arrived"):
        print "%s arrives as a strange place in the maze. It feels like this was all part of Discord's plan." % SHORTTOLONG[s[2]]
    elif s[:2] == ("event","discord"):
        print "Discord reduced %s's Willpower by 1!" % SHORTTOLONG[s[2]]
    elif s[:2] == ("event","discorded"):
        print "Discord turned %s against her own element!" % SHORTTOLONG[s[2]]
    elif s[:3] == ("effect","flutter fear"):
        print """Fluttershy is being a scaredy pony. Its not her fault.

Fear +1"""
    elif s[:2] == ("effect","rarity"):
        print "Rarity finds %s gem(s)." % s[2]
    elif s[:2] == ("effect","global fear"):
        print "The longer they stay, the more unpredictable the labyrinth gets.\n\nFear +1 to all ponies."
    elif s[:2] == ("effect","pinkie song"):
        print "Pinkie Pie sings a silly song. It echoes throughout the labyrinth.\n\nFear -1 to all ponies."
    elif s[0] == "calm":
        print "Shiny gems calms %s." % SHORTTOLONG[s[1]]
    elif s[0] == "land":
        pname = SHORTTOLONG[s[1]]
        ename = s[2].capitalize()+" "+"+"*(s[3]>0)+str(s[3])
        allft = flavtext[pname][ename] + flavtext["<Pony>"][ename]
        if DEBUG:
            print "DEBUG:",allft
        print random.choice(allft).replace("<Pony>",pname)
    elif s[0] == "trigger":
        print flavtext["<Pony>"][s[1]].replace("<Pony>",SHORTTOLONG[s[2]])
    elif s[0] == "limit":
        print "%s's %s cannot drop below 0 and is set to 0." % (SHORTTOLONG[s[2]],s[1])
    elif s[0] == "limit":
        print "%s's %s cannot reach above 3 and is set to 3." % (SHORTTOLONG[s[2]],s[1])
    elif s[:2] == ("error","arrived"):
        print "%s arrived at her destination and cannot move further." % SHORTTOLONG[s[2]]
    elif s == ("error","not enough gems"):
        print "You do not have enough gems (costs %s gems)" % GEMCOST
    #elif s[:2] == ("gameover","win"):
    elif s[0] == "gameover":
        print flavtext["<Pony>"][s[1]].replace("<Pony>",SHORTTOLONG[s[2]])
    elif s[:2] == ("instruction","command"):
        print flavtext["instruction"]["command"]
    elif s[:2] == ("instruction","full"):
        print flavtext["instruction"]["full"]
    else:
        for i in s:
            print i,
        print

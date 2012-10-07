from const import DEBUG, LONGPONYNAMES, LONGBLOCKNAMES, SHORTTOLONG
import random
"""
def log(*s):
    for i in s:
        print i,
    print
"""

def debug(*s):
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

def log(*s):
    if s == ("event","changeroute","AJ"):
        print "Rarity scarcely avoids a rock slide! That rocks lands elsewhere in the labyrinth."
    elif s[:3] == ("event","special","TS"):
        print "Twilight boosts %s's Willpower by 1 more!" % SHORTTOLONG[s[3]]
    elif s[:2] == ("event","arrived"):
        print "%s arrives as a strange place in the maze. It feels like this was all part of Discord's plan." % SHORTTOLONG[s[2]]
    elif s[:2] == ("event","discord"):
        print "Discord reduced %s's Willpower by 1!" % SHORTTOLONG[s[2]]
    elif s[:2] == ("event","discorded"):
        print "Discord turned %s against their own element!" % SHORTTOLONG[s[2]]
    elif s[:2] == ("effect","rarity"):
        print "Rarity finds %s gem(s)." % s[2]
    elif s[0] == "calm":
        print "Shiny gems calms %s." % SHORTTOLONG[s[1]]
    elif s[0] == "land":
        pname = SHORTTOLONG[s[1]]
        ename = s[2].capitalize()+" "+"+"*(s[3]>0)+str(s[3])
        allft = flavtext[pname][ename] + flavtext["<Pony>"][ename]
        if DEBUG:
            print allft
        print random.choice(allft).replace("<Pony>",pname)
    elif s[0] == "trigger":
        print flavtext["<Pony>"][s[1]].replace("<Pony>",SHORTTOLONG[s[2]])
    elif s[0] == "limit":
        print "%s's %s cannot drop below 0 and is set to 0." % (SHORTTOLONG[s[2]],s[1])
    elif s[0] == "limit":
        print "%s's %s cannot reach above 3 and is set to 3." % (SHORTTOLONG[s[2]],s[1])
    elif s[:2] == ("error","arrived"):
        print "%s arrived at her destination and cannot move further." % SHORTTOLONG[s[2]]
    else:
        for i in s:
            print i,
        print

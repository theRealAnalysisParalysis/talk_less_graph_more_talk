
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict
from pathlib import Path
import math

W, H = 1800, 1100
LEFT_PAD, RIGHT_PAD = 100, 100
TOP_PAD, BOTTOM_PAD = 100, 120
NODE_R = 24
FONT_SIZE = 16

BASE_T = 450.0
EPS = 1e-6
T_MIN, T_MAX = 40.0, 520.0

K_SPRING = 0.010
K_ORDER  = 0.060
K_REPEL  = 1200.0
DAMP     = 0.88
STEPS    = 1400
MIN_GAP  = 80.0

ONLY_SAME_LANE = True

RAW_NODES = [
("Best of Wives and Best of Women", 0),
("It's Quiet Uptown", 0),
("Non-Stop", 0),
("Stay Alive (Reprise)", 0),
("Stay Alive", 0),
("Take a Break", 0),
("That Would Be Enough", 0),
("The Schuyler Sisters", 0),
("A Winter's Ball", 1),
("Alexander Hamilton", 1),
("Guns and Ships", 1),
("Helpless", 1),
("Satisfied", 1),
("The Reynolds Pamphlet", 1),
("What'd I Miss", 1),
("Aaron Burr", 2),
("Hurricane", 2),
("The Election of 1800", 2),
("The Obedient Servant", 2),
("The Room Where It Happens", 2),
("Wait For It", 2),
("Blow Us All Away", 3),
("My Shot", 3),
("Right Hand Man", 3),
("Ten Duel Commandments", 3),
("The World Was Wide Enough", 3),
("Yorktown", 3),
("Cabinet Battle #1", 4),
("Cabinet Battle #2", 4),
("Meet Me Inside", 4),
("Finale (Who Lives, Who Dies, Who Tells Your Story)", 5),
("History Has Its Eye on You", 5),
("One Last Time", 5),
("Say No to This", 6),
("The Adams Administration", 6),
("We Know", 6),
("I Know Him", 7),
("What Comes Next", 7),
("You'll Be Back", 7),
("The Story of Tonight (Reprise)", 8),
("The Story of Tonight", 8),
("Burn", 9),
("Dear Theodosia", 10),
]

RAW_WEIGHTS = [
("A Winter's Ball","Helpless",0.12121199816465378),
("A Winter's Ball","What'd I Miss",0.1893939971923828),
("Aaron Burr","The Election of 1800",0.24888299405574799),
("Aaron Burr","The Room Where It Happens",0.33319199085235596),
("Alexander Hamilton","A Winter's Ball",0.27272701263427734),
("Alexander Hamilton","Guns and Ships",0.1889529973268509),
("Alexander Hamilton","Helpless",0.15976299345493317),
("Alexander Hamilton","Satisfied",0.3865880072116852),
("Best of Wives and Best of Women","Finale (Who Lives, Who Dies, Who Tells Your Story)",0.6533330082893372),
("Best of Wives and Best of Women","The World Was Wide Enough",0.21333299577236176),
("Blow Us All Away","The World Was Wide Enough",0.42935800552368164),
("Guns and Ships","The World Was Wide Enough",0.1424420028924942),
("Helpless","Satisfied",0.6038169860839844),
("Helpless","Say No to This",0.12771299481391907),
("History Has Its Eye on You","Finale (Who Lives, Who Dies, Who Tells Your Story)",6.570312023162842),
("History Has Its Eye on You","Hurricane",0.40625),
("History Has Its Eye on You","Non-Stop",0.28125),
("History Has Its Eye on You","One Last Time",0.28125),
("It's Quiet Uptown","Best of Wives and Best of Women",0.21333299577236176),
("My Shot","Blow Us All Away",0.4660550057888031),
("My Shot","Non-Stop",0.39969998598098755),
("My Shot","Right Hand Man",0.4196459949016571),
("My Shot","The World Was Wide Enough",0.30522701144218445),
("My Shot","Yorktown",0.9956120252609253),
("Non-Stop","Best of Wives and Best of Women",1.5466669797897339),
("Non-Stop","Finale (Who Lives, Who Dies, Who Tells Your Story)",0.11556600034236908),
("Non-Stop","Hurricane",0.43586599826812744),
("Non-Stop","It's Quiet Uptown",0.2070779949426651),
("Non-Stop","Take a Break",0.3188909888267517),
("Non-Stop","The Reynolds Pamphlet",0.10310500115156174),
("Non-Stop","The Room Where It Happens",0.10206799954175949),
("One Last Time","Hurricane",0.12328799813985825),
("Right Hand Man","Non-Stop",0.1649090051651001),
("Right Hand Man","Yorktown",0.379595011472702),
("Satisfied","Non-Stop",0.35783201456069946),
("Satisfied","The Reynolds Pamphlet",1.0787149667739868),
("Say No to This","We Know",3.020941972732544),
("Stay Alive","Stay Alive (Reprise)",0.3974139988422394),
("Take a Break","Blow Us All Away",0.20733900368213654),
("Take a Break","It's Quiet Uptown",0.12921899557113647),
("Take a Break","Stay Alive (Reprise)",2.339920997619629),
("Take a Break","The World Was Wide Enough",0.11911799758672714),
("Ten Duel Commandments","Blow Us All Away",0.9750890135765076),
("Ten Duel Commandments","Take a Break",0.2882559895515442),
("Ten Duel Commandments","The World Was Wide Enough",4.16726016998291),
("That Would Be Enough","Best of Wives and Best of Women",0.21333299577236176),
("That Would Be Enough","It's Quiet Uptown",0.985850989818573),
("That Would Be Enough","Non-Stop",4.068759918212891),
("That Would Be Enough","Take a Break",0.8476690053939819),
("The Adams Administration","We Know",0.12598399817943573),
("The Room Where It Happens","Hurricane",0.3125779926776886),
("The Room Where It Happens","The Obedient Servant",1.1073620319366455),
("The Room Where It Happens","We Know",0.2617799937725067),
("The Schuyler Sisters","It's Quiet Uptown",0.12921899557113647),
("The Schuyler Sisters","Non-Stop",0.5553320050239563),
("The Schuyler Sisters","Say No to This",0.12307699769735336),
("The Schuyler Sisters","Take a Break",0.4482870101928711),
("The Schuyler Sisters","That Would Be Enough",1.7179499864578247),
("The Story of Tonight (Reprise)","The Election of 1800",0.23301200568675995),
("The Story of Tonight (Reprise)","The World Was Wide Enough",0.24584700167179108),
("The Story of Tonight (Reprise)","Yorktown",0.16279099881649017),
("The Story of Tonight","The Story of Tonight (Reprise)",3.160428047180176),
("The Story of Tonight","The World Was Wide Enough",0.1336899995803833),
("Wait For It","Hurricane",3.5535519123077393),
("Wait For It","Non-Stop",0.16933700442314148),
("Wait For It","The Room Where It Happens",0.16933700442314148),
("Wait For It","The World Was Wide Enough",0.5361779928207397),
("Yorktown","Non-Stop",0.49789199233055115),
("Yorktown","The World Was Wide Enough",0.37469199299812317),
]

ORDER = {
"Alexander Hamilton": 1,"Aaron Burr": 2,"My Shot": 3,"The Story of Tonight": 4,"The Schuyler Sisters": 5,
"Farmer Refuted": 6,"You'll Be Back": 7,"Right Hand Man": 8,"A Winter's Ball": 9,"Helpless": 10,"Satisfied": 11,
"The Story of Tonight (Reprise)": 12,"Wait For It": 13,"Stay Alive": 14,"Ten Duel Commandments": 15,"Meet Me Inside": 16,
"That Would Be Enough": 17,"Guns and Ships": 18,"History Has Its Eye on You": 19,"Yorktown": 20,"What Comes Next": 21,
"Dear Theodosia": 22,"Non-Stop": 23,"What'd I Miss": 24,"Cabinet Battle #1": 25,"Take a Break": 26,"Say No to This": 27,
"The Room Where It Happens": 28,"Schuyler Defeated": 29,"Cabinet Battle #2": 30,"Washington on Your Side": 31,
"One Last Time": 32,"I Know Him": 33,"The Adams Administration": 34,"We Know": 35,"Hurricane": 36,"The Reynolds Pamphlet": 37,
"Burn": 38,"Blow Us All Away": 39,"Stay Alive (Reprise)": 40,"It's Quiet Uptown": 41,"The Election of 1800": 42,
"The Obedient Servant": 43,"Best of Wives and Best of Women": 44,"The World Was Wide Enough": 45,
"Finale (Who Lives, Who Dies, Who Tells Your Story)": 46
}

# Build nodes
nodes = []
name_to_idx = {}
for name, group in RAW_NODES:
    if name not in name_to_idx:
        idx = len(nodes)
        name_to_idx[name] = idx
        nodes.append({"name": name, "group": group})

# Weights -> undirected max
weights = defaultdict(float)
for a, b, w in RAW_WEIGHTS:
    if a not in name_to_idx or b not in name_to_idx: 
        continue
    i, j = name_to_idx[a], name_to_idx[b]
    if i == j: 
        continue
    key = tuple(sorted((i, j)))
    if w > weights[key]:
        weights[key] = w

# Lanes & order
max_lane = max(n["group"] for n in nodes)
LANE_SPACING = (H - TOP_PAD - BOTTOM_PAD) / (1 + max_lane)
ORDER_RANK = {n["name"]: ORDER.get(n["name"], 10_000) for n in nodes}
min_order = min(ORDER_RANK.values())
max_order = max(ORDER_RANK.values())

def base_x(ord_val: int) -> float:
    if max_order == min_order:
        return LEFT_PAD + (W - LEFT_PAD - RIGHT_PAD) / 2.0
    frac = (ord_val - min_order) / (max_order - min_order)
    return LEFT_PAD + frac * (W - LEFT_PAD - RIGHT_PAD)

for n in nodes:
    n["x"] = base_x(ORDER_RANK[n["name"]])
    n["y"] = TOP_PAD + n["group"] * LANE_SPACING

# Edges
edges = []
for (i, j), w in weights.items():
    ni, nj = nodes[i], nodes[j]
    if ONLY_SAME_LANE and ni["group"] != nj["group"]:
        continue
    t = BASE_T / max(w, EPS)
    t = max(T_MIN, min(T_MAX, t))
    edges.append((i, j, t, "W"))

lane_to_indices = defaultdict(list)
for idx, n in enumerate(nodes):
    lane_to_indices[n["group"]].append(idx)

for lane, idxs in lane_to_indices.items():
    idxs.sort(key=lambda k: ORDER_RANK[nodes[k]["name"]])
    for a, b in zip(idxs, idxs[1:]):
        edges.append((a, b, 110.0, "ORDER"))

# Solver
vx = [0.0]*len(nodes)
for step in range(STEPS):
    fx = [0.0]*len(nodes)

    for i, j, target, kind in edges:
        ni, nj = nodes[i], nodes[j]
        dx = nj["x"] - ni["x"]
        dist = abs(dx) + 1e-9
        k = K_ORDER if kind == "ORDER" else K_SPRING
        force = k * (dist - target)
        dirx = 1.0 if dx >= 0 else -1.0
        fx[i] += force * dirx
        fx[j] -= force * dirx

    for lane, idxs in lane_to_indices.items():
        for a in range(len(idxs)):
            for b in range(a+1, len(idxs)):
                i, j = idxs[a], idxs[b]
                ni, nj = nodes[i], nodes[j]
                dx = nj["x"] - ni["x"]
                dist2 = dx*dx + 0.01
                rep = K_REPEL / dist2
                dirx = 1.0 if dx >= 0 else -1.0
                fx[i] -= rep * dirx
                fx[j] += rep * dirx

    for i, n in enumerate(nodes):
        vx[i] = (vx[i] + fx[i]) * DAMP
        n["x"] += vx[i]
        n["x"] = max(LEFT_PAD + NODE_R, min(W - RIGHT_PAD - NODE_R, n["x"]))

# Monotone clamp
for lane, idxs in lane_to_indices.items():
    idxs.sort(key=lambda k: ORDER_RANK[nodes[k]["name"]])
    last_x = LEFT_PAD + NODE_R
    for k in idxs:
        nodes[k]["x"] = max(nodes[k]["x"], last_x)
        last_x = nodes[k]["x"] + MIN_GAP

# Render
def load_background():
    for p in (Path("/mnt/data/58030eae-9fe6-43f2-8f2d-7a049f42d92a.png"),
              Path("/mnt/data/9c400e32-c9dc-4802-a44e-2b8e88bb9f5b.png")):
        if p.exists():
            return Image.open(p).convert("RGBA").resize((W, H))
    bg = Image.new("RGBA", (W, H), (20,20,20,255))
    cx, cy = W//2, H//2
    maxr = math.hypot(cx, cy)
    px = bg.load()
    for y in range(H):
        for x in range(W):
            r = math.hypot(x-cx, y-cy)
            v = int(235 - 190*(r/maxr))
            v = max(30, min(235, v))
            px[x, y] = (v, v, v, 255)
    return bg

img = load_background()
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONT_SIZE)
except:
    font = ImageFont.load_default()

PALETTE = [
    (82, 186, 255), (140, 233, 154), (250, 176, 5), (255, 121, 97),
    (110, 64, 170), (255, 214, 102), (84, 160, 255), (255, 99, 132),
    (100, 181, 246), (255, 167, 38), (171, 71, 188)
]

for lane in sorted(set(n["group"] for n in nodes)):
    y = TOP_PAD + lane * LANE_SPACING
    for x in range(int(LEFT_PAD), int(W - RIGHT_PAD), 12):
        draw.line([(x, y), (x + 6, y)], fill=(255, 255, 255, 60), width=1)

for n in nodes:
    x, y = n["x"], n["y"]
    color = PALETTE[n["group"] % len(PALETTE)]
    bbox = [x-NODE_R, y-NODE_R, x+NODE_R, y+NODE_R]
    draw.ellipse(bbox, fill=(*color, 220), outline=(20,20,20,255), width=2)

for i, n in enumerate(nodes):
    x, y = n["x"], n["y"]
    label = n["name"].replace(" (Reprise)", "")
    tb = draw.textbbox((0,0), label, font=font)
    tw, th = tb[2], tb[3]
    dy = -NODE_R - 6 if (i % 2 == 0) else NODE_R + 6
    tx, ty = x - tw/2, y + dy
    draw.text((tx+1, ty+1), label, font=font, fill=(0,0,0,200))
    draw.text((tx, ty), label, font=font, fill=(255,255,255,255))

title = "Hamilton – Weighted Proximity (No Edges)"
tb = draw.textbbox((0,0), title, font=font)
draw.text((W/2 - tb[2]/2, 20), title, font=font, fill=(255,255,255,220))

out = Path("/hamilton_layout_v2.png")
img.save(out)
print(f"Saved: {out}")

import requests
import os
from typing import Final
from dotenv import load_dotenv
from osrparse import Replay
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from roundcorner import add_rounded_corners
#extract data from local replay

r = Replay.from_path("./My Angel Chino - BlackY vs. Yooh - HAVOX (Long Ver.) [RESPADOGI'S INSANE] (2024-06-05) Osu.osr")

beatmap_hash = r.beatmap_hash
player = r.username
play_maxcombo = str(r.max_combo)
c300 = r.count_300
c100 = r.count_100
c50 = r.count_50
c0 = r.count_miss
username = r.username
play_accuracy = (300*(c300) + 100*(c100) + 50*(c50)) / (300*(c300 + c100 + c50 + c0))

#extract data from beatmap online
load_dotenv()
userAPI: Final[str] = os.getenv("osu_API")
url = f"https://osu.ppy.sh/api/get_beatmaps?k={userAPI}&h={beatmap_hash}"

beatmap_data = requests.get(url)
if beatmap_data.status_code == 200:
    bdata = beatmap_data.json()
    beatmap_name = bdata[0]['title']
    max_combo = str(bdata[0]['max_combo'])
    diff_name = bdata[0]['version']
    circle_size = bdata[0]['diff_size']
    overall_diff = bdata[0]['diff_overall']
    approach_rate = bdata[0]['diff_approach']
    drain_HP = bdata[0]['diff_drain']
    beatmap_BPM = bdata[0]['bpm']
    mapper = bdata[0]['creator']
    star_rating = float(bdata[0]['difficultyrating'])
    map_status = bdata[0]['approved']
else: 
    print(f"There is something wrong, probably peppy got dunked")

#extract player avatar
if not os.path.exists(f'./player/{username}.png'):
    user = f"https://osu.ppy.sh/api/get_user?k={userAPI}&u={username}"
    user_data = requests.get(user)
    if user_data.status_code == 200:
        a_data = user_data.json()
        userID = a_data[0]['user_id']
    else: 
        print(f"There is something wrong, probably peppy got dunked")

        #fetching the avatar and download it

    avatar = f"https://a.ppy.sh/{userID}"
    avatar_data = requests.get(avatar)
    if avatar_data.status_code == 200:
        playerAvatar = Image.open(BytesIO(avatar_data.content))
        playerAvatar.save(f'./player/{username}.png')

        with Image.open(f'./player/{username}.png') as PlayerAvatar:
            a = add_rounded_corners(PlayerAvatar, radius=50).resize(size=(180, 180))
            a.save(f'./player/{username}.png')

    else:
        print(f"There is something wrong, probably peppy got dunked")
    
#Mod flags
NoMod       =  0
NoFail      =  1 << 0
Easy        =  1 << 1
Hidden      =  1 << 3
HardRock    =  1 << 4
SuddenDeath =  1 << 5
DoubleTime  =  1 << 6
Relax       =  1 << 7
HalfTime    =  1 << 8
Nightcore   =  1 << 9
Flashlight  =  1 << 10

#creating the image
background = Image.open("./deps/bone.png")
draw = ImageDraw.Draw(background)

font_path = "./fonts/BEBASNEUE-REGULAR.TTF"

playcombo = f"{play_maxcombo}/{max_combo}X"

texts = [
    {"type": "player", "text": f"{player}", "position": [244, 47.74], "font_size": 138.58},
    {"type": "beatmap_name", "text": f"{beatmap_name}", "position": (1425, 875.2), "font_size": 60},
    {"type": "playcombo", "text": f"{playcombo}", "position": (48.5, 968.8), "font_size": 70},
    {"type": "play_accuracy", "text": f"{play_accuracy:.2%}","position": [900, 951.8], "font_size": 90},
    {"type": "circle_size", "text": f"CS: {circle_size}", "position": [1774.41, 642], "font_size": 61.34},
    {"type": "overall_diff", "text": f"OD: {overall_diff}","position": [1774.41, 537.45], "font_size": 61.34},
    {"type": "approach_rate", "text": f"AR: {approach_rate}","position": [1774.41, 329.3], "font_size": 61.34},
    {"type": "drain_HP", "text": f"HP: {drain_HP}", "position": [1774.41, 748.3], "font_size": 61.34},
    {"type": "beatmap_BPM", "text": f"{beatmap_BPM}BPM", "position": [1765.51, 15], "font_size": 47},
    {"type": "mapper", "text": f"{mapper}", "position": [1575.1, 95.1], "font_size": 47},
    {"type": "star_rating", "text": f"{star_rating:.2f}*", "position": [1774.41, 433.46], "font_size": 61.34},
    {"type": "c300", "text": f"{str(c300)}x", "position": [26.39, 388.27], "font_size": 69.57},
    {"type": "c100", "text": f"{str(c100)}x", "position": [70.11, 523.1], "font_size": 69.57},
    {"type": "c50", "text": f"{str(c50)}x", "position": [70.11, 655.51], "font_size": 69.57},
    {"type": "c0", "text": f"{str(c0)}x", "position": [70.11, 790], "font_size": 69.57},
]

# Function to check if a data entry exists and update or append
def update_or_append_text(texts: list, type: str,  new_text: str, new_position: list[int], new_font_size: int):
    for item in texts:
        if item['type'] == type:
            # Update the existing entry
            item['position'] = new_position
            item['font_size'] = new_font_size
            return
    # If not found, append the new entry
    texts.append({"type": type, "text": new_text, "position": new_position, "font_size": new_font_size})

existing_attr = set()
unique_texts = []
for item in texts:
    if item['type'] not in existing_attr:
        unique_texts.append(item)
        existing_attr.add(item['type'])

texts = unique_texts

#handling SS plays
if play_accuracy == 1.0:
    for item in texts:
        if item['type'] == "play_accuracy":
            item['position'] = [875, 951.8]

#handling grade
grade_pos = [325, 190]

percent_50 = c50 / (c300 + c100 + c50 +  c0)
c300_percent = c300 / (c300 + c100 + c50 +  c0)
if (play_accuracy == 1):
    if (r.mods & Hidden or r.mods & Flashlight):
        XH_grade = Image.open('./statics/ranking-XH.png')
        background.paste(XH_grade, grade_pos, XH_grade)
    else:
        SS_grade = Image.open('./statics/ranking-X.png')
        background.paste(SS_grade, grade_pos, SS_grade)

elif (c300_percent < 1 and c300_percent > 0.9 and percent_50 <= 0.01 and c0 == 0):
    if (r.mods & Hidden or r.mods & Flashlight):
        SH_grade = Image.open('./statics/ranking-SH.png')
        background.paste(SH_grade, grade_pos, SH_grade)
    else:
        S_grade = Image.open('./statics/ranking-S.png')
        background.paste(S_grade, grade_pos, S_grade)

elif ((c300_percent > 0.8 and c300_percent <= 0.9 and c0 == 0) or (c300_percent > 0.9 and c0 > 0)):
    A_grade = Image.open('./statics/ranking-A.png')
    background.paste(A_grade, grade_pos, A_grade)

elif ((c300_percent > 0.7 and c300_percent <= 0.8 and c0 == 0) or (c300_percent > 0.8 and c300_percent <= 0.9 and c0 > 0)):
    B_grade = Image.open('./statics/ranking-B.png')
    background.paste(B_grade, grade_pos, B_grade)

elif (c300_percent > 0.6 and c300_percent <= 0.7):
    C_grade = Image.open('./statics/ranking-C.png')
    background.paste(C_grade, grade_pos, C_grade)

else:
    D_grade = Image.open('./statics/ranking-D.png')
    background.paste(D_grade, grade_pos, D_grade)

#handling text length
#handling combo
combo_based_position = 48.5
combo_increment = 7

combo_position = combo_based_position + (10 - len(playcombo))*combo_increment
for item in texts:
    if item['type'] == "playcombo":
        item['position'] = [combo_position, 968.8]

#handling mapper
mapper_base_position = 1575.1
position_increment = 8.5

adjusted_position = mapper_base_position + (14 - len(mapper)) * position_increment

for item in texts:
    if item['type'] == "mapper":
        item['position'] = [adjusted_position, 95.1]

#handling hit counter:
count_based_pos = 70.11
count_increment = 9.86
c300_pos = count_based_pos + (1 - len(str(c300)) * count_increment)
c100_pos = count_based_pos + (1 - len(str(c100)) * count_increment)
c50_pos = count_based_pos + (1 - len(str(c50)) * count_increment)
c0_pos = count_based_pos + (1 - len(str(c0)) * count_increment)

for item in texts:
    if item['type'] == "c100":
        item['position'] = [c100_pos, 523.1]
    elif item['type'] == "c300":
        item['position'] = [c300_pos, 388.27]
    elif item['type'] == "c50":
        item['position'] = [c50_pos, 655.51]
    elif item['type'] == "c0":
        item['position'] = [c0_pos, 790]
    

#checking map status
status_icon = [1670, 15]
if map_status == "1":
    texts.append({"type": "map status", "text": "Ranked", "position": [1507, 15], "font_size": 47})
    ranked = Image.open('./statics/ranked blue.png')
    background.paste(ranked, status_icon, ranked)

elif map_status == "2":
    texts.append({"type": "map status", "text": "Approved", "position": [1500.75, 18], "font_size": 40})
    approved = Image.open('./statics/approved.png')
    background.paste(approved, status_icon, approved)

elif map_status == "3":
    texts.append({"type": "map status", "text": "Qualified", "position": [1275.51, 15], "font_size": 38})
    qualified = Image.open('./statics/approved.png')
    background.paste(qualified, status_icon, qualified)

elif map_status == "4":
    texts.append({"type": "map status", "text": "Loved", "position": [1520, 13], "font_size": 47})
    loved = Image.open('./statics/loved.png')
    background.paste(loved, [1675, 17], loved)

#get the player avatar on screen
playAvatar = Image.open(f'./player/{username}.png')
background.paste(playAvatar, [35, 15], playAvatar)
#getting all da stuff on screen
for item in texts:
    font = ImageFont.truetype(font_path, item["font_size"])
    draw.text(item["position"], item["text"], font=font, fill="white")
    print(", ".join('{}: {}'.format(key, val) for key, val in item.items()))


#background.show()
background.save(f"./tests/{player} on {beatmap_name} [{diff_name}].png")
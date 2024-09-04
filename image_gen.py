import requests
import os
from typing import Final
from dotenv import load_dotenv
import osrparse
from osrparse import Replay, parse_replay_data
import PIL
from PIL import Image, ImageDraw, ImageFont

#extract data from local replay

r = Replay.from_path("./Kamensh1k - UNDEAD CORPORATION - MEGALOMANIA [woof] (2023-12-24) Osu.osr")

beatmap_hash = r.beatmap_hash
player = r.username
play_maxcombo = str(r.max_combo)
count300 = r.count_300
count100 = r.count_100
count50 = r.count_50
count0 = r.count_miss
play_accuracy = (300*(count300) + 100*(count100) + 50*(count50)) / (300*(count300 + count100 + count50 + count0))

print(f"Count100: {count100}, {type(count100)}")
print(f"Count50: {count50}, {type(count50)}")
print(f"Count0: {count0}, {type(count0)}")

#extract data from beatmap online
load_dotenv()
userAPI: Final[str] = os.getenv("osu_API")
url = f"https://osu.ppy.sh/api/get_beatmaps?k={userAPI}&h={beatmap_hash}"

print(url)

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    beatmap_name = data[0]['title']
    max_combo = str(data[0]['max_combo'])
    diff_name = data[0]['version']
    circle_size = data[0]['diff_size']
    overall_diff = data[0]['diff_overall']
    approach_rate = data[0]['diff_approach']
    drain_HP = data[0]['diff_drain']
    beatmap_BPM = data[0]['bpm']
    mapper = data[0]['creator']
    star_rating = float(data[0]['difficultyrating'])

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
    {"text": f"{player}", "position": [244, 47.74], "font_size": 138.58},
    {"text": f"{beatmap_name}", "position": (1425, 875.2), "font_size": 60},
    {"text": f"{playcombo}", "position": (48.5, 968.8), "font_size": 70},
    {"text": f"{play_accuracy:.2%}","position": [900, 951.8], "font_size": 90},
    {"text": f"CS: {circle_size}", "position": [1774.41, 642], "font_size": 61.34},
    {"text": f"OD: {overall_diff}","position": [1774.41, 537.45], "font_size": 61.34},
    {"text": f"AR: {approach_rate}","position": [1774.41, 329.3], "font_size": 61.34},
    {"text": f"HP: {drain_HP}", "position": [1774.41, 748.3], "font_size": 61.34},
    {"text": f"{beatmap_BPM}BPM", "position": [1765.51, 15], "font_size": 47},
    {"text": f"{mapper}", "position": [1575.1, 95.1], "font_size": 47},
    {"text": f"{star_rating:.2f}*", "position": [1774.41, 433.46], "font_size": 61.34},
    {"text": f"{str(count300)}x", "position": [26.39, 388.27], "font_size": 69.57},
    {"text": f"{str(count100)}x", "position": [70.1, 523.1], "font_size": 69.57},
    {"text": f"{str(count50)}x", "position": [70.11, 655.51], "font_size": 69.57},
    {"text": f"{str(count0)}x", "position": [70.12, 790], "font_size": 69.57},
]
   
# Function to check if a text entry exists and update or append
def update_or_append_text(texts, new_text, new_position, new_font_size):
    for item in texts:
        if item['text'] == new_text:
            # Update the existing entry
            item['position'] = new_position
            item['font_size'] = new_font_size
            return
    # If not found, append the new entry
    texts.append({"text": new_text, "position": new_position, "font_size": new_font_size})

existing_texts = set()
unique_texts = []
for item in texts:
    if item['text'] not in existing_texts:
        unique_texts.append(item)
        existing_texts.add(item['text'])

texts = unique_texts

#handling SS plays
if play_accuracy == 1.0:
    for item in texts:
        if item['text'] == f"{play_accuracy:.2%}":
            item['position'] = [875, 951.8]

#handling grade
grade_pos = [380, 190]

percent_50 = count50 / (count300 + count100 + count50 +  count0)
count300_percent = count300 / (count300 + count100 + count50 +  count0)
if (play_accuracy == 1):
    if (r.mods & Hidden or r.mods & Flashlight):
        XH_grade = Image.open('./statics/ranking-XH.png')
        background.paste(XH_grade, grade_pos, XH_grade)
    else:
        SS_grade = Image.open('./statics/ranking-X.png')
        background.paste(SS_grade, grade_pos, SS_grade)

elif (count300_percent < 1 and count300_percent > 0.9 and percent_50 <= 0.01 and count0 == 0):
    if (r.mods & Hidden or r.mods & Flashlight):
        SH_grade = Image.open('./statics/ranking-SH.png')
        background.paste(SH_grade, grade_pos, SH_grade)
    else:
        S_grade = Image.open('./statics/ranking-S.png')
        background.paste(S_grade, grade_pos, S_grade)

elif ((count300_percent > 0.8 and count300_percent <= 0.9 and count0 == 0) or (count300_percent > 0.9 and count0 > 0)):
    A_grade = Image.open('./statics/ranking-A.png')
    background.paste(A_grade, grade_pos, A_grade)

elif ((count300_percent > 0.7 and count300_percent <= 0.8 and count0 == 0) or (count300_percent > 0.8 and count300_percent <= 0.9 and count0 > 0)):
    B_grade = Image.open('./statics/ranking-B.png')
    background.paste(B_grade, grade_pos, B_grade)

elif (count300_percent > 0.6 and count300_percent <= 0.7):
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
    if item['text'] == f"{playcombo}":
        item['position'] = [combo_position, 968.8]

#handling mapper
mapper_base_position = 1575.1
position_increment = 8.5

adjusted_position = mapper_base_position + (14 - len(mapper)) * position_increment

for item in texts:
    if item['text'] == f"{mapper}":
        item['position'] = [adjusted_position, 95.1]

#handling hit counter:


#todo list: checking map status
#todo list: handling count100, count50 and count0 being "0x"





for item in texts:
    font = ImageFont.truetype(font_path, item["font_size"])
    draw.text(item["position"], item["text"], font=font, fill="white")
    print(f"Text: {item['text']}, Position: {item['position']}, Font Size: {item['font_size']}")


#background.show()
background.save(f"./tests/{player} on {beatmap_name} [{diff_name}].png")

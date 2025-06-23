import requests
import psutil
import os
from typing import Final
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from roundcorner import add_rounded_corners
import json
import time
import sys
#detecting if osu and tosu is running
def is_program_running(process_name):
    for proc in psutil.process_iter(['name']):
        try:
            # Check if process name matches
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Handle potential errors if a process disappears or access is denied
            pass
    return False

if not is_program_running("tosu.exe") and is_program_running("osu!.exe"):
    print(f"No instance of tosu and osu! detected! Quitting...")
    time.sleep(3)
    sys.exit()
  
#extract data from beatmap using tosu
load_dotenv()
userAPI: Final[str] = os.getenv("osu_API")

mapData = requests.get(url="http://localhost:24050/json")

if not mapData.status_code == 200:
    print(f"Please check if either osu! is running or tosu is running correctly.")
else:
    data = json.loads(mapData.content)
    #map stats:
    max_combo = data["menu"]["bm"]["stats"]["maxCombo"]
    circle_size = data["menu"]["bm"]["stats"]["CS"]
    overall_diff = data["menu"]["bm"]["stats"]["OD"]
    approach_rate = data["menu"]["bm"]["stats"]['AR']
    drain_HP = data["menu"]["bm"]["stats"]["HP"]
    beatmap_BPM = data["menu"]["bm"]["stats"]["BPM"]["common"]
    star_rating = data["menu"]["bm"]["stats"]["fullSR"]
    mapper = data["menu"]["bm"]["metadata"]["mapper"]
    beatmap_hash = data["menu"]["bm"]["md5"]
    titleUnicode = data["menu"]["bm"]["metadata"]["title"]
    diff_name = data["menu"]["bm"]["metadata"]["difficulty"]
    #result from the replay file
    username = data["resultsScreen"]["name"]
    play_maxcombo = data["resultsScreen"]["maxCombo"]
    play_accuracy = data["resultsScreen"]["accuracy"]
    c300 = data["resultsScreen"]["300"]
    c100 = data["resultsScreen"]["100"]
    c50 = data["resultsScreen"]["50"]
    c0 = data["resultsScreen"]["0"]
    mods_string = data["resultsScreen"]["mods"]["str"]
    mods_num = data["resultsScreen"]["mods"]["num"]
    grade = data["resultsScreen"]["grade"]
    submitted_time = data["resultsScreen"]["createdAt"]

ppData = requests.get(url=f"http://localhost:24050/api/calculate/pp?mode=0&mods={mods_num}&acc={play_accuracy}")

if not ppData.status_code == 200:
    print(f"Please check if either osu! is running or tosu is running correctly.")
else:
    pp_Data = json.loads(ppData.content)
    playPp = pp_Data["pp"]
    print(f"{playPp}")
#extract player avatar
if not os.path.exists('./players'):
    os.makedirs('./players')
    print("Created a folder for player avatars at ./players")
else:
    print("Folder for player avatars already exists")
if not os.path.exists(f'./players/{username}.png'):
    user = f"https://osu.ppy.sh/api/get_user?k={userAPI}&u={username}"
    user_data = requests.get(user)
    if user_data.status_code == 200:
        a_data = user_data.json()
        userID = a_data[0]['user_id']
        print(f"Collected avatar of {username}.")
    else: 
        print(f"There is something wrong, probably peppy got dunked.")

        #fetching the avatar and download it

    avatar = f"https://a.ppy.sh/{userID}"
    avatar_data = requests.get(avatar)
    if avatar_data.status_code == 200:
        playerAvatar = Image.open(BytesIO(avatar_data.content))
        playerAvatar.save(f'./players/{username}.png')
        print(f"Saved the avatar of {username} successfully.")
        with Image.open(f'./players/{username}.png') as PlayerAvatar:
            a = add_rounded_corners(PlayerAvatar, radius=50).resize(size=(180, 180))
            a.convert("RGBA")
            a.save(f'./players/{username}.png')
            print(f"Saved the corrected avatar player.")
    else:
        print(f"There is something wrong, probably peppy got dunked.")
else:
    print(f'Existed an image at ./players/{username}.png')

url = f"https://osu.ppy.sh/api/get_beatmaps?k={userAPI}&h={beatmap_hash}"

beatmap_data = requests.get(url)
if beatmap_data.status_code == 200:
    bdata = beatmap_data.json()
    map_status = bdata[0]['approved']
else: 
    print(f"There is something wrong, probably peppy got dunked")

#creating the image
background = Image.open("./deps/bone.png")
draw = ImageDraw.Draw(background)

font_path = "./fonts/BEBASNEUE-REGULAR.TTF"

playcombo = f"{play_maxcombo}/{max_combo}X"

texts_fields = [
    {"type": "player", "text": f"{username}", "position": [244, 47.74], "font_size": 138.58},
    {"type": "playcombo", "text": f"{playcombo}", "position": (48.5, 968.8), "font_size": 70},
    {"type": "play_accuracy", "text": f"{play_accuracy:.2f}%","position": [900, 951.8], "font_size": 90},
    {"type": "circle_size", "text": f"CS: {circle_size:.1f}", "position": [1774.41, 642], "font_size": 61.34},
    {"type": "drain_HP", "text": f"HP: {drain_HP:.1f}", "position": [1774.41, 748.3], "font_size": 61.34},
    {"type": "beatmap_BPM", "text": f"{int(beatmap_BPM)}BPM", "position": [1765.51, 15], "font_size": 47},
    {"type": "mapper", "text": f"{mapper}", "position": [1575.1, 95.1], "font_size": 47},
    {"type": "star_rating", "text": f"{star_rating:.2f}*", "position": [1774.41, 433.46], "font_size": 61.34},
    {"type": "c300", "text": f"{str(c300)}x", "position": [26.39, 388.27], "font_size": 69.57},
    {"type": "c100", "text": f"{str(c100)}x", "position": [70.11, 523.1], "font_size": 69.57},
    {"type": "c50", "text": f"{str(c50)}x", "position": [70.11, 655.51], "font_size": 69.57},
    {"type": "c0", "text": f"{str(c0)}x", "position": [70.11, 790], "font_size": 69.57},
]

existing_attr = set()
unique_texts = []
for item in texts_fields:
    if item['type'] not in existing_attr:
        unique_texts.append(item)
        existing_attr.add(item['type'])

texts_fields = unique_texts

#handling SS plays
if play_accuracy == 100.00:
    for item in texts_fields:
        if item['type'] == "play_accuracy":
            item['position'] = [875, 951.8]

if approach_rate >= 10:
    approach_rate = 10
    texts_fields.append({"type": "approach_rate", "text": f"AR: {int(approach_rate)}","position": [1774.41, 329.3], "font_size": 61.34})
else: 
    texts_fields.append({"type": "approach_rate", "text": f"AR: {approach_rate:.1f}","position": [1774.41, 329.3], "font_size": 61.34})
if overall_diff >= 10:
    overall_diff = 10
    texts_fields.append({"type": "overall_diff", "text": f"OD: {overall_diff}","position": [1774.41, 537.45], "font_size": 61.34})
else:
    texts_fields.append({"type": "overall_diff", "text": f"OD: {overall_diff:.1f}","position": [1774.41, 537.45], "font_size": 61.34})

#handling pp
formattedPp = int(playPp)
if formattedPp < 1000:
    texts_fields.append({"type": "pp", "text": f"{formattedPp}pp", "position": [400, 850], "font_size": 201})
elif formattedPp > 1000:
    texts_fields.append({"type": "pp", "text": f"{formattedPp}pp", "position": [360, 860], "font_size": 195})

#handling grade
grade_pos = [350, 230]

if grade == "XH":
    XH_grade = Image.open('./statics/ranking-XH.png')
    background.paste(XH_grade, grade_pos, XH_grade)
elif grade == "X":
    SS_grade = Image.open('./statics/ranking-X.png')
    background.paste(SS_grade, grade_pos, SS_grade)
elif grade == "SH":
    SH_grade = Image.open('./statics/ranking-SH.png')
    background.paste(SH_grade, grade_pos, SH_grade)
elif grade == "S":
    S_grade = Image.open('./statics/ranking-S.png')
    background.paste(S_grade, grade_pos, S_grade)
elif grade == "A":
    A_grade = Image.open('./statics/ranking-A.png')
    background.paste(A_grade, grade_pos, A_grade)  
elif grade == "B":
    B_grade = Image.open('./statics/ranking-B.png')
    background.paste(B_grade, grade_pos, B_grade)
elif (grade == "C"):
    C_grade = Image.open('./statics/ranking-C.png')
    background.paste(C_grade, grade_pos, C_grade)
elif grade == "D":
    D_grade = Image.open('./statics/ranking-D.png')
    background.paste(D_grade, grade_pos, D_grade)

#handling text length
    #handling combo
combo_based_position = 48.5
combo_increment = 7

combo_position = combo_based_position + (10 - len(playcombo))*combo_increment
for item in texts_fields:
    if item['type'] == "playcombo":
        item['position'] = [combo_position, 968.8]

#handling mapper
mapper_base_position = 1575.1
position_increment = 8.5

adjusted_position = mapper_base_position + (14 - len(mapper)) * position_increment

for item in texts_fields:
    if item['type'] == "mapper":
        item['position'] = [adjusted_position, 95.1]

#handling hit counter:
count_based_pos = 70.11
count_increment = 9.86
c300_pos = count_based_pos + (1 - len(str(c300)) * count_increment)
c100_pos = count_based_pos + (1 - len(str(c100)) * count_increment)
c50_pos = count_based_pos + (1 - len(str(c50)) * count_increment)
c0_pos = count_based_pos + (1 - len(str(c0)) * count_increment)

for item in texts_fields:
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
    texts_fields.append({"type": "map status", "text": "Ranked", "position": [1507, 15], "font_size": 47})
    ranked = Image.open('./statics/ranked blue.png')
    background.paste(ranked, status_icon, ranked)

elif map_status == "2":
    texts_fields.append({"type": "map status", "text": "Approved", "position": [1500.75, 18], "font_size": 40})
    approved = Image.open('./statics/approved.png')
    background.paste(approved, status_icon, approved)
    texts_fields.append({"type": "if ranked", "text": "*if ranked", "position": [505 ,805], "font_size": 47})

elif map_status == "3":
    texts_fields.append({"type": "map status", "text": "Qualified", "position": [1275.51, 15], "font_size": 38})
    qualified = Image.open('./statics/approved.png')
    background.paste(qualified, status_icon, qualified)
    texts_fields.append({"type": "if ranked", "text": "*if ranked", "position": [505 ,805], "font_size": 47})

elif map_status == "4":
    texts_fields.append({"type": "map status", "text": "Loved", "position": [1520, 13], "font_size": 47})
    loved = Image.open('./statics/loved.png')
    background.paste(loved, [1675, 17], loved)
    texts_fields.append({"type": "if ranked", "text": "*if ranked", "position": [505 ,805], "font_size": 47})

#get the player avatar on screen
playerAvatar = Image.open(f'./players/{username}.png')

print(f"Loaded the player avatar")
background.paste(playerAvatar, [35, 15], playerAvatar)

#get the mods on the screen
mod_pos = [(850, 730), (900, 730), (950, 730), (1000, 730)]

mods_keymap = {
    "NF": "NoFail", "DT": "DoubleTime", "EZ": "Easy", "FL": "Flashlight",
    "HR": "HardRock", "HD": "Hidden", "HT": "HalfTime", "NC": "Nightcore"
}

mods_image = {
    "NoFail": Image.open('./statics/nf.png'),
    "DoubleTime": Image.open('./statics/dt.png'),
    "Easy": Image.open('./statics/ez.png'),
    "Flashlight": Image.open('./statics/fl.png'),
    "HardRock": Image.open('./statics/hr.png'),
    "Hidden": Image.open('./statics/hd.png'),
    "HalfTime": Image.open('./statics/ht.png'),
    "Nightcore": Image.open('./statics/nc.png')
}


mod_pairs = [mods_string[i:i+2] for i in range(0, len(mods_string), 2)]

for i, mod_pair in enumerate(mod_pairs):
    if i < len(mod_pos):
        mod_key = mods_keymap.get(mod_pair)
        
        if mod_key and mod_key in mods_image:
            mod_img = mods_image[mod_key]
            x, y = mod_pos[i]
            background.paste(mod_img, (x, y), mod_img)

#getting the time on the screen
submitted_date = submitted_time.split("T")[0]
texts_fields.append({"type": "Date submmited", "text": f"{submitted_date}", "position": [1072, 27.7], "font_size": 72.7})

#getting all da texts on screen
for item in texts_fields:
    font = ImageFont.truetype(font_path, item["font_size"])
    draw.text(item["position"], item["text"], font=font, fill="white")
    print(", ".join('{}: {}'.format(key, val) for key, val in item.items()))

#fuck the background, why there is no function to define the layer for each item.
background.save(f"./tests/{username} on {titleUnicode} [{diff_name}].png")
#stop_application("tosu.exe")
import requests
import psutil
import os
from typing import Final
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from roundcorner import add_rounded_corners as rc
import json
import time
import sys
import re
import numpy as np
import shutil
import logging as l

logger = l.getLogger()

handler = l.StreamHandler()

log_level_str = os.environ.get('LOG_LEVEL', 'INFO').upper()
log_level = getattr(l, log_level_str, l.INFO)

handler.setLevel(log_level)

formatter = l.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter.default_time_format = '%H:%M:%S'
formatter.default_msec_format = '%s.%03d'
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.setLevel(l.DEBUG)

# Track the status of each required program
tosu_running = False
osu_running = False

# Iterate through all running processes
for proc in psutil.process_iter(['name']):
    try:
        current_process_name = proc.info['name'].lower()
        
        if "tosu.exe" in current_process_name:
            tosu_running = True
        
        if "osu!.exe" in current_process_name:
            osu_running = True
            
        if tosu_running and osu_running:
            break

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

# Check if both required programs are running
if not (tosu_running and osu_running):
    missing_programs = []
    if not tosu_running:
        missing_programs.append("tosu.exe")
    if not osu_running:
        missing_programs.append("osu!.exe")
    
    l.warning(f"The following required programs are not detected: {', '.join(missing_programs)}! Quitting...")
    time.sleep(2)
    sys.exit()
else:
    l.info("Both tosu.exe and osu!.exe are detected. Continuing...")
  
#extract data from beatmap using tosu
load_dotenv()
userAPI: Final[str] = os.getenv("osu_API")

mapData = requests.get(url="http://localhost:24050/json")

if not mapData.status_code == 200:
    l.error(f"Please check if either osu! is running or tosu is running correctly.")
    l.info("Quitting...")
    time.sleep(2)
    sys.exit()
else:
    data = json.loads(mapData.content)
    #background related data:
    osu_path = data["settings"]["folders"]["songs"]
    background_path = data["menu"]["bm"]["path"]["full"]
    background_true_path = f"{osu_path}\\{background_path}"
    #map stats:
    circle_size = data["menu"]["bm"]["stats"]["CS"]
    overall_diff = data["menu"]["bm"]["stats"]["OD"]
    approach_rate = data["menu"]["bm"]["stats"]['AR']
    drain_HP = data["menu"]["bm"]["stats"]["HP"]
    beatmap_BPM = data["menu"]["bm"]["stats"]["BPM"]["common"]
    star_rating = data["menu"]["bm"]["stats"]["fullSR"]
    mapper = data["menu"]["bm"]["metadata"]["mapper"]
    map_status = data["menu"]["bm"]["rankedStatus"]
    map_name = data["menu"]["bm"]["metadata"]["title"]
    titleUnicode = data["menu"]["bm"]["metadata"]["title"]
    diff_name = data["menu"]["bm"]["metadata"]["difficulty"]
    #result from the replay file
    username = data["resultsScreen"]["name"]
    play_maxcombo = data["resultsScreen"]["maxCombo"]
    play_accuracy = data["resultsScreen"]["accuracy"]
    c100 = data["resultsScreen"]["100"]
    c50 = data["resultsScreen"]["50"]
    c0 = data["resultsScreen"]["0"]
    mods_string = data["resultsScreen"]["mods"]["str"]
    mods_num = data["resultsScreen"]["mods"]["num"]
    grade = data["resultsScreen"]["grade"]
    submitted_time = data["resultsScreen"]["createdAt"]


invalid_chars_pattern = re.compile(r'[<>:"/\\|?*\x00-\x1F]')

sanitized_title = invalid_chars_pattern.sub('_', titleUnicode)
sanitized_diffName = invalid_chars_pattern.sub('_', diff_name)

if data["resultsScreen"]["name"] == "":
    l.critical(f"No replay is selected. Quitting...")
    time.sleep(2)
    sys.exit()
else:
    l.info(f"Replay of {username} on {map_name} loaded! Getting pp value...")

ppData = requests.get(url=f"http://localhost:24050/api/calculate/pp?mode=0&mods={mods_num}&acc={play_accuracy}")

if not ppData.status_code == 200:
    l.error(f"Please check if either osu! is running or tosu is running correctly.")
else:
    pp_Data = json.loads(ppData.content)
    playPp = pp_Data["pp"]

#extract player avatar
if not os.path.exists('./players'):
    os.makedirs('./players')
    l.info("Created a folder for player avatars at ./players")
else:
    l.info("Folder for player avatars already exists")
if not os.path.exists(f'./players/{username}.png'):
    user = f"https://osu.ppy.sh/api/get_user?k={userAPI}&u={username}"
    user_data = requests.get(user)
    if user_data.status_code == 200:
        a_data = user_data.json()
        userID = a_data[0]['user_id']
        l.info(f"Collected avatar of {username}.")
    else: 
       l.warning(f"""There is something wrong, probably peppy got dunked.
                       Avatar will need to add manually.""")

        #fetching the avatar and download it

    avatar = f"https://a.ppy.sh/{userID}"
    avatar_data = requests.get(avatar)
    if avatar_data.status_code == 200:
        playerAvatar = Image.open(BytesIO(avatar_data.content))
        playerAvatar.save(f'./players/{username}.png')
        with Image.open(f'./players/{username}.png') as PlayerAvatar:
            a = rc(PlayerAvatar, radius=50).resize(size=(180, 180))
            a.convert("RGBA")
            a.save(f'./players/{username}.png')
            l.info(f"Saved the avatar of {username} successfully.")
    else:
       l.warning(f"""There is something wrong, probably peppy got dunked.
                       Avatar will need to add manually.""")
else:
    l.info(f'Existed an image at ./players/{username}.png')


#creating the image
background = Image.open("./statics/core.png")
l.info("Loaded core.png")
draw = ImageDraw.Draw(background)

default_font_path = "./fonts/FabrikatMono_Regular.otf"
l.info("Loaded font")

texts_fields = [
    {"type": "player", "text": f"{username}", "position": [244, 47.74], "font_size": 138.58, "colour": "#FFFFFF"},
    {"type": "playcombo", "text": f"{play_maxcombo}", "position": [48.5, 968.8], "font_size": 40, "colour": "#FFFFFF"},
    {"type": "play_accuracy", "text": f"{play_accuracy:.2f}%","position": [900, 951.8], "font_size": 40, "colour": "#FFFFFF"},
    {"type": "beatmap_BPM", "text": f"{int(beatmap_BPM)}BPM", "position": [1765.51, 15], "font_size": 47, "colour": "#FFFFFF"},
    {"type": "mapper", "text": f"{mapper}", "position": [1575.1, 95.1], "font_size": 47, "colour": "#FFFFFF"},
    {"type": "star_rating", "text": f"{star_rating:.2f}*", "position": [1774.41, 433.46], "font_size": 61.34, "colour": "#FFFFFF"}, 
    #x will be re-calculte later in the code due to increament with text length 
    {"type": "c100", "text": f"{str(c100)}", "position": [0, 0], "font_size": 40, "colour": "#f131e4"},
    {"type": "c50", "text": f"{str(c50)}", "position": [0, 655.51], "font_size": 40, "colour": "#FFFFFF"},
    {"type": "c0", "text": f"{str(c0)}", "position": [0, 790], "font_size": 40, "colour": "#FFFFFF"},
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
    texts_fields.append({"type": "approach_rate", "text": f"{int(approach_rate)}","position": [1774.41, 329.3], "font_size": 40})
else: 
    texts_fields.append({"type": "approach_rate", "text": f"{approach_rate:.1f}","position": [1774.41, 329.3], "font_size": 40})
if overall_diff >= 10:
    overall_diff = 10
    texts_fields.append({"type": "overall_diff", "text": f"{overall_diff}","position": [1774.41, 537.45], "font_size": 40})
else:
    texts_fields.append({"type": "overall_diff", "text": f"{overall_diff:.1f}","position": [1774.41, 537.45], "font_size": 40})

#handling pp
formattedPp = int(playPp)
if formattedPp < 1000:
    texts_fields.append({"type": "pp", "text": f"{formattedPp}", "position": [624.02, 540], "font_size": 40})
elif formattedPp > 1000:
    texts_fields.append({"type": "pp", "text": f"{formattedPp}", "position": [612, 540], "font_size": 40})

#handling grade
grade_pos = [750, 230]

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
#handling player name
if len(str(username)) > 13:
    for item in texts_fields:
        if item['type'] == "player":
            item['font_size'] = 115

#handling combo
combo_based_position = 555
combo_increment = 9.86

combo_position = combo_based_position + (10 - len(str(play_maxcombo)))*combo_increment
for item in texts_fields:
    if item['type'] == "playcombo":
        item['position'] = [combo_position, 415]

#handling mapper
mapper_base_position = 1575.1
position_increment = 8.5

adjusted_position = mapper_base_position + (14 - len(mapper)) * position_increment

for item in texts_fields:
    if item['type'] == "mapper":
        item['position'] = [adjusted_position, 95.1]

#handling hit counter:
count_based_pos = 358
count_increment = 9.86
c100_pos = count_based_pos + (1 - len(str(c100)) * count_increment)
c50_pos = count_based_pos + (1 - len(str(c50)) * count_increment)
c0_pos = count_based_pos + (1 - len(str(c0)) * count_increment)

for item in texts_fields:
    if item['type'] == "c100":
        item['position'] = [c100_pos, 415]
    elif item['type'] == "c50":
        item['position'] = [c50_pos, 540]
    elif item['type'] == "c0":
        item['position'] = [c0_pos, 670]
    

#checking map status
status_icon = [1670, 15]

if map_status == 4:
    texts_fields.append({"type": "map status", "text": "Ranked", "position": [1507, 15], "font_size": 47})
    ranked = Image.open('./statics/ranked blue.png')
    background.paste(ranked, status_icon, ranked)

elif map_status == 5:
    texts_fields.append({"type": "map status", "text": "Approved", "position": [1500.75, 18], "font_size": 40})
    approved = Image.open('./statics/approved.png')
    background.paste(approved, status_icon, approved)
    texts_fields.append({"type": "if ranked", "text": "*if ranked", "position": [515 ,810], "font_size": 40})

elif map_status == 6:
    texts_fields.append({"type": "map status", "text": "Qualified", "position": [1275.51, 15], "font_size": 38})
    qualified = Image.open('./statics/approved.png')
    background.paste(qualified, status_icon, qualified)
    texts_fields.append({"type": "if ranked", "text": "*if ranked", "position": [515 ,810], "font_size": 40})

elif map_status == 7:
    texts_fields.append({"type": "map status", "text": "Loved", "position": [1520, 13], "font_size": 47})
    loved = Image.open('./statics/loved.png')
    background.paste(loved, [1675, 17], loved)
    texts_fields.append({"type": "if ranked", "text": "*if ranked", "position": [515 ,810], "font_size": 40})

#get the player avatar on screen
playerAvatar = Image.open(f'./players/{username}.png')

l.info(f"Loaded the player avatar")
background.paste(playerAvatar, [35, 15], playerAvatar)

#get the mods on the screen
mod_pos = [(850, 950), (900, 950), (950, 950), (1000, 950)]

mods_keymap = {
    "NF": "NoFail", "DT": "DoubleTime", "EZ": "Easy", "FL": "Flashlight",
    "HR": "HardRock", "HD": "Hidden", "HT": "HalfTime", "NC": "Nightcore"
}

mods_image = {
    "NoFail": Image.open('./statics/NF.png'),
    "DoubleTime": Image.open('./statics/DT.png'),
    "Easy": Image.open('./statics/EZ.png'),
    "Flashlight": Image.open('./statics/FL.png'),
    "HardRock": Image.open('./statics/HR.png'),
    "Hidden": Image.open('./statics/HD.png'),
    "HalfTime": Image.open('./statics/HT.png'),
    "Nightcore": Image.open('./statics/NC.png'),
    "AccuracyChallenge": Image.open('./statics/AC.png'),
    "StrictTracking": Image.open('./statics/ST.png'),
    "Blind": Image.open('./statics/BL.png'),
    "SuddenDeath": Image.open('./statics/SD.png'),
    "Perfect": Image.open('./statics/PF.png'),  
    "Daycore": Image.open('./statics/DC.png'),
}


mod_pairs = [mods_string[i:i+2] for i in range(0, len(mods_string), 2)]

for i, mod_pair in enumerate(mod_pairs):
    if i < len(mod_pos):
        mod_key = mods_keymap.get(mod_pair)
        
        if mod_key and mod_key in mods_image:
            mod_img = mods_image[mod_key]
            x, y = mod_pos[i]
            background.paste(mod_img, (x, y), mod_img)

#handling map name and map diff

mapName_length = len(str(map_name))
if mapName_length > 40:
    font_size_name = 35
elif mapName_length > 20:
    font_size_name = 45
else: 
    font_size_name = 69 

mapDiff_length = len(str(diff_name))
if mapDiff_length < 20:
    font_size_diff = 50
elif mapDiff_length < 30:
    font_size_diff = 45
elif mapDiff_length < 50:
    font_size_diff = 40

texts_fields.append({"type": "map_Diff", "text": f"{diff_name}", "position": [1600, 972.7], "font_size": font_size_diff, "anchor": "mm"})
texts_fields.append({"type": "map_Name", "text": f"{map_name}", "position": [1600, 900], "font_size": font_size_name, "anchor": "mm"})
#getting all da texts on screen
for item in texts_fields:
    font = ImageFont.truetype(item.get("font", default_font_path), item["font_size"])
    anchor_value = item.get("anchor", "la") 
    colour = item.get("colour", "white")
    draw.text(item["position"], item["text"], font=font, fill=colour, anchor=anchor_value, stroke_fill=(0,0,0), stroke_width=2.5)
    l.info(", ".join('{}: {}'.format(key, val) for key, val in item.items()))

if not os.path.exists("./results"):
    os.makedirs(f"./results")

if not os.path.exists("./cache"):
    os.makedirs(f"./cache")

#cropping the background:
position = [(0,0), (0, 1080), (1200, 1080), (1450, 0)]
# Open the image
img = Image.open(background_true_path).convert("RGBA") # Ensure image has an alpha channel
width, height = img.size
l.debug(f"Background picture has {width}px x {height}px dimension")
# Create a mask image with the same dimensions as the original image
mask = Image.new('L', (width, height), 0) # 'L' for 8-bit pixels, 0 for black

# Draw the polygon on the mask in white (255)
draw = ImageDraw.Draw(mask)
draw.polygon(position, fill=255)

# Apply the mask to the original image
# This will make areas outside the polygon transparent

inverted_mask = Image.eval(mask, lambda x: 255 - x) # <--- NEW LINE

dim_factor = 0.6  # Adjust this value between 0.0 (fully black) and 1.0 (original brightness)
dimmed_img_data = np.array(img) * dim_factor
dimmed_img = Image.fromarray(dimmed_img_data.astype(np.uint8))

# Create a new blank RGBA image (this will be our output image)
# This starts completely transparent
output_img = Image.new("RGBA", img.size)

# Paste the dimmed image using the inverted mask.
# This will put the dimmed 'outside' area onto the transparent background.
output_img.paste(dimmed_img, (0, 0), inverted_mask)


# Save the result
output_img.save(f"./cache/{sanitized_title} croppedbackground.png")

background.save(f"./cache/{username} on {sanitized_title} [{sanitized_diffName}].png")


final_img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
background_layer = Image.open(f"./cache/{sanitized_title} croppedbackground.png")
data_layer = Image.open(f"./cache/{username} on {sanitized_title} [{sanitized_diffName}].png")

final_img.paste(background_layer, (0, 0), background_layer)
final_img.paste(data_layer, (0, 0), data_layer)
final_img.save(f"./results/{username} on {sanitized_title} [{sanitized_diffName}].png")
time.sleep(1)
cache_folder_path = "./cache"
if os.path.exists(cache_folder_path) and os.path.isdir(cache_folder_path):
    l.info(f"Clearing contents of '{cache_folder_path}'...")
    for item in os.listdir(cache_folder_path):
        item_path = os.path.join(cache_folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path) # Remove files and symbolic links
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path) # Remove subdirectories and their contents
            l.info(f"Removed: {item_path}")
        except Exception as e:
            l.warning(f"Error removing {item_path}: {e}")
    l.info("Cache folder contents cleared successfully.")
elif not os.path.exists(cache_folder_path):
    l.warning(f"Cache folder '{cache_folder_path}' does not exist, no contents to clear.")
else:
    l.warning(f"'{cache_folder_path}' exists but is not a directory.")
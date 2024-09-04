import requests
import os
from typing import Final
from dotenv import load_dotenv
import osrparse
from osrparse import Replay, parse_replay_data

#extract data from local replay

r = Replay.from_path("./Kuina - Yooh - RPG [Collab Expert] (2024-03-03) Osu.osr")

beatmap_hash = r.beatmap_hash
player = r.username
play_maxcombo = str(r.max_combo)
count300 = r.count_300
count100 = r.count_100
count50 = r.count_50
count0 = r.count_miss
play_accuracy = (300*(count300) + 100*(count100) + 50*(count50)) / (300*(count300 + count100 + count50 + count0))

#extract data from beatmap online
load_dotenv()
userAPI: Final[str] = os.getenv("osu_API")
url = f"https://osu.ppy.sh/api/get_beatmaps?k={userAPI}&h={beatmap_hash}"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    beatmap_name = data[0]['title_unicode']
    max_combo = str(data[0]['max_combo'])
    diff_name = data[0]['version']
    circle_size = data[0]['diff_size']
    overall_diff = data[0]['diff_overall']
    approach_rate = data[0]['diff_approach']
    drain_HP = data[0]['diff_drain']
    beatmap_BPM = data[0]['bpm']
    mapper = data[0]['creator']
    star_rating = float(data[0]['difficultyrating'])

if (r.mods == 1 << 7):
    print("relax")
import os
import math
import random
import sqlite3
import requests
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from multiprocessing import Pool

class DataPoint:
    def __init__(self, app_id, title, screenshot_url, tags):
        self.app_id = app_id
        self.title = title
        self.screenshot_url = screenshot_url
        self.tags = tags

tag_dict = {
        'Platformer': 1625,
        'Action': 19,
        'Casual': 597,
        'Adventure': 21,
        'TwoD': 3871,
        'ThreeD': 4191,
        'Simulation': 599,
        'Strategy': 9,
        'RPG': 122,
        'Puzzle': 1664,
        'Horror': 1667,
        'Sports': 701
}

# <<< Getters

# Return Type: list of dictionaries containing 2 string keys: 'appid' and 'name'
#   'appid': int
#   'name': str
def get_all_steam_apps() -> list[dict]:
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(url)
    data = response.json()
    return data['applist']['apps']

# Returns a list of 'count' dictionary items that describe games
#   containing 'tag' in their tag list
def get_games_by_tag(tag: str, count: int) -> list[dict]:
    num_fetch = math.ceil(count / 100)
    tag_id = tag_dict[tag]

    result = []

    for fetch in range(num_fetch):
        start = (fetch * 100) + 1
        url = f'https://store.steampowered.com/search/results/?query=&start={start}&count={count}&dynamic_data=&force_infinite=1&tags={tag_id}&supportedlang=english&ndl=1&snr=1_7_7_240_7&infinite=1'

        response = requests.get(url).json()

        soup = BeautifulSoup(response['results_html'], 'html.parser')
        all_games_html = soup.find_all('a', class_='search_result_row ds_collapse_flag')

        for item in all_games_html:
            name = item.find('span', class_='title').text
            app_id = item.get('data-ds-appid')
            tag_ids = item.get('data-ds-tagids')
            tag_ids = f'{tag_ids[:-1]},{tag_dict[tag]}]' # This is to ensure that the the tag list contains the tag passed in to this method
                                                         # It will cause duplicate tag ids in some cases
            result.append({'name': name, 'app_id': app_id, 'tag_ids': tag_ids})
            if len(result) == count:
                break


    return result

# Returns: A 'count'-sized list of dictionary items describing a game
def get_random_steam_games(count:int = 1) -> list[dict]:
    all_apps = get_all_steam_apps()
    
    random_games = []
    while len(random_games) < count:
        random_game = random.choice(all_apps)
        app_id = random_game['appid']

        # Filter out invalid app ids and non-game apps like sountracks
        if is_valid_app_id(app_id) and is_game(app_id):
            random_games.append(random_game)

    return random_games

# Returns a string url of the first screenshot on an app's store page
def get_ss_url(app_id: int) -> str:
    response = get_store_response(app_id)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all screenshot thumbnails
    screenshots = soup.find_all("a", {"class": "highlight_screenshot_link"})
    if len(screenshots) == 0:
        raise Exception("No screenshots found on the store page.")

    # Get the href from the first screenshot
    first_screenshot_url = screenshots[0].get("href")
    
    return first_screenshot_url.split('?')[0]  # Remove any trailing query parameters

# Fetches a response by adding appropriate headers and cookies
def get_store_response(app_id: int) -> requests.Response:
    url = f"https://store.steampowered.com/app/{app_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    # Simulate having passed the age check with a cookie
    cookies = {
        'birthtime': '568022401',   # Arbitrary date: Jan 1, 1988
        'lastagecheckage': '1-January-1988',
        'mature_content': '1',
        'wants_mature_content': '1'
    }

    response = requests.get(url, headers=headers, cookies=cookies)
    return response

# >>> Getters

# <<< Validity Checks

def has_tag(tag: str, app_id: int) -> bool:
    response = get_store_response(app_id)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page, status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    genres_container = soup.find("div", {"id": "genresAndManufacturer", "class": "details_block"})
    genres_data_panel = genres_container.find('span')
    all_tags_links = genres_data_panel.find_all('a')
    all_tags = [link.text.lower() for link in all_tags_links]
    return tag.lower() in all_tags

def has_ss(app_id: int) -> bool:
    response = get_store_response(app_id)
    if response.status_code != 200:
        return False

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all screenshot thumbnails
    screenshots = soup.find_all("a", {"class": "highlight_screenshot_link"})
    if len(screenshots) == 0:
        print(f"No screenshots found on the store page for AppId: {appid}")
        return False

    return True

def has_store_page(app_id: int) -> bool:
    response = get_store_response(app_id)

    if response.status_code != 200:
        return False

    # Check if redirected to an invalid page (like the homepage or error page)
    final_url = response.url.lower()
    if "app" not in final_url or "agecheck" in final_url:
        return False

    # Some nonexistent apps still return 200 with a "not found" message
    if "app doesn't exist" in response.text.lower() or "application not found" in response.text.lower():
        return False

    return True

def is_valid_app_id(app_id: int) -> bool:
    url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
    response = requests.get(url).json()
    return response[f'{app_id}']['success']

def is_game(app_id: int) -> bool:
    url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
    response = requests.get(url).json()
    return response[f'{app_id}']['data']['type'] == 'game'

# >>> Validity Checks

def download_ss(url: str, path: str):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

def download_ss_for_tag(tag: str, download_dir: Path = Path('./data'), count: int = 100):
    tag_dir = download_dir / tag

    if not tag_dir.exists():
        os.mkdir(tag_dir)

    print(f'Downloading {tag} game screenshots...')
    games = get_games_by_tag(tag, count)
    for i, game in enumerate(games, start=1):
        app_id = game['app_id']
        try:
            ss_url = get_ss_url(app_id)
        except:
            print(f'Could not find ss url for {game["name"]} | app_id: {app_id}')
            continue

        download_ss(ss_url, f'{tag_dir}/{app_id}.jpeg')
        #write_tag_info_to_db(game)
        print(f'{tag}: {i}/{len(games)}')

    print(f'\n✅ Download Complete: {tag}')

def write_tag_info_to_db(game) -> None:
    connection = sqlite3.connect('data/tag_info.db')
    cursor = connection.cursor()

    tag_columns_description = ',\n'.join([f'{tag} BOOLEAN' for tag in tag_dict.keys()])

    tuple_entry = (game['app_id'], )

    # game['tag_ids'] returns a string in the format:
    #   [123,456,78]. Hence, we need to remove the brackets
    #   before calling .split
    tag_list = game['tag_ids'][1:-1].split(',')

    for tag in tag_dict.keys():
        game_has_tag = str(tag_dict[tag]) in tag_list
        tuple_entry += (int(game_has_tag), )

    cursor.execute(
        f'''
        CREATE TABLE IF NOT EXISTS games (
            app_id INTEGER PRIMARY KEY,
            {tag_columns_description}
        )
        '''
    )

    placeholders = ','.join(['?'] * len(tuple_entry))

    cursor.execute(
        f'''
        INSERT INTO games VALUES({placeholders})
        ''', 
        tuple_entry
    )

    connection.commit()
    connection.close()

# <<< Entry

# Run and print
if __name__ == "__main__":
    '''
    data_dir = Path('./data')

    if not data_dir.exists():
        os.mkdir(data_dir)

    with Pool(len(tag_dict)) as p:
        p.map(download_ss_for_tag, tag_dict.keys())
    '''

    games = get_games_by_tag('Action', 5)
    for game in games:
        write_tag_info_to_db(game)
# >>> Entry

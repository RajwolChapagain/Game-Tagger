import requests
import random
from bs4 import BeautifulSoup

class DataPoint:
    def __init__(self, app_id, title, screenshot_url, tags):
        self.app_id = app_id
        self.title = title
        self.screenshot_url = screenshot_url
        self.tags = tags

ss_url_dict = {}

# Fetch all Steam apps
def get_all_steam_games():
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(url)
    data = response.json()
    return data['applist']['apps']

# Returns a list of 'count' dictionary items containing AppId and Name
#   of games with 'tag' in their tag list
def get_games_by_tag(tag: str, count: int) -> list[dict]:
    all_games = get_all_steam_games()
    all_games_with_tag = []

    while len(all_games_with_tag) < count:
        random_game = random.choice(all_games)
        if is_eligible(random_game) and has_tag(tag, random_game):
            all_games_with_tag.append(random_game)

    return all_games_with_tag

# Returns: A 'count'-sized list of dictionary items each containing two keys:
#           'name' and 'appid'
def get_random_steam_games(count=5):
    all_games = get_all_steam_games()
    
    random_games = []
    while len(random_games) < count:
        random_game = random.choice(all_games)

        # Filter out ineligible entries
        if is_eligible(random_game):
            random_games.append(random_game)

    return random_games

def is_eligible(game):
    if has_name(game) and ss_exists(game['appid']):
        return True

    return False

def has_name(game):
    if len(game['name'].strip()) == 0:
        return False

    return True

def has_tag(tag: str, game: dict) -> bool:
    response = get_store_response(game['appid'])

    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page, status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    genres_container = soup.find("div", {"id": "genresAndManufacturer", "class": "details_block"})
    genres_data_panel = genres_container.find('span')
    all_tags_links = genres_data_panel.find_all('a')
    all_tags = [link.text.lower() for link in all_tags_links]
    return tag.lower() in all_tags

def ss_exists(app_id):
    response = get_store_response(app_id)
    if response.status_code != 200:
        return False

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all screenshot thumbnails
    screenshots = soup.find_all("a", {"class": "highlight_screenshot_link"})
    if len(screenshots) == 0:
        print(f"No screenshots found on the store page for AppId: {appid}")
        return False

    # Get the href from the first screenshot
    first_screenshot_url = screenshots[0].get("href")
    
    if len(first_screenshot_url) == 0:
        return False

    raw_url = first_screenshot_url.split('?')[0]  # Remove any trailing query parameters
    ss_url_dict[appid] = raw_url
    return True

def has_store_page(app_id: str) -> bool:
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


def is_valid_app_id(app_id: str) -> bool:
    url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
    response = requests.get(url).json()
    return response[f'{app_id}']['success']

def is_game(app_id: str) -> bool:
    url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
    response = requests.get(url).json()
    return response[f'{app_id}']['data']['type'] == 'game'

def get_ss(app_id: str):
    response = get_store_response(app_id)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page, status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all screenshot thumbnails
    screenshots = soup.find_all("a", {"class": "highlight_screenshot_link"})
    if not screenshots:
        raise Exception("No screenshots found on the store page.")

    # Get the href from the first screenshot
    first_screenshot_url = screenshots[0].get("href")
    
    if first_screenshot_url:
        return first_screenshot_url.split('?')[0]  # Remove any trailing query parameters

    raise Exception("Could not extract screenshot URL.")

def get_store_response(app_id: str) -> requests.Response:
    url = f"https://store.steampowered.com/app/{app_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    # Simulate having passed the age check with a cookie
    cookies = {
        'birthtime': '568022401',     # Arbitrary date: Jan 1, 1988
        'lastagecheckage': '1-January-1988',
        'mature_content': '1',
        'wants_mature_content': '1'
    }

    response = requests.get(url, headers=headers, cookies=cookies)
    return response

# Run and print
if __name__ == "__main__":
    print(get_store_response(101))
    '''
    games = get_games_by_tag('free to play', 3)

    for i, game in enumerate(games, 1):
        has_ss = ss_exists(game['appid'])
        print(f'{i}. Title: {game["name"]} | AppID: {game["appid"]}')
        print(f'URL: https://store.steampowered.com/app/{game["appid"]}')
        if has_ss:
            print(f'SS URL: {get_ss(game["appid"])}')

        print()
    '''

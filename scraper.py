import requests
import random
from bs4 import BeautifulSoup

ss_url_dict = {}

# Fetch all Steam apps
def get_all_steam_games():
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(url)
    data = response.json()
    return data['applist']['apps']

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

def ss_exists(appid):
    url = f"https://store.steampowered.com/app/{appid}/"
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
    if response.status_code != 200:
        return False

    # Check if redirected to an invalid page (like the homepage or error page)
    final_url = response.url.lower()
    if "app" not in final_url or "agecheck" in final_url:
        return False

    # Some nonexistent apps still return 200 with a "not found" message
    if "app doesn't exist" in response.text.lower() or "application not found" in response.text.lower():
        return False

    # If we made it this far, that means there is a store page

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

def get_ss(appid):
    if appid in ss_url_dict:
        return ss_url_dict[appid]

    url = f"https://store.steampowered.com/app/{appid}/"
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

# Run and print
if __name__ == "__main__":
    games = get_random_steam_games(50)

    for i, game in enumerate(games, 1):
        has_ss = ss_exists(game['appid'])
        print(f'{i}. Title: {game["name"]} | AppID: {game["appid"]}')
        print(f'URL: https://store.steampowered.com/app/{game["appid"]}')
        if has_ss:
            print(f'SS URL: {get_ss(game["appid"])}')

        print()

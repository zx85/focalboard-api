import requests
from dotenv import load_dotenv
import json
import os
import jmespath

# use the .env file for security y'know
# user_name = Focalboard username
# user_pass = Focalboard password
# repair_cafe_date = next date (needs to be in the title of the board)

load_dotenv()

url = "https://focalboard.zx85.me/api/v2"


def do_login(url, username, password):
    token = ""
    try:
        credentials = {"type": "normal", "username": username, "password": password}
        headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
        }
        session = requests.Session()
        req = session.post(url + "/login", json=credentials, headers=headers)
        if req.status_code == 200:
            token = req.json()["token"]

    except Exception as e:
        print(f"Failed to login because: {str(e)}")
    return token


def get_teams(url, token):
    teams = []
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": "Bearer " + token,
    }
    req = requests.get(url + "/teams", headers=headers)
    if req.status_code == 200:
        teams = req.json()
    return teams


def get_blocks(url, token, board_id):
    blocks = []
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": "Bearer " + token,
    }
    req = requests.get(url + "/boards/" + board_id + "/blocks", headers=headers)
    if req.status_code == 200:
        blocks = req.json()
    else:
        print(f"Oh no... status code {req.status_code}")
    return blocks


def get_boards(url, token, team):
    boards = []
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": "Bearer " + token,
    }
    req = requests.get(url + "/teams/" + team + "/boards", headers=headers)
    if req.status_code == 200:
        boards = req.json()
    return boards


def get_cards(url, token, board_id):
    cards = []
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": "Bearer " + token,
    }
    req = requests.get(url + "/boards/" + board_id + "/cards", headers=headers)
    if req.status_code == 200:
        cards = req.json()
    return cards


def create_card(url, token, board_id):
    response = {}
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": "Bearer " + token,
    }
    card_details = {
        "title": "playing with properties",
        "a9ctq6eyxy9pkcc18dpot439bsw": "ao9w4t3desyyektq1qrcz6nsxzw",
    }
    req = requests.post(
        url + "/boards/" + board_id + "/cards", json=card_details, headers=headers
    )
    if req.status_code == 200:
        response = req.json()
    print(json.dumps(response))


def main():
    username = os.getenv("user_name")
    password = os.getenv("user_pass")
    repair_cafe_date = os.getenv("repair_cafe_date")
    token = do_login(url, username, password)
    first_team_id = get_teams(url, token)[0]["id"]  # just one team right?
    board_id = [
        each_board["id"]
        for each_board in get_boards(url, token, first_team_id)
        if repair_cafe_date in each_board["title"]
    ][0]
    cards = get_cards(url, token, board_id)
    # print(json.dumps(cards))
    # Blocks does something but I don't know what
    # print(json.dumps(get_blocks(url, token, board_id)))
    create_card(url, token, board_id)
    # Haven't worked out how to change the status (eg to RECEIVED)
    # eg it does a PATCH to cb3ehj1e4ijg3pfqf383pri6wnr
    # With properties
    # a9ctq6eyxy9pkcc18dpot439bsw	"ao9w4t3desyyektq1qrcz6nsxzw"


if __name__ == "__main__":
    main()

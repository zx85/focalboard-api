import requests
from dotenv import load_dotenv
import json
import os
import jmespath

# API gubbins here: https://htmlpreview.github.io/?https://github.com/mattermost/focalboard/blob/main/server/swagger/docs/html/index.html

# use the .env file for security y'know
# user_name = Focalboard username
# user_pass = Focalboard password
# repair_cafe_date = next date (needs to be in the title of the board)

load_dotenv()

url = "https://focalboard.zx85.me/api/v2"
# This will likely change from board to board chiz chiz
received_tuple = {"a9ctq6eyxy9pkcc18dpot439bsw": "ao9w4t3desyyektq1qrcz6nsxzw"}


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


def create_card(url, token, board_id, title):
    response = {}
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": "Bearer " + token,
    }
    card_details = {
        "title": title,
    }
    req = requests.post(
        url + "/boards/" + board_id + "/cards", json=card_details, headers=headers
    )
    if req.status_code == 200:
        response = req.json()
    return response["id"]


def move_card_to_received(url, token, card_id, received_tuple):
    response = {}
    headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": "Bearer " + token,
    }

    req = requests.patch(
        url + "/cards/" + card_id,
        json=received_tuple,
        headers=headers,
    )
    if req.status_code == 200:
        # response = req.json()
        response = req.text
        print(response)
    return response


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

    # This bit creates a new card
    title = "Trying to patch"
    new_card_id = create_card(url, token, board_id, title)
    print(f"New card ID is {new_card_id}")

    # Haven't worked out how to change the status (eg to RECEIVED)
    # eg it does a PATCH to cb3ehj1e4ijg3pfqf383pri6wnr
    # With properties like "a9ctq6eyxy9pkcc18dpot439bsw": "ao9w4t3desyyektq1qrcz6nsxzw"
    # (As seen in developer mode on the browser)
    # TODO: get block_id from blocks and then patch that block?
    move_card_to_received(url, token, new_card_id, received_tuple)


if __name__ == "__main__":
    main()

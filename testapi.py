'''FocalBoard API integration code'''
# import json
import os
from pprint import pprint
import requests
from dotenv import load_dotenv
# import jmespath

# API gubbins here: https://htmlpreview.github.io/?https://github.com/mattermost/focalboard/blob/main/server/swagger/docs/html/index.html

# use the .env file for security y'know
# user_name = Focalboard username
# user_pass = Focalboard password
# repair_cafe_date = next date (needs to be in the title of the board)

class FbApiException(Exception):
    '''Exception caused by bad API-ness'''

class FbApiWrapper:
    '''Wrapper class to contain all the API functions and variables'''
    __URL = "https://focalboard.zx85.me/api/v2"
    __headers = {
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
    }

    def __init__(self, username, password):
        self.__username = username
        self.__password = password

    def __enter__(self):
        token = self.__do_login()
        if token:
            self.__headers["Authorization"] = f"Bearer {token}"
        else:
            raise FbApiException
        return self
 
    def __exit__(self, *args):
        pass

    def __do_login(self):
        '''(private) Login'''
        api_token = None
        with requests.Session() as s:
            credentials = {"type": "normal", "username": self.__username, "password": self.__password}
            response = s.post(self.__URL + "/login", headers=self.__headers, json=credentials)
            resp = response.json()
            api_token = resp["token"]
        return api_token


    def get_teams(self):
        '''get the list of teams'''
        teams = []
        with requests.Session() as s:
            response = s.get(self.__URL + "/teams", headers=self.__headers)
            teams = response.json()
        return teams


    def get_blocks(self, board_id):
        '''get the list of blocks'''
        blocks = []
        with requests.Session() as s:
            response = s.get(self.__URL + "/boards/" + board_id + "/blocks", headers=self.__headers)
            blocks = response.json()
        return blocks


    def get_boards(self, team):
        '''get the list of boards'''
        boards = []       
        with requests.Session() as s:
            response = s.get(self.__URL + "/teams/" + team + "/boards", headers=self.__headers)
            boards = response.json()
        return boards


    def get_cards(self, board_id):
        '''get the list of cards'''
        cards = []
        with requests.Session() as s:
            response = s.get(self.__URL + "/boards/" + board_id + "/cards", headers=self.__headers)
            cards = response.json()
        return cards


    def create_card(self, board_id, title):
        '''create a card'''
        response = {}
        card_details = {
            "title": title,
        }
        with requests.Session() as s:
            response = s.post(self.__URL + "/boards/" + board_id + "/cards", json=card_details, headers=self.__headers)
            response = response.json()
        return response["id"]


    def move_card_to_received(self, board_id, card_id):
        '''move a card to received - EXPERIMENTAL'''
        response = {}
        # TODO how the hell do we know what the magic status field is called and what to set it to?
        patch_json = {
            "updatedFields": {
                "properties": {
                    "a9ctq6eyxy9pkcc18dpot439bsw": "ao9w4t3desyyektq1qrcz6nsxzw"
                },
            },
            "deletedFields": []
        }

        # https://focalboard.zx85.me/api/v2/boards/bidz77spmbp875ept8566kykcar/blocks/c5yipweto7bbrfftpa99dpx9pra

        with requests.Session() as s:
            response = s.patch(self.__URL + "/boards/" + board_id + "/blocks/" + card_id, json=patch_json, headers=self.__headers)
            # response = req.text
            # pprint(response.json())
        return response


def main():
    '''main'''
    load_dotenv()
    username = os.getenv("user_name")
    password = os.getenv("user_pass")
    repair_cafe_date = os.getenv("repair_cafe_date")

    with FbApiWrapper(username, password) as api:

        first_team_id = api.get_teams()[0]["id"]  # just one team right?
        board_id = [
            each_board["id"]
            for each_board in api.get_boards(first_team_id)
            if repair_cafe_date in each_board["title"]
        ][0]
        cards = api.get_cards(board_id)
        # print(json.dumps(cards))

        # This bit creates a new card
        title = "Trying to patch"
        new_card_id = api.create_card(board_id, title)
        print(f"New card ID is {new_card_id}")

        api.move_card_to_received(board_id, new_card_id)


if __name__ == "__main__":
    main()

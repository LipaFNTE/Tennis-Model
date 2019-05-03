import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
from requests import get
import utils


def find_all_matches(table):
    matches = list()
    not_found = 0
    for match in table:
        try:
            reference = match.find_all("div", {"class": "score-content"})[0].find('a').get('href')
            matches.append(reference)
        except:
            not_found = not_found + 1

    print(f'Links not found for {not_found} matches. {len(matches)} matches found')
    return matches


def basic_match_information(match):
    X = dict()


def get_wins(player_info):
    wins_atr = bio.find_all('tr')[0].text
    wins_regex = re.search(r'Wins:(\d+)', wins_atr)
    return int(wins_regex.group(1))


def get_tour_round(match_info):
    return match_info.find("td", {"class": "round"}).text.strip()


def get_match_info(match_info):
    surface = match_info.find("span").text
    p_info = match_info.find_all("p")
    tour_name = match_info.find("a").text.strip()
    tour_round = p_info[1].text
    match_date = p_info[2].text
    return tour_name, tour_round, match_date, surface


def get_scores(match_score):
    scores = match_score.find_all("tr")
    winner = scores[0].find_all("td")[0].text.strip()
    winner_result = get_player_result(scores[0])
    loser_result = get_player_result(scores[1])


def get_player_result(scores):
    match_1 = scores[0]
    score_list = match_1.find_all("td")
    scores = [int(i.text.strip()) for i in score_list[1:]]


def get_players_name(player_0_info, player_1_info):
    return player_0_info.find("a").text.strip(), player_1_info.find("a").text.strip()


def create_player_dict(player_dict: dict, player_info, score_table):
    pass


def print_fataframe(df: pd.DataFrame):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)


def get_bio(player_info):
    bio = player_info.find("table", {"class": "bio-table table"})
    bio_info = bio.find_all('tr')
    #ranking = re.search(r'Ranking:(\d+)', bio_info[1].text)
    ranking = bio_info[0].find_all("td")[1].text
    country = bio_info[1].find_all("td")[1].text
    age = re.search(r'Age (\d+)', bio_info[2].find_all("td")[1].text)
    hand = bio_info[4].find_all("td")[1].text

    return int(ranking), country, age.group(1), hand


def build_player(player_html: BeautifulSoup):
    ranking, country, age, hand = get_bio(player_html)
    
    
def get_surface_stats(player_soup: BeautifulSoup):
    pass

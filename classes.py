from typing import Any

from bs4 import BeautifulSoup
import re, time, datetime, json, utils
import pandas as pd
from selenium import webdriver


class Ranking:

    def __init__(self, ranking_link_atp: str, ranking_link_wta: str, ranking_numbers: int):
        self.atp_rankings = self.create_rankings(ranking_link_atp, ranking_numbers)

    def create_rankings(self, ranking_link: str, ranking_numbers: int):
        ranks = dict()

        driver = webdriver.Chrome()
        driver.get(ranking_link)
        last_height = driver.execute_script("return document.body.scrollHeight")

        element = driver.find_element_by_id("rform-date")
        all_options = element.find_elements_by_tag_name("option")

        count = 0
        for option in all_options:
            option.click()
            option_soup = BeautifulSoup(utils.simple_get(driver.page_source), 'html_source')

            ranking_table = option_soup.find('tbody', {'class': 'flags'})
            ranking_places = ranking_table.find_all('tr')

            for pl in ranking_places:
                print(pl.find('td').text)

            count = count + 1
            if count == ranking_numbers:
                break

        return 0


class Match:
    def __init__(self, match_soup: BeautifulSoup):
        self.propagated_stats: dict = self.retrieve_stats(match_soup)
        self.id_link = self.propagated_stats['id_link']
        self.result: [int, int] = self.find_result(match_soup)
        self.gems_count = 0
        self.gems_sum = self.find_gems_sum(match_soup)
        self.player1: Player = self.propagated_stats['player1']
        self.player2: Player = self.propagated_stats['player2']
        self.H2H: H2H = self.propagated_stats['h2h']

    @staticmethod
    def find_result(match_soup):
        result_table = match_soup.find('table', {'class': 'result'})
        result_elements = re.findall(r'[0-9]+', result_table.find('td', {'class': 'gScore'}).text)
        return [int(result_elements[0]), int(result_elements[1])]

    def find_gems_sum(self, match_soup):
        result_table = match_soup.find('table', {'class': 'result'})
        result = result_table.find('td', {'class': 'gScore'})
        gems_in_sets = re.findall(r'[0-9]+-[0-9]+', result.find('span').text)
        pl_1_gems = 0
        pl_2_gems = 0
        for gem in gems_in_sets:
            gems = re.findall(r'[0-9]+', gem)
            pl_1_gems = pl_1_gems + int(gems[0])
            pl_2_gems = pl_2_gems + int(gems[1])

        self.gems_sum = pl_1_gems + pl_2_gems

        return [pl_1_gems, pl_2_gems]

    @staticmethod
    def find_match_id(match_soup):
        link = match_soup.find('head').find('meta', {'property': 'og:url'}).get('content')
        return int(re.findall(r'id=([0-9]+)', link)[0])


class Player:
    def __init__(self, stats: dict, rank: Ranking):
        self.id_link = stats['id_link']
        self.ranking = stats['ranking']
        self.current_year_matches = [stats['current_year_matches'][0], stats['current_year_matches'][1]]
        self.current_year_surface = [stats['current_year_surface'][0], stats['current_year_surface'][1]]
        self.all_years_surface = [stats['all_years_surface'][0], stats['all_years_surface'][1]]
        self.last_results = [stats['last_results'][0], stats['last_results'][1]]
        self.last_sets = [stats['last_sets'][0], stats['last_sets'][1]]
        self.last_gems = [stats['last_gems'][0], stats['last_gems'][1]]
        self.weighted_results = [stats['weighted_results'][0], stats['weighted_results'][1]]
        self.weighted_gems = [stats['weighted_gems'][0], stats['weighted_gems'][1]]

    def from_match_link(self, match_soup: BeautifulSoup, winner: bool, rank: Ranking):
        self.ranking = self._ranking_from_match(match_soup, winner)
        self.current_year_matches = self._cym_from_match(match_soup, winner)
        self.current_year_surface = self._cys_from_match(match_soup, winner)

    @staticmethod
    def _ranking_from_match(match_soup: BeautifulSoup, winner: bool):
        result_table = match_soup.find('table', {'class': 'result'})
        info_table = result_table.find('tbody')
        info_rows = info_table.find_all('tr')
        if winner:
            return int(info_rows[0].find('td', {'class': 'tr'}).text[:-1])
        else:
            return int(info_rows[0].find('td', {'class': 'tl'}).text[:-1])

    @staticmethod
    def _cym_from_match(match_soup: BeautifulSoup, winner: bool):
        if winner:
            info = match_soup.find('div', {'id': 'balMenu-2-data'}).find('tbody').find_all('tr')[0].\
                find('td', {'class': 'bold'}).text
            numb = re.findall(r'[0-9]+', info)
            return [int(numb[0]), int(numb[1])]
        else:
            info = match_soup.find('div', {'id': 'balMenu-3-data'}).find('tbody').find_all('tr')[0]. \
                find('td', {'class': 'bold'}).text
            numb = re.findall(r'[0-9]+', info)
            return [int(numb[0]), int(numb[1])]

    @staticmethod
    def _cys_from_match(match_soup: BeautifulSoup, winner: bool):
        matches_this_year = match_soup.find('div', {'id': 'balMenu-1-data'})
        matches_this_year_surface = matches_this_year.find_all('tr', {'class': 'selected'})
        if winner:
            stats = matches_this_year_surface[0].find_all('td', {'class': 'player'})[0].text
            numb = re.findall(r'[0-9]+', stats)
            return [int(numb[0]), int(numb[1])]
        else:
            stats = matches_this_year_surface[0].find_all('td', {'class': 'player'})[1].text
            numb = re.findall(r'[0-9]+', stats)
            return [int(numb[0]), int(numb[1])]

    @staticmethod
    def _ays_from_match(match_soup: BeautifulSoup, winner: bool):
        pass

    @staticmethod
    def _last_matches(match_soup: BeautifulSoup, winner: bool, rank: Ranking):
        if winner:
            soup = match_soup.find('div', {'class': 'half-l'})
        else:
            soup = match_soup.find('div', {'class': 'half-r'})

        matches = soup.find('table', {'class': 'result mutual'}).find_all('tr')
        last_matches = [0, 0]
        last_matches_w = [0, 0]
        last_sets = [0, 0]
        last_sets_w = [0, 0]
        last_gems = [0, 0]
        last_gems_w = [0, 0]
        last_gems_sum = 0

        for match in matches:
            if match.find('tr').get('class') == 'head':
                continue

            info = match.find_all('td')
            opponent = rank.atp_rankings[rank.atp_rankings.link == info[1].find_all('a')[0].get('href')]
            if 'lose' in info[0].get('class'):
                last_matches[1] = last_matches[1] + 1
                last_matches_w[1] = last_matches_w[1] + 1*opponent.ranking
                last_matches_w[0] = last_matches_w[0] - 1 * opponent.ranking
            else:
                last_matches[0] = last_matches[0] + 1
                last_matches_w[0] = last_matches_w[0] + 1 * opponent.ranking
                last_matches_w[1] = last_matches_w[1] + 1 * opponent.ranking

            sets = re.findall(r'[0-9]-[0-9]', info[2].find('a').get('title'))
            for s in sets:
                numbs = re.findall(r'[0-9]+', s)
                wins, loses = int(numbs[0]), int(numbs[1])
                if wins > loses:
                    last_sets[0], last_sets[1] = (last_sets[0] + wins), (last_sets[1] + loses)

    @staticmethod
    def _last_sets_from_match(match_soup: BeautifulSoup, winner: bool):
        pass

    @staticmethod
    def _last_gems_from_match(match_soup: BeautifulSoup, winner: bool):
        pass

    @staticmethod
    def _w_results_from_match(match_soup: BeautifulSoup, winner: bool):
        pass

    @staticmethod
    def _w_gems_from_match(match_soup: BeautifulSoup, winner: bool):
        pass


class H2H:
    pass

        
class SurfaceStats:
    def __init__(self, player_soup):
        self.stats = self.get_surface_stats(player_soup)

    def get_surface_stats(self, player_soup: BeautifulSoup):
        match_table = player_soup.find("table", {"class": "surface-stats-table"})
        match_table_tr = match_table.find_all("tr")
        start_year = datetime.datetime.now().year
        end_year = start_year - 1
        surfaces = self.generate_surface_dict()
        surface_stats = self.create_surface_stats_dict(start_year, end_year, surfaces)

        current_year = start_year
        tour = ''
        td_count = 0
        for tr in match_table_tr:
            if tr.get('class') is not None:
                current_year = int(tr.find("td").text)
                if current_year < end_year:
                    break
                td_count = 0
                continue
            else:
                match_table_td = tr.find_all("td")
                for td in match_table_td:
                    if 'hidden' in td.get('class')[0]:
                        continue

                    if 'tlabel' in td.get('class'):
                        tour = td.find('span').text
                        td_count = 0
                        if tour == 'Events':
                            tour = 'Other'
                    else:
                        result = re.findall(r'(\d+)', td.text.strip())
                        surface_stats[current_year][surfaces[td_count]][tour]['Wins'] = int(result[0])
                        surface_stats[current_year][surfaces[td_count]][tour]['Losses'] = int(result[1])
                        td_count = td_count + 1

        return surface_stats

    @staticmethod
    def generate_surface_dict():
        list1 = ['total', 'hard', 'hard_i', 'clay', 'clay_i', 'grass', 'carpet']
        list2 = list(range(7))

        return dict(zip(list2, list1))

    @staticmethod
    def create_surface_stats_dict(start_year: int, end_year: int, surface_dict: dict):
        surface_stats = {}
        for i in list(range(start_year, end_year-1, -1)):
            surface_stats[i] = {}
            for k in surface_dict.values():
                surface_stats[i][k] = {'Main Draw': {'Wins': 0,
                                                     'Losses': 0},
                                       'Other': {'Wins': 0,
                                                 'Losses': 0}}

        return surface_stats

    def __str__(self) -> str:
        return json.dumps(self.stats, indent=4, sort_keys=False)


class Player_ten:
    def __init__(self, player_soup: BeautifulSoup,  player_link: str, name: str,
                 surface_stats: SurfaceStats, updated: bool, rank: Ranking):
        self.name = name
        self.country, self.age, self.preferred_hand = self.get_bio(player_soup)
        self.player_link = player_link,
        self.sex = self.find_sex(rank)
        self.ranking = self.get_ranking(rank),
        self.surface_stats = surface_stats
        self.form_matches, self.weighted_form, self.gem_difference = self.get_last_form(player_soup, 3, rank)
        self.updated = updated

    @staticmethod
    def get_bio(player_info):
        bio = player_info.find("table", {"class": "bio-table table"})
        bio_info = bio.find_all('tr')
        # ranking = re.search(r'Ranking:(\d+)', bio_info[1].text)
        # ranking = bio_info[0].find_all("td")[1].text
        country = bio_info[1].find_all("td")[1].text
        age = re.search(r'Age (\d+)', bio_info[2].find_all("td")[1].text)
        hand = bio_info[4].find_all("td")[1].text

        if age is None:
            return country, 0, hand
        else:
            return country, age.group(1), hand

    def get_last_form(self, player: BeautifulSoup, n_matches: int, rank: Ranking):
        matches = player.find("table", {"class": "draw-table"}).find_all("tr")
        count = 0
        wins, losses = 0, 0
        weighted_wins, weighted_losses = 0, 0
        gem_win, gem_lose = 0, 0
        for match in matches:
            if count == n_matches:
                break

            if match.get('class') is not None:
                if 'event' in match.get('class')[0]:
                    continue

            infos = match.find_all('td')
            gem_results = re.findall(r'[0-9]-[0-9]', infos[4].text)
            if infos[2].text.strip() == self.name:
                ranking_weight = self.get_ranking_weight(self.ranking, rank.ranking[rank.name == infos[3].text.strip()])
                wins = wins + 1
                weighted_wins = weighted_wins + 1*ranking_weight
                gem_win = gem_win + sum([x[0] for x in gem_results])
                gem_lose = gem_lose + sum([x[2] for x in gem_results])
            else:
                ranking_weight = self.get_ranking_weight(self.ranking, rank.rank[rank.name == infos[2].text.strip()])
                losses = losses + 1
                weighted_losses = weighted_losses + 1*ranking_weight
                gem_win = gem_win + sum([x[2] for x in gem_results])
                gem_lose = gem_lose + sum([x[0] for x in gem_results])

            count = count + 1

        return (wins - losses), (weighted_wins - weighted_losses), (gem_win - gem_lose)

    @staticmethod
    def get_ranking_weight(player_rank, opponent_rank):
        if player_rank > opponent_rank:
            return 2 - 1 / (player_rank - opponent_rank)
        elif player_rank == opponent_rank:
            return 1
        else:
            return 1 / 2 + 1 / (2 * (opponent_rank - player_rank))

    def find_sex(self, rank: Ranking):
        if self.name in rank.ranking_atp.name:
            return 'male'
        elif self.name in rank.ranking_wta.name:
            return 'female'
        else:
            return None

    def get_ranking(self, rank: Ranking):
        if self.sex == 'male':
            if self.name in rank.ranking_atp.name.values:
                return rank.ranking_atp['rank'][rank.ranking_atp.name == self.name]
            else:
                return 1000
        else:
            if self.name in rank.ranking_wta.name.values:
                return rank.ranking_wta['rank'][rank.ranking_wta.name == self.name]
            else:
                return 1000


class Match:
    pass

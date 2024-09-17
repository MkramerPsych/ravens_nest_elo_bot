'''
Core logic for Armored Core VI ELO bot
Designed by Ahasuerus for Armored Scrims Server
'''
from typing import Optional
from datetime import datetime
from rich.table import Table
from rich.console import Console
import random
import string
import math

# constants
ELO_MAXIMUM = 2200 # the highest possible ELO
ELO_MINIMUM = 100 # the lowest possible ELO
ELO_TO_RANK = {
    'D': {'min': ELO_MINIMUM, 'max': 699},
    'C': {'min': 700, 'max': 949},
    'B': {'min': 950, 'max': 1249},
    'A': {'min': 1250, 'max': 1499},
    'S': {'min': 1500, 'max': 1699},
    'SS': {'min': 1700, 'max': ELO_MAXIMUM},
}

APPROVED_1S_MAPS = ['Contaminated City A', 'Xylem, the Floating City',
                    'Jorgen Refueling Base', 'Grid 086 A',
                      'Watchpoint Delta A']

APPROVED_3S_MAPS = ['Contaminated City B', 'Bona Dea Dunes A',
                    'Jorgen Refueling Base', 'Old Bertram Spaceport',
                    'Xylem, the Floating City']


# Helper functions
def get_rank_from_ELO(ELO: int):
    '''
    Get the rank from the ELO value

    :param ELO: The ELO value of the player

    returns: The rank of the player
    '''
    for rank, values in ELO_TO_RANK.items():
        if values['min'] <= ELO < values['max']:
            return rank
        elif ELO >= ELO_TO_RANK['SS']['min']:
            return f'SS_{ELO}'

def generate_keyword(length = 6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def probability_of_victory(player_ELO: int, opponent_ELO: int):
    '''
    Calculate the probability of a player winning a match

    :param player_ELO: The ELO value of the player
    :param opponent_ELO: The ELO value of the opponent

    returns: The probability of the player winning
    '''
    return 1.0 / (1 + math.pow(10, (player_ELO - opponent_ELO) / 400.0))

def ELO_formula(player_ELO: int, opponent_ELO: int, result: int, ELO_k: int = 30, ELO_max: int = 2200, ELO_min: int = 100):
    '''
    Calculate the new ELO value for a player after a match

    :param player_ELO: The current ELO value of the player
    :param opponent_ELO: The current ELO value of the opponent
    :param result: The result of the match (1 for win, 0 for loss)

    returns: The new ELO value of the players
    '''
    prob_beta_victory = probability_of_victory(player_ELO, opponent_ELO)
    prob_alpha_victory = probability_of_victory(opponent_ELO, player_ELO)
    player_ELO = round(player_ELO + ELO_k * (result - prob_alpha_victory))
    opponent_ELO = round(opponent_ELO + ELO_k * ((1 - result) - prob_beta_victory))
    player_ELO = min(max(player_ELO, ELO_min), ELO_max) # ensure ELO is within bounds
    opponent_ELO = min(max(opponent_ELO, ELO_min), ELO_max) # ensure ELO is within bounds
    return player_ELO, opponent_ELO


# core logic
class Player:
    '''
    Class representing a player in the database
    '''
    player_id: int
    player_name: str
    player_singles_ELO: float
    player_teams_ELO: float
    player_singles_rank: str
    player_teams_rank: str
    player_team: str
    singles_wins: int
    singles_losses: int
    teams_wins: int
    teams_losses: int
    singles_wl_ratio: float = 0.0
    teams_wl_ratio: float = 0.0

    def __init__(self, player_name: str, player_team: Optional[str] = None, player_id: Optional[str] = None):
        '''
        Called when a new player is added to the database

        :param player_name: The name of the player
        :param player_team: The team the player is on

        returns: None
        '''
        self.player_name = player_name
        self.player_id = player_id
        self.player_singles_ELO = ELO_TO_RANK['C']['min']
        self.player_teams_ELO = ELO_TO_RANK['C']['min']
        self.player_singles_rank = 'C'
        self.player_teams_rank = 'C'
        self.player_team = player_team
        self.singles_wins = 0
        self.singles_losses = 0
        self.teams_wins = 0
        self.teams_losses = 0

    def update_player_stats(self, result: int, match_type: str):
        '''
        Update the player's W/L stats and rank after a match

        :param result: The result of the match (1 for win, 0 for loss)
        '''
        if result == 1:
            if match_type == '1v1':
                self.singles_wins += 1
            elif match_type == '3v3 flex':
                self.teams_wins += 1
            else: # match_type of '3v3 reg'
                teams_db.get_team(self.player_team).wins += 1

        else:
            if match_type == '1v1':
                self.singles_losses += 1
            elif match_type == '3v3 flex':
                self.teams_losses += 1
            else: # match_type of '3v3 reg'
                teams_db.get_team(self.player_team).losses += 1

        self.update_WinLoss()  # Recalculate the W/L ratio
        self.player_singles_rank = get_rank_from_ELO(self.player_singles_ELO)
        self.player_teams_rank = get_rank_from_ELO(self.player_teams_ELO)

    def update_WinLoss(self):
        # Calculate the W/L ratio if losses are greater than 0
        if self.singles_losses > 0:
            self.singles_wl_ratio = self.singles_wins / self.singles_losses
        else:
            self.singles_wl_ratio = float('inf')

        if self.teams_losses > 0:
            self.teams_wl_ratio = self.teams_wins / self.teams_losses
        else:
            self.teams_wl_ratio = float('inf')

    def __str__(self):
        stats_table = Table(title=f"Stats for {self.player_name}")
        stats_table.add_column("Field", justify="right", style="cyan", no_wrap=True)
        stats_table.add_column("Value", style="magenta")

        stats_table.add_row("Player Name", self.player_name)
        stats_table.add_row("Player ID", str(self.player_id))
        stats_table.add_row("1v1s ELO", str(self.player_singles_ELO))
        stats_table.add_row("1v1s Rank", self.player_singles_rank)
        stats_table.add_row("Player Team", self.player_team if self.player_team else "N/A")
        stats_table.add_row("3v3s ELO", str(self.player_teams_ELO))
        stats_table.add_row("3v3s Rank", self.player_teams_rank)
        stats_table.add_row("1v1s Wins", str(self.singles_wins))
        stats_table.add_row("1v1s Losses", str(self.singles_losses))
        stats_table.add_row("1v1s W/L Ratio", f"{self.singles_wins / self.singles_losses:.2f}" if self.singles_losses > 0 else "N/A")
        stats_table.add_row("3v3s Wins", str(self.teams_wins))
        stats_table.add_row("3v3s Losses", str(self.teams_losses))
        stats_table.add_row("3v3s W/L Ratio", f"{self.teams_wins / self.teams_losses:.2f}" if self.teams_losses > 0 else "N/A")

        # print the table to the console and capture the output
        console = Console(force_terminal=False)
        with console.capture() as capture:
            console.print(stats_table)
        table_output = capture.get()

        # Send the captured table output as a message
        return f"```{table_output}```"

    def __repr__(self):
        return self.__str__()

class players_db:
    '''
    Class representing the database of players
    '''
    players: list[Player]

    def __init__(self):
        self.players = []

    def add_player(self, player_obj: Player):
        if player_obj not in self.players:
            self.players.append(player_obj)
        else:
            print(f'Player {player_obj.player_name} is already in the database')

    def add_players(self, player_objs: list[Player]):
        for player in player_objs:
            if player.player_name not in [p.player_name for p in self.players]:
                self.players.append(player)
            else:
                print(f'Player {player.player_name} is already in the database')

    def remove_player(self, player_name: str):
        for player in self.players:
            if player.player_name == player_name:
                self.players.remove(player)
                return

    def remove_players(self, player_names: list[str]):
        for player_name in player_names:
            self.remove_player(player_name)

    def get_player(self, player_name: str):
        if not self.players:
            return None
        for player in self.players:
            if player.player_name == player_name:
                return player
        return None

    def get_players(self, player_names: list[str]):
        return [player for player in self.players if player.player_name in player_names]

    def get_top_singles_players(self, num_players: int):
        sorted_players = sorted(self.players, key=lambda player: player.player_singles_ELO, reverse=True)
        return sorted_players[:num_players]

    def get_top_teams_players(self, num_players: int):
        sorted_players = sorted(self.players, key=lambda player: player.player_teams_ELO, reverse=True)
        return sorted_players[:num_players]

    def dump_players_db(self, file_path: str):
        with open(file_path, 'w') as file:
            for player in self.players:
                file.write(f"{player.player_name},{player.player_singles_ELO},{player.player_teams_ELO},{player.player_singles_rank},{player.player_teams_rank},{player.player_team},{player.singles_wins},{player.singles_losses},{player.teams_wins},{player.teams_losses},{player.singles_wl_ratio},{player.teams_wl_ratio}\n")

    def load_players_db(self, file_path: str):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data = line.strip().split(',')
                new_player = Player(data[0])
                new_player.player_singles_ELO = int(data[1])
                new_player.player_teams_ELO = int(data[2])
                new_player.player_singles_rank = data[3]
                new_player.player_teams_rank = data[4]
                new_player.player_team = data[5]
                new_player.singles_wins = int(data[6])
                new_player.singles_losses = int(data[7])
                new_player.teams_wins = int(data[8])
                new_player.teams_losses = int(data[9])
                new_player.singles_wl_ratio = float(data[10])
                new_player.teams_wl_ratio = float(data[11])
                self.add_player(new_player)

    def __str__(self):
        sorted_players = sorted(self.players, key=lambda player: player.player_singles_ELO, reverse=True)
        players_table = Table(title="Players Database")
        players_table.add_column("Player Name", justify="left", style="cyan", no_wrap=True)
        players_table.add_column("1v1s ELO", style="magenta")
        players_table.add_column("1v1s Rank", style="green")
        players_table.add_column("3v3s ELO", style="magenta")
        players_table.add_column("3v3s Rank", style="green")
        players_table.add_column("Player Team", style="yellow")
        players_table.add_column("1v1s Wins", style="blue")
        players_table.add_column("1v1s Losses", style="red")
        players_table.add_column("1v1s W/L Ratio", style="white")
        players_table.add_column("3v3s Wins", style="blue")
        players_table.add_column("3v3s Losses", style="red")
        players_table.add_column("3v3s W/L Ratio", style="white")

        for player in sorted_players:
            players_table.add_row(
            player.player_name,
            str(player.player_singles_ELO),
            player.player_singles_rank,
            str(player.player_teams_ELO),
            player.player_teams_rank,
            player.player_team if player.player_team else "N/A",
            str(player.singles_wins),
            str(player.singles_losses),
            f"{player.singles_wins / player.singles_losses:.2f}" if player.singles_losses > 0 else "N/A",
            str(player.teams_wins),
            str(player.teams_losses),
            f"{player.teams_wins / player.teams_losses:.2f}" if player.teams_losses > 0 else "N/A"
            )

        console = Console(force_terminal=False)
        with console.capture() as capture:
            console.print(players_table)
        table_output = capture.get()

        return f"```{table_output}```"

    def __len__(self):
        return len(self.players)

    def __repr__(self):
        return self.__str__()

# 3S LOGIC
class team:
    '''
    Class representing a team in the 3s database
    '''
    team_name: str
    roster: list[Player] # list of 3 player names
    team_ELO: float
    team_rank: str
    wins: int
    losses: int
    wl_ratio: float = 0.0

    def __init__(self, team_name: str, roster: list[Player]):
        '''
        Called when a new team is added to the database

        :param team_name: The name of the team
        :param roster: The list of player names on the team

        returns: None
        '''
        self.team_name = team_name
        self.roster = roster
        self.team_ELO = ELO_TO_RANK['C']['min']
        self.team_rank = 'C'
        self.wins = 0
        self.losses = 0

    def update_WinLoss(self):
        # Calculate the W/L ratio if losses are greater than 0
        if self.losses > 0:
            self.wl_ratio = self.wins / self.losses
        else:
            self.wl_ratio = float('inf')

    def update_team_stats(self, result: int):
        if result == 1:
            self.wins += 1
        else:
            self.losses += 1
        self.update_WinLoss()
        self.team_rank = get_rank_from_ELO(self.team_ELO)

    def add_to_team(self, player: Player):
        if len(self.roster) < 3:
            self.roster.append(player.player_name)
        else:
            raise ValueError('Team is currently full, please remove a player before adding another')

    def remove_from_team(self, player: Player):
        if player in self.roster:
            self.roster.remove(player.player_name)
        else:
            ValueError(f'Player {player.player_name} is not on the team')

    def __str__(self):
        team_table = Table(title=f"Stats for Team {self.team_name}")
        team_table.add_column("Field", justify="right", style="cyan", no_wrap=True)
        team_table.add_column("Value", style="magenta")

        team_table.add_row("Team Name", self.team_name)
        team_table.add_row("Roster", ', '.join(player.player_name for player in self.roster))
        team_table.add_row("Team ELO", str(self.team_ELO))
        team_table.add_row("Team Rank", self.team_rank)
        team_table.add_row("Wins", str(self.wins))
        team_table.add_row("Losses", str(self.losses))
        team_table.add_row("W/L Ratio", f"{self.wins / self.losses:.2f}" if self.losses > 0 else "N/A")

        console = Console(force_terminal=False)
        with console.capture() as capture:
            console.print(team_table)
        table_output = capture.get()

        return f"```{table_output}```"

    def __repr__(self):
        return self.__str__()

class teams_db:
    '''
    Class representing the database of teams
    '''
    teams: list[team]
    player_registry: players_db

    def __init__(self, player_registry: players_db):
        self.teams = []
        self.player_registry = player_registry

    def add_team(self, team_obj: team):
        self.teams.append(team_obj)

    def remove_team(self, team_name: str):
        for team in self.teams:
            if team.team_name == team_name:
                self.teams.remove(team)
                return

    def get_team(self, team_name: str):
        for team in self.teams:
            if team.team_name == team_name:
                return team
        return None

    def get_top_teams(self, num_teams: int):
        sorted_teams = sorted(self.teams, key=lambda team: team.team_ELO, reverse=True)
        return sorted_teams[:num_teams]

    def dump_teams_db(self, file_path: str):
        with open(file_path, 'w') as file:
            for team in self.teams:
                players_str = ','.join(player.player_name for player in team.roster)
                file.write(f"{team.team_name},{players_str},{team.team_ELO},{team.team_rank},{team.wins},{team.losses},{team.wl_ratio}\n")

    def load_teams_db(self, file_path: str):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data = line.strip().split(',')
                team_name = data[0]
                player1 = data[1]
                player2 = data[2]
                player3 = data[3]
                team_ELO = int(data[4])
                team_rank = data[5]
                wins = int(data[6])
                losses = int(data[7])
                wl_ratio = float(data[8])

                players = [player1, player2, player3]
                player_objs = [self.player_registry.get_player(player_name) for player_name in players]
                new_team = team(team_name, player_objs)
                new_team.team_ELO = team_ELO
                new_team.team_rank = team_rank
                new_team.wins = wins
                new_team.losses = losses
                new_team.wl_ratio = wl_ratio
                self.add_team(new_team)

    def __str__(self):
        sorted_teams = sorted(self.teams, key=lambda team: team.team_ELO, reverse=True)
        teams_table = Table(title="Teams Database")
        teams_table.add_column("Team Name", justify="left", style="cyan", no_wrap=True)
        teams_table.add_column("Team ELO", style="magenta")
        teams_table.add_column("Team Rank", style="green")
        teams_table.add_column("Wins", style="blue")
        teams_table.add_column("Losses", style="red")
        teams_table.add_column("W/L Ratio", style="white")

        for team in sorted_teams:
            teams_table.add_row(
            team.team_name,
            str(team.team_ELO),
            team.team_rank,
            str(team.wins),
            str(team.losses),
            f"{team.wins / team.losses:.2f}" if team.losses > 0 else "N/A"
            )

        console = Console(force_terminal=False)
        with console.capture() as capture:
            console.print(teams_table)
        table_output = capture.get()

        return f"```{table_output}```"

    def __len__(self):
        return len(self.teams)

    def __repr__(self):
        return self.__str__()


# MATCH LOGIC
class match:
    match_id: int # hash of all player names and time
    match_type: str # either [1v1 or 3v3]
    match_date: str # date of the match
    player_alpha: Optional[Player] = None  # name of the first player, only if match_type == 1v1
    player_beta: Optional[Player] = None  # name of the second player, only if match_type == 1v1
    team_alpha: Optional[team] = None  # name of the first team, only if match_type == 3v3
    team_beta: Optional[team] = None  # name of the second team, only if match_type == 3v3
    match_status: str # either completed, failed, or pending
    match_winner: str # name of the winning team [3v3] or player [1v1] or null [pending/failed]
    match_loser: str # name of the losing team [3v3] or player [1v1] or null [pending/failed]
    match_map: str # map played on [read in from constant APPROVED_1S_MAPS or APPROVED_3S_MAPS]
    keyword: str # keyword to be used for lobby

    def __init__(self, match_type: str, player_alpha: Optional[Player] = None, player_beta: Optional[Player] = None,
                 team_alpha: Optional[team|list[Player]] = None, team_beta: Optional[team|list[Player]] = None):
        self.match_date = datetime.now()
        self.match_id = abs(int(str(hash(self.match_date))[:8])) # god awful but works easy enough
        self.match_type = match_type
        self.player_alpha = player_alpha
        self.player_beta = player_beta
        self.team_alpha = team_alpha
        self.team_beta = team_beta
        self.match_map = None
        self.match_status = 'not_started'
        self.match_winner = None
        self.match_loser = None
        self.keyword = None

    def setup_match_parameters(self):
        if self.match_type == '1v1':
            self.match_map = random.choice(APPROVED_1S_MAPS)
        elif self.match_type == '3v3 flex':
            self.match_map = random.choice(APPROVED_3S_MAPS)
        elif self.match_type == '3v3 reg': # match_type == '3v3s reg'
            self.match_map = random.choice(APPROVED_3S_MAPS)
        else:
            raise ValueError('Invalid match type, please use either 1v1, 3v3 flex, or 3v3 reg')
        self.match_status = 'pending'
        self.keyword = generate_keyword()
        print(f'Match setup complete. Use Map: {self.match_map}, Use Keyword: {self.keyword}')

    def report_match_results(self, winner: team|Player|list[Player], loser: team|Player|list[Player]):
        self.match_status = 'completed'

        if self.match_type == '3v3 flex':
            self.match_winner = [player.player_name for player in winner]
            self.match_loser = [player.player_name for player in loser]
        else:
            self.match_winner = winner.player_name if self.match_type != '3v3 reg' else winner.team_name
            self.match_loser = loser.player_name if self.match_type != '3v3 reg' else loser.team_name

        if self.match_type == '1v1':
            print(f'Match results reported. WIN: {winner.player_name}, LOSS: {loser.player_name}')
            [winner.player_singles_ELO, loser.player_singles_ELO] = ELO_formula(winner.player_singles_ELO, loser.player_singles_ELO, 1)
            winner.update_player_stats(1, '1v1')
            loser.update_player_stats(0, '1v1')
        elif self.match_type == '3v3 flex':
            print(f'Match results reported. WIN: {winner[0].player_name, winner[1].player_name, winner[2].player_name}, LOSS: {loser[0].player_name, loser[1].player_name, loser[2].player_name}')
            for winner_player, loser_player in zip(winner, loser):
                winner_player.player_teams_ELO, loser_player.player_teams_ELO = ELO_formula(winner_player.player_teams_ELO, loser_player.player_teams_ELO, 1)
                winner_player.update_player_stats(1, '3v3 flex')
                loser_player.update_player_stats(0, '3v3 flex')
        else: # match_type == '3v3 reg'
            print(f'Match results reported. WIN: {winner.team_name}, LOSS: {loser.team_name}')
            [winner.team_ELO, loser.team_ELO] = ELO_formula(winner.team_ELO, loser.team_ELO, 1)
            print(f'Match results reported. WIN: {winner.team_name}, LOSS: {loser.team_name}')
            winner.update_team_stats(1)
            loser.update_team_stats(0)

    def __str__(self):
        match_table = Table(title=f"Match {self.match_id} Details")
        match_table.add_column("Field", justify="right", style="cyan", no_wrap=True)
        match_table.add_column("Value", style="magenta")

        match_table.add_row("Match ID", str(self.match_id))
        match_table.add_row("Match Type", self.match_type)
        match_table.add_row("Match Date", str(self.match_date))
        match_table.add_row("Match Status", self.match_status)
        if self.match_type == '3v3 flex':
            match_table.add_row("Winner", ', '.join(self.match_winner) if self.match_winner else "N/A")
            match_table.add_row("Loser", ', '.join(self.match_loser) if self.match_loser else "N/A")
        else:
            match_table.add_row("Winner", self.match_winner if self.match_winner else "N/A")
            match_table.add_row("Loser", self.match_loser if self.match_loser else "N/A")

        console = Console(force_terminal=False)
        with console.capture() as capture:
            console.print(match_table)
        table_output = capture.get()

        return f"```{table_output}```"

    def __repr__(self):
        return self.__str__()

class match_db:
    '''
    Class representing the database of matches
    '''
    matches: list[match]

    def __init__(self):
        self.matches = []

    def add_match(self, match_obj: match):
        self.matches.append(match_obj)

    def update_match(self, match_id: int, winner: team|Player, loser: team|Player):
        for match in self.matches:
            if match.match_id == match_id:
                match.report_match_results(winner, loser)
                return

    def remove_match(self, match_id: int):
        for match in self.matches:
            if match.match_id == match_id:
                self.matches.remove(match)
                return

    def get_match(self, match_id: int):
        for match in self.matches:
            if match.match_id == match_id:
                return match
        return None

    def dump_matches_db(self, file_path: str):
        with open(file_path, 'w') as file:
            for match in self.matches:
                if match.match_type == '3v3 flex':
                    winner = ', '.join(match.match_winner) if match.match_winner else "N/A"
                    loser = ', '.join(match.match_loser) if match.match_loser else "N/A"
                else:
                    winner = match.match_winner if match.match_winner else "N/A"
                    loser = match.match_loser if match.match_loser else "N/A"
                file.write(f"{match.match_id},{match.match_type},{match.match_map},{winner},{loser}\n")

    def load_matches_db(self, file_path: str):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data = line.strip().split(',')
                match_id = int(data[0])
                match_type = data[1]
                match_map = data[2]
                match_winner = str([data[3],data[4],data[5]])
                match_loser = str([data[6],data[7],data[8]])

                new_match = match(match_type)
                new_match.match_id = match_id
                new_match.match_map = match_map
                new_match.match_winner = match_winner
                new_match.match_loser = match_loser
                new_match.match_status = 'completed'
                self.add_match(new_match)

    def __str__(self):
        matches_table = Table(title="Matches Database")
        matches_table.add_column("Match ID", justify="left", style="cyan", no_wrap=True)
        matches_table.add_column("Match Type", style="magenta")
        matches_table.add_column("Map", style="green")
        matches_table.add_column("Winner", style="blue")
        matches_table.add_column("Loser", style="red")

        for match in self.matches:
            matches_table.add_row(
            str(match.match_id),
            match.match_type,
            match.match_map if match.match_map else "N/A",
            str(match.match_winner) if match.match_winner else "N/A",
            str(match.match_loser) if match.match_loser else "N/A"
            )

        console = Console(force_terminal=False)
        with console.capture() as capture:
            console.print(matches_table)
        table_output = capture.get()

        return f"```{table_output}```"

    def __len__(self):
        return len(self.matches)

    def __repr__(self):
        return self.__str__()

'''
Core logic for Armored Core VI ELO bot
Designed by Ahasuerus for Armored Scrims Server
'''
from typing import Optional
import discord
# constants
ELO_TO_RANK = {
    'D': {'min': 450, 'max': 700},
    'C': {'min': 700, 'max': 950},
    'B': {'min': 950, 'max': 1100},
    'A': {'min': 1100, 'max': 1350},
    'S': {'min': 1350, 'max': 1600}
}

APPROVED_1S_MAPS = []
APPROVED_3S_MAPS = ['Contaminated City B', 'Bona Dea Dunes A', 'Jorgen Refueling Base', 'Old Bertram Spaceport',
                    'Xylem, the Floating City']

def get_rank_from_ELO(ELO: int):
    '''
    Get the rank from the ELO value

    :param ELO: The ELO value of the player

    returns: The rank of the player
    '''
    for rank, values in ELO_TO_RANK.items():
        if values['min'] <= ELO < values['max']:
            return rank
        elif ELO >= ELO_TO_RANK['S']['max']:
            return f'S_{ELO}'
    


# core logic
class Player:
    '''
    Class representing a player in the database
    '''
    player_id: int
    player_name: str
    player_ELO: float
    player_rank: str
    wins: int
    losses: int
    wl_ratio: float = 0.0

    def __init__(self, player_name: str, player_team: Optional[str]):
        '''
        Called when a new player is added to the database

        :param player_name: The name of the player
        :param player_team: The team the player is on

        returns: None
        '''
        self.player_name = player_name
        self.player_id = hash(player_name)
        self.player_ELO = C_RANK_MIN_ELO
        self.player_rank = 'C'
        self.player_team = ''
        self.wins = 0
        self.losses = 0
        
    def update_player_stats(self, wins: int, losses: int):
        self.wins += wins
        self.losses += losses
        self.update_WinLoss()  # Recalculate the W/L ratio

    def __str__(self):
        return (f"ID: {self.player_id}, Name: {self.player_name}, ELO: {self.player_ELO}, "
                f"Rank: {self.player_rank}, Wins: {self.wins}, Losses: {self.losses}, "
                f"W/L Ratio: {self.wl_ratio:.2f}")
    
    def __repr__(self):
        return (f"Player({self.player_id}, {self.player_name}, {self.player_ELO}, "
                f"{self.player_rank}, {self.wins}, {self.losses}, {self.wl_ratio})")

# 3S LOGIC
class team:
    '''
    Class representing a team in the 3s database
    '''
    team_name: str
    roster: list[str] # list of 3 player names
    team_ELO: float
    team_rank: str
    wins: int
    losses: int
    wl_ratio: float = 0.0

    def __init__(self, team_name: str, roster: list[str]):
        '''
        Called when a new team is added to the database

        :param team_name: The name of the team
        :param roster: The list of player names on the team

        returns: None
        '''
        self.team_name = team_name
        self.roster = roster
        self.team_ELO = 700
        self.team_rank = 'C'
        self.wins = 0
        self.losses = 0

    def __init__(self, team_name: str, roster: list[str]):
        '''
        Called when a new team is added to the database

        :param team_name: The name of the team
        :param player1: The name of the first player on the team
        :param player2: The name of the second player on the team
        :param player3: The name of the third player on the team

        returns: None
        '''
        self.team_name = team_name
        self.roster = roster
        self.team_ELO = 700
        self.team_rank = 'C'
        self.wins = 0
        self.losses = 0

    def update_WinLoss(self):
        # Calculate the W/L ratio if losses are greater than 0
        if self.losses > 0:
            self.wl_ratio = self.wins / self.losses
        else:
            self.wl_ratio = float('inf')

    def update_team_stats(self, wins: int, losses: int):
        self.wins += wins
        self.team_ELO += self.update_team_ELO(wins, losses)
        self.losses += losses
        self.update_WinLoss()

    def update_team_ELO(self, wins: int, losses: int):
        pass

    def add_to_team(self, player_name: str):
        if len(self.roster) < 3:
            self.roster.append(player_name)
        else:
            raise ValueError('Team is full, please remove a player before adding another')

    def remove_from_team(self, player_name: str):
        if player_name in self.roster:
            self.roster.remove(player_name)
        else:
            ValueError('Player is not on the team')

    def __str__(self):
        return (f"Name: {self.team_name}, ELO: {self.team_ELO}, "
                f"Rank: {self.team_rank}, Wins: {self.wins}, Losses: {self.losses}, "
                f"W/L Ratio: {self.wl_ratio:.2f}")
    
    def __repr__(self):
        return (f"Team({self.team_name}, roster: {self.roster}, ELO: {self.team_ELO}, "
                f"Rank: {self.team_rank}, W: {self.wins}, L: {self.losses}, W/L: {self.wl_ratio})")
    
    def update_WinLoss(self):
        # Calculate the W/L ratio if losses are greater than 0
        if self.losses > 0:
            self.wl_ratio = self.wins / self.losses
        else:
            self.wl_ratio = float('inf')  # or use some other indicator of a perfect ratio

    

class teams_db:
    '''
    Class representing the database of teams
    '''
    teams: list[team]

    def __init__(self):
        self.teams = []

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

    def __str__(self):
        sorted_teams = sorted(self.teams, key=lambda team: team.team_ELO, reverse=True)
        return '\n'.join([str(team) for team in sorted_teams])
    
    def __len__(self):
        return len(self.teams)

    def __repr__(self):
        sorted_teams = sorted(self.teams, key=lambda team: team.team_ELO, reverse=True)
        return '\n'.join([repr(team) for team in sorted_teams])

# Match logic
class match:
    match_id: int # hash of all player names and time
    match_type: str # either 1v1 or 3v3
    match_date: str # date of the match
    match_status: str # either completed, failed, or pending
    match_winner: str # name of the winning team [3v3] or player [1v1] or null [pending/failed]
    match_loser: str # name of the losing team [3v3] or player [1v1] or null [pending/failed]
    match_map: str # map played on [read in from constant APPROVED_1S_MAPS or APPROVED_3S_MAPS]

threes_db = teams_db()
ksh = team('Koolish',['Kraydle', 'Hooli', 'Fish'])
rns = team('RnS',['RamenRook', 'Risa', 'Sabbath'])
threes_db.add_team(ksh)
threes_db.add_team(rns)
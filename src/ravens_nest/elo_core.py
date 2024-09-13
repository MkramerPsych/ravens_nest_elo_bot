'''
Core logic for Armored Core VI ELO bot
Designed by Ahasuerus for Armored Scrims Server
'''
from typing import Optional
from datetime import datetime
import random
import string

# constants
ELO_TO_RANK = {
    'D': {'min': 450, 'max': 700},
    'C': {'min': 700, 'max': 950},
    'B': {'min': 950, 'max': 1100},
    'A': {'min': 1100, 'max': 1350},
    'S': {'min': 1350, 'max': 1600}
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
        elif ELO >= ELO_TO_RANK['S']['max']:
            return f'S_{ELO}'

def generate_keyword(length = 6):
    characters = string.ascii_letters + string.digits 
    return ''.join(random.choice(characters) for _ in range(length))

# core logic
class Player:
    '''
    Class representing a player in the database
    '''
    player_id: int
    player_name: str
    player_ELO: float
    player_rank: str
    player_team: str
    wins: int
    losses: int
    wl_ratio: float = 0.0

    def __init__(self, player_name: str, player_team: Optional[str], player_id: Optional[str] = None):
        '''
        Called when a new player is added to the database

        :param player_name: The name of the player
        :param player_team: The team the player is on

        returns: None
        '''
        self.player_name = player_name
        self.player_id = player_id
        self.player_ELO = ELO_TO_RANK['C']['min']
        self.player_rank = 'C'
        self.player_team = player_team
        self.wins = 0
        self.losses = 0
        
    def update_player_stats(self, wins: int, losses: int):
        self.wins += wins
        self.losses += losses
        self.update_WinLoss()  # Recalculate the W/L ratio
        self.player_ELO += self.update_player_ELO(wins, losses)
        self.player_rank = get_rank_from_ELO(self.player_ELO)

    def update_WinLoss(self):
        # Calculate the W/L ratio if losses are greater than 0
        if self.losses > 0:
            self.wl_ratio = self.wins / self.losses
        else:
            self.wl_ratio = float('inf')

    def update_player_ELO(self, wins: int, losses: int):
        '''
        Kraydle and I need to discuss how we want to calculate ELO gains
        and losses. This will either leave rank untouched or call one
        of two subfunctions: promote() or demote()
        '''
        # TODO: adjust ELO based on wins and losses
        return 10 * (wins - losses)
        
    def _promote(self):
        '''
        Called when a player is promoted to a higher rank
        '''
        pass

    def _demote(self):
        '''
        Called when a player is demoted to a lower rank
        '''
        pass

    def __str__(self):
        return (f"ID: {self.player_id}, Name: {self.player_name}, ELO: {self.player_ELO}, Team Affiliation: {self.player_team or None}, "
                f"Rank: {self.player_rank}, Wins: {self.wins}, Losses: {self.losses}, "
                f"W/L Ratio: {self.wl_ratio:.2f}")
    
    def __repr__(self):
        return (f"Player({self.player_id}, {self.player_name}, {self.player_ELO}, {self.player_team}, "
                f"{self.player_rank}, {self.wins}, {self.losses}, {self.wl_ratio})")
    
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
            if player not in self.players:
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

    def __str__(self):
        sorted_players = sorted(self.players, key=lambda player: player.player_ELO, reverse=True)
        return '\n'.join([str(player) for player in sorted_players])
    
    def __len__(self):
        return len(self.players)

    def __repr__(self):
        sorted_players = sorted(self.players, key=lambda player: player.player_ELO, reverse=True)
        return '\n'.join([repr(player) for player in sorted_players])

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

    def __init__(self, team_name: str, roster: list[Player]):
        '''
        Called when a new team is added to the database

        :param team_name: The name of the team
        :param roster: The list of player names on the team

        returns: None
        '''
        self.team_name = team_name
        self.roster = [name.player_name for name in roster]
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

    def update_team_stats(self, wins: int, losses: int):
        self.wins += wins
        self.team_ELO += self.update_team_ELO(wins, losses)
        self.losses += losses
        self.update_WinLoss()

    def update_team_ELO(self, wins: int, losses: int):
        # TODO: come back and add real ELO adjustment calculation
        return 10 * (wins - losses)

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
        return (f"Name: {self.team_name}, ELO: {self.team_ELO}, "
                f"Rank: {self.team_rank}, Wins: {self.wins}, Losses: {self.losses}, "
                f"W/L Ratio: {self.wl_ratio:.2f}")
    
    def __repr__(self):
        return (f"Team({self.team_name}, roster: {self.roster}, ELO: {self.team_ELO}, "
                f"Rank: {self.team_rank}, W: {self.wins}, L: {self.losses}, W/L: {self.wl_ratio})")
    

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
                 team_alpha: Optional[team] = None, team_beta: Optional[team] = None):
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
        elif self.match_type == '3v3':
            self.match_map = random.choice(APPROVED_3S_MAPS)
        self.match_status = 'pending'
        self.keyword = generate_keyword()
        print(f'Match setup complete. Use Map: {self.match_map}, Use Keyword: {self.keyword}')

    def report_match_results(self, winner: team|Player, loser: team|Player):
        self.match_winner = winner.player_name if self.match_type == '1v1' else winner.team_name
        self.match_loser = loser.player_name if self.match_type == '1v1' else loser.team_name
        self.match_status = 'completed'
        if self.match_type == '1v1':
            print(f'Match results reported. WIN: {winner.player_name}, LOSS: {loser.player_name}')
            winner.update_player_stats(1, 0)
            loser.update_player_stats(0, 1)
        elif self.match_type == '3v3':
            winner.update_team_stats(1, 0)
            loser.update_team_stats(0, 1)
            print(f'Match results reported. WIN: {winner.team_name}, LOSS: {loser.team_name}')

    def __str__(self):
        if self.match_type == '1v1':
            participants = f"Player Alpha: {self.player_alpha.player_name}, Player Beta: {self.player_beta.player_name}"
        elif self.match_type == '3v3':
            participants = f"Team Alpha: {self.team_alpha.team_name}, Team Beta: {self.team_beta.team_name}"
        else:
            participants = "Unknown participants"
        
        return (f"Match ID: {self.match_id}, Type: {self.match_type}, Date: {self.match_date}, "
                f"Status: {self.match_status}, Winner: {self.match_winner}, Loser: {self.match_loser}, "
                f"Map: {self.match_map}, Keyword: {self.keyword}, {participants}")
    
    def __repr__(self):
        if self.match_type == '1v1':
            participants = f"Player Alpha: {self.player_alpha.player_name}, Player Beta: {self.player_beta.player_name}"
        elif self.match_type == '3v3':
            participants = f"Team Alpha: {self.team_alpha.team_name}, Team Beta: {self.team_beta.team_name}"
        else:
            participants = "Unknown participants"
        
        return (f"Match({self.match_id}, Type: {self.match_type}, Date: {self.match_date}, "
                f"Status: {self.match_status}, Winner: {self.match_winner}, Loser: {self.match_loser}, "
                f"Map: {self.match_map}, Keyword: {self.keyword}, {participants})")

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
    
    def __str__(self):
        return '\n'.join([str(match) for match in self.matches])
    
    def __len__(self):
        return len(self.matches)

    def __repr__(self):
        return '\n'.join([repr(match) for match in self.matches])

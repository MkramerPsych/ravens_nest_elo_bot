'''
ELO match queue system for the Ravens Nest.
Designed by Ahasuerus for Armored Scrims Server

'''
from ravens_nest.elo_core import *
from rich.table import Table
from rich.console import Console
import random

#def get_valid_match_from_queue(queue: MatchQueue):
    # if a player is at ELO 700 (C), they can only match
    # assume 50 person queue
    # compute every combination of 3 player teams and get their average ELO
    # (modify for party queue by grouping by party ID, calculating ELO for the party as a weighted average of party members)
    # order the resulting teams by the spread of their ELO amongst the roster (descending)
    # for the smallest spread team, iterate across remaining teams and find the smallest spread team that is within a
    # given ELO difference of the first team
        # if true:
            # make those two teams a match
        # if false:
            # increment the elo differerence between teams and try again


class MatchQueue:
    queue_type = str # '1v1', '3v3 flex', '3v3 registered' 
    players = list[(Player, bool, int)] # list of tuples of players, team names (if 3s), and whether they have rank restrictions, and party/team ID (if any)
    
    def __init__(self, queue_type):
        '''
        Initialize a MatchQueue object. Should only be called once
        to create a queue for a specific queue type.
        '''
        if queue_type not in ['1v1', '3v3 flex', '3v3 reg']: # TODO: make this a button once I figure out how discord does it
            raise ValueError("queue_type must be '1v1', '3v3 flex', or '3v3 reg'")
        self.queue_type = queue_type
        self.players = []

    def enqueue_player(self, player: Player, rank_restriction: bool = False, party_id: Optional[int] = None):
        if player in [p[0] for p in self.players]:
            raise ValueError("Player already in queue")
        else:
            if self.queue_type in ['1v1', '3v3 flex']:
                self.players.append((player, rank_restriction, party_id))
            else:
                raise ValueError("queue_type must be '1v1' or '3v3 flex' to queue solo")
        
    def enqueue_party(self, party: list[Player], rank_restriction: bool = False):
        '''
        Enqueue a party of players. This ensures all party members will queue together.
        '''
        if self.queue_type == '3v3 reg':
            raise ValueError("Cannot enqueue parties in 3v3 registered queue")
        else:
            party_id = random.randint(100000000000, 999999999999)
            for player in party:
                self.enqueue_player(player, rank_restriction, party_id)

    def enqueue_team(self, team: team, rank_restriction: bool = False):
        '''
        Enqueue a team. This ensures all team members will queue together.
        '''
        if self.queue_type != '3v3 reg':
            raise ValueError("Can only enqueue teams in 3v3 reg format")
        else:
            party_id = team.team_name
            for player in team.roster: # append each player to the queue in a party as a team
                self.players.append((player, rank_restriction, party_id))

    def dequeue_player(self, player: Player, rank_restriction: bool = False):
        self.players.remove((player, rank_restriction))

    def get_queue(self):
        return self.players
    
    def queue_match(self):
        '''
        check to see if queueing conditions are satisfied, and if so, create a match and 
        remove those players from theplayer queue.
        '''
        if self.queue_type == '3v3 flex': # check if there are enough players to make a 3s match
            pass
        elif self.queue_type == '3v3 reg': # check if there are enough players to make a 1s match
            pass
        else: # 1v1s
            pass
        
    def __len__(self):
        return len(self.players)
    
    def __str__(self):
        console = Console(force_terminal=False)
        table = Table(title=f"{self.queue_type.upper()} Queue: {len(self)} players currently in queue")

        table.add_column("Player Name", justify="left")
        table.add_column("ELO", justify="right")
        table.add_column("Rank Restriction", justify="left")
        if self.queue_type in ['3v3 flex', '3v3 reg']:
            table.add_column("Team", justify="left")
            table.add_column("Party ID", justify="right")

        for player, rank_restriction, party_id in self.players:
            if self.queue_type == '3v3 flex':
                table.add_row(
                    player.player_name,
                    str(player.player_teams_ELO),
                    f"{player.player_teams_rank}+" if rank_restriction else "None",
                    player.player_team,
                    str(party_id)
                )
            elif self.queue_type == '3v3 reg':
                team = teams_db.get_team(player.player_team)
                table.add_row(
                    player.player_name,
                    str(team.team_ELO),
                    f"{team.teams_rank}+" if rank_restriction else "None",
                    player.team_name,
                    str(party_id)
                )
            else:  # 1v1
                table.add_row(
                    player.player_name,
                    str(player.player_singles_ELO),
                    f"{player.player_singles_rank}+" if rank_restriction else "None"
                )

        with console.capture() as capture:
            console.print(table)
        table_output = capture.get()
        return f"```{table_output}```"
    
    def __repr__(self) -> str:
        return self.__str__()
    

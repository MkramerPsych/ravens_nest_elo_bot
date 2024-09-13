'''
ELO match queue system for the Ravens Nest.
Designed by Ahasuerus for Armored Scrims Server

'''
from ravens_nest.elo_core import *
from rich.table import Table
from rich.console import Console

class MatchQueue:
    queue_type = str # '1v1' or '3v3'
    players = list[(Player, bool, int)] # list of tuples of players, team names (if 3s), and whether they have rank restrictions, and party/team ID (if any)
    
    def __init__(self, queue_type):
        '''
        Initialize a MatchQueue object. Should only be called once
        to create a queue for a specific queue type.
        '''
        if queue_type not in ['1v1', '3v3']: # TODO: make this a button once I figure out how discord does it
            raise ValueError("queue_type must be '1v1' or '3v3'")
        self.queue_type = queue_type
        self.players = []

    def enqueue_player(self, player: Player, rank_restriction: bool = False, party_id: Optional[int] = None):
        if player in [p[0] for p in self.players]:
            raise ValueError("Player already in queue")
        else:
            if self.queue_type == '3v3':
                self.players.append((player, rank_restriction, party_id))
            elif self.queue_type == '1v1':
                self.players.append((player, rank_restriction, party_id))
            else:
                raise ValueError("queue_type must be '1v1' or '3v3'")
        
    def enqueue_party(self, party: list[Player], rank_restriction: bool = False):
        '''
        Enqueue a party of players. This ensures all party members will queue together.
        '''
        # party_id = abs(int(str(hash())[:8]))
        for player in party:
            pass

    def enqueue_team(self, team: team, rank_restriction: bool = False):
        '''
        Enqueue a team. This ensures all team members will queue together.
        '''
        if self.queue_type != '3v3':
            raise ValueError("Can only enqueue teams in 3v3 queue")
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
        remove those players from the queue.
        '''
        if self.queue_type == '3v3': # check if there are enough players to make a 3s match
            pass
        else: # check if there are enough players to make a 1s match
            pass
        
    def __len__(self):
        return len(self.players)
    
    def __str__(self):
        console = Console(force_terminal=False)
        table = Table(title=f"{self.queue_type.upper()} Queue: {len(self)} players currently in queue")

        if self.queue_type == '3v3':
            table.add_column("Player Name", justify="left")
            table.add_column("ELO", justify="right")
            table.add_column("Team", justify="left")
            table.add_column("Rank Restriction", justify="left")
            table.add_column("Party ID", justify="right")

            for player, rank_restriction, party_id in self.players:
                table.add_row(
                    player.player_name,
                    str(player.player_ELO),
                    player.player_team,
                    f"{player.player_rank}+" if rank_restriction else "None",
                    str(party_id)
                )
        elif self.queue_type == '1v1':
            table.add_column("Player Name", justify="left")
            table.add_column("ELO", justify="right")
            table.add_column("Rank Restriction", justify="left")

            for player, rank_restriction, _ in self.players:
                table.add_row(
                    player.player_name,
                    str(player.player_ELO),
                    f"{player.player_rank}+" if rank_restriction else "None"
                )

        with console.capture() as capture:
            console.print(table)
        table_output = capture.get()
        return f"```{table_output}```"
    
    def __repr__(self) -> str:
        return self.__str__()
    

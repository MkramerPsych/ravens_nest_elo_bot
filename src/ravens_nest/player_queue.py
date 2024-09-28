'''
ELO match queue system for the Ravens Nest.
Designed by Ahasuerus for Armored Scrims Server

'''
from ravens_nest.elo_core import *
from rich.table import Table
from rich.console import Console
import random

class MatchQueue:
    queue_type = str # '1v1', '3v3 flex', '3v3 registered'
    player_pool = players_db # initialize the database for individual players
    teams_pool = teams_db # initialize the database for registered teams
    queued_players = list[(Player, bool, int)] # list of tuples containing player, rank restriction, party ID
    queued_teams = list[(team, bool, int)] # list of tuples containing team, rank restriction, party ID

    def __init__(self, queue_type, player_pool, teams_pool):
        '''
        Initialize a MatchQueue object. Should only be called once
        to create a queue for a specific queue type.
        '''
        if queue_type not in ['1v1', '3v3 flex', '3v3 reg']: # TODO: make this a button once I figure out how discord does it
            raise ValueError("queue_type must be '1v1', '3v3 flex', or '3v3 reg'")
        self.queue_type = queue_type
        self.player_pool = player_pool
        self.teams_pool = teams_pool
        self.queued_players = []
        self.queued_teams = []

    def enqueue_player(self, player: Player, rank_restriction: bool = False, party_id: Optional[int] = None):
        if player in [p[0] for p in self.queued_players]:
            raise ValueError("Player already in queue")
        else:
            if self.queue_type in ['1v1', '3v3 flex']:
                self.queued_players.append((player, rank_restriction, party_id))
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
            self.queued_teams.append((team, rank_restriction, party_id))

    def dequeue_player(self, player: Player):
        for queued_player in self.queued_players:
            if queued_player[0] == player:
                self.queued_players.remove(queued_player)
                return
        raise ValueError(f"Player {player.player_name} not found in queue")

    def dequeue_team(self, team: team, rank_restriction: bool = False):
        for queued_team in self.queued_teams:
            if queued_team[0] == team:
                self.queued_teams.remove(queued_team)
                return
        raise ValueError(f"Team {team.team_name} not found in queue")

    def get_queue(self):
        if self.queue_type == '3v3 reg':
            return self.queued_teams
        else:
            return self.queued_players

    def _find_1v1_match(self, base_ELO_diff: int, max_ELO_diff: int):
        # until there aren't enough players to make a match
        while len(self.queued_players) >= 2:
            # initialize ELO_diff to the base value
            ELO_diff = base_ELO_diff
            ELO_diff_increment = base_ELO_diff

            # iterate through the queue
            for i, (player1, rank_restriction1, _) in enumerate(self.queued_players):
                while ELO_diff <= max_ELO_diff:
                    # iterate through the remaining players in the queue
                    for j, (player2, rank_restriction2, _) in enumerate(self.queued_players[i+1:], start=i+1):
                        # check if the ELO difference between the two players is within the given range
                        if abs(player1.player_singles_ELO - player2.player_singles_ELO) <= ELO_diff:
                            # check if the rank restrictions are met
                            if (not rank_restriction1 or (rank_restriction1 and player2.player_singles_rank <= player1.player_singles_rank)) and \
                               (not rank_restriction2 or (rank_restriction2 and player1.player_singles_rank <= player2.player_singles_rank)):
                                # if so, queue up a match between the two players
                                print(f"Match found: {player1.player_name} ({player1.player_singles_ELO}) and {player2.player_name} ({player2.player_singles_ELO})")
                                queued_match = match(player_alpha=player1, player_beta=player2, match_type='1v1')
                                # pop the combatants players from the queue
                                self.queued_players.pop(j)
                                self.queued_players.pop(i)
                                return queued_match
                    # if no match is found, increment the ELO difference and try again
                    ELO_diff += ELO_diff_increment
                ELO_diff = base_ELO_diff  # Reset ELO_diff for the next player
        print("No valid matches currently possible")
        return None

    def _find_3v3_reg_match(self, base_ELO_diff: int, max_ELO_diff: int):
        while len(self.queued_teams) >= 2:
            ELO_diff = base_ELO_diff
            ELO_diff_increment = base_ELO_diff

            for i, (team1, rank_restriction1, _) in enumerate(self.queued_teams):
                while ELO_diff <= max_ELO_diff:
                    for j, (team2, rank_restriction2, _) in enumerate(self.queued_teams[i+1:], start=i+1):
                        if abs(team1.team_ELO - team2.team_ELO) <= ELO_diff:
                            if (not rank_restriction1 or (rank_restriction1 and team2.team_rank <= team1.team_rank)) and \
                               (not rank_restriction2 or (rank_restriction2 and team1.team_rank <= team2.team_rank)):
                                print(f"Match found: {team1.team_name} ({team1.team_ELO}) and {team2.team_name} ({team2.team_ELO})")
                                queued_match = match(team_alpha=team1, team_beta=team2, match_type='3v3 reg')
                                self.queued_teams.pop(j)
                                self.queued_teams.pop(i)
                                return queued_match
                    ELO_diff += ELO_diff_increment
                ELO_diff = base_ELO_diff
        print("No valid matches currently possible")
        return None

    def _find_3v3_flex_match(self, base_ELO_diff: int, max_ELO_diff: int):
        while len(self.queued_players) >= 6:
            ELO_diff = base_ELO_diff
            possible_teams = []
            used_players = set()

            # Create all valid 3-player teams
            for i, (player1, _, party_id1) in enumerate(self.queued_players):
                if player1 in used_players:
                    continue

                # Party members should stay together
                if party_id1 is not None:
                    party_members = [p for p, _, party_id in self.queued_players if party_id == party_id1]
                    if len(party_members) == 3:
                        team_mean_ELO = sum(p.player_teams_ELO for p in party_members) / 3
                        possible_teams.append((party_members, team_mean_ELO, 0))
                        used_players.update(party_members)
                else:
                    for j, (player2, _, party_id2) in enumerate(self.queued_players[i+1:], start=i+1):
                        if player2 in used_players:
                            continue
                        for k, (player3, _, party_id3) in enumerate(self.queued_players[j+1:], start=j+1):
                            if player3 in used_players:
                                continue

                            if party_id1 == party_id2 == party_id3 or (party_id1 is None and party_id2 is None and party_id3 is None):
                                team = [player1, player2, player3]
                                team_mean_ELO = sum(p.player_teams_ELO for p in team) / 3
                                team_range_ELO = max(p.player_teams_ELO for p in team) - min(p.player_teams_ELO for p in team)
                                possible_teams.append((team, team_mean_ELO, team_range_ELO))

            # Sort teams by ELO range
            possible_teams.sort(key=lambda x: x[2], reverse=True)

            # Try finding a valid match within ELO_diff
            while ELO_diff <= max_ELO_diff:
                for i, (team1, mean_ELO1, _) in enumerate(possible_teams):
                    for j, (team2, mean_ELO2, _) in enumerate(possible_teams[i+1:], start=i+1):
                        # Ensure no overlapping players
                        if not any(player in team1 for player in team2):
                            if abs(mean_ELO1 - mean_ELO2) <= ELO_diff:
                                team1_names = [p.player_name for p in team1]
                                team2_names = [p.player_name for p in team2]
                                print(f"Match found: {team1_names} and {team2_names}")
                                queued_match = match(team_alpha=team1, team_beta=team2, match_type='3v3 flex')

                                # Remove the players from the queue
                                self.queued_players = [p for p in self.queued_players if p[0] not in team1 + team2]
                                return queued_match
                ELO_diff += base_ELO_diff

            print("No valid matches found within current ELO range.")
            return None


    def get_valid_match_from_queue(self, base_ELO_diff: int = 10, max_ELO_diff: int = 250):
        '''
        Returns a valid match from the queue based on the queue type
        '''
        if self.queue_type == '1v1':
            return self._find_1v1_match(base_ELO_diff, max_ELO_diff)
        elif self.queue_type == '3v3 flex':
            return self._find_3v3_flex_match(base_ELO_diff, max_ELO_diff)
        elif self.queue_type == '3v3 reg':
            return self._find_3v3_reg_match(base_ELO_diff, max_ELO_diff)
        else:
            raise ValueError("Invalid match type: must be '1v1', '3v3 flex', or '3v3 reg'")

    def __len__(self):
        if self.queue_type == '3v3 reg':
            return len(self.queued_teams)
        else:
            return len(self.queued_players)

    def __str__(self):
        console = Console(force_terminal=False)
        if self.queue_type == '3v3 reg':
            table = Table(title=f"{self.queue_type.upper()} Queue: {len(self)} teams currently in queue")
        else:
            table = Table(title=f"{self.queue_type.upper()} Queue: {len(self)} players currently in queue")

        if self.queue_type == '1v1':
            table.add_column("Player Name", justify="left")
            table.add_column("ELO", justify="right")
            table.add_column("Rank Restriction", justify="left")
            for player, rank_restriction, _ in self.queued_players:
                table.add_row(
                    player.player_name,
                    str(player.player_singles_ELO),
                    f"{player.player_singles_rank}+" if rank_restriction else "None"
                )

        elif self.queue_type == '3v3 flex':
            table.add_column("Player Name", justify="left")
            table.add_column("ELO", justify="right")
            table.add_column("Rank Restriction", justify="left")
            table.add_column("Team", justify="left")
            table.add_column("Party ID", justify="right")
            for player, rank_restriction, party_id in self.queued_players:
                table.add_row(
                    player.player_name,
                    str(player.player_teams_ELO),
                    f"{player.player_teams_rank}+" if rank_restriction else "None",
                    player.player_team,
                    str(party_id)
                )

        elif self.queue_type == '3v3 reg':
            table.add_column("Team Name", justify="left")
            table.add_column("Team ELO", justify="right")
            table.add_column("Rank Restriction", justify="left")
            for team, rank_restriction, party_id in self.queued_teams:
                table.add_row(
                    team.team_name,
                    str(team.team_ELO),
                    str(rank_restriction) if rank_restriction else "None",
                )

        with console.capture() as capture:
            console.print(table)
        table_output = capture.get()
        return f"```{table_output}```"

    def __repr__(self) -> str:
        return self.__str__()

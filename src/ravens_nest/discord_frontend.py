'''
Discord interaction frontend for ravens_nest bot
Designed by Ahasuerus for Armored Scrims Server
'''
import os
import discord
from discord import app_commands
from ravens_nest.elo_core import *
from ravens_nest.player_queue import *

# Download link for the bot - https://discord.com/oauth2/authorize?client_id=1283690474653220875 # 

# DISCORD BOT SETUP # 

# Create a client instance with the necessary intents
intents = discord.Intents.default()
intents.presences = True
intents.messages = True
client = discord.Client(intents=intents)

# Create a tree to register and manage slash commands
tree = app_commands.CommandTree(client)

# establish all databases and queues #
player_registry = players_db() # initialize the database
teams_registry = teams_db() # initialize the database
matches_db = match_db() # initialize the match database
ones_queue = MatchQueue('1v1')
threes_queue = MatchQueue('3v3')

# DISCORD BOT EVENTS - MAIN FUNCTIONS # 

# Event triggered when the bot is ready # 
@client.event
async def on_ready():
    '''
    Event triggered when the bot is ready. Prints to log.
    '''
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    await tree.sync()  # Sync the slash commands with Discord
    print('Slash commands synced.')
    # Set the bot's status to online and set a custom activity
    activity = discord.Game(name="Managing the Ravens Nest")
    await client.change_presence(status=discord.Status.online, activity=activity)
    print('Bot status set to online with custom activity.')
    print('Ready to receive commands.')

# ONBOARDING COMMANDS #
@tree.command(name="onboard_player", description="Onboards a player to the database.")
async def onboard_player(interaction: discord.Interaction, player_name: str, player_team: Optional[str] = None):
    '''
    Onboards a player to the database.
    '''
    # Check if the player is already in the database
    if player_registry.get_player(player_name):
        await interaction.response.send_message(f"Player {player_name} is already in the database.")
    else:
        # Add the player to the database
        new_player = Player(player_name, player_team)
        player_registry.add_player(new_player)
        if player_team:
            await interaction.response.send_message(f"Player {player_name} has been onboarded to team {player_team}. Welcome to the Ravens Nest.")
            print(f'Onboard player command used to onboard player {player_name} to team {player_team}.')
        else:
            await interaction.response.send_message(f"Player {player_name} has been onboarded. Welcome to the Ravens Nest.")
            print(f"Onboard player command used to onboard player {player_name}.")

@tree.command(name="onboard_team", description="Onboards a team to the database.")
async def onboard_team(interaction: discord.Interaction, team_name: str, player1: str, player2: str, player3: str):
    '''
    Onboards a team to the database.
    '''
    roster = [player_registry.get_player(player1), 
              player_registry.get_player(player2),
              player_registry.get_player(player3)] # to avoid discord type complaining
    
    if any(player is None for player in roster):
        missing_players = [player_name for player_name, player in zip([player1, player2, player3], roster) if player is None]
        await interaction.response.send_message(f"Player(s): [{', '.join(missing_players)}] is/are not in the database.")
        print(f"Onboard team command used to onboard team {team_name}, but player(s) {', '.join(missing_players)} is/are not in the database.")
        return
    
    for player in roster: # assign team name to roster players
        player.player_team = team_name

    # Check if the team is already in the database
    if teams_registry.get_team(team_name):
        await interaction.response.send_message(f"Team {team_name} is already in the database.")
    else:
        # Add the team to the database
        new_team = team(team_name, roster)
        teams_registry.add_team(new_team)
        await interaction.response.send_message(f"Team {team_name} has been onboarded. Welcome to the Ravens Nest.")
        print(f"Onboard team command used to onboard team {team_name}.")

@tree.command(name="remove_player", description="Removes a player from the database.")
async def remove_player(interaction: discord.Interaction, player_name: str):
    '''
    Removes a player from the database.
    '''
    player = player_registry.get_player(player_name)
    if player:
        player_registry.remove_player(player.player_name)
        await interaction.response.send_message(f"Player {player_name} has been removed from the database.")
        print(f"Remove player command used to remove player {player_name}.")
    else:
        await interaction.response.send_message(f"Player {player_name} is not in the database.")
        print(f"Remove player command used to remove player {player_name}, but player is not in the database.")

@tree.command(name="remove_team", description="Removes a team from the database.")
async def remove_team(interaction: discord.Interaction, team_name: str):
    '''
    Removes a team from the database.
    '''
    team = teams_registry.get_team(team_name)
    if team:
        teams_registry.remove_team(team)
        await interaction.response.send_message(f"Team {team_name} has been removed from the database.")
        print(f"Remove team command used to remove team {team_name}.")
    else:
        await interaction.response.send_message(f"Team {team_name} is not in the database.")
        print(f"Remove team command used to remove team {team_name}, but team is not in the database.")

@tree.command(name="playerstats", description="Views the stats of a player.")
async def playerstats(interaction: discord.Interaction, player_name: str):
    '''
    Views the stats of a player.
    '''
    player = player_registry.get_player(player_name)
    if player:
        await interaction.response.send_message(f"{player}")
    else:
        await interaction.response.send_message(f"Player {player_name} is not in the database.")
    print(f"Playerstats command used to view player {player_name}.") 

@tree.command(name="teamstats", description="Views the stats of a team.")
async def teamstats(interaction: discord.Interaction, team_name: str):
    '''
    Views the stats of a team.
    '''
    team = teams_registry.get_team(team_name)
    if team:
        await interaction.response.send_message(f"{team}")
    else:
        await interaction.response.send_message(f"Team {team_name} is not in the database.")
    print(f"Teamstats command used to view team {team_name}.")

# QUEUE COMMANDS #
@tree.command(name="solo_queue", description="Adds a player to a match queue.")
async def solo_queue(interaction: discord.Interaction, player_name: str, match_type: str, rank_restriction: Optional[bool] = False):
    '''
    Adds a player to a match queue.
    '''
    player = player_registry.get_player(player_name)
    if player:
        if match_type == '1v1':
            ones_queue.enqueue_player(player, rank_restriction, party_id=None)
            await interaction.response.send_message(f"Player {player_name} has been added to the 1v1 match queue.")
            print(f"solo_queue command used to add player {player_name} to the 1v1 match queue.")
        elif match_type == '3v3':
            threes_queue.enqueue_player(player, rank_restriction, party_id=None)
            await interaction.response.send_message(f"Player {player_name} has been added to the 3v3 match queue.")
            print(f"solo_queue command used to add player {player_name} to the 3v3 match queue.")
        else:
            await interaction.response.send_message("match_type must be '1v1' or '3v3'.")
            print(f"solo_queue command used to add player {player_name} to the match queue, but match_type is not '1v1' or '3v3'.")
    else:
        await interaction.response.send_message(f"Player {player_name} is not in the database.")
        print(f"solo_queue command used to add player {player_name} to match queue, but player is not in the database.")

#@tree.command(name="dequeue_player", description="Removes a player from any match queue.")

# @tree.command(name="queue_with_party", description="Adds a party of players to a match queue.")
# async def queue_with_party(interaction: discord.Interaction, match_type: str, party: list[str]):
#     '''
#     Adds a party of players to a match queue.
#     '''
#     if match_type not in ['1v1', '3v3']:
#         await interaction.response.send_message("match_type must be '1v1' or '3v3'.")
#         print(f"queue_with_party command used to add a party of players to a match queue, but match_type is not '1v1' or '3v3'.")
#         return
#     else:
#         pass

@tree.command(name="view_ones_queue", description="Views the 1v1 match queue.")
async def view_ones_queue(interaction: discord.Interaction):
    '''
    Views the 1v1 match queue.
    '''
    await interaction.response.send_message(f"{ones_queue}")
    print(f"view_ones_queue command used to view 1v1 match queue.")

@tree.command(name="view_threes_queue", description="Views the 3v3 match queue.")
async def view_threes_queue(interaction: discord.Interaction):
    '''
    Views the 3v3 match queue.
    '''
    await interaction.response.send_message(f"{threes_queue}")
    print(f"view_threes_queue command used to view 3v3 match queue.")

# MATCHING SLASH COMMANDS #
@tree.command(name="single_match_setup", description="Creates a match between two players.")
async def single_match_setup(interaction: discord.Interaction, player1: str, player2: str):
    '''
    Creates a match between two players.
    '''
    # Check if the players are in the database
    alpha = player_registry.get_player(player1)
    beta = player_registry.get_player(player2)

    if alpha and beta:
        # Create a match
        new_match = match(match_type='1v1', player_alpha=alpha, player_beta=beta)
        new_match.setup_match_parameters()
        matches_db.add_match(new_match)
        await interaction.response.send_message(f'Match setup for match `{new_match.match_id}` complete. Remember to create a 2 person lobby, rotation locked, with a 5 minute match timer. Use Map: {new_match.match_map}, Use Keyword: {new_match.keyword}')
        print(f'single_match_setup command used to create a match between {player1} and {player2}.')
    else:
        await interaction.response.send_message(f"Players {player1} and {player2} are not in the database.")
        print(f"single_match_setup command used to create a match between {player1} and {player2}, but one or both players are not in the database.")

@tree.command(name="team_match_setup", description="Creates a match between two teams.")
async def team_match_setup(interaction: discord.Interaction, team1: str, team2: str):
    '''
    Creates a match between two teams.
    '''
    # Check if the teams are in the database
    alpha_squad = teams_registry.get_team(team1)
    beta_squad = teams_registry.get_team(team2)

    if alpha_squad and beta_squad:
        # Create a match
        new_match = match(match_type='3v3', team_alpha=alpha_squad, team_beta=beta_squad)
        new_match.setup_match_parameters()
        matches_db.add_match(new_match)
        await interaction.response.send_message(f'Match setup for match `{new_match.match_id}` complete. Remember to create a 9 person lobby, rotation locked, with a 5 minute match timer. Use Map: {new_match.match_map}, Use Keyword: {new_match.keyword}')
        print(f'team_match_setup command used to create a match between {team1} and {team2}.')
    else:
        await interaction.response.send_message(f"Teams {team1} and {team2} are not in the database.")
        print(f"team_match_setup command used to create a match between {team1} and {team2}, but one or both teams are not in the database.")

@tree.command(name="cancel_match", description="Cancels a match.")
async def cancel_match(interaction: discord.Interaction, match_id: int):
    '''
    Cancels a match.
    '''
    match = matches_db.get_match(match_id)
    if match:
        matches_db.remove_match(match)
        await interaction.response.send_message(f"Match {match_id} has been cancelled and will not affect statistics.")
        print(f"cancel_match command used to cancel match {match_id}.")
    else:
        await interaction.response.send_message(f"Match {match_id} is not in the database.")
        print(f"cancel_match command used to cancel match {match_id}, but match is not in the database.")

@tree.command(name="match_results", description="Records the results of a match.")
async def match_results(interaction: discord.Interaction, match_id: int, win: str, lose: str):
    '''
    Records the results of a match.
    '''
    # Check if the match is in the database
    match = matches_db.get_match(match_id)
    if match:
        if match.match_status == "completed":
            await interaction.response.send_message(f"Match {match_id} has already been completed.")
            print(f"match_results command used to record results of match {match_id}, but match has already been completed.")
            return
        else:
            if match.match_type == '1v1':
                winner = player_registry.get_player(win)
                loser = player_registry.get_player(lose)
                match.report_match_results(winner, loser)
                await interaction.response.send_message(f"Match {match_id} results recorded. {winner.player_name} wins.")
            else:
                winner = teams_registry.get_team(win)
                loser = teams_registry.get_team(lose)
                match.report_match_results(winner, loser)
                await interaction.response.send_message(f"Match {match_id} results recorded. {winner.team_name} wins.")
            print(f"match_results command used to record results of match {match_id}.")

@tree.command(name="match_summary", description="Views the status of a match.")
async def match_summary(interaction: discord.Interaction, match_id: int):
    '''
    Views the status of a match.
    '''
    match = matches_db.get_match(match_id)
    if match:
        await interaction.response.send_message(f"{match}")
    else:
        await interaction.response.send_message(f"Match {match_id} is not in the database.")
    print(f"match_summary command used to view match {match_id}.")

# HELP COMMAND #
@tree.command(name="help", description="Displays all commands available.")
async def help(interaction: discord.Interaction):
    '''
    Displays all commands available.
    '''
    help_message = '''
    **Ravens Nest Bot Commands**
    `/onboard_player [player_name] [player_team]` - Onboards a player to the database.
    `/onboard_team [team_name] [player1] [player2] [player3]` - Onboards a team to the database.
    `/remove_player [player_name]` - Removes a player from the database.
    `/remove_team [team_name]` - Removes a team from the database.
    `/playerstats [player_name]` - Views the stats of a player.
    `/teamstats [team_name]` - Views the stats of a team.
    `/single_match_setup [player1] [player2]` - Creates a match between two players.
    `/team_match_setup [team1] [team2]` - Creates a match between two teams.
    `/match_results [match_id] [win] [lose]` - Records the results of a match.
    `/match_summary [match_id]` - Views the status of a match.
    '''
    await interaction.response.send_message(help_message)
    print(f"Help command used to display all available commands.")


# Start the bot # 
bot_token = os.environ.get('DISCORD_BOT_TOKEN')

if bot_token:
    print("Bot token found, initializing bot.")
    client.run(bot_token) # activate the Ravens Nest bot
else:
    raise ValueError("Bot token not found. Please set the DISCORD_BOT_TOKEN environment variable.")


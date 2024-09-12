'''
Discord interaction frontend for ravens_nest bot
Designed by Ahasuerus for Armored Scrims Server
'''
import discord
import os
from discord import app_commands
from ravens_nest.elo_core import *
from ravens_nest.player_queue import *

# Download link for the bot - https://discord.com/oauth2/authorize?client_id=1283690474653220875 # 

# DISCORD BOT SETUP # 

# Create a client instance with the necessary intents
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Create a tree to register and manage slash commands
tree = app_commands.CommandTree(client)

player_registry = players_db() # initialize the database
teams_registry = teams_db() # initialize the database
matches_db = match_db() # initialize the match database

# DISCORD BOT EVENTS - MAIN FUNCTIONS # 

# Event triggered when the bot is ready
@client.event
async def on_ready():
    '''
    Event triggered when the bot is ready. Prints to log.
    '''
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    await tree.sync()  # Sync the slash commands with Discord
    print('Slash commands synced.')


# Define the /onboard_player slash command
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
        await interaction.response.send_message(f"Player(s): {', '.join(missing_players)} is/are not in the database.")
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

# Define the /queue slash command

# Define the /match command
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
        await interaction.response.send_message(f'Match setup for match `{new_match.match_id}` complete. Use Map: {new_match.match_map}, Use Keyword: {new_match.keyword}')
        print(f'team_match_setup command used to create a match between {team1} and {team2}.')
    else:
        await interaction.response.send_message(f"Teams {team1} and {team2} are not in the database.")
        print(f"team_match_setup command used to create a match between {team1} and {team2}, but one or both teams are not in the database.")

@tree.command(name="match_results", description="Records the results of a match.")
async def match_results(interaction: discord.Interaction, match_id: int, win: str, lose: str):
    '''
    Records the results of a match.
    '''
    winner = teams_registry.get_team(win)
    loser = teams_registry.get_team(lose)
    # Check if the match is in the database
    match = matches_db.get_match(match_id)
    if match:
        if match.match_status == "completed":
            await interaction.response.send_message(f"Match {match_id} has already been completed.")
            print(f"match_results command used to record results of match {match_id}, but match has already been completed.")
            return
        else:
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

# Start the bot
bot_token = os.environ.get('DISCORD_BOT_TOKEN')

if bot_token:
    print("Bot token found, initializing bot.")
    client.run(bot_token)
else:
    raise ValueError("Bot token not found. Please set the DISCORD_BOT_TOKEN environment variable.")


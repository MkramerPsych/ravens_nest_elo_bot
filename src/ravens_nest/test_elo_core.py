'''
Testing cases for core ELO logic
Designed by Ahasuerus for Armored Scrims Server
'''
from ravens_nest.elo_core import *

# generate databases #
player_registry = players_db() # initialize the database for individual players
teams_registry = teams_db(player_registry) # initialize the database for registered teams
random_teams_registry = teams_db(player_registry) # initialize the database for non-registered teams
matches_db = match_db() # initialize the match logging database


# add some players #
hooli = Player('Hooli', 'Koolish')
kraydle = Player('Kraydle', 'Koolish')
fish = Player('Fish', 'Koolish')
ramenrook = Player('RamenRook', 'RnS')
risa = Player('Risa', 'RnS')
sabbath = Player('Sabbath', 'team1')
Prism = Player('Prism', 'team2')
Hai_Yena = Player('Hai_Yena', 'team2')
Cicada = Player('Cicada', 'team2')
Neer_do_well = Player('Neer_do_well', 'team1')
basterisk = Player('Basterisk', 'team1')

# onboard them to the database #
player_registry.add_players([hooli, kraydle, fish, ramenrook, risa, sabbath, Prism, Hai_Yena, Cicada, Neer_do_well, basterisk])

# add some of them to teams #
team2 = team('team2',[Prism, Hai_Yena, Cicada])
team1 = team('team1',[Neer_do_well, sabbath, basterisk])
teams_registry.add_team(team1)
teams_registry.add_team(team2)

# lets have a 3v3 reg match between our two teams #
test_3s_match = match('3v3 reg', team_alpha=team1, team_beta=team2)
test_3s_match.setup_match_parameters()
test_3s_match.report_match_results(team2, team1)
matches_db.add_match(test_3s_match)

# lets have a 3v3 flex match between two queued random teams #
team_alpha = [Prism, Hai_Yena, Cicada]
team_beta = [Neer_do_well, sabbath, basterisk]
test_3s_flex_match = match('3v3 flex', team_alpha, team_beta)
test_3s_flex_match.setup_match_parameters()
test_3s_flex_match.report_match_results(team_alpha, team_beta)
matches_db.add_match(test_3s_flex_match)

# and some ones matches as well
test_1v1_match = match('1v1', hooli, kraydle)
test_1v1_match.setup_match_parameters()
test_1v1_match.report_match_results(hooli, kraydle)
matches_db.add_match(test_1v1_match)

test_1v1_match = match('1v1', hooli, fish)
test_1v1_match.setup_match_parameters()
test_1v1_match.report_match_results(hooli, fish)
matches_db.add_match(test_1v1_match)

test_1v1_match = match('1v1', hooli, ramenrook)
test_1v1_match.setup_match_parameters()
test_1v1_match.report_match_results(hooli, ramenrook)
matches_db.add_match(test_1v1_match)

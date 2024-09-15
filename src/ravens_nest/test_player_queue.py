# test functions #
from ravens_nest.elo_core import *
from ravens_nest.player_queue import *

# set up databases #
player_registry = players_db() # initialize the database for individual players
teams_registry = teams_db() # initialize the database for registered teams
matches_db = match_db() # initialize the match logging database

# set up queues 
ones_queue = MatchQueue('1v1', player_registry, teams_registry)
threes_reg_queue = MatchQueue('3v3 reg', player_registry, teams_registry)
threes_flex_queue = MatchQueue('3v3 flex', player_registry, teams_registry)

# add some players
hooli = Player('Hooli', 'Koolish')
kraydle = Player('Kraydle', 'Koolish')
fish = Player('Fish', 'Koolish')
ramenrook = Player('RamenRook', 'RnS')
risa = Player('Risa', 'RnS')
sabbath = Player('Sabbath', 'RnS')
Prism = Player('Prism')
Hai_Yena = Player('Hai_Yena')
Cicada = Player('Cicada')

# onboard them to the database
player_registry.add_players([hooli, kraydle, fish, ramenrook, risa, sabbath, Prism, Hai_Yena, Cicada])

# add some teams
koolish = team('Koolish', [hooli, kraydle, fish])
rns = team('RnS', [ramenrook, risa, sabbath])

# onboard them to the database
teams_registry.add_team(koolish)
teams_registry.add_team(rns)

# test ones queue logic
ones_queue.enqueue_player(hooli)
ones_queue.enqueue_player(kraydle)
ones_queue.enqueue_player(fish)
ones_queue.enqueue_player(ramenrook)
ones_queue.enqueue_player(risa)
ones_queue.enqueue_player(sabbath)
ones_queue.enqueue_player(Prism)
ones_queue.enqueue_player(Hai_Yena)
ones_queue.enqueue_player(Cicada)


# test threes queue logic
threes_reg_queue.enqueue_team(koolish)
threes_reg_queue.enqueue_team(rns)

# test threes flex queue logic
threes_flex_queue.enqueue_player(hooli)
threes_flex_queue.enqueue_player(kraydle)
threes_flex_queue.enqueue_player(fish)
threes_flex_queue.enqueue_party([Prism, Hai_Yena, Cicada])
team_alpha = [hooli, kraydle, fish]
team_beta = [Prism, Hai_Yena, Cicada]

# have a simulated 3v3 flex match between teams 
test_3s_flex_match = match('3v3 flex', team_alpha, team_beta)
test_3s_flex_match.setup_match_parameters()
test_3s_flex_match.report_match_results(team_alpha, team_beta)
matches_db.add_match(test_3s_flex_match)

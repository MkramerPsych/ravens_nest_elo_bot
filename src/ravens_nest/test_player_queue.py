# test functions #
from ravens_nest.elo_core import *
from ravens_nest.player_queue import *

# set up queues 
ones_queue = MatchQueue('1v1')
threes_queue = MatchQueue('3v3')

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

# add some teams
koolish = team('Koolish', [hooli, kraydle, fish])
rns = team('RnS', [ramenrook, risa, sabbath])

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
threes_queue.enqueue_team(koolish)
threes_queue.enqueue_team(rns)
threes_queue.enqueue_player(Prism)
threes_queue.enqueue_player(Hai_Yena)
threes_queue.enqueue_player(Cicada)
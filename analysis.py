import atexit
from collections import defaultdict
import os
import subprocess
import time

from pymongo import MongoClient, ASCENDING

from blokus.blokus import Player, Blokus

DATABASE_NAME = 'blokus'

# start mongodb process and end it when program errors or completes
# mongod --dbpath=database --port=27015
data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'database')
mongop = subprocess.Popen(
    ['mongod', '--dbpath', data_dir, '--port', '27015'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
atexit.register(mongop.kill)
print(f'Started mongodb with data dir {data_dir}')

client = MongoClient('localhost', 27015)
db = client[DATABASE_NAME]


def analyze():
    N_GAMES = 1000
    N_PLAYERS = 4
    BOARD_SIZE = (20, 20)

    # all players play with the same play style
    stats = defaultdict(lambda: defaultdict(list))
    # main loop
    for game_number in range(N_GAMES):
        # player types
        for type_index in range(N_PLAYERS+1):
            player_types = (['random'] * type_index) + (['big_first'] * (N_PLAYERS-type_index))
            print(game_number, player_types)
            start_time = time.time()
            game = Blokus([Player(ix+1, heuristic=heuristic_type) for ix, heuristic_type in enumerate(player_types)], BOARD_SIZE)
            game.play()
            total_time = time.time() - start_time
            n_empty = game.board.number_of_empty_spaces()
            sum_scores = sum(player.score() for player in game.players)
            n_plays = game.play_counter

            result = db.games.insert_one({
                'final_state': game.board.state,
                'players': [
                    {
                        'score': player.score(),
                        'heuristic': player.heuristic,
                        'n_plays': player.n_plays
                    }
                    for player in game.players
                ],
                'total_time': total_time,
                'n_empty': n_empty,
                'sum_scores': sum_scores,
                'n_plays': n_plays
            })

            _ = db.turns.insert_many([{'game': result.inserted_id, 'state': turn} for turn in game.turns])

    time.sleep(1)
    print('NUMBER OF DOCUMENTS', db.games.count_documents({}))
    for heuristic_type in stats:
        for stat_name in stats[heuristic_type]:
            print(heuristic_type, stat_name, 'average', sum(stats[heuristic_type][stat_name])/len(stats[heuristic_type][stat_name]))

    #

if __name__ == '__main__':
    analyze()


# 45 games each:
# random total_time average 9.036394532521566
# random n_empty average 147.48888888888888
# random sum_scores average 103.4888888888889
# random n_plays average 75.86666666666666
# big_first total_time average 10.296419768863254
# big_first n_empty average 124.06666666666666
# big_first sum_scores average 80.06666666666666
# big_first n_plays average 78.44444444444444
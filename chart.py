import atexit
from collections import defaultdict
import os
import subprocess

import matplotlib.pyplot as plt
import numpy as np
from pymongo import MongoClient, ASCENDING

DATABASE_NAME = 'blokus'

def is_port_in_use(port:int):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# start mongodb process and end it when program errors or completes
# mongod --dbpaths=database --port=27015
if not is_port_in_use(27015):
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


def get_group(document):
    return ''.join(player['heuristic'][0].upper() for player in document['players'])

def chart():
    groups = defaultdict(lambda: defaultdict(list))
    for document in db.games.find({}):
        group = get_group(document)
        for player_index, player in enumerate(document['players']):
            groups[group][player_index].append(player['score'])

    for group in groups:
        for player_index in groups[group]:
            groups[group][player_index] = sum(groups[group][player_index]) / len(groups[group][player_index])

    labels = [group for group in groups]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()

    stuff = []
    for player_index in range(4):
        player_data = []

        for label in labels:
            player_data.append(groups[label][player_index])
        offset = ((player_index+1)/2)-2
        thing = ax.bar(x + (offset*width), player_data, width, label=f'Player {player_index}')
        stuff.append(thing)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Scores')
    ax.set_title('Scores by group and player')
    print(labels)
    print(x)
    # ax.set_xticks(x, labels)
    ax.legend()

    for thing in stuff:
        ax.bar_label(thing, padding=3)

    fig.tight_layout()

    plt.show()



if __name__ == '__main__':
    chart()





# 45 games each:
# random total_time average 9.036394532521566
# random n_empty average 147.48888888888888
# random sum_scores average 103.4888888888889
# random n_plays average 75.86666666666666
# big_first total_time average 10.296419768863254
# big_first n_empty average 124.06666666666666
# big_first sum_scores average 80.06666666666666
# big_first n_plays average 78.44444444444444
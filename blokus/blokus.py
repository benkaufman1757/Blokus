import argparse
import os
from copy import deepcopy
from pprint import pprint
from random import shuffle
from typing import List, Tuple
import uuid

import imageio
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np


one_piece = [
    [1]
]
two_piece = [
    [1,1]
]
three_straight_piece = [
    [1,1,1]
]
three_l_piece = [
    [1,0],
    [1,1],
]

four_straight_piece = [
    [1,1,1,1]
]

four_l_piece = [
    [1,0],
    [1,0],
    [1,1]
]

small_t_piece = [
    [1,0],
    [1,1],
    [1,0]
]

square_piece = [
    [1,1],
    [1,1]
]

small_z_piece = [
    [1,1,0],
    [0,1,1]
]

five_straight_piece = [
    [1,1,1,1,1]
]

five_l_piece = [
    [1,0],
    [1,0],
    [1,0],
    [1,1]
]

long_z_piece = [
    [1,1,0,0],
    [0,1,1,1]
]

square_plus_1_piece = [
    [1,1,0],
    [1,1,1]
]

phone_piece = [
    [1,0,1],
    [1,1,1]
]

submarine_piece = [
    [1,1,1,1],
    [0,0,1,0]
]

big_t_piece = [
    [1,1,1],
    [0,1,0],
    [0,1,0]
]

big_l_piece = [
    [1,0,0],
    [1,0,0],
    [1,1,1]
]

stairs_piece = [
    [1,0,0],
    [1,1,0],
    [0,1,1]
]

big_z_piece = [
    [1,1,0],
    [0,1,0],
    [0,1,1]
]

weird_piece = [
    [1,0,0],
    [1,1,1],
    [0,1,0]
]

plus_sign_piece = [
    [0,1,0],
    [1,1,1],
    [0,1,0]
]

# locals().keys()
ALL_PIECES = [one_piece, two_piece, three_straight_piece, three_l_piece, four_straight_piece, four_l_piece, small_t_piece, square_piece, small_z_piece, five_straight_piece, five_l_piece, long_z_piece, square_plus_1_piece, phone_piece, submarine_piece, big_t_piece, big_l_piece, stairs_piece, big_z_piece, weird_piece, plus_sign_piece]

class Piece:
    def __init__(self, shape:List[List[int]], owner:int) -> None:
        self.shape = shape
        self.owner = owner
        self.placed = False
        self.n_tiles = sum(sum(self.shape,[]))

    def get_all_orientations(self):
        # didn't give this much thought, what are all of the different orientations of a piece?
        reflections = [lambda x: x, lambda x: np.flipud(x), lambda x: np.fliplr(x)]
        rotations = [lambda x: x, lambda x: np.rot90(x),lambda x: np.rot90(np.rot90(x)),lambda x: np.rot90(np.rot90(np.rot90(x)))]
        for reflection in reflections:
            for rotation in rotations:
                # I think this is a good use case for a generator
                yield reflection(rotation(self.shape))

class Player:
    def __init__(self, player_id:int) -> None:
        if player_id < 1:
            raise Exception('Invalid player id')
        self.id = player_id
        self.pieces = [Piece(piece, self.id) for piece in ALL_PIECES]

    def get_valid_moves(self, board, first_move=None):
        valid_moves = []
        remaining_piece_indexes = []
        for index, piece in enumerate(self.pieces):
            if not piece.placed:
                remaining_piece_indexes.append(index)
        for piece in remaining_piece_indexes:
            # maybe placed pieces save "playable" locations
            for y, board_row in enumerate(board.state):
                for x, tile in enumerate(board_row):
                    if tile == 0:
                        for orientation in self.pieces[piece].get_all_orientations():
                            self.pieces[piece].shape = orientation
                            if board.check_placement(self.pieces[piece], x, y, first_move=first_move):
                                self.pieces[piece].placed = True
                                valid_moves.append((piece, self.pieces[piece], x, y))
        return valid_moves

    def get_move(self, board, first_move=None):
        remaining_piece_indexes = []
        for index, piece in enumerate(self.pieces):
            if not piece.placed:
                remaining_piece_indexes.append(index)
        shuffle(remaining_piece_indexes)
        for piece in remaining_piece_indexes:
            # maybe placed pieces save "playable" locations
            for y, board_row in enumerate(board.state):
                for x, tile in enumerate(board_row):
                    if tile == 0:
                        for orientation in self.pieces[piece].get_all_orientations():
                            self.pieces[piece].shape = orientation
                            if board.check_placement(self.pieces[piece], x, y, first_move=first_move):
                                self.pieces[piece].placed = True
                                return self.pieces[piece], x, y
        return None, None, None

    def score(self):
        # not putting in the +5 for using 1 piece last
        return sum([piece.n_tiles for piece in self.pieces if not piece.placed])

# class MaxNPlayer(Player):
#     def __init__(self, max_depth=5, *args, **kwargs) -> None:
#         super(MaxNPlayer, self).__init__(*args, **kwargs)
#         self.max_depth = max_depth

#     def get_move(self, board, players, turn, first_move=None):
#         # board.draw_board()
#         board_copy = deepcopy(board)
#         # board_copy.draw_board()
#         players_copy = deepcopy(players)
#         score, move = self._minimax(0, board_copy, players_copy, turn, first_move=first_move)
#         print(score)
#         return move

#     def _minimax(self, current_depth, board, players, turn, first_move=None):
#         print('depth', current_depth)
#         board.draw_board()
#         current_player = players[turn % len(players)]
#         # print(board)
#         valid_moves = current_player.get_valid_moves(board, first_move=first_move)
#         if current_depth == self.max_depth or not valid_moves:
#             return current_player.score(), None

#         # best_value = float('-inf') if is_max_turn else float('inf')
#         best_value = float('-inf')
#         for action_index, (piece_index, piece, x, y) in enumerate(valid_moves):
#             board_copy = deepcopy(board)
#             board_copy.place_piece(piece, x, y)
#             current_player.pieces[piece_index].placed = True

#             child_value, child_action = self._minimax(current_depth+1, board_copy, players, turn+1)

#             if best_value < child_value:
#                 best_value = child_value
#                 best_action = child_action
#         print(best_action)
#         return best_value, best_action


class Board:
    def __init__(self, x_size:int, y_size:int) -> None:
        if x_size < 1 or y_size < 1:
            raise Exception(f'Invalid board size ({x_size},{y_size})')
        self.x_size = x_size
        self.y_size = y_size
        self.state = [[0 for _ in range(x_size)] for _ in range(y_size)]

    def draw_board(self) -> None:
        pprint(self.state)

    def out_of_bounds(self, x:int, y:int) -> bool:
        return x < 0 or x >= self.x_size or y < 0 or y >= self.y_size

    def check_placement(self, piece:Piece, x:int, y:int, first_move:Tuple[int]=None) -> bool:
        if self.out_of_bounds(x, y):
            # print('case 1')
            return False

        # don't consider placing on border
        if x + len(piece.shape[0]) > self.x_size or y + len(piece.shape) > self.y_size:
            # print('case 2')
            return False

        # for each non-empty tile in a piece make sure it is:
        # 1) On the board
        # 2) Not overlapping with another piece
        # 3) Not sharing an edge with an existing piece on the board
        # additionally make sure at least one non-empty tile touches
        # the corner of an existing "friendly" piece
        touching_corner = False
        touching_start = False
        for y_offset, piece_row in enumerate(piece.shape):
            for x_offset, piece_tile in enumerate(piece_row):
                if piece_tile > 0:
                    # overlapping pieces
                    if self.state[y+y_offset][x+x_offset] != 0:
                        # print('case 3')
                        return False
                    # check if adjacent locations are owned by the same person
                    for i, j in [(0,1),(1,0),(0,-1),(-1,0)]:
                        if not self.out_of_bounds(x+x_offset+i, y+y_offset+j):
                            if self.state[y+y_offset+j][x+x_offset+i] == piece.owner:
                                # print('case 4')
                                return False
                    if not first_move:
                        # check that a corner is touching another corner
                        for i, j in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                            if not self.out_of_bounds(x+x_offset+i, y+y_offset+j):
                                if self.state[y+y_offset+j][x+x_offset+i] == piece.owner:
                                    touching_corner = True
                    else:
                        if first_move[0] == x+x_offset and first_move[1] == y+y_offset:
                            touching_start = True

        return touching_corner or touching_start

    def place_piece(self, piece:Piece, x:int, y:int) -> None:
        for y_offset, piece_row in enumerate(piece.shape):
            for x_offset, piece_tile in enumerate(piece_row):
                if piece_tile != 0:
                    self.state[y+y_offset][x+x_offset] += piece.owner

class Blokus:
    # initial_positions
    def __init__(self, n_players:int, board_size:Tuple[int], starting_positions:List[Tuple[int]]=None, save_game:bool=False) -> None:
        self.id = str(uuid.uuid4())
        self.save_game = save_game
        if self.save_game:
            self.folder = os.path.join('games', self.id)
            self.turns_folder = os.path.join(self.folder, 'turns')
            os.makedirs(self.folder)
            os.makedirs(self.turns_folder)

        if n_players > 4:
            raise Exception('Max of 4 players')

        self.n_players = n_players
        self.players = [Player(i+1) for i in range(n_players)]
        # self.players = [MaxNPlayer(player_id=i+1, max_depth=5) for i in range(n_players)]
        self.board = Board(board_size[0], board_size[1])
        if not starting_positions:
            self.starting_positions = {
                1: (0,0),
                2: (board_size[0]-1,board_size[1]-1),
                3: (board_size[0]-1,0),
                4: (0,board_size[1]-1),
            }
        else:
            self.starting_positions = starting_positions

        self.play_counter = 0


    def play(self):
        turn_file_paths = []
        no_plays = {}
        while sum(no_plays.values()) < self.n_players:
            first_move = None
            current_player = self.players[self.play_counter % self.n_players]
            if self.play_counter // self.n_players == 0:
                first_move = self.starting_positions[current_player.id]

            # piece_index, piece, piece_x, piece_y = current_player.get_move(self.board, self.players, self.play_counter, first_move=first_move)
            piece, piece_x, piece_y = current_player.get_move(self.board, first_move=first_move)
            if piece:
                self.board.place_piece(piece, piece_x, piece_y)
            else:
                no_plays[current_player.id] = 1

            if self.save_game:
                fig = self.get_board()
                file_path = os.path.join(self.turns_folder, f'turn_{str(self.play_counter)}.png')
                fig.savefig(file_path)
                plt.close(fig)
                turn_file_paths.append(file_path)

            self.play_counter += 1
            # self.board.draw_board()
            # _ = input('Press enter to continue...')

        print('Game Over!')
        print(f'Game ID: {self.id}')
        print(f'Game lasted {self.play_counter} plays!')
        for player in self.players:
            print(f'Player {player.id} score: {player.score()}')

        if self.save_game:
            with imageio.get_writer(os.path.join(self.folder,'game.gif'), mode='I') as writer:
                for filename in turn_file_paths:
                    image = imageio.imread(filename)
                    writer.append_data(image)

    def get_board(self):
        # create discrete colormap
        cmap = colors.ListedColormap(['w', 'r', 'b', 'g', 'y'])
        bounds = np.linspace(0, self.n_players, self.n_players+1)
        norm = colors.BoundaryNorm(bounds, cmap.N, extend='max')

        fig, ax = plt.subplots()
        ax.imshow(self.board.state, cmap=cmap, norm=norm)

        # draw gridlines
        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
        ax.set_xticks(np.arange(-.5, self.board.x_size, 1))
        ax.set_yticks(np.arange(-.5, self.board.y_size, 1))
        ax.get_xaxis().set_ticklabels([])
        ax.get_yaxis().set_ticklabels([])

        return fig

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play a game of blokus.')
    parser.add_argument('--save', dest='save', action='store_const',
                    const=True, default=False,
                    help='save turn files and a gif of the game')
    args = parser.parse_args()
    game = Blokus(4, (20, 20), save_game=args.save)
    game.play()

# TODO:
# store possible next locations in each piece, don't enumerate board
# minmax for 2 player, can this be made more general?
# which algorithms work for this type of game? reinforcement?
# create animation from games
# save games to a database

# Links
# https://dke.maastrichtuniversity.nl/m.winands/documents/Multi_Overview.pdf
# https://webdocs.cs.ualberta.ca/~bowling/papers/06aaai-probmaxn.pdf

from __future__ import annotations
import argparse
import copy
import sys
import time
from typing import List


cache = {} # you can use this to implement state caching!


def directions(piece: str) -> list[tuple[int, int]]:
    if piece == "b":
        return [(1, 1), (-1, 1)]
    elif piece == 'r':
        return [(1, -1), (-1, -1)]
    else:
        return [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def promote(board, x, y):
    if board[y][x] == 'b' and y == 7:
        board[y][x] = 'B'
    elif board[y][x] == 'r' and y == 0:
        board[y][x] = 'R'


class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board, turn, depth):
        self.board = board
        self.turn = turn
        self.depth = depth

    def __repr__(self):
        s = ""
        for i in range(8):
            for j in range(8):
                s += self.board[i][j]
            s += "\n"
        return s

    def __hash__(self):
        return hash(str(self.board))

    def __eq__(self, other):
        return self.board == other.board

    def next_state(self, board):
        return State(board, get_next_turn(self.turn), self.depth - 1)

    def single_moves(self, x, y) -> List[State]:
        moves = []
        piece = self.board[y][x]
        if piece == '.' or piece.lower() != self.turn:
            return []
        for dx, dy in directions(piece):
            new_x, new_y = x + dx, y + dy
            if new_x < 0 or new_x >= 8 or new_y < 0 or new_y >= 8:
                continue
            if self.board[new_y][new_x] == '.':
                new_board = copy.deepcopy(self.board)  # TODO: get rid of this if too slow
                new_board[new_y][new_x] = new_board[y][x]
                promote(new_board, new_x, new_y)
                new_board[y][x] = '.'
                moves.append(self.next_state(new_board))
        return moves

    def double_moves(self, x, y) -> List[State]:
        moves = []
        piece = self.board[y][x]
        if piece == '.' or piece.lower() != self.turn:
            return []
        for dx, dy in directions(piece):
            new_x, new_y = x + 2 * dx, y + 2 * dy
            capture_x, capture_y = x + dx, y + dy
            if new_x < 0 or new_x >= 8 or new_y < 0 or new_y >= 8:
                continue
            if self.board[new_y][new_x] == '.' and self.board[capture_y][capture_x] in get_opp_char(self.turn):
                new_board = copy.deepcopy(self.board)
                new_board[new_y][new_x] = new_board[y][x]
                new_board[y][x] = '.'
                new_board[y + dy][x + dx] = '.'
                promote(new_board, new_x, new_y)
                further_jumps = State(new_board, self.turn, self.depth).double_moves(new_x, new_y)
                if further_jumps:
                    moves.extend(further_jumps)
                else:
                    moves.append(self.next_state(new_board))
        return moves

    def generate_successors(self) -> List[State]:
        moves_single = []
        moves_double = []
        for y in range(8):
            for x in range(8):
                moves_single.extend(self.single_moves(x, y))
                moves_double.extend(self.double_moves(x, y))
        return moves_double if moves_double else moves_single

    def is_terminal(self):
        return 0 in self.count()

    def count(self):
        b_pieces, r_pieces = 0, 0
        for row in self.board:
            for col in row:
                if col == 'b':
                    b_pieces += 1
                elif col == 'B':
                    b_pieces += 2
                elif col == 'r':
                    r_pieces += 1
                elif col == 'R':
                    r_pieces += 2
        return r_pieces, b_pieces

    def eval(self):
        return self.count()[0] - self.count()[1]



def get_opp_char(player):
    if player in ['b', 'B']:
        return ['r', 'R']
    else:
        return ['b', 'B']


def get_next_turn(curr_turn):
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'


def read_from_file(filename):
    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board



if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--inputfile",
    #     type=str,
    #     required=True,
    #     help="The input file that contains the puzzles."
    # )
    # parser.add_argument(
    #     "--outputfile",
    #     type=str,
    #     required=True,
    #     help="The output file that contains the solution."
    # )
    # args = parser.parse_args()
    #
    # initial_board = read_from_file(args.inputfile)
    # state = State(initial_board)
    # turn = 'r'
    # ctr = 0
    #
    # sys.stdout = open(args.outputfile, 'w')
    #
    # sys.stdout = sys.__stdout__
    board = read_from_file('checkers.txt')
    state = State(board, 'r', 5)
    print(str(state))
    print(state.generate_successors())
    print(state.eval())


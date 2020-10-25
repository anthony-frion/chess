'''
Hello, and thank you for paying attention to my work !

This file is a fully functional tetris game : all you have to do is execute
it and a pygame window will show up.

You can press 'F' whenever you want to flip the board and see the other player's perspective.
This enables you to play with someone else if you want to.

Also, this code is made in a way that makes it quite easy to implement a chess AI on top of it
(which is why it is longer than it could have been).
An update will come out soon on my Github page that will include a 'minimax' type AI.

Enjoy !
'''

# A few useful auxilary functions 

def sgn(x) :
    if x > 0 :
        return 1
    elif x < 0 :
        return -1
    else :
        return 0

def fst(couple) :
    (a, b) = couple
    return a

def snd(couple) :
    (a, b) = couple
    return b


import pygame as pg
from pygame.locals import *
import copy as cp
import time

# Global variables for the graphical interface
square_size = (60, 60)
window_size = (600, 600)
background_color = (0, 200, 0)

pg.init()
window = pg.display.set_mode(window_size)

# A few useful sprites
empty_board_sprite = pg.image.load('graphics/empty_board.png') # empty board sprite
possible_sprite = pg.image.load('graphics/possible.png').convert_alpha() # yellow circle indicating a possible move
previous_move_sprite = pg.image.load('graphics/previous_move.png').convert_alpha()

# Sprites for the white pieces
white_pawn_sprite = pg.image.load('graphics/Chess_plt60.png').convert_alpha()
white_bishop_sprite = pg.image.load('graphics/Chess_blt60.png').convert_alpha()
white_knight_sprite = pg.image.load('graphics/Chess_nlt60.png').convert_alpha()
white_king_sprite = pg.image.load('graphics/Chess_klt60.png').convert_alpha()
white_rook_sprite = pg.image.load('graphics/Chess_rlt60.png').convert_alpha()
white_queen_sprite = pg.image.load('graphics/Chess_qlt60.png').convert_alpha()

# Sprites for the black pieces
black_pawn_sprite = pg.image.load('graphics/Chess_pdt60.png').convert_alpha()
black_bishop_sprite = pg.image.load('graphics/Chess_bdt60.png').convert_alpha()
black_knight_sprite = pg.image.load('graphics/Chess_ndt60.png').convert_alpha()
black_king_sprite = pg.image.load('graphics/Chess_kdt60.png').convert_alpha()
black_rook_sprite = pg.image.load('graphics/Chess_rdt60.png').convert_alpha()
black_queen_sprite = pg.image.load('graphics/Chess_qdt60.png').convert_alpha()


# Move and eat range for the pawns
white_pawn_move_range = [(0, 1)]
black_pawn_move_range = [(0, -1)]

white_pawn_eat_range = [(1, 1), (-1, 1)]
black_pawn_eat_range = [(1, -1), (-1, -1)]

# Definition of all the possible moves of the different pieces

bishop_move_range = []
for k in range(1, 8) :
    bishop_move_range.append((k, k))
    bishop_move_range.append((k, -k))
    bishop_move_range.append((-k, k))
    bishop_move_range.append((-k, -k))
bishop_eat_range = bishop_move_range

rook_move_range = []
for k in range(1, 8) :
    rook_move_range.append((0, k))
    rook_move_range.append((0, -k))
    rook_move_range.append((k, 0))
    rook_move_range.append((-k, 0))
rook_eat_range = rook_move_range

knight_move_range = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
knight_eat_range = knight_move_range

king_move_range = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
king_eat_range = king_move_range

queen_move_range = []
for k in range(1, 8) :
    queen_move_range.append((k, k))
    queen_move_range.append((k, -k))
    queen_move_range.append((-k, k))
    queen_move_range.append((-k, -k))
    queen_move_range.append((0, k))
    queen_move_range.append((0, -k))
    queen_move_range.append((k, 0))
    queen_move_range.append((-k, 0))
queen_eat_range = queen_move_range

# Abstractlass for the pieces
class piece :
    def __init__(self, color, type, move_range, eat_range, value) :
        self.color = color
        self.type = type
        self.move_range = move_range
        self.eat_range = eat_range
        self.value = value

# Each type of piece is assigned a class that inherits from the 'piece' class

class pawn(piece) :
    def __init__(self, color) :
        self.has_moved = False
        if color == "white" :
            super().__init__(color, "pawn", white_pawn_move_range, white_pawn_eat_range, 1)
        elif color == "black" :
            super().__init__(color, "pawn", black_pawn_move_range, black_pawn_eat_range, 1)
        else :
            print("Error : color must be 'black' or 'white'")

class bishop(piece) :
    def __init__(self, color) :
        if color == "white" or color == "black" :
            super().__init__(color, "bishop", bishop_move_range, bishop_eat_range, 3.2)
        else :
            print("Error : color must be 'black' or 'white'")
            
class rook(piece) :
    def __init__(self, color) :
        self.has_moved = False
        if color == "white" or color == "black" :
            super().__init__(color, "rook", rook_move_range, rook_eat_range, 5)
        else :
            print("Error : color must be 'black' or 'white'")

class knight(piece) :
    def __init__(self, color) :
        if color == "white" or color == "black" :
            super().__init__(color, "knight", knight_move_range, knight_eat_range, 3)
        else :
            print("Error : color must be 'black' or 'white'")

class king(piece) :
    def __init__(self, color) :
        self.has_moved = False
        if color == "white" or color == "black" :
            super().__init__(color, "king", king_move_range, king_eat_range, 0)
        else :
            print("Error : color must be 'black' or 'white'")

class queen(piece) :
    def __init__(self, color) :
        if color == "white" or color == "black" :
            super().__init__(color, "queen", queen_move_range, queen_eat_range, 9)
        else :
            print("Error : color must be 'black' or 'white'")

# Class that defines the whole state of a chess game
class position :
    
    def __init__(self, pieces_matrix, window, player_turn) :
        self.pieces_matrix = pieces_matrix
        self.window = window
        self.player_turn = player_turn
        self.perspective = 'white'
        self.attackers = {"white": {}, "black": {}}
        self.squares_attacked = {"white": {}, "black": {}}
        for i in range(8) :
            for j in range(8) :
                self.attackers["white"][(i, j)] = []
                self.attackers["black"][(i, j)] = []
                self.squares_attacked["white"][(i, j)] = []
                self.squares_attacked["black"][(i, j)] = []
        self.selected_piece = None
        self.legal_moves = {}
        self.illegal_moves = {}
        self.en_passant = []
        self.previous_moves = []
        self.check = self.is_check()
        self.mate = self.is_mate()
        self.draw = False
        self.last_take_or_pawn_move = 0
        
    # Returns a copy of the position, so that the original object is
    # unchanged when its copy changes
    def get_copy(self) :
        matrix_copy = []
        for i in range(8) :
            matrix_copy.append(self.pieces_matrix[i].copy())
        copy = position(matrix_copy, None, self.player_turn)
        copy.attackers = {}
        for color in ["white", "black"] :
            copy.attackers[color] = {}
            for x in self.attackers[color] :
                copy.attackers[color][x] = self.attackers[color][x].copy()
        copy.squares_attacked = {}
        for color in ["white", "black"] :
            copy.squares_attacked[color] = {}
            for x in self.squares_attacked[color] :
                copy.squares_attacked[color][x] = self.squares_attacked[color][x].copy()
        copy.check = self.check
        copy.legal_moves = {}
        copy.illegal_moves = {}
        copy.en_passant = self.en_passant
        copy.previous_moves = cp.copy(self.previous_moves)
        copy.draw = self.draw
        copy.last_take_or_pawn_move = self.last_take_or_pawn_move
        return copy
               
    # Returns the color of the opponent, i.e. the player who last played
    def get_opponent(self) :
        if self.player_turn == "white" :
            return "black"
        elif self.player_turn == "black" :
            return "white"
        else :
            print("Error : color must be 'black' or 'white'")
        
    
    
    # Computes all the legal moves of the chess position
    def compute_legal_moves(self) :
        legal_moves = {}
        illegal_moves = {}
        king_position = None
        for i in range(8) :
            for j in range(8) :
                if self.pieces_matrix[i][j] != None and self.pieces_matrix[i][j].type == "king" and self.pieces_matrix[i][j].color == self.player_turn :
                    king_position = (i, j)
                legal_moves[(i, j)] = []
                illegal_moves[(i, j)] = []
        if not self.check :
            if not self.pieces_matrix[fst(king_position)][snd(king_position)].has_moved :
                for square in [(2, 0), (6, 0), (2, 7), (6, 7)] :
                    if square in self.squares_attacked[self.player_turn][king_position] :
                        self.squares_attacked[self.player_turn][king_position].remove(square)
                if self.player_turn == "white" :
                    if self.pieces_matrix[0][0] != None and self.pieces_matrix[0][0].type == "rook" and not self.pieces_matrix[0][0].has_moved :
                        if king_position in self.squares_attacked["white"][(0, 0)] :
                            if self.attackers["black"][(2, 0)] == [] and self.attackers["black"][(3, 0)] == [] :
                                self.squares_attacked["white"][king_position].append((2, 0))
                    if self.pieces_matrix[7][0] != None and self.pieces_matrix[7][0].type == "rook" and not self.pieces_matrix[7][0].has_moved :
                        if king_position in self.squares_attacked["white"][(7, 0)] :
                            if self.attackers["black"][(5, 0)] == [] and self.attackers["black"][(6, 0)] == [] :
                                self.squares_attacked["white"][king_position].append((6, 0))
                if self.player_turn == "black" :
                    if self.pieces_matrix[0][7] != None and self.pieces_matrix[0][7].type == "rook" and not self.pieces_matrix[0][7].has_moved :
                        if king_position in self.squares_attacked["black"][(0, 7)] :
                            if self.attackers["white"][(2, 7)] == [] and self.attackers["white"][(3, 7)] == [] :
                                   self.squares_attacked["black"][king_position].append((2, 7))
                    if self.pieces_matrix[7][7] != None and self.pieces_matrix[7][7].type == "rook" and not self.pieces_matrix[7][7].has_moved :
                        if king_position in self.squares_attacked["black"][(7, 7)] :
                            if self.attackers["white"][(5, 7)] == [] and self.attackers["white"][(6, 7)] == [] :
                                self.squares_attacked["black"][king_position].append((6, 7))
            for i in range(8) :
                for j in range(8) :
                    if self.pieces_matrix[i][j] != None and self.pieces_matrix[i][j].color == self.player_turn :
                        if self.pieces_matrix[i][j].type == "king" :
                            for move in self.squares_attacked[self.player_turn][(i, j)] :
                                a, b = move
                                if self.pieces_matrix[fst(move)][snd(move)] != None and self.pieces_matrix[fst(move)][snd(move)].color == self.player_turn :
                                    illegal_moves[(i, j)].append(move)
                                elif self.attackers[self.get_opponent()][move] != [] :
                                    for attacker in self.attackers[self.get_opponent()][move] :
                                        if (fst(move) - fst(attacker), snd(move) - snd(attacker)) in self.pieces_matrix[fst(attacker)][snd(attacker)].eat_range :
                                            illegal_moves[(i, j)].append(move)
                                            break
                                        for square in [(a-1, b-1), (a+1, b-1), (a+1, b+1), (a-1, b+1)] :
                                            if fst(square) >= 0 and fst(square) < 8 and snd(square) >= 0 and snd(square) < 8 :
                                                if self.pieces_matrix[fst(square)][snd(square)] != None and self.pieces_matrix[fst(square)][snd(square)].type == "pawn" and self.pieces_matrix[fst(square)][snd(square)].color == self.get_opponent() :
                                                    if (a - fst(square), b - snd(square)) in self.pieces_matrix[fst(square)][snd(square)].eat_range :
                                                        illegal_moves[(i, j)].append(move)
                                                        break
                                else :
                                    possible = True
                                    (a, b) = move
                                    for square in [(a-1, b-1), (a-1, b+1), (a+1, b-1), (a+1, b+1)] :
                                        if fst(square) >= 0 and fst(square) < 8 and snd(square) >= 0 and snd(square) < 8 :
                                            if self.pieces_matrix[fst(square)][snd(square)] != None and self.pieces_matrix[fst(square)][snd(square)].type == "pawn" and self.pieces_matrix[fst(square)][snd(square)].color == self.get_opponent() :
                                                if (a - fst(square), b - snd(square)) in self.pieces_matrix[fst(square)][snd(square)].eat_range :
                                                    possible = False
                                    if not possible :
                                        illegal_moves[(i, j)].append(move)
                        else :
                            if self.attackers[self.get_opponent()][(i, j)] != [] :
                                if abs(i - fst(king_position)) == abs(j - snd(king_position)) or i == fst(king_position) or j == snd(king_position) :
                                    direction_king = (sgn(fst(king_position) - i), sgn(snd(king_position) - j))
                                    a, b = i + fst(direction_king), j + snd(direction_king)
                                    while (a, b) != king_position and self.pieces_matrix[a][b] == None :
                                        a, b = a + fst(direction_king), b + snd(direction_king)
                                    if (a, b) == king_position :
                                        attacks = self.attackers[self.get_opponent()][(i, j)]
                                        for attack in attacks :
                                            if self.pieces_matrix[fst(attack)][snd(attack)].type in ["bishop", "rook", "queen"] :
                                                if (sgn(i - fst(attack)), sgn(j - snd(attack))) == direction_king :
                                                    square_between = fst(attack) + fst(direction_king), snd(attack) + snd(direction_king)
                                                    squares_between = [attack]
                                                    while square_between != king_position :
                                                        squares_between.append(square_between)
                                                        square_between = fst(square_between) + fst(direction_king), snd(square_between) + snd(direction_king)
                                                    for square in self.squares_attacked[self.player_turn][(i, j)] :
                                                        if square not in squares_between :
                                                            illegal_moves[(i, j)].append(square)
                        if self.pieces_matrix[i][j].type == "pawn" :
                            for move in self.squares_attacked[self.player_turn][(i, j)] :
                                if (fst(move) - i, snd(move) - j) in self.pieces_matrix[i][j].eat_range :
                                    if self.pieces_matrix[fst(move)][snd(move)] == None or self.pieces_matrix[fst(move)][snd(move)].color == self.player_turn :
                                        if ((i, j), move) not in self.en_passant :
                                            illegal_moves[(i, j)].append(move)
                                elif abs(snd(move) - j) == 2 :
                                    if self.pieces_matrix[fst(move)][snd(move)] != None :
                                        illegal_moves[(i, j)].append(move)
                                    elif self.pieces_matrix[fst(move)][j + (snd(move) - j) // 2] != None :
                                        illegal_moves[(i, j)].append(move)
        else :
            attacks = self.attackers[self.get_opponent()][king_position]
            if len(attacks) == 1 :
                square_between = attacks[0]
                for square in self.attackers[self.player_turn][attacks[0]] :
                    a, b = square
                    if square != king_position :
                        if self.attackers[self.get_opponent()][square] != [] :
                            if abs(a - fst(king_position)) == abs(b - snd(king_position)) or a == fst(king_position) or b == snd(king_position) :
                                attacks_ = self.attackers[self.get_opponent()][(a, b)]
                                direction_king = (sgn(fst(king_position) - a), sgn(snd(king_position) - b))
                                a_, b_ = a + fst(direction_king), b + snd(direction_king)
                                while (a_, b_) != king_position and self.pieces_matrix[a_][b_] == None :
                                    a_, b_ = a_ + fst(direction_king), b_ + snd(direction_king)
                                if (a_, b_) == king_position :
                                    possible = True
                                    for attack in attacks_ :
                                        if self.pieces_matrix[fst(attack)][snd(attack)].type in ["bishop", "rook", "queen"] :
                                            if (sgn(a - fst(attack)), sgn(b - snd(attack))) == direction_king :
                                                possible = False
                                    if possible :
                                        legal_moves[square].append(square_between)
                                else :
                                    legal_moves[square].append(square_between)
                            else :
                                legal_moves[square].append(square_between)
                        else :
                            legal_moves[square].append(square_between)
                if self.pieces_matrix[fst(attacks[0])][snd(attacks[0])].type in ["bishop", "rook", "queen"] :
                    direction = (sgn(fst(king_position) - fst(attacks[0])), sgn(snd(king_position) - snd(attacks[0])))
                    square_between = fst(attacks[0]) + fst(direction), snd(attacks[0]) + snd(direction)
                    while square_between != king_position :
                        for square in self.attackers[self.player_turn][square_between] :
                            a, b = square
                            if square != king_position and (fst(square_between) - a, snd(square_between) - b) in self.pieces_matrix[a][b].move_range :
                                if self.attackers[self.get_opponent()][square] != [] :
                                    if abs(a - fst(king_position)) == abs(b - snd(king_position)) or a == fst(king_position) or b == snd(king_position) :
                                        attacks = self.attackers[self.get_opponent()][(a, b)]
                                        direction_king = (sgn(fst(king_position) - a), sgn(snd(king_position) - b))
                                        a_, b_ = a + fst(direction_king), b + snd(direction_king)
                                        while (a_, b_) != king_position and self.pieces_matrix[a_][b_] == None :
                                            a_, b_ = a_ + fst(direction_king), b_ + snd(direction_king)
                                        if (a_, b_) == king_position :
                                            possible = True
                                            for attack in attacks :
                                                if self.pieces_matrix[fst(attack)][snd(attack)].type in ["bishop", "rook", "queen"] :
                                                    if (sgn(a - fst(attack)), sgn(b - snd(attack))) == direction_king :
                                                        possible = False
                                            if possible :
                                                legal_moves[square].append(square_between)
                                        else :
                                            legal_moves[square].append(square_between)
                                    else :
                                        legal_moves[square].append(square_between)
                                else :
                                    legal_moves[square].append(square_between)
                        square_between = fst(square_between) + fst(direction), snd(square_between) + snd(direction)
            for move in self.squares_attacked[self.player_turn][king_position] :
                if self.pieces_matrix[fst(move)][snd(move)] == None or self.pieces_matrix[fst(move)][snd(move)].color != self.player_turn :
                    attackers = [x for x in self.attackers[self.get_opponent()][move]]
                    for attacker in attackers :
                        if self.pieces_matrix[fst(attacker)][snd(attacker)].type == "pawn" :
                            if fst(move) == fst(attacker) :
                                attackers.remove(attacker)
                    if attackers == []  :
                        possible = True
                        (a, b) = move
                        for attack in self.attackers[self.get_opponent()][king_position] :
                            if (a - fst(attack), b - snd(attack)) in self.pieces_matrix[fst(attack)][snd(attack)].eat_range :
                                possible = False
                        for square in [(a-1, b-1), (a-1, b+1), (a+1, b-1), (a+1, b+1)] :
                            if fst(square) >= 0 and fst(square) < 8 and snd(square) >= 0 and snd(square) < 8 :
                                if self.pieces_matrix[fst(square)][snd(square)] != None and self.pieces_matrix[fst(square)][snd(square)].type == "pawn" and self.pieces_matrix[fst(square)][snd(square)].color == self.get_opponent() :
                                    if (a - fst(square), b - snd(square)) in self.pieces_matrix[fst(square)][snd(square)].eat_range :
                                        possible = False
                        if possible :
                            legal_moves[king_position].append(move)
        self.legal_moves = legal_moves
        self.illegal_moves = illegal_moves
        
    # Returns the square of the board corresponding to the coordinates
    # of a pygame window on which the user clicked
    def position_to_square(self, x, y) :
        if x > 60 and x < 540 and y > 60 and y < 540 :
            x_, y_ = x - 60, 540 - y
            if self.perspective == 'white' :
                return x_ // 60, y_ // 60
            else :
                return (480 - x_) // 60, (480 - y_) // 60
        else :
            return None
        
    # Compute the list of legal moves for this position
    def list_of_moves(self) :
        moves = []
        if self.check :
            for i in range(8) :
                for j in range(8) :
                    for x in self.legal_moves[(i, j)] :
                        moves.append(((i, j), x))
        else :
            for i in range(8) :
                for j in range(8) :
                    for x in self.squares_attacked[self.player_turn][(i, j)] :
                        a, b = x
                        if self.pieces_matrix[a][b] == None or self.pieces_matrix[a][b].color != self.player_turn :
                            if x not in self.illegal_moves[(i, j)] :
                                moves.append(((i, j), x))
        return moves
                      
    # Computes what happens when the user clicks on the pygame window                  
    def click_on_position(self, x, y) :
        if self.position_to_square(x, y) == None :
            return
        i, j = self.position_to_square(x, y)
        
        if self.pieces_matrix[i][j] != None and self.pieces_matrix[i][j].color == self.player_turn :
            if self.selected_piece != None :
                self.show_appropriate_perspective()
            self.selected_piece = (i, j)
            if not self.check :
                possible_moves = self.squares_attacked[self.player_turn][self.selected_piece]
            else :
                possible_moves = self.legal_moves[self.selected_piece]
            for square in possible_moves :
                i, j = square
                if self.pieces_matrix[i][j] == None or self.pieces_matrix[i][j].color != self.player_turn :
                    if self.check or square not in self.illegal_moves[self.selected_piece] :
                        if self.perspective == 'white' :
                            self.window.blit(possible_sprite, (60 + 60*fst(square), 480-60*snd(square)))
                        else :
                            self.window.blit(possible_sprite, (480 - 60*fst(square), 60 + 60*snd(square)))
        elif self.selected_piece != None and self.check and (i, j) in self.legal_moves[self.selected_piece] :
            self.make_a_move(self.selected_piece, (i, j))
            self.show_appropriate_perspective()
        elif self.selected_piece != None and not self.check and (i, j) in self.squares_attacked[self.player_turn][self.selected_piece] and (i, j) not in self.illegal_moves[self.selected_piece] :
            self.make_a_move(self.selected_piece, (i, j))
            self.show_appropriate_perspective()
        elif self.pieces_matrix[i][j] != None and self.pieces_matrix[i][j].color == self.player_turn :
            self.show_appropriate_perspective()
            self.selected_piece = (i, j)
            possible_moves = self.legal_moves[self.selected_piece]
    
    # Computes the possible moves of the piece located on the square (i, j)
    # Be careful : some of these moves might be illegal if they expose the king
    def possible_moves_from_square(self, i, j) :
        if self.pieces_matrix[i][j] != None and self.pieces_matrix[i][j].color == self.player_turn :
            if self.pieces_matrix[i][j].type == "pawn" :
                for move in self.pieces_matrix[i][j].move_range :
                    (a, b) = move
                    if i+a >= 0 and i+a < 8 and j+b >= 0 and j+b < 8 :
                        if self.pieces_matrix[i+a][j+b] == None :
                            self.attackers[self.player_turn][(i+a, j+b)].append((i, j))
                            self.squares_attacked[self.player_turn][(i, j)].append((i+a, j+b))
                    if not self.pieces_matrix[i][j].has_moved :
                        if self.pieces_matrix[i+a][j+b] == None and self.pieces_matrix[i+2*a][j+2*b] == None :
                            self.attackers[self.player_turn][(i+2*a, j+2*b)].append((i, j))
                            self.squares_attacked[self.player_turn][(i, j)].append((i+2*a, j+2*b))
                for move in self.pieces_matrix[i][j].eat_range :
                    (a, b) = move
                    if i+a >= 0 and i+a < 8 and j+b >= 0 and j+b < 8 :
                        self.attackers[self.player_turn][(i+a, j+b)].append((i, j))
                        self.squares_attacked[self.player_turn][(i, j)].append((i+a, j+b))
            elif self.pieces_matrix[i][j].type in ["king", "knight"] :
                for move in self.pieces_matrix[i][j].move_range :
                    (a, b) = move
                    if i+a >= 0 and i+a < 8 and j+b >= 0 and j+b < 8 :
                        self.attackers[self.player_turn][(i+a, j+b)].append((i, j))
                        self.squares_attacked[self.player_turn][(i, j)].append((i+a, j+b))
                            
            if self.pieces_matrix[i][j].type in ["bishop", "queen"] :
                for direction in [(-1, -1), (-1, 1), (1, -1), (1, 1)] :
                    a, b = i + fst(direction), j + snd(direction)
                    while a >= 0 and a < 8 and b >= 0 and b < 8 and self.pieces_matrix[a][b] == None :
                        self.attackers[self.player_turn][(a, b)].append((i, j))
                        self.squares_attacked[self.player_turn][(i, j)].append((a, b))
                        a, b = a + fst(direction), b + snd(direction)
                    if a >= 0 and a < 8 and b >= 0 and b < 8 :
                        self.attackers[self.player_turn][(a, b)].append((i, j))
                        self.squares_attacked[self.player_turn][(i, j)].append((a, b))
            if self.pieces_matrix[i][j].type in ["rook", "queen"] :
                for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)] :
                    a, b = i + fst(direction), j + snd(direction)
                    while a >= 0 and a < 8 and b >= 0 and b < 8 and self.pieces_matrix[a][b] == None :
                        self.attackers[self.player_turn][(a, b)].append((i, j))
                        self.squares_attacked[self.player_turn][(i, j)].append((a, b))
                        a, b = a + fst(direction), b + snd(direction)
                    if a >= 0 and a < 8 and b >= 0 and b < 8 :
                        self.attackers[self.player_turn][(a, b)].append((i, j))
                        self.squares_attacked[self.player_turn][(i, j)].append((a, b))
    
    # Returns a list of the enemy pieces that the selected piece could
    # attack from the selected position, and a list of the ally pieces
    # that it could defend.
    def targets_from_square(self, piece, i, j) :
        targets = []
        protected = []
        if piece.type == "pawn" :
            for move in piece.eat_range :
                (a, b) = move
                if i+a >= 0 and i+a < 8 and j+b >= 0 and j+b < 8 :
                    if self.pieces_matrix[i+a][j+b] != None :
                        if self.pieces_matrix[i+a][j+b].color != piece.color :
                            targets.append((i+a, j+b))
                        else :
                            protected.append((i+a, j+b))
        elif piece.type in ["king", "knight"] :
            for move in piece.move_range :
                (a, b) = move
                if i+a >= 0 and i+a < 8 and j+b >= 0 and j+b < 8 :
                    if self.pieces_matrix[i+a][j+b] != None :
                        if self.pieces_matrix[i+a][j+b].color != piece.color :
                            targets.append((i+a, j+b))
                        else :
                            protected.append((i+a, j+b))
        if piece.type in ["bishop", "queen"] :
            for direction in [(-1, -1), (-1, 1), (1, -1), (1, 1)] :
                a, b = i + fst(direction), j + snd(direction)
                while a >= 0 and a < 8 and b >= 0 and b < 8 and self.pieces_matrix[a][b] == None :
                    a, b = a + fst(direction), b + snd(direction)
                if a >= 0 and a < 8 and b >= 0 and b < 8 :
                    if self.pieces_matrix[a][b] != None :
                        if self.pieces_matrix[a][b].color != piece.color :
                            targets.append((a, b))
                        else :
                            protected.append((a, b))
        if piece.type in ["rook", "queen"] :
            for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)] :
                a, b = i + fst(direction), j + snd(direction)
                while a >= 0 and a < 8 and b >= 0 and b < 8 and self.pieces_matrix[a][b] == None :
                    a, b = a + fst(direction), b + snd(direction)
                if a >= 0 and a < 8 and b >= 0 and b < 8 :
                    if self.pieces_matrix[a][b] != None :
                        if self.pieces_matrix[a][b].color != piece.color :
                            targets.append((a, b))
                        else :
                            protected.append((a, b))
        return targets, protected
                    
    # Computes the special move 'castle' of the king
    def castle(self, piece_position, new_position, graphics, compute_legal, print_stuff) :
        player = self.player_turn
        self.squares_attacked[self.player_turn][piece_position].remove(new_position)
        if new_position == (2, 0) :
            self.make_a_move((4, 0), (3, 0), False, False, False)
            self.player_turn = player
            self.make_a_move((3, 0), (2, 0), False, False, False)
            self.player_turn = player
            self.make_a_move((0, 0), (3, 0), graphics, compute_legal, print_stuff)
        elif new_position == (6, 0) :
            self.make_a_move((4, 0), (5, 0), False, False, False)
            self.player_turn = player
            self.make_a_move((5, 0), (6, 0), False, False, False)
            self.player_turn = player
            self.make_a_move((7, 0), (5, 0), graphics, compute_legal, print_stuff)
        elif new_position == (2, 7) :
            self.make_a_move((4, 7), (3, 7), False, False, False)
            self.player_turn = player
            self.make_a_move((3, 7), (2, 7), False, False, False)
            self.player_turn = player
            self.make_a_move((0, 7), (3, 7), graphics, compute_legal, print_stuff)
        elif new_position == (6, 7) :
            self.make_a_move((4, 7), (5, 7), False, False, False)
            self.player_turn = player
            self.make_a_move((5, 7), (6, 7), False, False, False)
            self.player_turn = player
            self.make_a_move((7, 7), (5, 7), graphics, compute_legal, print_stuff)
               
    # Changes the state of the position to take into account all the
    # consequences of the selected move
    def make_a_move(self, piece_position, new_position, graphics=True, compute_legal=True, print_stuff=True) :
        a1, b1 = piece_position
        a2, b2 = new_position
        if self.pieces_matrix[a2][b2] != None or self.pieces_matrix[a1][b1].type == 'pawn' :
            self.last_take_or_pawn_move = 0
        else :
            self.last_take_or_pawn_move += 1
        moving_piece = self.pieces_matrix[a1][b1]
        if (piece_position, new_position) in self.en_passant :
            player = self.player_turn
            self.make_a_move(piece_position, (a2, b1), False, False, False)
            self.player_turn = player
            self.make_a_move((a2, b1), (a2, b2), graphics, compute_legal, print_stuff)
            self.player_turn = self.get_opponent()
        if moving_piece.type in ["pawn", "rook", "king"] :
            moving_piece.has_moved = True
            if moving_piece.type == "king" and abs(fst(new_position) - fst(piece_position)) >= 2 :
                self.castle(piece_position, new_position, graphics, compute_legal, print_stuff)
                return
        if self.pieces_matrix[4][0] != None and self.pieces_matrix[4][0].type == "king" :
            for square in [(2, 0), (6, 0)] :
                if square in self.squares_attacked[self.player_turn][(4, 0)] :
                    self.squares_attacked[self.player_turn][(4, 0)].remove(square)
        if self.pieces_matrix[4][7] != None and self.pieces_matrix[4][7].type == "king" :
            for square in [(2, 7), (6, 7)] :
                if square in self.squares_attacked[self.player_turn][(4, 7)] :
                    self.squares_attacked[self.player_turn][(4, 7)].remove(square)
        self.pieces_matrix[a1][b1] = None
        self.pieces_matrix[a2][b2] = moving_piece
        if moving_piece.type == "pawn" and b2 in [0, 7] :
            self.pieces_matrix[a2][b2] = queen(self.player_turn)
        self.possible_moves_from_square(a2, b2)
        for square in self.squares_attacked[self.player_turn][piece_position] :
            self.attackers[self.player_turn][square].remove(piece_position)
        self.squares_attacked[self.player_turn][piece_position] = []
        opponent = self.get_opponent()
        for square in self.squares_attacked[opponent][new_position] :
            self.attackers[opponent][square].remove(new_position)
        self.squares_attacked[opponent][new_position] = []
        for square in [(a1, b1-1), (a1, b1+1)] :
            if fst(square) >= 0 and fst(square) < 8 and snd(square) >= 0 and snd(square) < 8 :
                if self.pieces_matrix[fst(square)][snd(square)] != None and self.pieces_matrix[fst(square)][snd(square)].type == "pawn" :
                    if (0, b1 - snd(square)) in self.pieces_matrix[fst(square)][snd(square)].move_range :
                        self.attackers[self.pieces_matrix[fst(square)][snd(square)].color][(a1, b1)].append(square)
                        self.squares_attacked[self.pieces_matrix[fst(square)][snd(square)].color][square].append((a1, b1))
        for square in [(a1, b1-2), (a1, b1+2)] :
            if fst(square) >= 0 and fst(square) < 8 and snd(square) >= 0 and snd(square) < 8 :
                if self.pieces_matrix[fst(square)][snd(square)] != None and self.pieces_matrix[fst(square)][snd(square)].type == "pawn" :
                    if not self.pieces_matrix[fst(square)][snd(square)].has_moved and (a1, (b1+snd(square))//2) in self.squares_attacked[self.pieces_matrix[fst(square)][snd(square)].color][square] :
                        self.attackers[self.pieces_matrix[fst(square)][snd(square)].color][(a1, b1)].append(square)
                        self.squares_attacked[self.pieces_matrix[fst(square)][snd(square)].color][square].append((a1, b1))
        for square in [(a2-1, b2-1), (a2+1, b2-1), (a2-1, b2+1), (a2+1, b2+1)] :
            if fst(square) >= 0 and fst(square) < 8 and snd(square) >= 0 and snd(square) < 8 :
                if self.pieces_matrix[fst(square)][snd(square)] != None and self.pieces_matrix[fst(square)][snd(square)].type == "pawn" and self.pieces_matrix[fst(square)][snd(square)].color != self.player_turn :
                    if (a2 - fst(square), b2 - snd(square)) in self.pieces_matrix[fst(square)][snd(square)].eat_range :
                        if (a2, b2) not in self.squares_attacked[self.pieces_matrix[fst(square)][snd(square)].color][square] :
                            self.attackers[self.pieces_matrix[fst(square)][snd(square)].color][(a2, b2)].append(square)
                            self.squares_attacked[self.pieces_matrix[fst(square)][snd(square)].color][square].append((a2, b2))
        for square in [(a2, b2-2), (a2, b2+2)] :
            if fst(square) >= 0 and fst(square) < 8 and snd(square) >= 0 and snd(square) < 8 :
                if self.pieces_matrix[fst(square)][snd(square)] != None and self.pieces_matrix[fst(square)][snd(square)].type == "pawn" :
                    if square in self.attackers[self.pieces_matrix[fst(square)][snd(square)].color][(a2, b2)] :
                        self.attackers[self.pieces_matrix[fst(square)][snd(square)].color][(a2, b2)].remove(square)
                        self.squares_attacked[self.pieces_matrix[fst(square)][snd(square)].color][square].remove((a2, b2))
        self.en_passant = []
        if moving_piece.type == "pawn" and abs(b2-b1) == 2 :
            for square in [(a2-1, b2), (a2+1, b2)] :
                if fst(square) >= 0 and fst(square) < 8 :
                    a, b = square
                    if self.pieces_matrix[a][b] != None and self.pieces_matrix[a][b].type == "pawn" and self.pieces_matrix[a][b].color == self.get_opponent() :
                        self.attackers[self.get_opponent()][(a2, b1 + (b2-b1)//2)].append(square)
                        self.squares_attacked[self.get_opponent()][square].append((a2, b1 + (b2-b1)//2))
                        self.en_passant.append((square, (a2, b1 + (b2-b1)//2)))
        self.block_unblock_square(piece_position)
        self.block_unblock_square(new_position)
        self.player_turn = self.get_opponent()
        self.check = self.is_check()
        if compute_legal or self.check :
            self.compute_legal_moves()
            self.mate = self.is_mate()
            self.draw = self.is_draw()
        if graphics :
            self.show_appropriate_perspective()    
        self.previous_moves.append((piece_position, new_position, self.pieces_matrix[a2][b2]))
                
    # Blocks or unblocks a square to update the possible moves of all 
    # the long range pieces that were attacking this square
    def block_unblock_square(self, blocked_square) :
        for color in ["white", "black"] :
            attackers_copy = [attacker for attacker in self.attackers[color][blocked_square]]
            for square in attackers_copy :
                if self.pieces_matrix[fst(square)][snd(square)].type in ["bishop", "rook", "queen"] :
                    direction = sgn(fst(blocked_square) - fst(square)), sgn(snd(blocked_square) - snd(square))
                    a, b = fst(square) + fst(direction), snd(square) + snd(direction)
                    while a >= 0 and a < 8 and b >= 0 and b < 8 :
                        if square in self.attackers[color][(a, b)] :
                            self.attackers[color][(a, b)].remove(square)
                            self.squares_attacked[color][square].remove((a, b))
                        a, b = a + fst(direction), b + snd(direction)
                    a, b = fst(square) + fst(direction), snd(square) + snd(direction)
                    while a >= 0 and a < 8 and b >= 0 and b < 8 and self.pieces_matrix[a][b] == None :
                        self.attackers[color][(a, b)].append(square)
                        self.squares_attacked[color][square].append((a, b))
                        a, b = a + fst(direction), b + snd(direction)
                    if a >= 0 and a < 8 and b >= 0 and b < 8 :
                        self.attackers[color][(a, b)].append(square)
                        self.squares_attacked[color][square].append((a, b))
                elif self.pieces_matrix[fst(square)][snd(square)].type == "pawn" :
                    a, b = blocked_square
                    if fst(square) == fst(blocked_square) and abs(snd(blocked_square) - snd(square)) == 1 :
                        if (fst(square), snd(blocked_square)) in self.squares_attacked[color][square] :
                            if self.pieces_matrix[a][b] != None and ((a, b)) in self.squares_attacked[color][square] :
                                self.attackers[color][(a, b)].remove(square)
                                self.squares_attacked[color][square].remove((a, b))
                            elif ((a, b)) not in self.squares_attacked[color][square] :
                                self.attackers[color][(a, b)].append(square)
                                self.squares_attacked[color][square].append((a, b))
                                if not self.pieces_matrix[square].has_moved and self.pieces_matrix[a][b + (b - snd(square))] == None :
                                    self.attackers[color][(a, b + b - snd(square))].append(square)
                                    self.squares_attacked[color][square].append((a, b + b - snd(square)))
                        if snd(square) + 2*(snd(blocked_square) - snd(square)) >= 0 and snd(square) + 2*(snd(blocked_square) - snd(square)) < 8 :
                            if (fst(square), snd(square) + 2*(snd(blocked_square) - snd(square))) in self.squares_attacked[color][square] and self.pieces_matrix[a][b] != None :
                                self.attackers[color][(fst(square), snd(square) + 2*(snd(blocked_square) - snd(square)))].remove(square)
                                self.squares_attacked[color][square].remove((fst(square), snd(square) + 2*(snd(blocked_square) - snd(square))))
                            if (fst(square), snd(square) + 2*(snd(blocked_square) - snd(square))) not in self.squares_attacked[color][square] and self.pieces_matrix[a][b] == None :
                                if not self.pieces_matrix[fst(square)][snd(square)].has_moved :
                                    self.attackers[color][(fst(square), snd(square) + 2*(snd(blocked_square) - snd(square)))].append(square)
                                    self.squares_attacked[color][square].append((fst(square), snd(square) + 2*(snd(blocked_square) - snd(square))))
                    
    # Updates the lists of possible moves of each piece of the board
    def update_possible_moves(self) :
        for i in range(8) :
            for j in range(8) :
                self.possible_moves_from_square(i, j)
        self.player_turn = self.get_opponent()
        for i in range(8) :
            for j in range(8) :
                self.possible_moves_from_square(i, j)
        self.player_turn = self.get_opponent()
                    
    # Returns a boolean telling wether the current position is a 'check'
    def is_check(self) :
        for i in range(8) :
            for j in range(8) :
                if self.pieces_matrix[i][j] != None and self.pieces_matrix[i][j].type == "king" and self.pieces_matrix[i][j].color == self.player_turn :
                    return self.attackers[self.get_opponent()][(i, j)] != []
    
    # Returns a boolean telling wether the current position is a 'checkmate'
    def is_mate(self) :
        if self.check :
            for i in range(8) :
                for j in range(8) :
                    if self.legal_moves[(i, j)] != [] :
                        return False
            return True
        return False
    
    # Returns a boolean telling wether the current position is a 'draw'
    def is_draw(self) :
        if self.last_take_or_pawn_move >= 50 :
            return True
        if self.draw :
            return True
        if len(self.previous_moves) >= 10 and self.last_take_or_pawn_move >= 9 :
            i = 1
            while i <= 5 and self.previous_moves[-i] == self.previous_moves[-i-4] :
                i += 1
            if i == 6 :
                origin1, destination1, piece1 = self.previous_moves[-6]
                origin2, destination2, piece2 = self.previous_moves[-10]
                if destination1 == destination2 and piece1 == piece2 :
                    return True
        if len(self.previous_moves) >= 18 and self.last_take_or_pawn_move >= 17 :
            i = 1
            while i <= 18 and self.previous_moves[-i] == self.previous_moves[-i-6] :
                i += 1
            if i == 19 :
                return True
        if not self.check :
            i, j = 0, 0
            moves = []
            while i < 8 and moves == [] :
                if (i, j) not in self.illegal_moves :
                    print(self.illegal_moves)
                for square in self.squares_attacked[self.player_turn][(i, j)] :
                    if square not in self.illegal_moves[(i, j)] :
                        moves.append(square)
                        break
                if j == 7 :
                    i, j = i+1, 0
                else :
                    j += 1
            if i == 8 :
                return True
        return False
          
    # Variables used to show the rows and columns of the board      
    pg.font.init()
    black = (0, 0, 0)
    font = pg.font.SysFont("Arial", 30)
    global A, B, C, D, E, F, G, H
    A = font.render('A', 1, black)
    B = font.render('B', 1, black)
    C = font.render('C', 1, black)
    D = font.render('D', 1, black)
    E = font.render('E', 1, black)
    F = font.render('F', 1, black)
    G = font.render('G', 1, black)
    H = font.render('H', 1, black)
    global letters
    letters = [A, B, C, D, E, F, G, H]
    global N1, N2, N3, N4, N5, N6, N7, N8
    N1 = font.render('1', 1, black)
    N2 = font.render('2', 1, black)
    N3 = font.render('3', 1, black)
    N4 = font.render('4', 1, black)
    N5 = font.render('5', 1, black)
    N6 = font.render('6', 1, black)
    N7 = font.render('7', 1, black)
    N8 = font.render('8', 1, black)
    global numbers
    numbers = [N1, N2, N3, N4, N5, N6, N7, N8]
    
    # Flips the board to see the opposite perspective
    def flip_board(self) :
        if self.perspective == 'white' :
            self.perspective = 'black'
        else :
            self.perspective = 'white'
                   
    # Shows the board from the white player's perspective
    def show_white_perspective(self) :
        self.window.fill(background_color)
        self.window.blit(empty_board_sprite, (60, 60))
        if self.previous_moves != [] :
            move = self.previous_moves[-1]
            (i1, j1), (i2, j2), piece = move
            self.window.blit(previous_move_sprite, (60 + 60*i1, 480 - 60*j1))
            self.window.blit(previous_move_sprite, (60 + 60*i2, 480 - 60*j2))
        for i in range(8) :
            for j in range(8) :
                sprite = pieces_to_sprites(self.pieces_matrix[i][j])
                if sprite != None :
                    self.window.blit(sprite, (60 + fst(square_size)*i, 480 - snd(square_size)*j))
        for i in range(8) :
            self.window.blit(letters[i], (80 + 60*i, 540))
        for j in range(8) :
            self.window.blit(numbers[7-j], (35, 72 + 60*j))

    # Shows the board from the black player's perspective
    def show_black_perspective(self) :
        self.window.fill(background_color)
        self.window.blit(empty_board_sprite, (60, 60))
        if self.previous_moves != [] :
            move = self.previous_moves[-1]
            (i1, j1), (i2, j2), piece = move
            self.window.blit(previous_move_sprite, (60 + 60*(7-i1), 480 - 60*(7-j1)))
            self.window.blit(previous_move_sprite, (60 + 60*(7-i2), 480 - 60*(7-j2)))
        for i in range(8) :
            for j in range(8) :
                sprite = pieces_to_sprites(self.pieces_matrix[7-i][7-j])
                if sprite != None :
                    self.window.blit(sprite, (60 + fst(square_size)*i, 480 - snd(square_size)*j))
        for i in range(8) :
            self.window.blit(letters[7-i], (80 + 60*i, 540))
        for j in range(8) :
            self.window.blit(numbers[j], (35, 72 + 60*j))

    # Shows the perspective of the player whose turn it is
    def show_appropriate_perspective(self) :
        if self.perspective == 'white' :
            self.show_white_perspective()
        elif self.perspective == 'black' :
            self.show_black_perspective()
        else :
            raise Exception("Error : the perspective value {} is not valid.".format(self.perspective))
    
    # Hash function for the 'position' object
    def __hash__(self) :
        return hash_func(self.pieces_matrix) + hash(self.player_turn)
    
    # Equality test for 2 chess positions
    def __eq__(self, other) :
        return self.pieces_matrix == other.pieces_matrix and self.player_turn == other.player_turn

# Hash functions for python list and dict objects
def hash_func(object) :
    if type(object) == list :
        return hash(tuple([hash_func(element) for element in object]))
    elif type(object) == dict :
        return hash(tuple([hash_func(key) + hash_func(object[key]) for key in object]))
    else :
        return hash(object)


# Definition of the initial chess position
initial_position_matrix = [[None for j in range(8)] for i in range(8)]

for i in range(8) :
    initial_position_matrix[i][1] = pawn("white")
    initial_position_matrix[i][6] = pawn("black")
    
initial_position_matrix[0][0] = rook("white")
initial_position_matrix[1][0] = knight("white")
initial_position_matrix[2][0] = bishop("white")
initial_position_matrix[3][0] = queen("white")
initial_position_matrix[4][0] = king("white")
initial_position_matrix[5][0] = bishop("white")
initial_position_matrix[6][0] = knight("white")
initial_position_matrix[7][0] = rook("white")

initial_position_matrix[0][7] = rook("black")
initial_position_matrix[1][7] = knight("black")
initial_position_matrix[2][7] = bishop("black")
initial_position_matrix[3][7] = queen("black")
initial_position_matrix[4][7] = king("black")
initial_position_matrix[5][7] = bishop("black")
initial_position_matrix[6][7] = knight("black")
initial_position_matrix[7][7] = rook("black")

# Function that associates any 'piece' object to its corresponding sprite
def pieces_to_sprites(piece) :
    if piece == None :
        return None
    if piece.color == "white" and piece.type == "pawn" :
        return white_pawn_sprite
    if piece.color == "white" and piece.type == "bishop" :
        return white_bishop_sprite
    if piece.color == "white" and piece.type == "knight" :
        return white_knight_sprite
    if piece.color == "white" and piece.type == "rook" :
        return white_rook_sprite
    if piece.color == "white" and piece.type == "king" :
        return white_king_sprite
    if piece.color == "white" and piece.type == "queen" :
        return white_queen_sprite
    if piece.color == "black" and piece.type == "pawn" :
        return black_pawn_sprite
    if piece.color == "black" and piece.type == "bishop" :
        return black_bishop_sprite
    if piece.color == "black" and piece.type == "knight" :
        return black_knight_sprite
    if piece.color == "black" and piece.type == "rook" :
        return black_rook_sprite
    if piece.color == "black" and piece.type == "king" :
        return black_king_sprite
    if piece.color == "black" and piece.type == "queen" :
        return black_queen_sprite
    else :
        return None

font = pg.font.SysFont("Arial", 30)
black = (0, 0, 0)

# Lauches a chess game
def play() :
    window.fill(background_color)
    board_state = position(initial_position_matrix, window, "white")
    board_state.update_possible_moves()
    board_state.compute_legal_moves()
    board_state.show_appropriate_perspective()
    keep = True
    while keep :
        pg.time.Clock().tick(100)
        for event in pg.event.get() :
            if event.type == KEYDOWN and event.key == K_ESCAPE :
                keep = False
            if event.type == KEYDOWN and event.key == K_f :
                board_state.flip_board()
                board_state.show_appropriate_perspective()
            if event.type == MOUSEBUTTONDOWN and event.button == 1 :
                x, y = pg.mouse.get_pos()
                board_state.click_on_position(x, y)
            if event.type == KEYDOWN and event.key == K_SPACE :
                print(board_state.previous_moves)
        if board_state.is_mate() :
            rectangle = pg.Rect(175, 210, 250, 130)
            pg.draw.rect(window, (255, 255, 255), rectangle)
            label = font.render("Game over.", 1, black)
            window.blit(label, (230, 220))
            if board_state.player_turn == 'white' :
                label2 = font.render("Black player won.", 1, black)
            else :
                label2 = font.render("White player won.", 1, black)
            window.blit(label2, (190, 280))
        elif board_state.is_draw() :
            rectangle = pg.Rect(175, 210, 250, 130)
            pg.draw.rect(window, (255, 255, 255), rectangle)
            label = font.render("Game over.", 1, black)
            window.blit(label, (230, 220))
            label2 = font.render("It's a tie.", 1, black)
            window.blit(label2, (250, 280))
        pg.display.flip()

    pg.quit()
            
if __name__ == '__main__' :
    play()
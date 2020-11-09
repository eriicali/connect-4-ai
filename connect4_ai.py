import numpy
import pygame
import math
import random
import sys

# global variables

# colour RGB values
# board colour
BLUE = (15, 100, 255)

# text colour
BLACK = (0, 0, 0)

# empty space
WHITE = (255, 255, 255)

# player chip
RED = (255, 0, 0)

# ai chip
YELLOW = (255, 255, 0)

# number of rows and columns in the connect 4 board
ROWS = 6
COLUMNS = 7

# the side length of the square that each circle is bounded within
SIDELENGTH = 100

# radius of each chip
RADIUS = int(SIDELENGTH / 2 - 5)

# player is represented by 0, AI is represented by 1
PLAYER = 0
AI = 1

# since the board is filled with zeros at the start, we will use 1 to represent the player piece and 2 to represent the AI piece
PLAYER_CHIP = 1
AI_CHIP = 2

# empty spot is represented by 0
EMPTY = 0

# the "window" is the length of partitions of the board we'll be inspecting to check for wins
# since the game is connect 4, the window length will be 4
WIN_LENGTH = 4


# this function create a new board
def create_board():
    # np.zeros returns a new array of a given size, filled with zeros.
    myBoard = numpy.zeros((ROWS, COLUMNS))
    return myBoard


# this function drops a new chip in the board at a specified position
def drop_chip(myBoard, myRow, myCol, chip):
    myBoard[myRow][myCol] = chip


# this function draws the connect 4 board
def draw_board(myBoard):
    # draws the blue background and the white circles representing empty spots
    for c in range(COLUMNS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c * SIDELENGTH, r * SIDELENGTH + SIDELENGTH, SIDELENGTH, SIDELENGTH))
            pygame.draw.circle(screen, WHITE, (int(c * SIDELENGTH + SIDELENGTH / 2), int(r * SIDELENGTH + SIDELENGTH + SIDELENGTH / 2)), RADIUS)
    # draws all the chips put in by the AI and the player
    for c in range(COLUMNS):
        for r in range(ROWS):
            if myBoard[r][c] == PLAYER_CHIP:
                pygame.draw.circle(screen, RED, (int(c * SIDELENGTH + SIDELENGTH / 2), height - int(r * SIDELENGTH + SIDELENGTH / 2)), RADIUS)
            elif myBoard[r][c] == AI_CHIP:
                pygame.draw.circle(screen, YELLOW, (int(c * SIDELENGTH + SIDELENGTH / 2), height - int(r * SIDELENGTH + SIDELENGTH / 2)), RADIUS)
    pygame.display.update()


# this function checks whether the specified column has any remaining spots
def has_spots_left(myBoard, myCol) -> bool:
    return myBoard[ROWS - 1][myCol] == 0


# this function gets the next available row in the specified column
def next_empty_row(myBoard, myCol) -> int:
    for r in range(ROWS):
        if myBoard[r][myCol] == 0:
            return r


# this function returns a list of columns that have empty spaces left
def get_valid_columns(myBoard) -> list:
    valid_columns = []
    for c in range(COLUMNS):
        if has_spots_left(myBoard, c):
            valid_columns.append(c)
    return valid_columns


# this function checks the entire board for winning moves
def has_win(myBoard, chip) -> bool:
    # check horizontal locations for win
    for c in range(COLUMNS - 3):
        for r in range(ROWS):
            if myBoard[r][c] == chip and myBoard[r][c + 1] == chip and myBoard[r][c + 2] == chip and myBoard[r][c + 3] == chip:
                return True

    # check vertical locations for win
    for c in range(COLUMNS):
        for r in range(ROWS - 3):
            if myBoard[r][c] == chip and myBoard[r + 1][c] == chip and myBoard[r + 2][c] == chip and myBoard[r + 3][c] == chip:
                return True

    # check positively sloped diagonals for win
    for c in range(COLUMNS - 3):
        for r in range(ROWS - 3):
            if myBoard[r][c] == chip and myBoard[r + 1][c + 1] == chip and myBoard[r + 2][c + 2] == chip and myBoard[r + 3][c + 3] == chip:
                return True

    # check negatively sloped diagonals for win
    for c in range(COLUMNS - 3):
        for r in range(3, ROWS):
            if myBoard[r][c] == chip and myBoard[r - 1][c + 1] == chip and myBoard[r - 2][c + 2] == chip and myBoard[r - 3][c + 3] == chip:
                return True
    return False


# this function determines the score of a certain window on the connect 4 board
def score_window(window, chip) -> int:
    # initialize the opponent piece based who's turn it is
    opponent_chip = PLAYER_CHIP
    if chip == PLAYER_CHIP:
        opponent_chip = AI_CHIP
    score = 0
    # a win is weighted 100
    if window.count(chip) == 4:
        score += 150
    # 3 pieces in a window and an empty space is almost a win, so it's weighted 10
    elif window.count(chip) == 3 and window.count(EMPTY) == 1:
        score += 50
    # 2 pieces in a window and 2 empty spaces is weighted 5
    elif window.count(chip) == 2 and window.count(EMPTY) == 2:
        score += 2
    # if the opponent is close to a win, the weighting is negative
    if window.count(opponent_chip) == 3 and window.count(EMPTY) == 1:
        score -= 100
    if window.count(opponent_chip) == 2 and window.count(EMPTY) == 2:
        score -= 5
    return score


# this function returns the total score of a specified player based on the current board
def get_total_score(myBoard, chip) -> int:
    score = 0
    window = []
    # count the number of pieces for a specified player in the center column
    # make it prefer the center column
    # center_col = [i for i in list(myBoard[:, 3])]
    center_col = [myBoard[i][3] for i in range(ROWS)]
    center_col_count = center_col.count(chip)
    score += center_col_count * 8
    # count the total score for the rows
    for r in range(ROWS):
        row_array = list(myBoard[r])
        for c in range(COLUMNS-3):
            window = row_array[c:c+WIN_LENGTH]
            score += score_window(window, chip)
    # count the total score for the columns
    for c in range(COLUMNS):
        col_array = [int(i) for i in list(myBoard[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r+WIN_LENGTH]
            score += score_window(window, chip)
    # count the total score for positively sloped diagonals
    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            window = [myBoard[r+i][c+i] for i in range(WIN_LENGTH)]
        score += score_window(window, chip)
    # count the total score for negatively sloped diagonals
    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            window = [myBoard[r+3-i][c+i] for i in range(WIN_LENGTH)]
        score += score_window(window, chip)
    return score


# helper function for my minimax algorithm
# checks whether the node is a terminal node (somebody won, or a tie occurred)
def is_terminal_node(myBoard) -> bool:
    return has_win(myBoard, PLAYER_CHIP) or has_win(myBoard, AI_CHIP) or len(get_valid_columns(myBoard)) == 0


# this function determines the best column to drop the AI chip in
def minimax(myBoard, depth, maximizingPlayer) -> tuple:
    # find all the columns that still have empty spaces
    valid_locations = get_valid_columns(myBoard)
    is_terminal = is_terminal_node(myBoard)
    # base case
    if depth == 0 or is_terminal:
        if is_terminal:
            # AI won
            if has_win(myBoard, AI_CHIP):
                return None, 100000000
            # Player won
            elif has_win(myBoard, PLAYER_CHIP):
                return None, -100000000
            # tie
            else:
                return None, 0
        # depth == 0
        else:
            return None, get_total_score(myBoard, AI_CHIP)
    # recursive case
    # maximizing player is AI
    if maximizingPlayer:
        column = 0
        value = -math.inf
        # iterate through all the valid columns
        for c in valid_locations:
            # get the next open row
            r = next_empty_row(myBoard, c)
            # create a copy of the board in a separate memory location
            # the purpose of this copy is to "look into the future"
            # and determine which one is the best column to drop the chip in
            b_copy = myBoard.copy()
            drop_chip(b_copy, r, c, AI_CHIP)
            # takes index 1 since minimax() returns a tuple of size 2
            # recursive call
            score = minimax(b_copy, depth-1, False)[1]
            # search for the highest new score
            if score > value:
                value = score
                column = c
        return column, value
    # minimizing player: person
    else:
        column = 0
        value = math.inf
        # iterate through all the valid columns
        for c in valid_locations:
            # create a copy of the board in a separate memory location
            # the purpose of this copy is to "look into the future"
            # and determine which one is the best column to drop the chip in
            r = next_empty_row(myBoard, c)
            b_copy = myBoard.copy()
            drop_chip(b_copy, r, c, PLAYER_CHIP)
            # takes index 1 since minimax() returns a tuple of size 2
            # recursive call
            score = minimax(b_copy, depth-1, True)[1]
            # search for the lowest new score
            if score < value:
                value = score
                column = c
        return column, value


board = create_board()

game_over = False

pygame.init()
# width of game window
width = COLUMNS * SIDELENGTH
# height of game window
height = (ROWS + 1) * SIDELENGTH
# size of game window as a tuple
size = (width, height)

screen = pygame.display.set_mode(size)

draw_board(board)

pygame.display.update()

font = pygame.font.SysFont("monospace", 80)
drop_sound = pygame.mixer.Sound("dropping.wav")
# randomize who goes first
turn = random.randint(PLAYER, AI)

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        # draw white rectangle at the top
        pygame.draw.rect(screen, WHITE, (0, 0, width, SIDELENGTH))
        if event.type == pygame.MOUSEMOTION:
            xCoor = event.pos[0]
            # have the chip follow the mouse of the player
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (xCoor, int(SIDELENGTH / 2)), RADIUS)
        pygame.display.update()
        # drop chip
        if event.type == pygame.MOUSEBUTTONDOWN:
            if turn == PLAYER:
                xCoor = event.pos[0]
                # calculate the column to drop the chip in
                col = int(math.floor(xCoor / SIDELENGTH))

                if has_spots_left(board, col):
                    row = next_empty_row(board, col)
                    # drop chip in the next empty row
                    drop_chip(board, row, col, PLAYER_CHIP)
                    drop_sound.play()
                    if has_win(board, PLAYER_CHIP):
                        # display message telling the user who won
                        label = font.render("RED WINS", 1, BLACK)
                        screen.blit(label, (40, 10))
                        game_over = True
                    turn += 1
                    turn = turn % 2
                    draw_board(board)
    # keep the program running for 4 more seconds after the game is over
    # this allows the user to confirm who won and who lost
    if game_over:
        pygame.time.wait(5000)
    # AI Input
    if turn == AI and not game_over:
        # tuple unpacking the two return values
        col, minimax_score = minimax(board, 3, True)
        if has_spots_left(board, col):
            # the AI takes 1 second to place their move
            pygame.time.wait(500)
            row = next_empty_row(board, col)
            drop_chip(board, row, col, AI_CHIP)
            drop_sound.play()
            if has_win(board, AI_CHIP):
                # display message telling the user who won
                label = font.render("YELLOW WINS", 1, BLACK)
                screen.blit(label, (40, 10))
                game_over = True
            draw_board(board)
            turn += 1
            turn = turn % 2
    # keep the program running for 4 more seconds after the game is over
    # this allows the user to confirm who won and who lost
    if game_over:
        pygame.time.wait(5000)

from pyautogui import click, locateAll, screenshot
from cv2 import imread
from keyboard import is_pressed
from chess import Board
from chess import engine as eng
from fen_maker import make_fen
from time import sleep
from pyscreeze import ImageNotFoundException
print("Imports done")

#lichess
BOARD_SIZE = 728
CELL_SIZE = BOARD_SIZE//8
BOARD_TOP = 276
BOARD_LEFT = 108
# 108,276
# 837,1004
CONFIDENCE = 0.7

img_path = r"lichesspieces\\"
    
# settings map to control output and logging
settings = {
    'show board':True,
    'show line':False,
    'line upper limit':10
}

piece_map = {
    0: 'black_king',
    1: 'black_queen',
    2: 'black_rook',
    3: 'black_bishop',
    4: 'black_knight',
    5: 'black_pawn',
    6: 'white_king',
    7: 'white_queen',
    8: 'white_rook',
    9: 'white_bishop',
    10: 'white_knight',
    11: 'white_pawn'
}

fen_map = {
    0: 'k',
    1: 'q',
    2: 'r',
    3: 'b',
    4: 'n',
    5: 'p',
    6: 'K',
    7: 'Q',
    8: 'R',
    9: 'B',
    10: 'N',
    11: 'P'
}

# initialize images into memory for faster function (images do not have to be retreived every move)
img_map = {}
for p in range(12):
    piece_path = img_path + piece_map[p] + ".png"
    img_map[p] = imread(piece_path)

# function to wait for change in board (opponent moved)
def wait_for_board_change():
    board_img = screenshot('screenshot.png',(BOARD_LEFT,BOARD_TOP,BOARD_SIZE,BOARD_SIZE))
    while screenshot('screenshot.png',(BOARD_LEFT,BOARD_TOP,BOARD_SIZE,BOARD_SIZE))==board_img:
        if is_pressed('r'): return 0
        continue
    sleep(1)
    return 1

# make fen from board (fen needed to generate chess.Board which engine needs)
def make_fen(board_img):
    # initialize board and take ss of board
    board_matrix = [['_' for _ in range(8)] for __ in range(8)]

    # detect each piece on board ss
    for p in range(12):
        # get boxes of each piece occurence
        try:    arr = list(locateAll(img_map[p],board_img,confidence=CONFIDENCE))
        except ImageNotFoundException:  continue
        # convert img coords into x,y
        for i in range(len(arr)):
            box = arr[i]
            x = round(box.left/CELL_SIZE)
            y = round(box.top/CELL_SIZE)
            arr[i] = (x,y)
        
        # arr has multiple dupicate positions
        # list(set(arr)) removes them
        arr = list(set(arr))

        # add piece to board matrix
        for x,y in arr:
            board_matrix[y][x] = fen_map[p]

    if side=='b':
        for i in range(4):
            board_matrix[i] = board_matrix[i][::-1]
            board_matrix[7-i] = board_matrix[7-i][::-1]
            board_matrix[i],board_matrix[7-i] = board_matrix[7-i],board_matrix[i]

    #make fen
    fen = ''
    for row in board_matrix:
        gap = 0
        for i in range(8):
            square = row[i]
            # if blank, increment gap
            if square=="_":
                gap+=1
                if i==7:    fen+=str(gap) # if row ends with blanks, add gap to fen
            else:
                if gap!=0: #consecutive pieces have gap=0
                    fen+=str(gap)
                    gap = 0
                fen+=square
        fen+='/'
    return fen[:-1]+' '+side #remove last '/'

# file map to convert board coord to screen coord
file_map = {
    'a':0,
    'b':1,
    'c':2,
    'd':3,
    'e':4,
    'f':5,
    'g':6,
    'h':7
}

# converts board coord to screen coord and then moves piece
def make_move(move:str): # move is 4 letter str with square coords, eg: e2e4
    x1 = file_map[move[0]]
    y1 = 8-int(move[1])
    x2 = file_map[move[2]]
    y2 = 8-int(move[3])
    #convertions for black
    if side=='b':
        x1 = 7-x1
        x2 = 7-x2
        y1 = 7-y1
        y2 = 7-y2
    
    # conv to screen coords
    x1 = int(BOARD_LEFT+CELL_SIZE*(x1+0.5))
    x2 = int(BOARD_LEFT+CELL_SIZE*(x2+0.5))
    y1 = int(BOARD_TOP+CELL_SIZE*(y1+0.5))
    y2 = int(BOARD_TOP+CELL_SIZE*(y2+0.5))

    #make move
    click(x1,y1)
    click(x2,y2)

    if move[-1] in 'qnrb':
        promote_y = {'q':7,'n':6,'r':5,'b':4}[move[-1]]
        y = int(BOARD_TOP+CELL_SIZE*(7.5-promote_y))
        #sleep(1)
        click(x2,y)

    sleep(0.5)
    return

# gets fen, makes board, gets move, gets info/analysis, makes move, outputs eval (and board if enabled)
def compute_and_move():
    cur_fen = make_fen(screenshot('screenshot.png',(BOARD_LEFT,BOARD_TOP,BOARD_SIZE,BOARD_SIZE))) #gets board and fen
    board = Board(fen=cur_fen) # converted to chess.Board
    
    if settings['show board']: # prints board if enabled
        print("Loaded board with position:",cur_fen)
        print(board)
    
    analysis = engine.analyse(board,lim) # analyses
    print("Depth:",analysis['depth']) # depth to which engine searched
    
    score = analysis['score'] # get score from engine
    eval = str(score.white())

    if eval=='0':    eval = '0.00'   # if eval=='0', output '0.00'
    elif '#' in eval:   eval = eval[1]+'M'+eval[2:] # if mate, output <sign> M <moves>
    else:   eval = eval[0]+"{:.2f}".format(int(eval[1:])/100) # if normal eval, print in pawns (not centipawns)
    print("Eval:",eval)
    
    line = analysis['pv'] # gets optimal line
    best_move = str(line[0]) # best move
    print("Best move:",best_move)

    if settings['show line']:
        print('Optimal Line: ',end='')
        line_len = min(len(line),settings['line upper limit'])
        if line_len==1:
            print(line[0])
        else:
            for i in range(line_len-1):   print(str(line[i]),end=',')
            print(str(line[i+1]))
    
    print()
    make_move(best_move) # actually make move


# show available engines
print("Code | Name                      | Estimated Elo ")
print("0    | Stockfish 16              | 3600          ")
print("1    | Stockfish 15              | 3585          ")
print("2    | Stockfish 14              | 3525          ")
print("3    | Berserk                   | 3490          ")
print("4    | Ethereal 14               | 3485          ")
print("5    | Komodo 14                 | 3460          ")
print("6    | Leela Chess DNNL BLAS     | 3370          ")
print("7    | Octochess                 | 2883          ")

# get engine code from user
eng_code = input("Enter engine code: ")
while eng_code not in '01234567' or eng=='':  eng_code = input("Enter engine code: ")
eng_code = int(eng_code)
eng_path_map = {
    0:r'Engines\stockfish_16\stockfish-windows-x86-64-avx2.exe',
    1:r'Engines\stockfish_15\stockfish_15_win_x64_popcnt\stockfish_15_x64_popcnt.exe',
    2:r'Engines\stockfish_14\stockfish_14_win_x64_popcnt\stockfish_14_x64_popcnt.exe',
    3:r'Engines\Berserk-11.1_Windows_x64\Berserk-11.1_Windows_x86-64-popcnt.exe',
    4:r'Engines\ethereal_14\Ethereal-14.07_Windows_x64\Ethereal-14.07_Windows_x86-64-ssse3.exe',
    5:r'Engines\komodo-14\Windows\komodo-14.1-64bit-bmi2.exe',
    6:r'Engines\leela chess 0\lc0.exe',
    7:r'Engines\Octochess\octochess-r5190\octochess-windows-generic-r5190.exe'
}
engine_path = eng_path_map[eng_code]
engine = eng.SimpleEngine.popen_uci(engine_path) #synchronised engine
print("Engine loaded")

# input time limit per move
def inp_time():
    while True:
        try:
            t = float(input("Enter time limit per move: "))
            if t<=0:    raise ValueError
            break
        except ValueError:
            continue
    return t

# main driver begins
while True:
    lim = eng.Limit(time=inp_time()) # set time limit for engine (in seconds)
    
    # side/color input
    side = input("White or Black (w/b): ")
    while side not in ['w','b']:    side = input("White or Black (w/b): ")

    input("Press enter to make first move")
    # make first move without board change as it might not be detected
    try:
        compute_and_move()
    except Exception as e:
        print(e)

    while not is_pressed('r'): # play game until 'r' is pressed (or error is raised)
        wait_for_board_change()
        if is_pressed('r'):
            break
        try:
            compute_and_move()
        except eng.EngineTerminatedError: # probable board eror
            print("Engine died unexpectedly")
            break
        except eng.EngineError:
            print("Engine died unexpectedly") # probabale board error
            break
        except Exception as e:
            print(e)
    
    # in case of error or user input ('r'), reload fresh engine
    print("New game initialized")
    del engine
    engine = eng.SimpleEngine.popen_uci(engine_path)
    print("Engine reloaded")
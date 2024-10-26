from pyautogui import locateAll,screenshot
from cv2 import imread
from pyscreeze import ImageNotFoundException

#lichess
BOARD_SIZE = 728
CELL_SIZE = BOARD_SIZE//8
BOARD_TOP = 276
BOARD_LEFT = 108
# 108,276
# 837,1004
CONFIDENCE = 0.7

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

# initialize images into memory for faster function
img_map = {}
for p in range(12):
    piece_path = r"lichesspieces\\" + piece_map[p] + ".png"
    img_map[p] = imread(piece_path)

def make_fen(side:str):
    # initialize board and take ss of board
    board_img = screenshot('screenshot.png',(BOARD_LEFT,BOARD_TOP,BOARD_SIZE,BOARD_SIZE))
    board_matrix = [['_' for _ in range(8)] for __ in range(8)]

    # detect each piece on board ss
    for p in range(12):
        # get boxes of each piece occurence
        try:
            arr = list(locateAll(img_map[p],board_img,confidence=CONFIDENCE))
        except ImageNotFoundException:
            continue
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

print(make_fen(''))
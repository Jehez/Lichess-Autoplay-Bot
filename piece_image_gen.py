#lichess play stockfish as white
#take ss before move

import cv2
from cv2 import imread,imshow,waitKey,destroyAllWindows
from pyautogui import screenshot

#lichess
BOARD_SIZE = 728
CELL_SIZE = BOARD_SIZE//8
BOARD_TOP = 276
BOARD_LEFT = 108
# 108,276
# 837,1004

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

# take a screenshot
screenshot('screenshot.png',(BOARD_LEFT,BOARD_TOP,BOARD_SIZE,BOARD_SIZE))

ss = imread('screenshot.png')

piece_code = 0

# row,col co_ords
co_ords = [
    (0,4),
    (0,3),
    (0,0),
    (0,2),
    (0,1),
    (1,0),
    (7,4),
    (7,3),
    (7,0),
    (7,2),
    (7,1),
    (6,0)
]

peice_code = 0
for row,col in co_ords:
    x = col*CELL_SIZE
    y = row*CELL_SIZE
    piece_image = ss[y:y + CELL_SIZE, x: x + CELL_SIZE]
    imshow('scr', piece_image)
    waitKey(0)
    path = r"lichesspieces\\" + piece_map[piece_code] + ".png"
    cv2.imwrite(path, piece_image)
    piece_code+=1

# clean up windows
destroyAllWindows()
'''
led8x8Font.py
  Horizontal raster data for a simple 8x8 font.
'''
import time

# global oct2bin = ['000','001','010','011','100','101','110','111']
global OCT2BIN
OCT2BIN = ['___','__*','_*_','_**','*__','*_*','**_','***']

# from 8x8font.h
#
FontData = {
    " ": [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00], # space 0x20
    "!": [0x30,0x78,0x78,0x30,0x30,0x00,0x30,0x00], # !
    "\"": [0x6C,0x6C,0x6C,0x00,0x00,0x00,0x00,0x00], # "
    "#": [0x6C,0x6C,0xFE,0x6C,0xFE,0x6C,0x6C,0x00], # #
    "$": [0x18,0x3E,0x60,0x3C,0x06,0x7C,0x18,0x00], # $
    "%": [0x00,0x63,0x66,0x0C,0x18,0x33,0x63,0x00], # %
    "&": [0x1C,0x36,0x1C,0x3B,0x6E,0x66,0x3B,0x00], # &
    "'": [0x30,0x30,0x60,0x00,0x00,0x00,0x00,0x00], # '
    "(": [0x0C,0x18,0x30,0x30,0x30,0x18,0x0C,0x00], # (
    ")": [0x30,0x18,0x0C,0x0C,0x0C,0x18,0x30,0x00], # )
    "*": [0x00,0x66,0x3C,0xFF,0x3C,0x66,0x00,0x00], # *
    "+": [0x00,0x30,0x30,0xFC,0x30,0x30,0x00,0x00], # +
    ",": [0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x30], # ,
    "-": [0x00,0x00,0x00,0x7E,0x00,0x00,0x00,0x00], # -
    ".": [0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x00], # .
    "/": [0x03,0x06,0x0C,0x18,0x30,0x60,0x40,0x00], # /
    "0": [0x3E,0x63,0x63,0x6B,0x63,0x63,0x3E,0x00], # 0 0x30
    "1": [0x18,0x38,0x58,0x18,0x18,0x18,0x7E,0x00], # 1
    "2": [0x3C,0x66,0x06,0x1C,0x30,0x66,0x7E,0x00], # 2
    "3": [0x3C,0x66,0x06,0x1C,0x06,0x66,0x3C,0x00], # 3
    "4": [0x0E,0x1E,0x36,0x66,0x7F,0x06,0x0F,0x00], # 4
    "5": [0x7E,0x60,0x7C,0x06,0x06,0x66,0x3C,0x00], # 5
    "6": [0x1C,0x30,0x60,0x7C,0x66,0x66,0x3C,0x00], # 6
    "7": [0x7E,0x66,0x06,0x0C,0x18,0x18,0x18,0x00], # 7
    "8": [0x3C,0x66,0x66,0x3C,0x66,0x66,0x3C,0x00], # 8
    "9": [0x3C,0x66,0x66,0x3E,0x06,0x0C,0x38,0x00], # 9
    ":": [0x00,0x18,0x18,0x00,0x00,0x18,0x18,0x00], # :
    ";": [0x00,0x18,0x18,0x00,0x00,0x18,0x18,0x30], # ;
    "<": [0x0C,0x18,0x30,0x60,0x30,0x18,0x0C,0x00], # <
    "=": [0x00,0x00,0x7E,0x00,0x00,0x7E,0x00,0x00], # =
    ">": [0x30,0x18,0x0C,0x06,0x0C,0x18,0x30,0x00], # >
    "?": [0x3C,0x66,0x06,0x0C,0x18,0x00,0x18,0x00], # ?
    "\@": [0x3E,0x63,0x6F,0x69,0x6F,0x60,0x3E,0x00], # @ 0x40
    "A": [0x18,0x3C,0x66,0x66,0x7E,0x66,0x66,0x00], # A
    "B": [0x7E,0x33,0x33,0x3E,0x33,0x33,0x7E,0x00], # B
    "C": [0x1E,0x33,0x60,0x60,0x60,0x33,0x1E,0x00], # C
    "D": [0x7C,0x36,0x33,0x33,0x33,0x36,0x7C,0x00], # D
    "E": [0x7F,0x31,0x34,0x3C,0x34,0x31,0x7F,0x00], # E
    "F": [0x7F,0x31,0x34,0x3C,0x34,0x30,0x78,0x00], # F
    "G": [0x1E,0x33,0x60,0x60,0x67,0x33,0x1F,0x00], # G
    "H": [0x66,0x66,0x66,0x7E,0x66,0x66,0x66,0x00], # H
    "I": [0x3C,0x18,0x18,0x18,0x18,0x18,0x3C,0x00], # I
    "J": [0x0F,0x06,0x06,0x06,0x66,0x66,0x3C,0x00], # J
    "K": [0x73,0x33,0x36,0x3C,0x36,0x33,0x73,0x00], # K
    "L": [0x78,0x30,0x30,0x30,0x31,0x33,0x7F,0x00], # L
    "M": [0x63,0x77,0x7F,0x7F,0x6B,0x63,0x63,0x00], # M
    "N": [0x63,0x73,0x7B,0x6F,0x67,0x63,0x63,0x00], # N
    "O": [0x3E,0x63,0x63,0x63,0x63,0x63,0x3E,0x00], # O
    "P": [0x7E,0x33,0x33,0x3E,0x30,0x30,0x78,0x00], # P 0x50
    "Q": [0x3C,0x66,0x66,0x66,0x6E,0x3C,0x0E,0x00], # Q
    "R": [0x7E,0x33,0x33,0x3E,0x36,0x33,0x73,0x00], # R
    "S": [0x3C,0x66,0x30,0x18,0x0C,0x66,0x3C,0x00], # S
    "T": [0x7E,0x5A,0x18,0x18,0x18,0x18,0x3C,0x00], # T
    "U": [0x66,0x66,0x66,0x66,0x66,0x66,0x7E,0x00], # U
    "V": [0x66,0x66,0x66,0x66,0x66,0x3C,0x18,0x00], # V
    "W": [0x63,0x63,0x63,0x6B,0x7F,0x77,0x63,0x00], # W
    "X": [0x63,0x63,0x36,0x1C,0x1C,0x36,0x63,0x00], # X
    "Y": [0x66,0x66,0x66,0x3C,0x18,0x18,0x3C,0x00], # Y
    "Z": [0x7F,0x63,0x46,0x0C,0x19,0x33,0x7F,0x00], # Z
    "": [0x3C,0x30,0x30,0x30,0x30,0x30,0x3C,0x00], # [
    "\\": [0x60,0x30,0x18,0x0C,0x06,0x03,0x01,0x00], # \ (backslash)
    "]": [0x3C,0x0C,0x0C,0x0C,0x0C,0x0C,0x3C,0x00], # ]
    "^": [0x08,0x1C,0x36,0x63,0x00,0x00,0x00,0x00], # ^
    "_": [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF], # _
    "`": [0x18,0x18,0x0C,0x00,0x00,0x00,0x00,0x00], # ` 0x60
    "a": [0x00,0x00,0x3C,0x06,0x3E,0x66,0x3B,0x00], # a
    "b": [0x70,0x30,0x3E,0x33,0x33,0x33,0x6E,0x00], # b
    "c": [0x00,0x00,0x3C,0x66,0x60,0x66,0x3C,0x00], # c
    "d": [0x0E,0x06,0x3E,0x66,0x66,0x66,0x3B,0x00], # d
    "e": [0x00,0x00,0x3C,0x66,0x7E,0x60,0x3C,0x00], # e
    "f": [0x1C,0x36,0x30,0x78,0x30,0x30,0x78,0x00], # f
    "g": [0x00,0x00,0x3B,0x66,0x66,0x3E,0x06,0x7C], # g
    "h": [0x70,0x30,0x36,0x3B,0x33,0x33,0x73,0x00], # h
    "i": [0x18,0x00,0x38,0x18,0x18,0x18,0x3C,0x00], # i
    "j": [0x06,0x00,0x06,0x06,0x06,0x66,0x66,0x3C], # j
    "k": [0x70,0x30,0x33,0x36,0x3C,0x36,0x73,0x00], # k
    "l": [0x38,0x18,0x18,0x18,0x18,0x18,0x3C,0x00], # l
    "m": [0x00,0x00,0x66,0x7F,0x7F,0x6B,0x63,0x00], # m
    "n": [0x00,0x00,0x7C,0x66,0x66,0x66,0x66,0x00], # n
    "o": [0x00,0x00,0x3C,0x66,0x66,0x66,0x3C,0x00], # o
    "p": [0x00,0x00,0x6E,0x33,0x33,0x3E,0x30,0x78], # p 0x70
    "q": [0x00,0x00,0x3B,0x66,0x66,0x3E,0x06,0x0F], # q
    "r": [0x00,0x00,0x6E,0x3B,0x33,0x30,0x78,0x00], # r
    "s": [0x00,0x00,0x3E,0x60,0x3C,0x06,0x7C,0x00], # s
    "t": [0x08,0x18,0x3E,0x18,0x18,0x1A,0x0C,0x00], # t
    "u": [0x00,0x00,0x66,0x66,0x66,0x66,0x3B,0x00], # u
    "v": [0x00,0x00,0x66,0x66,0x66,0x3C,0x18,0x00], # v
    "w": [0x00,0x00,0x63,0x6B,0x7F,0x7F,0x36,0x00], # w
    "x": [0x00,0x00,0x63,0x36,0x1C,0x36,0x63,0x00], # x
    "y": [0x00,0x00,0x66,0x66,0x66,0x3E,0x06,0x7C], # y
    "z": [0x00,0x00,0x7E,0x4C,0x18,0x32,0x7E,0x00], # z
    "{": [0x0E,0x18,0x18,0x70,0x18,0x18,0x0E,0x00], # {
    "|": [0x0C,0x0C,0x0C,0x00,0x0C,0x0C,0x0C,0x00], # |
    "}": [0x70,0x18,0x18,0x0E,0x18,0x18,0x70,0x00], # }
    "~": [0x3B,0x6E,0x00,0x00,0x00,0x00,0x00,0x00]  # ~
}


def bin(x, digits=0):
    global OCT2BIN
    binstring = [OCT2BIN[int(n)] for n in oct(x)]
    return ''.join(binstring).lstrip('0').zfill(digits)
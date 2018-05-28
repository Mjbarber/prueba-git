import os
import sqlite3

# The score and number of tiles for each letter in the Spanish version
# of the game
# 2 cuadros en blanco (0 puntos)
# 1 punto: A ×11, E ×11, O ×8, S ×7, I ×6, U ×6, N ×5, L ×4, R ×4, T ×4
# 2 puntos: C ×4, D ×4, G ×2
# 3 puntos: M ×3, B ×3, P ×2
# 4 puntos: F ×2, H ×2, V ×2, Y ×1
# 6 puntos: J ×2
# 8 puntos: K ×1, LL ×1, Ñ ×1, Q ×1, RR ×1, W ×1, X ×1
# 10 puntos: Z ×1

# A string with each letter in the Spanish alphabet
abecedario = 'abcdefghijklmnñopqrstuvwxyz'

conn = sqlite3.connect('scrabble.sqlite')
cur = conn.cursor()

# A SQLite DB where we will store the words and its scores
cur.execute('''CREATE TABLE IF NOT EXISTS Words(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    word TEXT UNIQUE,
    score INTEGER,
    valid BOOLEAN
)''')

# A function to clean a word for the scoring
def clean_word(pal):
    accents = ['á', 'é', 'í', 'ó', 'ú']
    no_accents = ['a', 'e', 'i' ,'o', 'u']    
    # We get the word in lower case, and in the first genre 
    # (the 2nd goes after , in our dictionaries)
    cad = pal.lower().strip()
    if ',' in cad:
        cad = cad[ : cad.find(',')]
    # We get the word with no accents nor capital letters
    for i in range(4):
        if accents[i] in cad:
            cad = cad.replace(accents[i], no_accents[i])
            break
    return cad        


# A function to get the score of a word
def get_sc(word):
    # A dictionary with the score of each letter in the game
    sc_dic = {'a': 1,  'e': 1, 'o': 1, 's': 1, 'i': 1,
        'u': 1, 'n': 1, 'l': 1, 'r': 1, 't': 1,
        'c': 2, 'd': 2, 'g': 2,
        'm': 3, 'b': 3, 'p': 3,
        'f': 4, 'h': 4, 'v': 4, 'y': 4,
        'j': 6,
        'k': 8, 'll': 8,  'ñ': 8,  'q': 8, 'rr': 8,
        'w': 8, 'x': 0,
        'z': 10}
    st = clean_word(word)
    # We get and add the score for each letter in the previously cleaned word
    # taking into account the double letters
    suma = 0
    i = 0
    while i < len(st):
        if  (i < len(st)-1) and st[i] == st[i+1] == 'r':
            char = 'rr'
            i = i + 2
        elif(i < len(st) - 1) and st[i] == st[i+1] == 'l':
            char = 'll'
            i = i + 2
        else:
            char = st[i]
            i = i + 1
        if char not in sc_dic: continue 
        suma = suma + sc_dic[char]
    return suma    


# A function to check if a word is possible to build in the game,
# beacuse each letter can be used only a number of times
# (number of tiles with the letter)
def valid_check(word):
    limit_dic = {'a': 11,  'e': 11, 'o': 8, 's': 7, 'i': 6,
        'u': 6, 'n': 5, 'l': 4, 'r': 4, 't': 4,
        'c': 5, 'd': 4, 'g': 2,
        'm': 3, 'b': 3, 'p': 2,
        'f': 2, 'h': 2, 'v': 2, 'y': 1,
        'j': 2,
        'k': 1, 'll': 1, 'ñ': 1,  'q': 1, 'rr': 1,
        'w': 1, 'x': 1,
        'z': 1}
    st = clean_word(word)
    # For each letter in the word, we check if it is an invalid
    # character or if it appears in the word more times than the 
    # number allowed by the game 
    dic = dict()
    flag = True
    for letter in st:
        dic[letter] = dic.get(letter, 0) +1
    for letter in st:
        if (letter not in limit_dic) or (dic[letter] > limit_dic[letter]):
            flag = False
            break
    return flag        


print ('María', '->', get_sc('María'))

# A funtion to get the score and check for every word starting in a 
# concrete letter (each letter has its own dictionary). It stores
# everything on the DB
def sc_letter(letra):
    file_name = letra + '.txt'
    path = os.path.join(os.getcwd(), 'rae_dics')
    path = os.path.join(path, file_name)
    fhand = open(path, encoding="utf-8")
    for line in fhand:
        palabra = line.strip()
        score =  get_sc(line)
        valid = valid_check(line)
        print(palabra, '->', score)
        cur.execute( '''INSERT OR IGNORE INTO Words (word, score, valid) 
        VALUES (?, ?, ? )''', (palabra, score, valid) )
    conn.commit()

# We get the score for every letter in 'abecedario'
for letter in abecedario:
    sc_letter(letter)

cur.close()

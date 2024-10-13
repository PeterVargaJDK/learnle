from learnle_site.games.crosswords import (
    CrossWordsGrid
)
from tests.crosswords.assertions import (
    assert_grid_equals
)


def test_empty_grid():
    grid = CrossWordsGrid()
    assert_grid_equals(grid, '■')


def test_one_char_word():
    grid = CrossWordsGrid(['a'])
    assert_grid_equals(grid, '''
    A
    ''')


def test_two_char_word():
    grid = CrossWordsGrid(['ab'])
    assert_grid_equals(grid, '''
    AB
    ''')


def test_two_words_same_length__first_letter_in_common():
    grid = CrossWordsGrid(['dig', 'dry'])
    assert_grid_equals(grid, '''
    DIG
    R■■
    Y■■
    ''')


def test_two_words_same_length__second_letter_in_common():
    grid = CrossWordsGrid(['dig', 'odd'])
    assert_grid_equals(grid, '''
    O■■
    DIG
    D■■
    ''')


def test_two_words_same_length__last_letter_in_common():
    grid = CrossWordsGrid(['dig', 'rug'])
    assert_grid_equals(grid, '''
    ■■R
    ■■U
    DIG
    ''')


def test_three_words__two_words_share_a_character():
    grid = CrossWordsGrid(['doggy', 'ding', 'trudge'])
    assert_grid_equals(grid, '''
    ■■T■■
    ■■R■■
    ■■U■■
    ■■D■■
    DOGGY
    I■E■■
    N■■■■
    G■■■■
    ''')


def test_three_words__second_fits_into_third():
    grid = CrossWordsGrid(['doggy', 'drag', 'amend'])
    assert_grid_equals(grid, '''
    DOGGY
    R■■■■
    AMEND
    G■■■■
    ''')


def test_four_words__second_fits_into_third__too_close_to_first_word():
    grid = CrossWordsGrid(['dorm', 'drag', 'arm', 'ridge', 'might', 'height'])
    assert_grid_equals(grid, '''
    ■■■■■A■
    ■■■DORM
    ■■■R■M■
    ■M■A■■■
    RIDGE■■
    ■G■■■■■
    ■HEIGHT
    ■T■■■■■
    ''')


def test_single_word_should_not_intersects_other_words():
    grid = CrossWordsGrid(['mould', 'among', 'new', 'undo'])
    assert_grid_equals(grid, '''
    ■■■■U
    A■■■N
    MOULD
    O■■■O
    NEW■■
    G■■■■
    ''')


def test_single_word_should_intersects_other_words_if_only_common_letters_intersect():
    grid = CrossWordsGrid(['mould', 'among', 'new', 'unwind'])
    assert_grid_equals(grid, '''
    A■■■■
    MOULD
    O■N■■
    NEW■■
    G■I■■
    ■■N■■
    ■■D■■
    ''')


def test_endpoints_should_not_touch():
    grid = CrossWordsGrid(['efg', 'bde', 'jigc', 'abc'])
    assert_grid_equals(grid, '''
    B■J
    D■I
    EFG
    ■■C
    ''')


# def test_single_word_should_intersects_other_words_if_only_common_letters_intersect2():
#     grid = CrossWordsGrid([
#         'element',
#         'room',
#         'equip',
#         'remain',
#         'professional',
#         'supply',
#         'as',
#         'string',
#         'rotten',
#         'defend',
#         'pity',
#         'sink',
#         'origin',
#         'fresh',
#         'blind',
#         'competence',
#         'retiree',
#         'injection',
#         'debate',
#         'decorative',
#         'oxrxm'
#     ])

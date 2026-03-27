OP_NOT = '!'
OP_AND = '&'
OP_OR = '|'
OP_IMP = '->'
OP_EQ = '~'
OP_OR_ALT = 'v'

REP_IMP = '>'

VAL_TRUE = 1
VAL_FALSE = 0

PRIORITIES = {
    OP_NOT: 4,
    OP_AND: 3,
    OP_OR: 2,
    REP_IMP: 1,
    OP_EQ: 1,
    '(': 0
}

ALLOWED_VARS = {'a', 'b', 'c', 'd', 'e'}
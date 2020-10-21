tokens = [
    'FLOAT',
    'INTEGER',
    'UNQUOTED_STRING',
    'QUOTED_STRING'
]

reserved = {
    'store_suit_point': 'STORE_SUIT_POINT',
    'group': 'GROUP',
    'visgroup': 'VISGROUP',
    'vis': 'VIS',
    'STREET_POINT': 'STREET_POINT',
    'FRONT_DOOR_POINT': 'FRONT_DOOR_POINT',
    'SIDE_DOOR_POINT': 'SIDE_DOOR_POINT',
    'COGHQ_IN_POINT': 'COGHQ_IN_POINT',
    'COGHQ_OUT_POINT': 'COGHQ_OUT_POINT',
    'suit_edge': 'SUIT_EDGE',
    'battle_cell': 'BATTLE_CELL',
    'prop': 'PROP',
    'pos': 'POS',
    'hpr': 'HPR',
    'scale': 'SCALE',
    'code': 'CODE',
    'color': 'COLOR',
    'model': 'MODEL',
    'store_node': 'STORE_NODE',
    'sign': 'SIGN',
    'baseline': 'BASELINE',
    'width': 'WIDTH',
    'height': 'HEIGHT',
    'stomp': 'STOMP',
    'stumble': 'STUMBLE',
    'indent': 'INDENT',
    'wiggle': 'WIGGLE',
    'kern': 'KERN',
    'text': 'TEXT',
    'letters': 'LETTERS',
    'store_font': 'STORE_FONT',
    'flat_building': 'FLAT_BUILDING',
    'wall': 'WALL',
    'windows': 'WINDOWS',
    'count': 'COUNT',
    'cornice': 'CORNICE',
    'landmark_building': 'LANDMARK_BUILDING',
    'title': 'TITLE',
    'article': 'ARTICLE',
    'building_type': 'BUILDING_TYPE',
    'door': 'DOOR',
    'store_texture': 'STORE_TEXTURE',
    'street': 'STREET',
    'texture': 'TEXTURE',
    'graphic': 'GRAPHIC',
    'hood_model': 'HOODMODEL',
    'place_model': 'PLACEMODEL',
    'nhpr': 'NHPR',
    'flags': 'FLAGS',
    'node': 'NODE',
    'flat_door': 'FLAT_DOOR',
    'anim': 'ANIM',
    'cell_id': 'CELL_ID',
    'anim_prop': 'ANIM_PROP',
    'interactive_prop': 'INTERACTIVE_PROP',
    'anim_building': 'ANIM_BUILDING'
}
tokens += reserved.values()
t_ignore = ' \t'

literals = '[],'


def t_ignore_COMMENT(t):
    pass
t_ignore_COMMENT.__doc__ = r'[/]{2,2}.*'


def t_ignore_ML_COMMENT(t):
    pass
t_ignore_ML_COMMENT.__doc__ = r'\/\*([^*]|[\r\n])*\*/'


def t_QUOTED_STRING(t):
    t.value = t.value[1:-1]
    return t
t_QUOTED_STRING.__doc__ = r'["][^"]*["]'


def t_FLOAT(t):
    t.value = float(t.value)
    return t
t_FLOAT.__doc__ = r'[+-]?\d*[.]\d*([e][+-]\d*)?'


def t_INTEGER(t):
    t.value = int(t.value)
    return t
t_INTEGER.__doc__ = r'[+-]?\d+'


def t_UNQUOTED_STRING(t):
    if t.value in reserved:
        t.type = reserved[t.value]
    return t
t_UNQUOTED_STRING.__doc__ = r'[^ \t\n\r\[\],"]+'


def t_newline(t):
    t.lexer.lineno += len(t.value)
t_newline.__doc__ = r'\n+'


def t_error(t):
    t.lexer.skip(1)

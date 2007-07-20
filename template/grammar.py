import re
import sys

RESERVED = ("GET", "CALL", "SET", "DEFAULT", "INSERT", "INCLUDE", "PROCESS",
            "WRAPPER", "BLOCK", "END", "USE", "PLUGIN", "FILTER", "MACRO",
            "PYTHON", "RAWPYTHON", "TO", "STEP", "AND", "OR", "NOT", "DIV",
            "MOD", "IF", "UNLESS", "ELSE", "ELSIF", "FOR", "NEXT", "WHILE",
            "SWITCH", "CASE", "META", "IN", "TRY", "THROW", "CATCH", "FINAL",
            "LAST", "RETURN", "STOP", "CLEAR", "VIEW", "DEBUG")

CMPOP = {"!=": "!=", "==": "==", "<": "<", ">": ">", ">=": ">=", "<=": "<="}

LEXTABLE = {
  "FOREACH": "FOR",
  "BREAK":   "LAST",
  "&&":      "AND",
  "||":      "OR",
  "!":       "NOT",
  "|":       "FILTER",
  ".":       "DOT",
  "_":       "CAT",
  "..":      "TO",
  "=":       "ASSIGN",
  "=>":      "ASSIGN",
  ",":       "COMMA",
  "\\":      "REF",
  "and":     "AND",
  "or":      "OR",
  "not":     "NOT",
  "mod":     "MOD",
  "div":     "DIV",
  }

tokens = ("(", ")", "[", "]", "{", "}", "${", "$", "+", "/", ";", ":", "?")
cmpop  = CMPOP.keys()
binop  = ("-", "*", "%")

for x in RESERVED:
  LEXTABLE[x] = x
for x in cmpop:
  LEXTABLE[x] = "CMPOP"
for x in binop:
  LEXTABLE[x] = "BINOP"
for x in tokens:
  LEXTABLE[x] = x


STATES = [
	{#State 0
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'template': 52,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'switch': 34,
			'try': 35,
			'assign': 19,
			'block': 72,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 1
		"ACTIONS":  {
			"$": 43,
			'LITERAL': 75,
			'IDENT': 2,
			"${": 37
		},
		"GOTOS":  {
			'setlist': 76,
			'item': 39,
			'assign': 19,
			'node': 23,
			'ident': 74
		}
	},
	{#State 2
		"DEFAULT":  -130
	},
	{#State 3
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 79,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 4
		"DEFAULT":  -23
	},
	{#State 5
		"ACTIONS":  {
			";": 80
		}
	},
	{#State 6
		"DEFAULT":  -37
	},
	{#State 7
		"DEFAULT":  -14
	},
	{#State 8
		"ACTIONS":  {
			"\"": 89,
			"$": 86,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 90,
			'filename': 85,
			'name': 82
		}
	},
	{#State 9
		"ACTIONS":  {
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"]": 94,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 96,
			'item': 39,
			'range': 93,
			'node': 23,
			'ident': 77,
			'term': 95,
			'list': 92,
			'lterm': 56
		}
	},
	{#State 10
		"ACTIONS":  {
			";": 97
		}
	},
	{#State 11
		"DEFAULT":  -5
	},
	{#State 12
		"ACTIONS":  {
			";": -20
		},
		"DEFAULT":  -27
	},
	{#State 13
		"DEFAULT":  -78,
		"GOTOS":  {
			'@5-1': 98
		}
	},
	{#State 14
		"ACTIONS":  {
			'IDENT': 99
		},
		"DEFAULT":  -87,
		"GOTOS":  {
			'blockargs': 102,
			'metadata': 101,
			'meta': 100
		}
	},
	{#State 15
		"ACTIONS":  {
			'IDENT': 99
		},
		"GOTOS":  {
			'metadata': 103,
			'meta': 100
		}
	},
	{#State 16
		"ACTIONS":  {
			'DOT': 104,
			'ASSIGN': 105
		},
		"DEFAULT":  -109
	},
	{#State 17
		"ACTIONS":  {
			"\"": 89,
			"$": 86,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 106,
			'filename': 85,
			'name': 82
		}
	},
	{#State 18
		"ACTIONS":  {
			'IDENT': 107
		}
	},
	{#State 19
		"DEFAULT":  -149
	},
	{#State 20
		"DEFAULT":  -12
	},
	{#State 21
		"ACTIONS":  {
			"{": 30,
			'LITERAL': 78,
			'IDENT': 108,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 39,
			'loopvar': 110,
			'node': 23,
			'ident': 77,
			'term': 109,
			'lterm': 56
		}
	},
	{#State 22
		"DEFAULT":  -40
	},
	{#State 23
		"DEFAULT":  -127
	},
	{#State 24
		"DEFAULT":  -6
	},
	{#State 25
		"ACTIONS":  {
			"\"": 117,
			"$": 114,
			'LITERAL': 116,
			'FILENAME': 83,
			'IDENT': 111,
			'NUMBER': 84,
			"${": 37
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 118,
			'filename': 85,
			'lvalue': 112,
			'lnameargs': 115,
			'item': 113,
			'name': 82
		}
	},
	{#State 26
		"DEFAULT":  -113
	},
	{#State 27
		"ACTIONS":  {
			"$": 43,
			'IDENT': 2,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'ident': 119
		}
	},
	{#State 28
		"ACTIONS":  {
			'LITERAL': 124,
			'FILENAME': 83,
			'IDENT': 120,
			'NUMBER': 84
		},
		"DEFAULT":  -87,
		"GOTOS":  {
			'blockargs': 123,
			'filepart': 87,
			'filename': 122,
			'blockname': 121,
			'metadata': 101,
			'meta': 100
		}
	},
	{#State 29
		"DEFAULT":  -43
	},
	{#State 30
		"ACTIONS":  {
			"$": 43,
			'LITERAL': 129,
			'IDENT': 2,
			"${": 37
		},
		"DEFAULT":  -119,
		"GOTOS":  {
			'params': 128,
			'hash': 125,
			'item': 126,
			'param': 127
		}
	},
	{#State 31
		"DEFAULT":  -25
	},
	{#State 32
		"ACTIONS":  {
			"\"": 117,
			"$": 114,
			'LITERAL': 116,
			'FILENAME': 83,
			'IDENT': 111,
			'NUMBER': 84,
			"${": 37
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 118,
			'filename': 85,
			'lvalue': 112,
			'lnameargs': 130,
			'item': 113,
			'name': 82
		}
	},
	{#State 33
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -2,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 131,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 34
		"DEFAULT":  -22
	},
	{#State 35
		"DEFAULT":  -24
	},
	{#State 36
		"ACTIONS":  {
			"\"": 89,
			"$": 86,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 132,
			'filename': 85,
			'name': 82
		}
	},
	{#State 37
		"ACTIONS":  {
			"\"": 60,
			"$": 43,
			'LITERAL': 78,
			'IDENT': 2,
			'REF': 27,
			'NUMBER': 26,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 133,
			'item': 39,
			'node': 23,
			'ident': 77
		}
	},
	{#State 38
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 134,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 39
		"ACTIONS":  {
			"(": 135
		},
		"DEFAULT":  -128
	},
	{#State 40
		"ACTIONS":  {
			";": 136
		}
	},
	{#State 41
		"DEFAULT":  -38
	},
	{#State 42
		"DEFAULT":  -11
	},
	{#State 43
		"ACTIONS":  {
			'IDENT': 137
		}
	},
	{#State 44
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 138,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 45
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 139,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 46
		"DEFAULT":  -42
	},
	{#State 47
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 140,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 48
		"ACTIONS":  {
			'IF': 144,
			'FILTER': 143,
			'FOR': 142,
			'WHILE': 146,
			'WRAPPER': 145,
			'UNLESS': 141
		}
	},
	{#State 49
		"DEFAULT":  -39
	},
	{#State 50
		"DEFAULT":  -10
	},
	{#State 51
		"ACTIONS":  {
			"\"": 89,
			"$": 86,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 147,
			'filename': 85,
			'name': 82
		}
	},
	{#State 52
		"ACTIONS":  {
			'': 148
		}
	},
	{#State 53
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 57,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 149,
			'term': 58,
			'expr': 151,
			'assign': 150,
			'lterm': 56
		}
	},
	{#State 54
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 152,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 55
		"ACTIONS":  {
			"\"": 89,
			"$": 86,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 153,
			'filename': 85,
			'name': 82
		}
	},
	{#State 56
		"DEFAULT":  -103
	},
	{#State 57
		"ACTIONS":  {
			'ASSIGN': 154
		},
		"DEFAULT":  -112
	},
	{#State 58
		"DEFAULT":  -146
	},
	{#State 59
		"DEFAULT":  -15
	},
	{#State 60
		"DEFAULT":  -176,
		"GOTOS":  {
			'quoted': 155
		}
	},
	{#State 61
		"ACTIONS":  {
			"\"": 89,
			"$": 86,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 156,
			'filename': 85,
			'name': 82
		}
	},
	{#State 62
		"ACTIONS":  {
			";": -16,
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -26
	},
	{#State 63
		"DEFAULT":  -13
	},
	{#State 64
		"DEFAULT":  -36
	},
	{#State 65
		"ACTIONS":  {
			"\"": 89,
			"$": 86,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 167,
			'filename': 85,
			'name': 82
		}
	},
	{#State 66
		"DEFAULT":  -9
	},
	{#State 67
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 168,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 68
		"DEFAULT":  -104
	},
	{#State 69
		"ACTIONS":  {
			"$": 43,
			'LITERAL': 75,
			'IDENT': 2,
			"${": 37
		},
		"GOTOS":  {
			'setlist': 169,
			'item': 39,
			'assign': 19,
			'node': 23,
			'ident': 74
		}
	},
	{#State 70
		"ACTIONS":  {
			"$": 43,
			'COMMA': 171,
			'LITERAL': 75,
			'IDENT': 2,
			"${": 37
		},
		"DEFAULT":  -19,
		"GOTOS":  {
			'item': 39,
			'assign': 170,
			'node': 23,
			'ident': 74
		}
	},
	{#State 71
		"DEFAULT":  -8
	},
	{#State 72
		"DEFAULT":  -1
	},
	{#State 73
		"DEFAULT":  -21
	},
	{#State 74
		"ACTIONS":  {
			'ASSIGN': 172,
			'DOT': 104
		}
	},
	{#State 75
		"ACTIONS":  {
			'ASSIGN': 154
		}
	},
	{#State 76
		"ACTIONS":  {
			"$": 43,
			'COMMA': 171,
			'LITERAL': 75,
			'IDENT': 2,
			"${": 37
		},
		"DEFAULT":  -30,
		"GOTOS":  {
			'item': 39,
			'assign': 170,
			'node': 23,
			'ident': 74
		}
	},
	{#State 77
		"ACTIONS":  {
			'DOT': 104
		},
		"DEFAULT":  -109
	},
	{#State 78
		"DEFAULT":  -112
	},
	{#State 79
		"ACTIONS":  {
			'CMPOP': 164,
			"?": 158,
			";": 173,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			'OR': 162
		}
	},
	{#State 80
		"DEFAULT":  -7
	},
	{#State 81
		"DEFAULT":  -173
	},
	{#State 82
		"DEFAULT":  -166
	},
	{#State 83
		"DEFAULT":  -172
	},
	{#State 84
		"DEFAULT":  -174
	},
	{#State 85
		"ACTIONS":  {
			'DOT': 174
		},
		"DEFAULT":  -168
	},
	{#State 86
		"ACTIONS":  {
			"$": 43,
			'IDENT': 2,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'ident': 175
		}
	},
	{#State 87
		"DEFAULT":  -171
	},
	{#State 88
		"DEFAULT":  -169
	},
	{#State 89
		"DEFAULT":  -176,
		"GOTOS":  {
			'quoted': 176
		}
	},
	{#State 90
		"DEFAULT":  -35
	},
	{#State 91
		"ACTIONS":  {
			"+": 177,
			"(": 178
		},
		"DEFAULT":  -156,
		"GOTOS":  {
			'args': 179
		}
	},
	{#State 92
		"ACTIONS":  {
			"{": 30,
			'COMMA': 182,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"]": 180,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 181,
			'lterm': 56
		}
	},
	{#State 93
		"ACTIONS":  {
			"]": 183
		}
	},
	{#State 94
		"DEFAULT":  -107
	},
	{#State 95
		"DEFAULT":  -116
	},
	{#State 96
		"ACTIONS":  {
			'TO': 184
		},
		"DEFAULT":  -104
	},
	{#State 97
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 185,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 98
		"ACTIONS":  {
			";": 186
		}
	},
	{#State 99
		"ACTIONS":  {
			'ASSIGN': 187
		}
	},
	{#State 100
		"DEFAULT":  -99
	},
	{#State 101
		"ACTIONS":  {
			'COMMA': 189,
			'IDENT': 99
		},
		"DEFAULT":  -86,
		"GOTOS":  {
			'meta': 188
		}
	},
	{#State 102
		"ACTIONS":  {
			";": 190
		}
	},
	{#State 103
		"ACTIONS":  {
			'COMMA': 189,
			'IDENT': 99
		},
		"DEFAULT":  -17,
		"GOTOS":  {
			'meta': 188
		}
	},
	{#State 104
		"ACTIONS":  {
			"$": 43,
			'IDENT': 2,
			'NUMBER': 192,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 191
		}
	},
	{#State 105
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'WRAPPER': 55,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			"\"": 60,
			'PROCESS': 61,
			'FILTER': 25,
			'RETURN': 64,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 193,
			'DEFAULT': 69,
			"{": 30,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'term': 58,
			'loop': 4,
			'expr': 195,
			'wrapper': 46,
			'atomexpr': 48,
			'atomdir': 12,
			'mdir': 194,
			'sterm': 68,
			'filter': 29,
			'ident': 149,
			'perl': 31,
			'setlist': 70,
			'switch': 34,
			'try': 35,
			'assign': 19,
			'directive': 196,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 106
		"DEFAULT":  -33
	},
	{#State 107
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'INCLUDE': 17,
			"(": 198,
			'SWITCH': 54,
			'WRAPPER': 55,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			"\"": 60,
			'PROCESS': 61,
			'FILTER': 25,
			'RETURN': 64,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 193,
			'DEFAULT': 69,
			"{": 30,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'term': 58,
			'loop': 4,
			'expr': 199,
			'wrapper': 46,
			'atomexpr': 48,
			'atomdir': 12,
			'mdir': 197,
			'sterm': 68,
			'filter': 29,
			'ident': 149,
			'perl': 31,
			'setlist': 70,
			'switch': 34,
			'try': 35,
			'assign': 19,
			'directive': 196,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 108
		"ACTIONS":  {
			'IN': 201,
			'ASSIGN': 200
		},
		"DEFAULT":  -130
	},
	{#State 109
		"DEFAULT":  -156,
		"GOTOS":  {
			'args': 202
		}
	},
	{#State 110
		"ACTIONS":  {
			";": 203
		}
	},
	{#State 111
		"ACTIONS":  {
			'ASSIGN': -130
		},
		"DEFAULT":  -173
	},
	{#State 112
		"ACTIONS":  {
			'ASSIGN': 204
		}
	},
	{#State 113
		"DEFAULT":  -159
	},
	{#State 114
		"ACTIONS":  {
			"$": 43,
			'IDENT': 205,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'ident': 175
		}
	},
	{#State 115
		"ACTIONS":  {
			";": 206
		}
	},
	{#State 116
		"ACTIONS":  {
			'ASSIGN': -161
		},
		"DEFAULT":  -169
	},
	{#State 117
		"DEFAULT":  -176,
		"GOTOS":  {
			'quoted': 207
		}
	},
	{#State 118
		"DEFAULT":  -158
	},
	{#State 119
		"ACTIONS":  {
			'DOT': 104
		},
		"DEFAULT":  -110
	},
	{#State 120
		"ACTIONS":  {
			'ASSIGN': 187
		},
		"DEFAULT":  -173
	},
	{#State 121
		"DEFAULT":  -83
	},
	{#State 122
		"ACTIONS":  {
			'DOT': 174
		},
		"DEFAULT":  -84
	},
	{#State 123
		"ACTIONS":  {
			";": 208
		}
	},
	{#State 124
		"DEFAULT":  -85
	},
	{#State 125
		"ACTIONS":  {
			"}": 209
		}
	},
	{#State 126
		"ACTIONS":  {
			'ASSIGN': 210
		}
	},
	{#State 127
		"DEFAULT":  -122
	},
	{#State 128
		"ACTIONS":  {
			"$": 43,
			'COMMA': 212,
			'LITERAL': 129,
			'IDENT': 2,
			"${": 37
		},
		"DEFAULT":  -118,
		"GOTOS":  {
			'item': 126,
			'param': 211
		}
	},
	{#State 129
		"ACTIONS":  {
			'ASSIGN': 213
		}
	},
	{#State 130
		"DEFAULT":  -73
	},
	{#State 131
		"DEFAULT":  -4
	},
	{#State 132
		"ACTIONS":  {
			";": 214
		}
	},
	{#State 133
		"ACTIONS":  {
			"}": 215
		}
	},
	{#State 134
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'BINOP': 161
		},
		"DEFAULT":  -142
	},
	{#State 135
		"DEFAULT":  -156,
		"GOTOS":  {
			'args': 216
		}
	},
	{#State 136
		"DEFAULT":  -76,
		"GOTOS":  {
			'@4-2': 217
		}
	},
	{#State 137
		"DEFAULT":  -132
	},
	{#State 138
		"ACTIONS":  {
			'CMPOP': 164,
			"?": 158,
			";": 218,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			'OR': 162
		}
	},
	{#State 139
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -29
	},
	{#State 140
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -28
	},
	{#State 141
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 219,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 142
		"ACTIONS":  {
			"{": 30,
			'LITERAL': 78,
			'IDENT': 108,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 39,
			'loopvar': 220,
			'node': 23,
			'ident': 77,
			'term': 109,
			'lterm': 56
		}
	},
	{#State 143
		"ACTIONS":  {
			"\"": 117,
			"$": 114,
			'LITERAL': 116,
			'FILENAME': 83,
			'IDENT': 111,
			'NUMBER': 84,
			"${": 37
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 118,
			'filename': 85,
			'lvalue': 112,
			'lnameargs': 221,
			'item': 113,
			'name': 82
		}
	},
	{#State 144
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 222,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 145
		"ACTIONS":  {
			"\"": 89,
			"$": 86,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 223,
			'filename': 85,
			'name': 82
		}
	},
	{#State 146
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 224,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 147
		"DEFAULT":  -41
	},
	{#State 148
		"DEFAULT":  0
	},
	{#State 149
		"ACTIONS":  {
			'DOT': 104,
			'ASSIGN': 172
		},
		"DEFAULT":  -109
	},
	{#State 150
		"ACTIONS":  {
			")": 225
		}
	},
	{#State 151
		"ACTIONS":  {
			'CMPOP': 164,
			"?": 158,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			")": 226,
			'OR': 162
		}
	},
	{#State 152
		"ACTIONS":  {
			'CMPOP': 164,
			"?": 158,
			";": 227,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			'OR': 162
		}
	},
	{#State 153
		"ACTIONS":  {
			";": 228
		}
	},
	{#State 154
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 229,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 155
		"ACTIONS":  {
			"\"": 234,
			'TEXT': 231,
			";": 233,
			"$": 43,
			'IDENT': 2,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'ident': 230,
			'quotable': 232
		}
	},
	{#State 156
		"DEFAULT":  -34
	},
	{#State 157
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 235,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 158
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 236,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 159
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 237,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 160
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 238,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 161
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 239,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 162
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 240,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 163
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 241,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 164
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 242,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 165
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 243,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 166
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 244,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 167
		"DEFAULT":  -32
	},
	{#State 168
		"ACTIONS":  {
			'CMPOP': 164,
			"?": 158,
			";": 245,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			'OR': 162
		}
	},
	{#State 169
		"ACTIONS":  {
			"$": 43,
			'COMMA': 171,
			'LITERAL': 75,
			'IDENT': 2,
			"${": 37
		},
		"DEFAULT":  -31,
		"GOTOS":  {
			'item': 39,
			'assign': 170,
			'node': 23,
			'ident': 74
		}
	},
	{#State 170
		"DEFAULT":  -147
	},
	{#State 171
		"DEFAULT":  -148
	},
	{#State 172
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 246,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 173
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 247,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 174
		"ACTIONS":  {
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 248
		}
	},
	{#State 175
		"ACTIONS":  {
			'DOT': 104
		},
		"DEFAULT":  -156,
		"GOTOS":  {
			'args': 249
		}
	},
	{#State 176
		"ACTIONS":  {
			"\"": 250,
			'TEXT': 231,
			";": 233,
			"$": 43,
			'IDENT': 2,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'ident': 230,
			'quotable': 232
		}
	},
	{#State 177
		"ACTIONS":  {
			"\"": 89,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'filename': 85,
			'name': 251
		}
	},
	{#State 178
		"DEFAULT":  -156,
		"GOTOS":  {
			'args': 252
		}
	},
	{#State 179
		"ACTIONS":  {
			"{": 30,
			'COMMA': 258,
			'LITERAL': 256,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"DEFAULT":  -163,
		"GOTOS":  {
			'sterm': 68,
			'item': 254,
			'param': 255,
			'node': 23,
			'ident': 253,
			'term': 257,
			'lterm': 56
		}
	},
	{#State 180
		"DEFAULT":  -105
	},
	{#State 181
		"DEFAULT":  -114
	},
	{#State 182
		"DEFAULT":  -115
	},
	{#State 183
		"DEFAULT":  -106
	},
	{#State 184
		"ACTIONS":  {
			"\"": 60,
			"$": 43,
			'LITERAL': 78,
			'IDENT': 2,
			'REF': 27,
			'NUMBER': 26,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 259,
			'item': 39,
			'node': 23,
			'ident': 77
		}
	},
	{#State 185
		"ACTIONS":  {
			'FINAL': 260,
			'CATCH': 262
		},
		"DEFAULT":  -72,
		"GOTOS":  {
			'final': 261
		}
	},
	{#State 186
		"ACTIONS":  {
			'TEXT': 263
		}
	},
	{#State 187
		"ACTIONS":  {
			"\"": 266,
			'LITERAL': 265,
			'NUMBER': 264
		}
	},
	{#State 188
		"DEFAULT":  -97
	},
	{#State 189
		"DEFAULT":  -98
	},
	{#State 190
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'template': 267,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 72,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 191
		"DEFAULT":  -125
	},
	{#State 192
		"DEFAULT":  -126
	},
	{#State 193
		"ACTIONS":  {
			";": 268
		}
	},
	{#State 194
		"DEFAULT":  -89
	},
	{#State 195
		"ACTIONS":  {
			";": -150,
			"+": 157,
			'LITERAL': -150,
			'IDENT': -150,
			'CAT': 163,
			"$": -150,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			'COMMA': -150,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162,
			"${": -150
		},
		"DEFAULT":  -26
	},
	{#State 196
		"DEFAULT":  -92
	},
	{#State 197
		"DEFAULT":  -91
	},
	{#State 198
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 57,
			'IDENT': 269,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 39,
			'margs': 270,
			'node': 23,
			'ident': 149,
			'term': 58,
			'expr': 151,
			'assign': 150,
			'lterm': 56
		}
	},
	{#State 199
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -26
	},
	{#State 200
		"ACTIONS":  {
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 271,
			'lterm': 56
		}
	},
	{#State 201
		"ACTIONS":  {
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 272,
			'lterm': 56
		}
	},
	{#State 202
		"ACTIONS":  {
			"{": 30,
			'COMMA': 258,
			'LITERAL': 256,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"DEFAULT":  -64,
		"GOTOS":  {
			'sterm': 68,
			'item': 254,
			'param': 255,
			'node': 23,
			'ident': 253,
			'term': 257,
			'lterm': 56
		}
	},
	{#State 203
		"DEFAULT":  -56,
		"GOTOS":  {
			'@1-3': 273
		}
	},
	{#State 204
		"ACTIONS":  {
			"\"": 89,
			"$": 86,
			'LITERAL': 88,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'names': 91,
			'nameargs': 274,
			'filename': 85,
			'name': 82
		}
	},
	{#State 205
		"ACTIONS":  {
			'ASSIGN': -132
		},
		"DEFAULT":  -130
	},
	{#State 206
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 275,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 207
		"ACTIONS":  {
			"\"": 276,
			'TEXT': 231,
			";": 233,
			"$": 43,
			'IDENT': 2,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'ident': 230,
			'quotable': 232
		}
	},
	{#State 208
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 277,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 209
		"DEFAULT":  -108
	},
	{#State 210
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 278,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 211
		"DEFAULT":  -120
	},
	{#State 212
		"DEFAULT":  -121
	},
	{#State 213
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 279,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 214
		"DEFAULT":  -74,
		"GOTOS":  {
			'@3-3': 280
		}
	},
	{#State 215
		"DEFAULT":  -131
	},
	{#State 216
		"ACTIONS":  {
			"{": 30,
			'COMMA': 258,
			'LITERAL': 256,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			")": 281,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 254,
			'param': 255,
			'node': 23,
			'ident': 253,
			'term': 257,
			'lterm': 56
		}
	},
	{#State 217
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 282,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 218
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 283,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 219
		"ACTIONS":  {
			'CMPOP': 164,
			"?": 158,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -47
	},
	{#State 220
		"DEFAULT":  -58
	},
	{#State 221
		"DEFAULT":  -81
	},
	{#State 222
		"ACTIONS":  {
			'CMPOP': 164,
			"?": 158,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -45
	},
	{#State 223
		"DEFAULT":  -66
	},
	{#State 224
		"ACTIONS":  {
			'CMPOP': 164,
			"?": 158,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -61
	},
	{#State 225
		"DEFAULT":  -144
	},
	{#State 226
		"DEFAULT":  -145
	},
	{#State 227
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 284,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 228
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 285,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 229
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -151
	},
	{#State 230
		"ACTIONS":  {
			'DOT': 104
		},
		"DEFAULT":  -177
	},
	{#State 231
		"DEFAULT":  -178
	},
	{#State 232
		"DEFAULT":  -175
	},
	{#State 233
		"DEFAULT":  -179
	},
	{#State 234
		"DEFAULT":  -111
	},
	{#State 235
		"ACTIONS":  {
			'DIV': 159,
			'MOD': 165,
			"/": 166
		},
		"DEFAULT":  -135
	},
	{#State 236
		"ACTIONS":  {
			":": 286,
			'CMPOP': 164,
			"?": 158,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			'OR': 162
		}
	},
	{#State 237
		"ACTIONS":  {
			'MOD': 165
		},
		"DEFAULT":  -136
	},
	{#State 238
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'BINOP': 161
		},
		"DEFAULT":  -140
	},
	{#State 239
		"ACTIONS":  {
			"+": 157,
			'DIV': 159,
			'MOD': 165,
			"/": 166
		},
		"DEFAULT":  -133
	},
	{#State 240
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'BINOP': 161
		},
		"DEFAULT":  -141
	},
	{#State 241
		"ACTIONS":  {
			"+": 157,
			'CMPOP': 164,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'BINOP': 161
		},
		"DEFAULT":  -139
	},
	{#State 242
		"ACTIONS":  {
			"+": 157,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'BINOP': 161
		},
		"DEFAULT":  -138
	},
	{#State 243
		"DEFAULT":  -137
	},
	{#State 244
		"ACTIONS":  {
			'DIV': 159,
			'MOD': 165
		},
		"DEFAULT":  -134
	},
	{#State 245
		"DEFAULT":  -59,
		"GOTOS":  {
			'@2-3': 287
		}
	},
	{#State 246
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -150
	},
	{#State 247
		"ACTIONS":  {
			'ELSIF': 290,
			'ELSE': 288
		},
		"DEFAULT":  -50,
		"GOTOS":  {
			'else': 289
		}
	},
	{#State 248
		"DEFAULT":  -170
	},
	{#State 249
		"ACTIONS":  {
			"{": 30,
			'COMMA': 258,
			'LITERAL': 256,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"DEFAULT":  -162,
		"GOTOS":  {
			'sterm': 68,
			'item': 254,
			'param': 255,
			'node': 23,
			'ident': 253,
			'term': 257,
			'lterm': 56
		}
	},
	{#State 250
		"DEFAULT":  -167
	},
	{#State 251
		"DEFAULT":  -165
	},
	{#State 252
		"ACTIONS":  {
			"{": 30,
			'COMMA': 258,
			'LITERAL': 256,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			")": 291,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 254,
			'param': 255,
			'node': 23,
			'ident': 253,
			'term': 257,
			'lterm': 56
		}
	},
	{#State 253
		"ACTIONS":  {
			'DOT': 104,
			'ASSIGN': 292
		},
		"DEFAULT":  -109
	},
	{#State 254
		"ACTIONS":  {
			"(": 135,
			'ASSIGN': 210
		},
		"DEFAULT":  -128
	},
	{#State 255
		"DEFAULT":  -153
	},
	{#State 256
		"ACTIONS":  {
			'ASSIGN': 213
		},
		"DEFAULT":  -112
	},
	{#State 257
		"DEFAULT":  -152
	},
	{#State 258
		"DEFAULT":  -155
	},
	{#State 259
		"DEFAULT":  -117
	},
	{#State 260
		"ACTIONS":  {
			";": 293
		}
	},
	{#State 261
		"ACTIONS":  {
			'END': 294
		}
	},
	{#State 262
		"ACTIONS":  {
			";": 296,
			'DEFAULT': 297,
			'FILENAME': 83,
			'IDENT': 81,
			'NUMBER': 84
		},
		"GOTOS":  {
			'filepart': 87,
			'filename': 295
		}
	},
	{#State 263
		"ACTIONS":  {
			'END': 298
		}
	},
	{#State 264
		"DEFAULT":  -102
	},
	{#State 265
		"DEFAULT":  -100
	},
	{#State 266
		"ACTIONS":  {
			'TEXT': 299
		}
	},
	{#State 267
		"ACTIONS":  {
			'END': 300
		}
	},
	{#State 268
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 301,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 269
		"ACTIONS":  {
			'COMMA': -96,
			'IDENT': -96,
			")": -96
		},
		"DEFAULT":  -130
	},
	{#State 270
		"ACTIONS":  {
			'COMMA': 304,
			'IDENT': 302,
			")": 303
		}
	},
	{#State 271
		"DEFAULT":  -156,
		"GOTOS":  {
			'args': 305
		}
	},
	{#State 272
		"DEFAULT":  -156,
		"GOTOS":  {
			'args': 306
		}
	},
	{#State 273
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 307,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 274
		"DEFAULT":  -157
	},
	{#State 275
		"ACTIONS":  {
			'END': 308
		}
	},
	{#State 276
		"ACTIONS":  {
			'ASSIGN': -160
		},
		"DEFAULT":  -167
	},
	{#State 277
		"ACTIONS":  {
			'END': 309
		}
	},
	{#State 278
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -124
	},
	{#State 279
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -123
	},
	{#State 280
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 310,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 281
		"DEFAULT":  -129
	},
	{#State 282
		"ACTIONS":  {
			'END': 311
		}
	},
	{#State 283
		"ACTIONS":  {
			'ELSIF': 290,
			'ELSE': 288
		},
		"DEFAULT":  -50,
		"GOTOS":  {
			'else': 312
		}
	},
	{#State 284
		"ACTIONS":  {
			'CASE': 313
		},
		"DEFAULT":  -55,
		"GOTOS":  {
			'case': 314
		}
	},
	{#State 285
		"ACTIONS":  {
			'END': 315
		}
	},
	{#State 286
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 316,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 287
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 317,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 288
		"ACTIONS":  {
			";": 318
		}
	},
	{#State 289
		"ACTIONS":  {
			'END': 319
		}
	},
	{#State 290
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 320,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 291
		"DEFAULT":  -164
	},
	{#State 292
		"ACTIONS":  {
			'NOT': 38,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"(": 53,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'expr': 321,
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 58,
			'lterm': 56
		}
	},
	{#State 293
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 322,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 294
		"DEFAULT":  -67
	},
	{#State 295
		"ACTIONS":  {
			'DOT': 174,
			";": 323
		}
	},
	{#State 296
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 324,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 297
		"ACTIONS":  {
			";": 325
		}
	},
	{#State 298
		"DEFAULT":  -79
	},
	{#State 299
		"ACTIONS":  {
			"\"": 326
		}
	},
	{#State 300
		"DEFAULT":  -82
	},
	{#State 301
		"ACTIONS":  {
			'END': 327
		}
	},
	{#State 302
		"DEFAULT":  -94
	},
	{#State 303
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'WRAPPER': 55,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			"\"": 60,
			'PROCESS': 61,
			'FILTER': 25,
			'RETURN': 64,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 193,
			'DEFAULT': 69,
			"{": 30,
			"${": 37
		},
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'term': 58,
			'loop': 4,
			'expr': 199,
			'wrapper': 46,
			'atomexpr': 48,
			'atomdir': 12,
			'mdir': 328,
			'sterm': 68,
			'filter': 29,
			'ident': 149,
			'perl': 31,
			'setlist': 70,
			'switch': 34,
			'try': 35,
			'assign': 19,
			'directive': 196,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 304
		"DEFAULT":  -95
	},
	{#State 305
		"ACTIONS":  {
			"{": 30,
			'COMMA': 258,
			'LITERAL': 256,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"DEFAULT":  -62,
		"GOTOS":  {
			'sterm': 68,
			'item': 254,
			'param': 255,
			'node': 23,
			'ident': 253,
			'term': 257,
			'lterm': 56
		}
	},
	{#State 306
		"ACTIONS":  {
			"{": 30,
			'COMMA': 258,
			'LITERAL': 256,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"DEFAULT":  -63,
		"GOTOS":  {
			'sterm': 68,
			'item': 254,
			'param': 255,
			'node': 23,
			'ident': 253,
			'term': 257,
			'lterm': 56
		}
	},
	{#State 307
		"ACTIONS":  {
			'END': 329
		}
	},
	{#State 308
		"DEFAULT":  -80
	},
	{#State 309
		"DEFAULT":  -88
	},
	{#State 310
		"ACTIONS":  {
			'END': 330
		}
	},
	{#State 311
		"DEFAULT":  -77
	},
	{#State 312
		"ACTIONS":  {
			'END': 331
		}
	},
	{#State 313
		"ACTIONS":  {
			";": 332,
			'DEFAULT': 334,
			"{": 30,
			'LITERAL': 78,
			'IDENT': 2,
			"\"": 60,
			"$": 43,
			"[": 9,
			'NUMBER': 26,
			'REF': 27,
			"${": 37
		},
		"GOTOS":  {
			'sterm': 68,
			'item': 39,
			'node': 23,
			'ident': 77,
			'term': 333,
			'lterm': 56
		}
	},
	{#State 314
		"ACTIONS":  {
			'END': 335
		}
	},
	{#State 315
		"DEFAULT":  -65
	},
	{#State 316
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -143
	},
	{#State 317
		"ACTIONS":  {
			'END': 336
		}
	},
	{#State 318
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 337,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 319
		"DEFAULT":  -46
	},
	{#State 320
		"ACTIONS":  {
			'CMPOP': 164,
			"?": 158,
			";": 338,
			"+": 157,
			'MOD': 165,
			'DIV': 159,
			"/": 166,
			'AND': 160,
			'CAT': 163,
			'BINOP': 161,
			'OR': 162
		}
	},
	{#State 321
		"ACTIONS":  {
			"+": 157,
			'CAT': 163,
			'CMPOP': 164,
			"?": 158,
			'DIV': 159,
			'MOD': 165,
			"/": 166,
			'AND': 160,
			'BINOP': 161,
			'OR': 162
		},
		"DEFAULT":  -154
	},
	{#State 322
		"DEFAULT":  -71
	},
	{#State 323
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 339,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 324
		"ACTIONS":  {
			'FINAL': 260,
			'CATCH': 262
		},
		"DEFAULT":  -72,
		"GOTOS":  {
			'final': 340
		}
	},
	{#State 325
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 341,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 326
		"DEFAULT":  -101
	},
	{#State 327
		"DEFAULT":  -93
	},
	{#State 328
		"DEFAULT":  -90
	},
	{#State 329
		"DEFAULT":  -57
	},
	{#State 330
		"DEFAULT":  -75
	},
	{#State 331
		"DEFAULT":  -44
	},
	{#State 332
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 342,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 333
		"ACTIONS":  {
			";": 343
		}
	},
	{#State 334
		"ACTIONS":  {
			";": 344
		}
	},
	{#State 335
		"DEFAULT":  -51
	},
	{#State 336
		"DEFAULT":  -60
	},
	{#State 337
		"DEFAULT":  -49
	},
	{#State 338
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 345,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 339
		"ACTIONS":  {
			'FINAL': 260,
			'CATCH': 262
		},
		"DEFAULT":  -72,
		"GOTOS":  {
			'final': 346
		}
	},
	{#State 340
		"DEFAULT":  -70
	},
	{#State 341
		"ACTIONS":  {
			'FINAL': 260,
			'CATCH': 262
		},
		"DEFAULT":  -72,
		"GOTOS":  {
			'final': 347
		}
	},
	{#State 342
		"DEFAULT":  -54
	},
	{#State 343
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 348,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 344
		"ACTIONS":  {
			'SET': 1,
			'PERL': 40,
			'NOT': 38,
			'IDENT': 2,
			'CLEAR': 41,
			'UNLESS': 3,
			'IF': 44,
			"$": 43,
			'STOP': 6,
			'CALL': 45,
			'THROW': 8,
			'GET': 47,
			"[": 9,
			'TRY': 10,
			'LAST': 49,
			'DEBUG': 51,
			'RAWPERL': 13,
			'META': 15,
			'INCLUDE': 17,
			"(": 53,
			'SWITCH': 54,
			'MACRO': 18,
			'WRAPPER': 55,
			";": -18,
			'FOR': 21,
			'NEXT': 22,
			'LITERAL': 57,
			'TEXT': 24,
			"\"": 60,
			'PROCESS': 61,
			'RETURN': 64,
			'FILTER': 25,
			'INSERT': 65,
			'NUMBER': 26,
			'REF': 27,
			'WHILE': 67,
			'BLOCK': 28,
			'DEFAULT': 69,
			"{": 30,
			'USE': 32,
			'VIEW': 36,
			"${": 37
		},
		"DEFAULT":  -3,
		"GOTOS":  {
			'item': 39,
			'node': 23,
			'rawperl': 59,
			'term': 58,
			'loop': 4,
			'use': 63,
			'expr': 62,
			'capture': 42,
			'statement': 5,
			'view': 7,
			'wrapper': 46,
			'atomexpr': 48,
			'chunk': 11,
			'defblock': 66,
			'atomdir': 12,
			'anonblock': 50,
			'sterm': 68,
			'defblockname': 14,
			'filter': 29,
			'ident': 16,
			'perl': 31,
			'setlist': 70,
			'chunks': 33,
			'try': 35,
			'switch': 34,
			'assign': 19,
			'block': 349,
			'directive': 71,
			'macro': 20,
			'condition': 73,
			'lterm': 56
		}
	},
	{#State 345
		"ACTIONS":  {
			'ELSIF': 290,
			'ELSE': 288
		},
		"DEFAULT":  -50,
		"GOTOS":  {
			'else': 350
		}
	},
	{#State 346
		"DEFAULT":  -68
	},
	{#State 347
		"DEFAULT":  -69
	},
	{#State 348
		"ACTIONS":  {
			'CASE': 313
		},
		"DEFAULT":  -55,
		"GOTOS":  {
			'case': 351
		}
	},
	{#State 349
		"DEFAULT":  -53
	},
	{#State 350
		"DEFAULT":  -48
	},
	{#State 351
		"DEFAULT":  -52
	}
]; 

factory = None

# while (<DATA>) {
# print;
# if (/^def (rule\d+)/) {
# print qq(  print "$1: args=%r" % (args,)\n);
# }
# }
# __DATA__

def rule1(*args):
  return factory.template(args[1])

def rule2(*args):
  return factory.block(args[1])

def rule3(*args):
  return factory.block()

def rule4(*args):
  if len(args) >= 3 and args[2] is not None:
    args[1].append(args[2])
  return args[1]

def rule5(*args):
  if len(args) >= 2 and args[1] is not None:
    return [args[1]]
  else:
    return []

def rule6(*args):
  return factory.textblock(args[1])

def rule7(*args):
  if not args[1]:
    return ""
  else:
    return args[0].location() + args[1]

def rule16(*args):
  return factory.get(args[1])

def rule17(*args):
  return args[0].add_metadata(args[2])

def rule19(*args):
  return factory.set(args[1])

def rule26(*args):
  return factory.get(args[1])

def rule28(*args):
  return factory.get(args[2])

def rule29(*args):
  return factory.call(args[2])

def rule30(*args):
  return factory.set(args[2])

def rule31(*args):
  return factory.default(args[2])

def rule32(*args):
  return factory.insert(args[2])

def rule33(*args):
  return factory.include(args[2])

def rule34(*args):
  return factory.process(args[2])

def rule35(*args):
  return factory.throw(args[2])

def rule36(*args):
  return factory.return_()

def rule37(*args):
  return factory.stop()

def rule38(*args):
  return "output = ''"

def rule39(*args):
  if args[0].INFOR or args[0].INWHILE:
    return "break LOOP"  # FIXME: This won't work, obviously.
  else:
    return "break"

def rule40(*args):
  if args[0].INFOR:
    return factory.next()
  elif args[0].INWHILE:
    return "continue LOOP"  # FIXME: This won't work, obviously.
  else:
    return "continue"

def rule41(*args):
  if args[2][0][0] in ("'on'", "'off'"):
    args[0].debug_dirs = args[2][0][0] == "'on'"
    return factory.debug(args[2])
  else:
    if args[0].debug_dirs:
      return factory.debug(args[2])
    else:
      return ""

def rule44(*args):
  return factory.if_(*(args[2], args[4], args[5]))

def rule45(*args):
  return factory.if_(*(args[3], args[1]))

def rule46(*args):
  return factory.if_(*("not (%s)" % args[2], args[4], args[5]))

def rule47(*args):
  return factory.if_(*("not (%s)" % args[3], args[1]))

def rule48(*args):
  args[5].insert(0, [args[2], args[4]])
  return args[5]

def rule49(*args):
  return [args[3]]

def rule50(*args):
  return [None]

def rule51(*args):
  return factory.switch(*(args[2], args[5]))

def rule52(*args):
  args[5].insert(0, [args[2], args[4]])
  return args[5]

def rule53(*args):
  return [args[4]]

def rule54(*args):
  return [args[3]]

def rule55(*args):
  return [None]

def rule56(*args):
  retval = args[0].INFOR
  args[0].INFOR += 1
  return retval

def rule57(*args):
  args[0].INFOR -= 1
  return factory.foreach(*(args[2] + [args[5]]))

def rule58(*args):
  return factory.foreach(*(args[3] + [args[1]]))

def rule59(*args):
  retval = args[0].INWHILE
  args[0].INWHILE += 1
  return retval

def rule60(*args):
  args[0].INWHILE -= 1
  return factory.while_(*(args[2], args[5]))

def rule61(*args):
  return factory.while_(*(args[3], args[1]))

def rule62(*args):
  return [args[1], args[3], args[4]]

def rule63(*args):
  return [args[1], args[3], args[4]]

def rule64(*args):
  return [0, args[1], args[2]]

def rule65(*args):
  return factory.wrapper(*(args[2], args[4]))

def rule66(*args):
  return factory.wrapper(*(args[3], args[1]))

def rule67(*args):
  return factory.try_(*(args[3], args[4]))

def rule68(*args):
  args[5].insert(0, [args[2], args[4]])
  return args[5]

def rule69(*args):
  args[5].insert(0, [None, args[4]])
  return args[5]

def rule70(*args):
  args[4].insert(0, [None, args[3]])
  return args[4]

def rule71(*args):
  return [args[3]]

def rule72(*args):
  return [0]

def rule73(*args):
  return factory.use(args[2])

def rule74(*args):
  return args[0].push_defblock()

def rule75(*args):
  return factory.view(*(args[2], args[5]. args[0].pop_defblock()))

def rule76(*args):
  raise None  # PERL

def rule77(*args):
  raise None  # PERL

def rule78(*args):
  raise None  # PERL

def rule79(*args):
  raise None  # PERL

def rule80(*args):
  return factory.filter_(*(args[2], args[4]))

def rule81(*args):
  return factory.filter_(*(args[3], args[1]))

def rule82(*args):
  name = "/".join(args[0].DEFBLOCKS)
  args[0].DEFBLOCKS.pop()
  args[0].define_block(name, args[4])
  return None

def rule83(*args):
  args[0].DEFBLOCKS.append(args[2])
  return args[2]

def rule85(*args):
  args[1] = re.sub(r"'(.*)'", r"\1", args[1])
  return args[1]

def rule88(*args):
  if args[2]:
    sys.stderr.write("experimental block args: [%s]\n" % ", ".join(args[2]))
  return factory.anon_block(args[4])

def rule89(*args):
  return factory.capture(*(args[1], args[3]))

def rule90(*args):
  return factory.macro(*(args[2], args[6], args[4]))

def rule91(*args):
  return factory.macro(*(args[2], args[3]))

def rule93(*args):
  return args[3]

def rule94(*args):
  args[1].append(args[2])
  return args[1]

def rule95(*args):
  return args[1]

def rule96(*args):
  return [args[1]]

def rule97(*args):
  args[1].extend(args[2])
  return args[1]

def rule100(*args):
  if args[3] and args[3][0] == "'":
    args[3] = args[3][1:]
  if args[3] and args[3][-1] == "'":
    args[3] = args[3][:-1]
  args[3] = re.sub(r"\\'", "'", args[3])
  return [args[1], args[3]]

def rule101(*args):
  return [args[1], args[4]]

def rule102(*args):
  return [args[1], args[3]]

def rule105(*args):
  return "util.make_list(%s)" % args[2]

def rule106(*args):
  return "util.make_list(%s)" % args[2]

def rule107(*args):
  return "[ ]"

def rule108(*args):
  return "{ %s }" % args[2]

def rule109(*args):
  return factory.ident(args[1])

def rule110(*args):
  return factory.identref(args[2])

def rule111(*args):
  return factory.quoted(args[2])

def rule114(*args):
  return "%s, %s" % (args[1], args[2])

def rule117(*args):
  return "xrange(int(%s), int(%s) + 1)" % (args[1], args[3])

def rule119(*args):
  return ""

def rule120(*args):
  return "%s, %s" % (args[1], args[2])

def rule123(*args):
  return "%s: %s" % (args[1], args[3])

def rule124(*args):
  # return "%s => %s" % (args[1], args[3])  # And this is too.
  return "%s: %s" % (args[1], args[3])

def rule125(*args):
  args[1].extend(args[3])
  return args[1]

def rule126(*args):
  args[1].extend(x for comp in args[3].split(".") for x in (comp, 0))
  return args[1]

def rule128(*args):
  return [args[1], 0]

def rule129(*args):
  return [args[1], factory.args(args[3])]

def rule130(*args):
  return "'%s'" % args[1]

def rule131(*args):
  return args[2]

def rule132(*args):
  if args[0].V1DOLLAR:
    return "'%s'" % args[2]
  else:
    return factory.ident(["'%s'" % args[2], 0])

def rule133(*args):
  return "%s %s %s" % (args[1], args[2], args[3])

def rule134(*args):
  return "%s %s %s" % (args[1], args[2], args[3])

def rule135(*args):
  return "%s %s %s" % (args[1], args[2], args[3])

def rule136(*args):
  return "int(%s / %s)" % (args[1], args[3])

def rule137(*args):
  return "%s %% %s" % (args[1], args[3])

def rule138(*args):
  return "%s %s %s" % (args[1], CMPOP[args[2]], args[3])

def rule139(*args):
  return "str(%s) + str(%s)" % (args[1], args[3])

def rule140(*args):
  return "(perlbool(%s) and perlbool(%s)).value" % (args[1], args[3])

def rule141(*args):
  return "(perlbool(%s) or perlbool(%s)).value" % (args[1], args[3])

def rule142(*args):
  return "not perlbool(%s)" % args[2]

def rule143(*args):
  return "(perlbool(%s) and perlbool(%s, True) or perlbool(%s, False)).value" \
      % (args[1], args[3], args[5])

def rule144(*args):
  return factory.assign(*args[2])

def rule145(*args):
  return "(%s)" % args[2]

def rule147(*args):
  args[1].extend(args[2])
  return args[1]

def rule150(*args):
  return [args[1], args[3]]

def rule151(*args):
  return [args[1], args[3]]

def rule152(*args):
  args[1].append(args[2])
  return args[1]

def rule153(*args):
  args[1][0].append(args[2])
  return args[1]


def rule154(*args):
  args[1][0].append("'', %s" % factory.assign(*(args[2], args[4])))
  return args[1]

def rule155(*args):
  return args[1]

def rule156(*args):
  return [ [] ]

def rule157(*args):
  args[3].append(args[1])
  return args[3]

def rule160(*args):
  return factory.quoted(args[2])

def rule162(*args):
  return [[factory.ident(args[2])], args[3]]

def rule163(*args):
  return [args[1], args[2]]

def rule164(*args):
  return [args[1], args[3]]

def rule165(*args):
  args[1].append(args[3])
  return args[1]

def rule166(*args):
  return [args[1]]

def rule167(*args):
  return factory.quoted(args[2])

def rule168(*args):
  return "'%s'" % args[1]

def rule170(*args):
  return "%s.%s" % (args[1], args[3])

def rule175(*args):
  if args[2] is not None:
    args[1].append(args[2])
  return args[1]

def rule176(*args):
  return []

def rule177(*args):
  return factory.ident(args[1])

def rule178(*args):
  return factory.text(args[1])

def rule179(*args):
  return None




RULES = [
	[#rule 0
		 '$start', 2, None
	],
	[#rule 1
		 'template', 1, rule1
## sub
## #line 64 "parser.yp"
## { $factory->template($_[1])           }
	],
	[#rule 2
		 'block', 1, rule2
## sub
## #line 67 "parser.yp"
## { $factory->block($_[1])              }
	],
	[#rule 3
		 'block', 0, rule3
## sub
## #line 68 "parser.yp"
## { $factory->block()                   }
	],
	[#rule 4
		 'chunks', 2, rule4
## sub
## #line 71 "parser.yp"
## { push(@{$_[1]}, $_[2]) 
## 					if defined $_[2]; $_[1]           }
	],
	[#rule 5
		 'chunks', 1, rule5
## sub
## #line 73 "parser.yp"
## { defined $_[1] ? [ $_[1] ] : [ ]     }
	],
	[#rule 6
		 'chunk', 1, rule6
## sub
## #line 76 "parser.yp"
## { $factory->textblock($_[1])          }
	],
	[#rule 7
		 'chunk', 2, rule7
## sub
## #line 77 "parser.yp"
## { return '' unless $_[1];
##                            $_[0]->location() . $_[1];
##                          }
	],
	[#rule 8
		 'statement', 1, None
	],
	[#rule 9
		 'statement', 1, None
	],
	[#rule 10
		 'statement', 1, None
	],
	[#rule 11
		 'statement', 1, None
	],
	[#rule 12
		 'statement', 1, None
	],
	[#rule 13
		 'statement', 1, None
	],
	[#rule 14
		 'statement', 1, None
	],
	[#rule 15
		 'statement', 1, None
	],
	[#rule 16
		 'statement', 1, rule16
## sub
## #line 90 "parser.yp"
## { $factory->get($_[1])                }
	],
	[#rule 17
		 'statement', 2, rule17
## sub
## #line 91 "parser.yp"
## { $_[0]->add_metadata($_[2]);         }
	],
	[#rule 18
		 'statement', 0, None
	],
	[#rule 19
		 'directive', 1, rule19
## sub
## #line 95 "parser.yp"
## { $factory->set($_[1])                }
	],
	[#rule 20
		 'directive', 1, None
	],
	[#rule 21
		 'directive', 1, None
	],
	[#rule 22
		 'directive', 1, None
	],
	[#rule 23
		 'directive', 1, None
	],
	[#rule 24
		 'directive', 1, None
	],
	[#rule 25
		 'directive', 1, None
	],
	[#rule 26
		 'atomexpr', 1, rule26
## sub
## #line 109 "parser.yp"
## { $factory->get($_[1])                }
	],
	[#rule 27
		 'atomexpr', 1, None
	],
	[#rule 28
		 'atomdir', 2, rule28
## sub
## #line 113 "parser.yp"
## { $factory->get($_[2])                }
	],
	[#rule 29
		 'atomdir', 2, rule29
## sub
## #line 114 "parser.yp"
## { $factory->call($_[2])               }
	],
	[#rule 30
		 'atomdir', 2, rule30
## sub
## #line 115 "parser.yp"
## { $factory->set($_[2])                }
	],
	[#rule 31
		 'atomdir', 2, rule31
## sub
## #line 116 "parser.yp"
## { $factory->default($_[2])            }
	],
	[#rule 32
		 'atomdir', 2, rule32
## sub
## #line 117 "parser.yp"
## { $factory->insert($_[2])             }
	],
	[#rule 33
		 'atomdir', 2, rule33
## sub
## #line 118 "parser.yp"
## { $factory->include($_[2])            }
	],
	[#rule 34
		 'atomdir', 2, rule34
## sub
## #line 119 "parser.yp"
## { $factory->process($_[2])            }
	],
	[#rule 35
		 'atomdir', 2, rule35
## sub
## #line 120 "parser.yp"
## { $factory->throw($_[2])              }
	],
	[#rule 36
		 'atomdir', 1, rule36
## sub
## #line 121 "parser.yp"
## { $factory->return()                  }
	],
	[#rule 37
		 'atomdir', 1, rule37
## sub
## #line 122 "parser.yp"
## { $factory->stop()                    }
	],
	[#rule 38
		 'atomdir', 1, rule38
## sub
## #line 123 "parser.yp"
## { "\$output = '';";                   }
	],
	[#rule 39
		 'atomdir', 1, rule39
## sub
## #line 124 "parser.yp"
## { $_[0]->{ infor } || $_[0]->{ inwhile }
##                                         ? 'last loop;'
##                                         : 'last;'                         }
	],
	[#rule 40
		 'atomdir', 1, rule40
## sub
## #line 127 "parser.yp"
## { $_[0]->{ infor }
## 					? $factory->next()
## 				        : ($_[0]->{ inwhile }
##                                            ? 'next loop;'
##                                            : 'next;')                     }
	],
	[#rule 41
		 'atomdir', 2, rule41
## sub
## #line 132 "parser.yp"
## { if ($_[2]->[0]->[0] =~ /^'(on|off)'$/) {
## 				          $_[0]->{ debug_dirs } = ($1 eq 'on');
## 					  $factory->debug($_[2]);
## 				      }
## 				      else {
## 					  $_[0]->{ debug_dirs } ? $factory->debug($_[2]) : '';
## 				      }
## 				    }
	],
	[#rule 42
		 'atomdir', 1, None
	],
	[#rule 43
		 'atomdir', 1, None
	],
	[#rule 44
		 'condition', 6, rule44
## sub
## #line 145 "parser.yp"
## { $factory->if(@_[2, 4, 5])           }
	],
	[#rule 45
		 'condition', 3, rule45
## sub
## #line 146 "parser.yp"
## { $factory->if(@_[3, 1])              }
	],
	[#rule 46
		 'condition', 6, rule46
## sub
## #line 148 "parser.yp"
## { $factory->if("!($_[2])", @_[4, 5])  }
	],
	[#rule 47
		 'condition', 3, rule47
## sub
## #line 149 "parser.yp"
## { $factory->if("!($_[3])", $_[1])     }
	],
	[#rule 48
		 'else', 5, rule48
## sub
## #line 153 "parser.yp"
## { unshift(@{$_[5]}, [ @_[2, 4] ]);
## 				      $_[5];                              }
	],
	[#rule 49
		 'else', 3, rule49
## sub
## #line 155 "parser.yp"
## { [ $_[3] ]                           }
	],
	[#rule 50
		 'else', 0, rule50
## sub
## #line 156 "parser.yp"
## { [ undef ]                           }
	],
	[#rule 51
		 'switch', 6, rule51
## sub
## #line 160 "parser.yp"
## { $factory->switch(@_[2, 5])          }
	],
	[#rule 52
		 'case', 5, rule52
## sub
## #line 164 "parser.yp"
## { unshift(@{$_[5]}, [ @_[2, 4] ]); 
## 				      $_[5];                              }
	],
	[#rule 53
		 'case', 4, rule53
## sub
## #line 166 "parser.yp"
## { [ $_[4] ]                           }
	],
	[#rule 54
		 'case', 3, rule54
## sub
## #line 167 "parser.yp"
## { [ $_[3] ]                           }
	],
	[#rule 55
		 'case', 0, rule55
## sub
## #line 168 "parser.yp"
## { [ undef ]                           }
	],
	[#rule 56
		 '@1-3', 0, rule56
## sub
## #line 171 "parser.yp"
## { $_[0]->{ infor }++                  }
	],
	[#rule 57
		 'loop', 6, rule57
## sub
## #line 172 "parser.yp"
## { $_[0]->{ infor }--;
## 				      $factory->foreach(@{$_[2]}, $_[5])  }
	],
	[#rule 58
		 'loop', 3, rule58
## sub
## #line 176 "parser.yp"
## { $factory->foreach(@{$_[3]}, $_[1])  }
	],
	[#rule 59
		 '@2-3', 0, rule59
## sub
## #line 177 "parser.yp"
## { $_[0]->{ inwhile }++                }
	],
	[#rule 60
		 'loop', 6, rule60
## sub
## #line 178 "parser.yp"
## { $_[0]->{ inwhile }--;
##                                       $factory->while(@_[2, 5])           }
	],
	[#rule 61
		 'loop', 3, rule61
## sub
## #line 180 "parser.yp"
## { $factory->while(@_[3, 1])           }
	],
	[#rule 62
		 'loopvar', 4, rule62
## sub
## #line 183 "parser.yp"
## { [ @_[1, 3, 4] ]                     }
	],
	[#rule 63
		 'loopvar', 4, rule63
## sub
## #line 184 "parser.yp"
## { [ @_[1, 3, 4] ]                     }
	],
	[#rule 64
		 'loopvar', 2, rule64
## sub
## #line 185 "parser.yp"
## { [ 0, @_[1, 2] ]                     }
	],
	[#rule 65
		 'wrapper', 5, rule65
## sub
## #line 189 "parser.yp"
## { $factory->wrapper(@_[2, 4])         }
	],
	[#rule 66
		 'wrapper', 3, rule66
## sub
## #line 191 "parser.yp"
## { $factory->wrapper(@_[3, 1])         }
	],
	[#rule 67
		 'try', 5, rule67
## sub
## #line 195 "parser.yp"
## { $factory->try(@_[3, 4])             }
	],
	[#rule 68
		 'final', 5, rule68
## sub
## #line 199 "parser.yp"
## { unshift(@{$_[5]}, [ @_[2,4] ]);
## 				      $_[5];                              }
	],
	[#rule 69
		 'final', 5, rule69
## sub
## #line 202 "parser.yp"
## { unshift(@{$_[5]}, [ undef, $_[4] ]);
## 				      $_[5];                              }
	],
	[#rule 70
		 'final', 4, rule70
## sub
## #line 205 "parser.yp"
## { unshift(@{$_[4]}, [ undef, $_[3] ]);
## 				      $_[4];                              }
	],
	[#rule 71
		 'final', 3, rule71
## sub
## #line 207 "parser.yp"
## { [ $_[3] ]                           }
	],
	[#rule 72
		 'final', 0, rule72
## sub
## #line 208 "parser.yp"
## { [ 0 ] }
	],
	[#rule 73
		 'use', 2, rule73
## sub
## #line 211 "parser.yp"
## { $factory->use($_[2])                }
	],
	[#rule 74
		 '@3-3', 0, rule74
## sub
## #line 214 "parser.yp"
## { $_[0]->push_defblock();		  }
	],
	[#rule 75
		 'view', 6, rule75
## sub
## #line 215 "parser.yp"
## { $factory->view(@_[2,5],
## 						     $_[0]->pop_defblock) }
	],
	[#rule 76
		 '@4-2', 0, rule76
## sub
## #line 219 "parser.yp"
## { ${$_[0]->{ inperl }}++;             }
	],
	[#rule 77
		 'perl', 5, rule77
## sub
## #line 220 "parser.yp"
## { ${$_[0]->{ inperl }}--;
## 				      $_[0]->{ eval_perl } 
## 				      ? $factory->perl($_[4])             
## 				      : $factory->no_perl();              }
	],
	[#rule 78
		 '@5-1', 0, rule78
## sub
## #line 226 "parser.yp"
## { ${$_[0]->{ inperl }}++; 
## 				      $rawstart = ${$_[0]->{'line'}};     }
	],
	[#rule 79
		 'rawperl', 5, rule79
## sub
## #line 228 "parser.yp"
## { ${$_[0]->{ inperl }}--;
## 				      $_[0]->{ eval_perl } 
## 				      ? $factory->rawperl($_[4], $rawstart)
## 				      : $factory->no_perl();              }
	],
	[#rule 80
		 'filter', 5, rule80
## sub
## #line 235 "parser.yp"
## { $factory->filter(@_[2,4])           }
	],
	[#rule 81
		 'filter', 3, rule81
## sub
## #line 237 "parser.yp"
## { $factory->filter(@_[3,1])           }
	],
	[#rule 82
		 'defblock', 5, rule82
## sub
## #line 242 "parser.yp"
## { my $name = join('/', @{ $_[0]->{ defblocks } });
## 				      pop(@{ $_[0]->{ defblocks } });
## 				      $_[0]->define_block($name, $_[4]); 
## 				      undef
## 				    }
	],
	[#rule 83
		 'defblockname', 2, rule83
## sub
## #line 249 "parser.yp"
## { push(@{ $_[0]->{ defblocks } }, $_[2]);
## 				      $_[2];
## 				    }
	],
	[#rule 84
		 'blockname', 1, None
	],
	[#rule 85
		 'blockname', 1, rule85
## sub
## #line 255 "parser.yp"
## { $_[1] =~ s/^'(.*)'$/$1/; $_[1]      }
	],
	[#rule 86
		 'blockargs', 1, None
	],
	[#rule 87
		 'blockargs', 0, None
	],
	[#rule 88
		 'anonblock', 5, rule88
## sub
## #line 263 "parser.yp"
## { local $" = ', ';
## 				      print stderr "experimental block args: [@{ $_[2] }]\n"
## 					  if $_[2];
## 				      $factory->anon_block($_[4])         }
	],
	[#rule 89
		 'capture', 3, rule89
## sub
## #line 269 "parser.yp"
## { $factory->capture(@_[1, 3])         }
	],
	[#rule 90
		 'macro', 6, rule90
## sub
## #line 273 "parser.yp"
## { $factory->macro(@_[2, 6, 4])        }
	],
	[#rule 91
		 'macro', 3, rule91
## sub
## #line 274 "parser.yp"
## { $factory->macro(@_[2, 3])           }
	],
	[#rule 92
		 'mdir', 1, None
	],
	[#rule 93
		 'mdir', 4, rule93
## sub
## #line 278 "parser.yp"
## { $_[3]                               }
	],
	[#rule 94
		 'margs', 2, rule94
## sub
## #line 281 "parser.yp"
## { push(@{$_[1]}, $_[2]); $_[1]        }
	],
	[#rule 95
		 'margs', 2, rule95
## sub
## #line 282 "parser.yp"
## { $_[1]                               }
	],
	[#rule 96
		 'margs', 1, rule96
## sub
## #line 283 "parser.yp"
## { [ $_[1] ]                           }
	],
	[#rule 97
		 'metadata', 2, rule97
## sub
## #line 286 "parser.yp"
## { push(@{$_[1]}, @{$_[2]}); $_[1]     }
	],
	[#rule 98
		 'metadata', 2, None
	],
	[#rule 99
		 'metadata', 1, None
	],
	[#rule 100
		 'meta', 3, rule100
## sub
## #line 291 "parser.yp"
## { for ($_[3]) { s/^'//; s/'$//; 
## 						       s/\\'/'/g  }; 
## 					 [ @_[1,3] ] }
	],
	[#rule 101
		 'meta', 5, rule101
## sub
## #line 294 "parser.yp"
## { [ @_[1,4] ] }
	],
	[#rule 102
		 'meta', 3, rule102
## sub
## #line 295 "parser.yp"
## { [ @_[1,3] ] }
	],
	[#rule 103
		 'term', 1, None
	],
	[#rule 104
		 'term', 1, None
	],
	[#rule 105
		 'lterm', 3, rule105
## sub
## #line 307 "parser.yp"
## { "[ $_[2] ]"                         }
	],
	[#rule 106
		 'lterm', 3, rule106
## sub
## #line 308 "parser.yp"
## { "[ $_[2] ]"                         }
	],
	[#rule 107
		 'lterm', 2, rule107
## sub
## #line 309 "parser.yp"
## { "[ ]"                               }
	],
	[#rule 108
		 'lterm', 3, rule108
## sub
## #line 310 "parser.yp"
## { "{ $_[2]  }"                        }
	],
	[#rule 109
		 'sterm', 1, rule109
## sub
## #line 313 "parser.yp"
## { $factory->ident($_[1])              }
	],
	[#rule 110
		 'sterm', 2, rule110
## sub
## #line 314 "parser.yp"
## { $factory->identref($_[2])           }
	],
	[#rule 111
		 'sterm', 3, rule111
## sub
## #line 315 "parser.yp"
## { $factory->quoted($_[2])             }
	],
	[#rule 112
		 'sterm', 1, None
	],
	[#rule 113
		 'sterm', 1, None
	],
	[#rule 114
		 'list', 2, rule114
## sub
## #line 320 "parser.yp"
## { "$_[1], $_[2]"                      }
	],
	[#rule 115
		 'list', 2, None
	],
	[#rule 116
		 'list', 1, None
	],
	[#rule 117
		 'range', 3, rule117
## sub
## #line 325 "parser.yp"
## { $_[1] . '..' . $_[3]                }
	],
	[#rule 118
		 'hash', 1, None
	],
	[#rule 119
		 'hash', 0, rule119
## sub
## #line 330 "parser.yp"
## { "" }
	],
	[#rule 120
		 'params', 2, rule120
## sub
## #line 333 "parser.yp"
## { "$_[1], $_[2]"                      }
	],
	[#rule 121
		 'params', 2, None
	],
	[#rule 122
		 'params', 1, None
	],
	[#rule 123
		 'param', 3, rule123
## sub
## #line 338 "parser.yp"
## { "$_[1] => $_[3]"                    }
	],
	[#rule 124
		 'param', 3, rule124
## sub
## #line 339 "parser.yp"
## { "$_[1] => $_[3]"                    }
	],
	[#rule 125
		 'ident', 3, rule125
## sub
## #line 342 "parser.yp"
## { push(@{$_[1]}, @{$_[3]}); $_[1]     }
	],
	[#rule 126
		 'ident', 3, rule126
## sub
## #line 343 "parser.yp"
## { push(@{$_[1]}, 
## 					   map {($_, 0)} split(/\./, $_[3]));
## 				      $_[1];			          }
	],
	[#rule 127
		 'ident', 1, None
	],
	[#rule 128
		 'node', 1, rule128
## sub
## #line 349 "parser.yp"
## { [ $_[1], 0 ]                        }
	],
	[#rule 129
		 'node', 4, rule129
## sub
## #line 350 "parser.yp"
## { [ $_[1], $factory->args($_[3]) ]    }
	],
	[#rule 130
		 'item', 1, rule130
## sub
## #line 353 "parser.yp"
## { "'$_[1]'"                           }
	],
	[#rule 131
		 'item', 3, rule131
## sub
## #line 354 "parser.yp"
## { $_[2]                               }
	],
	[#rule 132
		 'item', 2, rule132
## sub
## #line 355 "parser.yp"
## { $_[0]->{ v1dollar }
## 				       ? "'$_[2]'" 
## 				       : $factory->ident(["'$_[2]'", 0])  }
	],
	[#rule 133
		 'expr', 3, rule133
## sub
## #line 360 "parser.yp"
## { "$_[1] $_[2] $_[3]"                 }
	],
	[#rule 134
		 'expr', 3, rule134
## sub
## #line 361 "parser.yp"
## { "$_[1] $_[2] $_[3]"                 }
	],
	[#rule 135
		 'expr', 3, rule135
## sub
## #line 362 "parser.yp"
## { "$_[1] $_[2] $_[3]"                 }
	],
	[#rule 136
		 'expr', 3, rule136
## sub
## #line 363 "parser.yp"
## { "int($_[1] / $_[3])"                }
	],
	[#rule 137
		 'expr', 3, rule137
## sub
## #line 364 "parser.yp"
## { "$_[1] % $_[3]"                     }
	],
	[#rule 138
		 'expr', 3, rule138
## sub
## #line 365 "parser.yp"
## { "$_[1] $cmpop{ $_[2] } $_[3]"       }
	],
	[#rule 139
		 'expr', 3, rule139
## sub
## #line 366 "parser.yp"
## { "$_[1]  . $_[3]"                    }
	],
	[#rule 140
		 'expr', 3, rule140
## sub
## #line 367 "parser.yp"
## { "$_[1] && $_[3]"                    }
	],
	[#rule 141
		 'expr', 3, rule141
## sub
## #line 368 "parser.yp"
## { "$_[1] || $_[3]"                    }
	],
	[#rule 142
		 'expr', 2, rule142
## sub
## #line 369 "parser.yp"
## { "! $_[2]"                           }
	],
	[#rule 143
		 'expr', 5, rule143
## sub
## #line 370 "parser.yp"
## { "$_[1] ? $_[3] : $_[5]"             }
	],
	[#rule 144
		 'expr', 3, rule144
## sub
## #line 371 "parser.yp"
## { $factory->assign(@{$_[2]})          }
	],
	[#rule 145
		 'expr', 3, rule145
## sub
## #line 372 "parser.yp"
## { "($_[2])"                           }
	],
	[#rule 146
		 'expr', 1, None
	],
	[#rule 147
		 'setlist', 2, rule147
## sub
## #line 376 "parser.yp"
## { push(@{$_[1]}, @{$_[2]}); $_[1]     }
	],
	[#rule 148
		 'setlist', 2, None
	],
	[#rule 149
		 'setlist', 1, None
	],
	[#rule 150
		 'assign', 3, rule150
## sub
## #line 382 "parser.yp"
## { [ $_[1], $_[3] ]                    }
	],
	[#rule 151
		 'assign', 3, rule151
## sub
## #line 383 "parser.yp"
## { [ @_[1,3] ]                         }
	],
	[#rule 152
		 'args', 2, rule152
## sub
## #line 390 "Parser.yp"
## { push(@{$_[1]}, $_[2]); $_[1]        }
	],
	[#Rule 153
		 'args', 2, rule153
## sub
## #line 391 "Parser.yp"
## { push(@{$_[1]->[0]}, $_[2]); $_[1]   }
	],
	[#Rule 154
		 'args', 4, rule154
## sub
## #line 392 "Parser.yp"
## { push(@{$_[1]->[0]}, "'', " . 
## 				      $factory->assign(@_[2,4])); $_[1]  }
	],
	[#Rule 155
		 'args', 2, rule155
## sub
## #line 394 "Parser.yp"
## { $_[1]                               }
	],
	[#Rule 156
		 'args', 0, rule156
## sub
## #line 395 "Parser.yp"
## { [ [ ] ]                             }
	],
	[#Rule 157
		 'lnameargs', 3, rule157
## sub
## #line 405 "Parser.yp"
## { push(@{$_[3]}, $_[1]); $_[3]        }
	],
	[#Rule 158
		 'lnameargs', 1, None
	],
	[#Rule 159
		 'lvalue', 1, None
	],
	[#Rule 160
		 'lvalue', 3, rule160
## sub
## #line 410 "Parser.yp"
## { $factory->quoted($_[2])             }
	],
	[#Rule 161
		 'lvalue', 1, None
	],
	[#Rule 162
		 'nameargs', 3, rule162
## sub
## #line 414 "Parser.yp"
## { [ [$factory->ident($_[2])], $_[3] ]   }
	],
	[#Rule 163
		 'nameargs', 2, rule163
## sub
## #line 415 "Parser.yp"
## { [ @_[1,2] ] }
	],
	[#Rule 164
		 'nameargs', 4, rule164
## sub
## #line 416 "Parser.yp"
## { [ @_[1,3] ] }
	],
	[#Rule 165
		 'names', 3, rule165
## sub
## #line 419 "Parser.yp"
## { push(@{$_[1]}, $_[3]); $_[1] }
	],
	[#Rule 166
		 'names', 1, rule166
## sub
## #line 420 "Parser.yp"
## { [ $_[1] ]                    }
	],
	[#Rule 167
		 'name', 3, rule167
## sub
## #line 423 "Parser.yp"
## { $factory->quoted($_[2])  }
	],
	[#Rule 168
		 'name', 1, rule168
## sub
## #line 424 "Parser.yp"
## { "'$_[1]'" }
	],
	[#Rule 169
		 'name', 1, None
	],
	[#Rule 170
		 'filename', 3, rule170
## sub
## #line 436 "Parser.yp"
## { "$_[1].$_[3]" }
	],
	[#Rule 171
		 'filename', 1, None
	],
	[#Rule 172
		 'filepart', 1, None
	],
	[#Rule 173
		 'filepart', 1, None
	],
	[#Rule 174
		 'filepart', 1, None
	],
	[#Rule 175
		 'quoted', 2, rule175
## sub
## #line 450 "Parser.yp"
## { push(@{$_[1]}, $_[2]) 
## 				          if defined $_[2]; $_[1]         }
	],
	[#Rule 176
		 'quoted', 0, rule176
## sub
## #line 452 "Parser.yp"
## { [ ]                                 }
	],
	[#Rule 177
		 'quotable', 1, rule177
## sub
## #line 455 "Parser.yp"
## { $factory->ident($_[1])              }
	],
	[#Rule 178
		 'quotable', 1, rule178
## sub
## #line 456 "Parser.yp"
## { $factory->text($_[1])               }
	],
	[#Rule 179
		 'quotable', 1, rule179
## sub
## #line 457 "Parser.yp"
## { undef                               }
	]
];
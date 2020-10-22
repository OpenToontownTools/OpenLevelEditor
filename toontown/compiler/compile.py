#!/usr/bin/env python3
import os
import sys
import glob

if ConfigVariableString("compiler") == 'clash':
    # Clash uses an old version of libpandadna's compiler
    from .clashdna.dna.base import DNAStorage
    from .clashdna.dna.components import DNARoot
    from .clashdna.dna.parser.tokens import *

if ConfigVariableString("compiler") == 'libpandadna':
    from .libpandadna.dna.base import DNAStorage
    from .libpandadna.dna.components import DNARoot
    from .libpandadna.dna.parser.tokens import *
from ply import lex

lexer = lex.lex(optimize = 0)


class DNAError(Exception):
    pass


import builtins

builtins.DNAError = DNAError


def loadDNAFile(dnaStore, filename):
    root = DNARoot.DNARoot(name = 'root', dnaStore = dnaStore)
    with open(filename, 'r') as f:
        data = f.read().strip()
        if not data:
            print('Warning', filename, 'is an empty file.')
            return ''
        f.seek(0)
        root.read(f)
    return root.traverse(recursive = True, verbose = 0)


def process_single_file(filename):
    dnaStore = DNAStorage.DNAStorage()
    rootData = loadDNAFile(dnaStore, filename)

    data = dnaStore.dump(verbose = 0)
    output = os.path.splitext(filename)[0] + '.pdna'
    print('Writing...', output)
    data.extend(rootData)

    with open(output, 'wb') as f:
        f.write(b'PDNA\n')
        f.write(b'\x00')
        f.write(b'\n')
        f.write(data)

    print(f'Done saving {filename}.')

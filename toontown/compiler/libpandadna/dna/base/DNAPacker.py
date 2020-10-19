import struct
from typing import Union

# Byte orders...
LITTLE_ENDIAN = '<'
BIG_ENDIAN = '>'

# Data types...

# Signed integers...
INT8 = 'b'
INT16 = 'h'
INT32 = 'i'
INT64 = 'q'

# Unsigned integers...
UINT8 = 'B'
UINT16 = 'H'
UINT32 = 'I'
UINT64 = 'Q'

# Strings...
STRING = 'S'

# Booleans...
BOOLEAN = '?'

# Floats... (signed)
FLOAT32 = 'f'
FLOAT64 = 'd'  # double


class DNAPacker(bytearray):
    def __init__(self, name='DNAPacker', packer=None, verbose=False):
        if packer is not None:
            super().__init__(packer)
        else:
            super().__init__()
        self.name = name
        self.verbose = verbose

    def debug(self, message: str):
        if self.verbose:
            print(f'{self.name}: {message}')

    def pack(self, fieldName: str, value: Union[str, int, float, bool], dataType: str, byteOrder=LITTLE_ENDIAN):
        self.debug(f'packing... {fieldName}: {repr(value)}')

        # If we're packing a string, add the length header:
        if dataType == STRING:
            self.extend(struct.pack(UINT16, len(value)))
            self.extend(value.encode('utf-8'))
        elif dataType in {FLOAT32, FLOAT64}:
            self.extend(struct.pack(byteOrder + dataType, float(value)))
        else:
            self.extend(struct.pack(byteOrder + dataType, int(value)))

    def packColor(self, fieldName: str, r, g, b, a=None, byteOrder=LITTLE_ENDIAN):
        self.debug(f'packing... {fieldName}: ({r}, {g}, {b}, {a})')

        for component in (r, g, b, a):
            if component is not None:
                self.extend(struct.pack(byteOrder + UINT8, int(component * 255)))

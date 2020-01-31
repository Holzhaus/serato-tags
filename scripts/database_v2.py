#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import struct
import io
import sys


FIELDPARSERS = {
    'b': lambda x: struct.unpack('?', x)[0],
    'o': lambda x: tuple(parse(io.BytesIO(x))),
    'p': lambda x: (x[1:] + b'\00').decode('utf-16'),
    'r': lambda x: tuple(parse(io.BytesIO(x))),
    's': lambda x: struct.unpack('>H', x)[0],
    't': lambda x: (x[1:] + b'\00').decode('utf-16'),
    'u': lambda x: struct.unpack('>I', x)[0],
}

FIELDNAMES = {
    # Database
    'vrsn': 'Version',
    'otrk': 'Track',
    'ttyp': 'File Type',
    'pfil': 'File Path',
    'tsng': 'Song Title',
    'tlen': 'Length',
    'tbit': 'Bitrate',
    'tsmp': 'Sample Rate',
    'tbpm': 'BPM',
    'tadd': 'Date added',
    'uadd': 'Date added',
    'tkey': 'Key',
    'bbgl': 'Beatgrid Locked',
    'tart': 'Artist',
    'utme': 'File Time',
    'bmis': 'Missing',
    # Crates
    'osrt': 'Sorting',
    'brev': 'Reverse Order',
    'ovct': 'Column Title',
    'tvcn': 'Column Name',
    'tvcw': 'Column Width',
    'ptrk': 'Track Path',
}


def parse(fp):
    for i, header in enumerate(iter(lambda: fp.read(8), b'')):
        assert len(header) == 8
        name_ascii, length = struct.unpack('>4sI', header)

        name = name_ascii.decode('ascii')
        type_id = name[0]

        # vrsn field has no type_id, but contains text
        if name == 'vrsn':
            type_id = 't'

        data = fp.read(length)
        assert len(data) == length

        try:
            fieldparser = FIELDPARSERS[type_id]
        except KeyError:
            value = data
        else:
            value = fieldparser(data)

        yield name, length, value


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE', type=argparse.FileType('rb'))
    args = parser.parse_args(argv)

    for name, length, value in parse(args.file):
        fieldname = FIELDNAMES.get(name, 'Unknown')
        if isinstance(value, tuple):
            print('{name} ({fieldname}, {length} B)'.format(
                name=name,
                fieldname=fieldname,
                length=length,
            ))
            for name, length, value in value:
                fieldname = FIELDNAMES.get(name, 'Unknown')
                print('  {name} ({fieldname}, {length} B): {value!r}'.format(
                    name=name,
                    fieldname=fieldname,
                    length=length,
                    value=value,
                ))
        else:
            print('{name} ({length} B): {value!r}'.format(
                name=name,
                length=length,
                fieldname=fieldname,
                value=value,
            ))

    return 0


if __name__ == '__main__':
    sys.exit(main())

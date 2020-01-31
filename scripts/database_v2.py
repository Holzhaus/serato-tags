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
    'vrsn': 'Version',
    'trk': 'Track',
    'typ': 'File Type',
    'fil': 'File Name',
    'sng': 'Song Title',
    'len': 'Length',
    'siz': 'File Size',
    'bit': 'Bitrate',
    'smp': 'Sample Rate',
    'bpm': 'BPM',
    'add': 'Date added',
    'key': 'Key',
    'fsb': 'File Size',
    'bgl': 'Beatgrid Locked',
}


def parse(fp):
    for i, header in enumerate(iter(lambda: fp.read(8), b'')):
        assert len(header) == 8
        type_id_ascii, name_ascii, length = struct.unpack('>c3sI', header)

        type_id = type_id_ascii.decode('ascii')
        name = name_ascii.decode('ascii')

        # vrsn field has no type_id, but contains text
        if type_id == 'v' and name == 'rsn':
            name = 'vrsn'
            type_id = 't'

        data = fp.read(length)
        assert len(data) == length

        try:
            fieldparser = FIELDPARSERS[type_id]
        except KeyError:
            value = data
        else:
            value = fieldparser(data)

        yield name, type_id, length, value


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE', type=argparse.FileType('rb'))
    args = parser.parse_args(argv)

    for name, type_id, length, value in parse(args.file):
        fieldname = FIELDNAMES.get(name, 'Unknown')
        if isinstance(value, tuple):
            print('{name}[{type_id}] ({fieldname}, {length} B)'.format(
                name=name,
                type_id=type_id,
                fieldname=fieldname,
                length=length,
            ))
            for name, type_id, length, value in value:
                fieldname = FIELDNAMES.get(name, 'Unknown')
                print('  {name}[{type_id}] ({fieldname}, {length} B): {value!r}'.format(
                    name=name,
                    type_id=type_id,
                    fieldname=fieldname,
                    length=length,
                    value=value,
                ))
        else:
            print('{name}[{type_id}] ({length} B): {value!r}'.format(
                name=name,
                type_id=type_id,
                length=length,
                fieldname=fieldname,
                value=value,
            ))

    return 0


if __name__ == '__main__':
    sys.exit(main())

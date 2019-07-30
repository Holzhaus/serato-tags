#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import configparser
import io
import shutil
import subprocess
import os
import tempfile
import struct
import sys
import mutagen

FMT_VERSION = 'BB'


def readbytes(fp):
    for x in iter(lambda: fp.read(1), b''):
        if x == b'\00':
            break
        yield x


def parse(fp):
    version = struct.unpack(FMT_VERSION, fp.read(2))
    assert version == (0x01, 0x01)

    for i in range(3):
        data = b''.join(readbytes(fp))
        yield float(data.decode('ascii'))


def dump(bpm, field2, field3):
    data = struct.pack(FMT_VERSION, 0x01, 0x01)
    for value, decimals in ((bpm, 2), (field2, 3), (field3, 3)):
        data += '{:.{}f}'.format(value, decimals).encode('ascii')
        data += b'\x00'
    return data


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE')
    parser.add_argument('-e', '--edit', action='store_true')
    args = parser.parse_args(argv)

    tagfile = mutagen.File(args.file)
    if tagfile is not None:
        try:
            tag = tagfile['GEOB:Serato Autotags']
        except KeyError:
            print('File is missing "GEOB:Serato Autotags" tag')
            return 1
        else:
            fp = io.BytesIO(tag.data)
    else:
        fp = open(args.file, mode='rb')

    with fp:
        bpm, field2, field3 = parse(fp)

    if args.edit:
        editor = shutil.which(os.getenv('EDITOR', 'vi'))
        if not editor:
            print('No suitable $EDITOR found.', file=sys.stderr)
            return 1

        with tempfile.NamedTemporaryFile() as f:
            f.write((
                'bpm: {}\n'
                'field2: {}\n'
                'field3: {}\n'
            ).format(bpm, field2, field3).encode('ascii'))
            f.flush()
            status = subprocess.call((editor, f.name))
            f.seek(0)
            output = f.read()

        if status != 0:
            print('Command executation failed with status: {}'.format(status),
                  file=sys.stderr)
            return 1

        cp = configparser.ConfigParser()
        try:
            cp.read_string('[Autotags]\n' + output.decode())
            bpm = cp.getfloat('Autotags', 'bpm')
            field2 = cp.getfloat('Autotags', 'field2')
            field3 = cp.getfloat('Autotags', 'field3')
        except Exception:
            print('Invalid input, no changes made', file=sys.stderr)
            return 1

        new_data = dump(bpm, field2, field3)
        if tagfile:
            if tagfile is not None:
                tagfile['GEOB:Serato Autotags'] = mutagen.id3.GEOB(
                    encoding=0,
                    mime='application/octet-stream',
                    desc='Serato Autotags',
                    data=new_data,
                )
                tagfile.save()
        else:
            with open(args.file, mode='wb') as fp:
                fp.write(new_data)
    else:
        print('BPM: {}'.format(bpm))
        print('field2: {}'.format(field2))
        print('field3: {}'.format(field3))

    return 0


if __name__ == '__main__':
    sys.exit(main())

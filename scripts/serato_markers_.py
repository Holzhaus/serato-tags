#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import io
import struct
import sys
import mutagen

FMT_VERSION = 'BB'


def parse(fp):
    version = struct.unpack(FMT_VERSION, fp.read(2))
    assert version == (0x02, 0x05)

    num_entries = struct.unpack('>I', fp.read(4))[0]
    for i in range(num_entries):
        entry_data = fp.read(0x16)
        assert len(entry_data) == 0x16

        yield struct.unpack('>BIBIB5sIBB', entry_data)

    data = fp.read(4)  # What is this
    print(data)
    assert data.startswith(b'\x07')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE')
    args = parser.parse_args(argv)

    tagfile = mutagen.File(args.file)
    if tagfile is not None:
        try:
            tag = tagfile['GEOB:Serato Markers_']
        except KeyError:
            print('File is missing "GEOB:Serato Markers_" tag')
            return 1
        else:
            fp = io.BytesIO(tag.data)
    else:
        fp = open(args.file, mode='rb')

    with fp:
        for entry in parse(fp):
            print(entry)

    return 0


if __name__ == '__main__':
    sys.exit(main())

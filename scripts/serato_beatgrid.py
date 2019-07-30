#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import collections
import io
import struct
import sys
import mutagen

FMT_VERSION = 'BB'

BeatgridMarker = collections.namedtuple('BeatgridMarker', (
    'position',
    'beats_till_next_marker',
    'bpm',
))


def parse(fp):
    version = struct.unpack(FMT_VERSION, fp.read(2))
    assert version == (0x01, 0x00)

    num_markers = struct.unpack('>I', fp.read(4))[0]
    for i in range(num_markers):
        position = struct.unpack('>f', fp.read(4))[0]
        data = fp.read(4)
        if i == num_markers - 1:
            bpm = struct.unpack('>f', data)[0]
            beats_till_next_marker = None
        else:
            bpm = None
            beats_till_next_marker = struct.unpack('>I', data)[0]
        yield BeatgridMarker(position, beats_till_next_marker, bpm)

    # TODO: What's the meaning of this byte?
    footer = fp.read(1)
    #print(struct.unpack('sbB', footer*3)))
    assert fp.read() == b''


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE')
    parser.add_argument('-e', '--edit', action='store_true')
    args = parser.parse_args(argv)

    tagfile = mutagen.File(args.file)
    if tagfile is not None:
        try:
            tag = tagfile['GEOB:Serato BeatGrid']
        except KeyError:
            print('File is missing "GEOB:Serato BeatGrid" tag')
            return 1
        else:
            fp = io.BytesIO(tag.data)
    else:
        fp = open(args.file, mode='rb')

    with fp:
        for marker in parse(fp):
            print(marker)

    return 0


if __name__ == '__main__':
    sys.exit(main())

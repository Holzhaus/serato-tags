#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import struct
import io
import sys
import mutagen
from PIL import Image
from PIL import ImageColor

FMT_VERSION = 'BB'


def parse(fp):
    version = struct.unpack(FMT_VERSION, fp.read(2))
    assert version == (0x01, 0x05)

    for x in iter(lambda: fp.read(16), b''):
        assert len(x) == 16
        yield bytearray(x)


def draw_waveform(data):
    img = Image.new('RGB', (240, 16), "black")
    pixels = img.load()

    for i in range(img.size[0]):
        rowdata = next(data)
        factor = (len([x for x in rowdata if x < 0x80]) / len(rowdata))

        for j, value in enumerate(rowdata):
            # The algorithm to derive the colors from the data has no real
            # mathematical background and was found by experimenting with
            # different values.
            color = 'hsl({hue:.2f}, {saturation:d}%, {luminance:.2f}%)'.format(
                hue=(factor * 1.5 * 360) % 360,
                saturation=40,
                luminance=(value / 0xFF) * 100,
            )
            pixels[i, j] = ImageColor.getrgb(color)

    return img


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE')
    args = parser.parse_args(argv)

    tagfile = mutagen.File(args.file)
    if tagfile is not None:
        try:
            tag = tagfile['GEOB:Serato Overview']
        except KeyError:
            print('File is missing "GEOB:Serato Overview" tag')
            return 1
        else:
            fp = io.BytesIO(tag.data)
    else:
        fp = open(args.file, mode='rb')

    with fp:
        data = parse(fp)
        img = draw_waveform(data)

    img.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())

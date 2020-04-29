#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import base64
import os.path
import mutagen


def get_serato_tagdata(tagfile, decode=False):
    if tagfile and tagfile.tags:
        if isinstance(tagfile, (mutagen.mp3.MP3, mutagen.aiff.AIFF)):
            for tagname, tagvalue in tagfile.tags.items():
                if tagname.startswith('GEOB:Serato '):
                    yield tagname[5:], tagvalue.data
        elif isinstance(tagfile, (mutagen.flac.FLAC, mutagen.mp4.MP4)):
            for tagname, tagvalue in tagfile.tags.items():
                if not tagname.startswith('serato_') and \
                        not tagname.startswith('----:com.serato.dj:'):
                    continue

                if isinstance(tagfile, mutagen.flac.FLAC):
                    encoded_data = tagvalue[0].encode('utf-8')
                else:
                    encoded_data = bytes(tagvalue[0])

                fixed_data = encoded_data

                length = len(fixed_data.splitlines()[-1])
                if length % 4 == 1:
                    fixed_data += b'A=='
                elif length % 4 == 2:
                    fixed_data += b'=='
                elif length % 4 == 3:
                    fixed_data += b'='
                data = base64.b64decode(fixed_data)

                if not data.startswith(b'application/octet-stream\0'):
                    print('Failed to parse tag: {}'.format(tagname))
                    continue
                fieldname_endpos = data.index(b'\0', 26)
                fieldname = data[26:fieldname_endpos].decode()
                fielddata = data[fieldname_endpos + 1:]
                yield fieldname, fielddata if decode else encoded_data
        elif isinstance(tagfile, mutagen.oggvorbis.OggVorbis):
            for tagname, tagvalue in tagfile.tags.items():
                if not tagname.startswith('serato_'):
                    continue
                yield tagname, tagvalue[0].encode('utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('output_dir')
    parser.add_argument('input_file')
    parser.add_argument('-d', '--decode', action='store_true')
    args = parser.parse_args(argv)

    tagfile = mutagen.File(args.input_file)
    for field, value in get_serato_tagdata(tagfile, decode=args.decode):
        filename = '{name}.octet-stream'.format(name=field)
        filepath = os.path.join(args.output_dir, filename)
        print('Writing {}field "{}" to file: {}'.format(
            'decoded ' if args.decode else '', field, filepath))
        with open(filepath, mode='wb') as fp:
            fp.write(value)


if __name__ == '__main__':
    main()

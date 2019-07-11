#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import base64
import collections
import io
import struct

UnknownEntry = collections.namedtuple('UnknownEntry', 'unknown_data')
BpmLockEntry = collections.namedtuple('BpmLockEntry', 'field1')
ColorEntry = collections.namedtuple('ColorEntry', 'field1 color')
CueEntry = collections.namedtuple(
    'CueEntry', 'field1 index field3 color field5')


def readbytes(fp):
    for x in iter(lambda: fp.read(1), b''):
        if x == b'\00':
            break
        yield x


def parse_tag(data):
    assert data[:2] == b'\x01\x01'
    b64len = data[2:].index(b'\x00')
    fp = io.BytesIO(base64.b64decode(data[2:2+b64len]))
    assert fp.read(2) == b'\x01\x01'
    while True:
        entry_type = b''.join(readbytes(fp))
        if entry_type == b'':
            break
        entry_len = struct.unpack('>I', fp.read(4))[0]
        assert entry_len > 0

        if entry_type == b'BPMLOCK':
            assert entry_len == 1
            yield BpmLockEntry(fp.read(entry_len))
        elif entry_type == b'COLOR':
            fmt = 'c3s'
            entry_data = struct.unpack(fmt, fp.read(entry_len))
            yield ColorEntry(*entry_data)
        elif entry_type == b'CUE':
            fmt = 'cB5s3s3s'
            assert struct.calcsize(fmt) == entry_len
            field1, index, field3, color, field5 = struct.unpack(
                fmt, fp.read(entry_len))
            yield CueEntry(
                field1, index, field3, struct.unpack('3B', color), field5)
        else:
            yield UnknownEntry(fp.read(entry_len))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'tag_file', metavar='TAG_FILE', type=argparse.FileType('rb'))
    args = parser.parse_args(argv)
    data = args.tag_file.read()
    for entry in parse_tag(data):
        print(repr(entry))


if __name__ == '__main__':
    main()


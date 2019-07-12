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
LoopEntry = collections.namedtuple('LoopEntry', 'field1 index startposition endposition field5 field6 locked name')
CueEntry = collections.namedtuple(
    'CueEntry', 'field1 index position field4 color field6 name')


def readbytes(fp):
    for x in iter(lambda: fp.read(1), b''):
        if x == b'\00':
            break
        yield x


def parse_tag(data):
    assert data[:2] == b'\x01\x01'
    b64len = data[2:].index(b'\x00')

    fp = io.BytesIO()
    for line in data[2:2+b64len].splitlines():
        if (len(line) % 4) == 1:
            line = line[:-1]
        else:
            line = line + b'='*(4 - (len(line) % 4))
        fp.write(base64.b64decode(line))
    fp.seek(0)

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
            fmt = '>cBIc3s2s'
            assert struct.calcsize(fmt) <= entry_len
            field1, index, position, field4, color, field6 = struct.unpack(
                fmt, fp.read(struct.calcsize(fmt)))
            name = b''.join(readbytes(fp)).decode('utf-8')
            yield CueEntry(
                field1, index, position, field4, struct.unpack('3B', color),
                field6, name)
        elif entry_type == b'LOOP':
            fmt = '>cBII8sB?'
            assert struct.calcsize(fmt) <= entry_len
            entry_data = struct.unpack(fmt, fp.read(struct.calcsize(fmt)))
            name = b''.join(readbytes(fp)).decode('utf-8')
            yield LoopEntry(*entry_data, name)
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


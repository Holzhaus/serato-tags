#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import base64
import io
import struct
import mutagen

FMT_VERSION = 'BB'


def readbytes(fp):
    for x in iter(lambda: fp.read(1), b''):
        if x == b'\00':
            break
        yield x


class Entry(object):
    def __init__(self, *args):
        assert len(args) == len(self.FIELDS)
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)

    def __repr__(self):
        return '{name}({data})'.format(
            name=self.__class__.__name__,
            data=', '.join('{}={!r}'.format(name, getattr(self, name))
                           for name in self.FIELDS))


class UnknownEntry(Entry):
    NAME = None
    FIELDS = ('data',)

    @classmethod
    def load(cls, data):
        return cls(data)

    def dump(self):
        return self.data


class BpmLockEntry(Entry):
    NAME = 'BPMLOCK'
    FIELDS = ('field1',)
    FMT = 'B'

    @classmethod
    def load(cls, data):
        return cls(*struct.unpack(cls.FMT, data))

    def dump(self):
        return struct.pack(self.FMT, self.field1)


class ColorEntry(Entry):
    NAME = 'COLOR'
    FMT = 'c3s'
    FIELDS = ('field1', 'color',)

    @classmethod
    def load(cls, data):
        return cls(*struct.unpack(cls.FMT, data))

    def dump(self):
        return struct.pack(self.FMT, self.field1, self.color)


class CueEntry(Entry):
    NAME = 'CUE'
    FMT = '>cBIc3s2s'
    FIELDS = ('field1', 'index', 'position', 'field4', 'color', 'field6',
              'name',)

    @classmethod
    def load(cls, data):
        info_size = struct.calcsize(cls.FMT)
        info = struct.unpack(cls.FMT, data[:info_size])
        name, nullbyte, other = data[info_size:].partition(b'\x00')
        assert nullbyte == b'\x00'
        assert other == b''
        return cls(*info, name.decode('utf-8'))

    def dump(self):
        return b''.join((
            struct.pack(self.FMT, self.field1, self.index, self.position,
                        self.field4, self.color, self.field6),
            self.name.encode('utf-8'),
            b'\x00',
        ))


class LoopEntry(Entry):
    NAME = 'LOOP'
    FMT = '>cBII8sB?'
    FIELDS = ('field1', 'index', 'startposition', 'endposition', 'field5',
              'field6', 'locked', 'name',)

    @classmethod
    def load(cls, data):
        info_size = struct.calcsize(cls.FMT)
        info = struct.unpack(cls.FMT, data[:info_size])
        name, nullbyte, other = data[info_size:].partition(b'\x00')
        assert nullbyte == b'\x00'
        assert other == b''
        return cls(*info, name.decode('utf-8'))

    def dump(self):
        return b''.join((
            struct.pack(self.FMT, self.field1, self.index, self.startposition,
                        self.endposition, self.field5, self.field6,
                        self.locked),
            self.name.encode('utf-8'),
            b'\x00',
        ))


def parse(data):
    versionlen = struct.calcsize(FMT_VERSION)
    version = struct.unpack(FMT_VERSION, data[:versionlen])
    assert version == (0x01, 0x01)

    b64data = data[versionlen:data.index(b'\x00', versionlen)].replace(b'\n', b'')
    padding = b'A==' if len(b64data) % 4 == 1 else (b'=' * (-len(b64data) % 4))
    payload = base64.b64decode(b64data + padding)
    fp = io.BytesIO(payload)
    assert struct.unpack(FMT_VERSION, fp.read(2)) == (0x01, 0x01)
    while True:
        entry_name = b''.join(readbytes(fp)).decode('utf-8')
        if not entry_name:
            break
        entry_len = struct.unpack('>I', fp.read(4))[0]
        assert entry_len > 0

        entry_type = UnknownEntry
        for entry_cls in (BpmLockEntry, ColorEntry, CueEntry, LoopEntry):
            if entry_cls.NAME == entry_name:
                entry_type = entry_cls

        yield entry_type.load(fp.read(entry_len))


def dump(entries):
    version = struct.pack(FMT_VERSION, 0x01, 0x01)

    contents = [version]
    for entry in entries:
        if entry.NAME is None:
            contents.append(entry.dump())
        else:
            data = entry.dump()
            contents.append(b''.join((
                entry.NAME.encode('utf-8'),
                b'\x00',
                struct.pack('>I', (len(data))),
                data,
            )))

    payload = b''.join(contents)
    payload_base64 = bytearray(base64.b64encode(payload).replace(b'=', b'A'))

    i = 72
    while i < len(payload_base64):
        payload_base64.insert(i, 0x0A)
        i += 73

    data = version
    data += payload_base64
    return data.ljust(470, b'\x00')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE')
    args = parser.parse_args(argv)

    tagfile = mutagen.File(args.file)
    if tagfile is not None:
        data = tagfile.tags['GEOB:Serato Markers2'].data
    else:
        with open(args.file, mode='rb') as fp:
            data = fp.read()

    for entry in parse(data):
        print(entry)


if __name__ == '__main__':
    main()


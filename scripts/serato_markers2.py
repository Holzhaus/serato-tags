#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import ast
import base64
import configparser
import io
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
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
    FIELDS = ('enabled',)
    FMT = '?'

    @classmethod
    def load(cls, data):
        return cls(*struct.unpack(cls.FMT, data))

    def dump(self):
        return struct.pack(self.FMT, *(getattr(self, f) for f in self.FIELDS))


class ColorEntry(Entry):
    NAME = 'COLOR'
    FMT = 'c3s'
    FIELDS = ('field1', 'color',)

    @classmethod
    def load(cls, data):
        return cls(*struct.unpack(cls.FMT, data))

    def dump(self):
        return struct.pack(self.FMT, *(getattr(self, f) for f in self.FIELDS))


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
        struct_fields = self.FIELDS[:-1]
        return b''.join((
            struct.pack(self.FMT, *(getattr(self, f) for f in struct_fields)),
            self.name.encode('utf-8'),
            b'\x00',
        ))


class LoopEntry(Entry):
    NAME = 'LOOP'
    FMT = '>cBII4s4sB?'
    FIELDS = ('field1', 'index', 'startposition', 'endposition', 'field5',
              'field6', 'color', 'locked', 'name',)

    @classmethod
    def load(cls, data):
        info_size = struct.calcsize(cls.FMT)
        info = struct.unpack(cls.FMT, data[:info_size])
        name, nullbyte, other = data[info_size:].partition(b'\x00')
        assert nullbyte == b'\x00'
        assert other == b''
        return cls(*info, name.decode('utf-8'))

    def dump(self):
        struct_fields = self.FIELDS[:-1]
        return b''.join((
            struct.pack(self.FMT, *(getattr(self, f) for f in struct_fields)),
            self.name.encode('utf-8'),
            b'\x00',
        ))


class FlipEntry(Entry):
    NAME = 'FLIP'
    FMT1 = 'cB?'
    FMT2 = '>BI'
    FMT3 = '>BI16s'
    FIELDS = ('field1', 'index', 'enabled', 'name', 'loop', 'num_actions',
              'actions')

    @classmethod
    def load(cls, data):
        info1_size = struct.calcsize(cls.FMT1)
        info1 = struct.unpack(cls.FMT1, data[:info1_size])
        name, nullbyte, other = data[info1_size:].partition(b'\x00')
        assert nullbyte == b'\x00'

        info2_size = struct.calcsize(cls.FMT2)
        loop, num_actions = struct.unpack(cls.FMT2, other[:info2_size])
        action_data = other[info2_size:]
        actions = []
        for i in range(num_actions):
            type_id, size = struct.unpack(cls.FMT2, action_data[:info2_size])
            action_data = action_data[info2_size:]
            if type_id == 0:
                payload = struct.unpack('>dd', action_data[:size])
                actions.append(("JUMP", *payload))
            elif type_id == 1:
                payload = struct.unpack('>ddd', action_data[:size])
                actions.append(("CENSOR", *payload))
            action_data = action_data[size:]
        assert action_data == b''

        return cls(*info1, name.decode('utf-8'), loop, num_actions, actions)

    def dump(self):
        raise NotImplementedError('FLIP entry dumps are not implemented!')


def get_entry_type(entry_name):
    entry_type = UnknownEntry
    for entry_cls in (BpmLockEntry, ColorEntry, CueEntry, LoopEntry, FlipEntry):
        if entry_cls.NAME == entry_name:
            entry_type = entry_cls
            break
    return entry_type


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

        entry_type = get_entry_type(entry_name)
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


def ui_ask(question, choices, default=None):
    text = '{question} [{choices}]? '.format(
        question=question,
        choices='/'.join(
            x.upper() if x == default else x
            for x in (*choices.keys(), '?')
        )
    )

    while True:
        answer = input(text).lower()
        if default and answer == '':
            answer = default

        if answer in choices.keys():
            return answer
        else:
            print('\n'.join(
                '{} - {}'.format(choice, desc)
                for choice, desc in (*choices.items(), ('?', 'print help'))
            ))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE')
    parser.add_argument('-e', '--edit', action='store_true')
    args = parser.parse_args(argv)

    if args.edit:
        text_editor = shutil.which(os.getenv('EDITOR', 'vi'))
        if not text_editor:
            print('No suitable $EDITOR found.', file=sys.stderr)
            return 1

        hex_editor = shutil.which(os.getenv('HEXEDITOR', 'bvi'))
        if not hex_editor:
            print('No suitable HEXEDITOR found.', file=sys.stderr)
            return 1

    tagfile = mutagen.File(args.file)
    if tagfile is not None:
        try:
            data = tagfile['GEOB:Serato Markers2'].data
        except KeyError:
            print('File is missing "GEOB:Serato Markers2" tag')
            return 1
    else:
        with open(args.file, mode='rb') as fp:
            data = fp.read()

    entries = list(parse(data))
    new_entries = []
    action = None

    width = math.floor(math.log10(len(entries)))+1
    for entry_index, entry in enumerate(entries):
        if args.edit:
            if action not in ('q', '_'):
                print('{:{}d}: {!r}'.format(entry_index, width, entry))
                action = ui_ask('Edit this entry', {
                    'y': 'edit this entry',
                    'n': 'do not edit this entry',
                    'q': ('quit; do not edit this entry or any of the '
                          'remaining ones'),
                    'a': 'edit this entry and all later entries in the file',
                    'b': 'edit raw bytes',
                    'r': 'remove this entry',
                }, default='n')

            if action in ('y', 'a', 'b'):
                while True:
                    with tempfile.NamedTemporaryFile() as f:
                        if action == 'b':
                            f.write(entry.dump())
                            editor = hex_editor
                        else:
                            if action == 'a':
                                entries_to_edit = ((
                                    '{:{}d}: {}'.format(i, width, e.NAME),
                                    e,
                                ) for i, e in enumerate(
                                    entries[entry_index:], start=entry_index))
                            else:
                                entries_to_edit = ((entry.NAME, entry),)

                            for section, e in entries_to_edit:
                                f.write('[{}]\n'.format(section).encode())
                                for field in e.FIELDS:
                                    f.write('{}: {!r}\n'.format(
                                        field, getattr(e, field),
                                    ).encode())
                                f.write(b'\n')
                            editor = text_editor
                        f.flush()
                        status = subprocess.call((editor, f.name))
                        f.seek(0)
                        output = f.read()

                    if status != 0:
                        if ui_ask('Command failed, retry', {
                            'y': 'edit again',
                            'n': 'leave unchanged',
                        }) == 'n':
                            break
                    else:
                        try:
                            if action != 'b':
                                cp = configparser.ConfigParser()
                                cp.read_string(output.decode())
                                sections = tuple(sorted(cp.sections()))
                                if action != 'a':
                                    assert len(sections) == 1

                                results = []
                                for section in sections:
                                    l, s, r = section.partition(': ')
                                    entry_type = get_entry_type(r if s else l)

                                    e = entry_type(*(
                                        ast.literal_eval(
                                            cp.get(section, field),
                                        ) for field in entry_type.FIELDS
                                    ))
                                    results.append(entry_type.load(e.dump()))
                            else:
                                results = [entry.load(output)]
                        except Exception as e:
                            print(str(e))
                            if ui_ask('Content seems to be invalid, retry', {
                                'y': 'edit again',
                                'n': 'leave unchanged',
                            }) == 'n':
                                break
                        else:
                            for i, e in enumerate(results, start=entry_index):
                                print('{:{}d}: {!r}'.format(i, width, e))
                            subaction = ui_ask(
                                'Above content is valid, save changes', {
                                    'y': 'save current changes',
                                    'n': 'discard changes',
                                    'e': 'edit again',
                                }, default='y')
                            if subaction == 'y':
                                new_entries.extend(results)
                                if action == 'a':
                                    action = '_'
                                break
                            elif subaction == 'n':
                                if action == 'a':
                                    action = 'q'
                                new_entries.append(entry)
                                break
            elif action in ('r', '_'):
                continue
            else:
                new_entries.append(entry)
        else:
            print('{:{}d}: {!r}'.format(entry_index, width, entry))

    if args.edit:
        if new_entries == entries:
            print('No changes made.')
        else:
            new_data = dump(new_entries)

            if tagfile is not None:
                tagfile['GEOB:Serato Markers2'] = mutagen.id3.GEOB(
                    encoding=0,
                    mime='application/octet-stream',
                    desc='Serato Markers2',
                    data=new_data,
                )
                tagfile.save()
            else:
                with open(args.file, mode='wb') as fp:
                    fp.write(new_data)

    return 0


if __name__ == '__main__':
    sys.exit(main())

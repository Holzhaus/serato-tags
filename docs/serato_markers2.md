# Serato Markers2

This tag stores various kinds of track "markers" like Cue Points, Saved Loops, Flips.
It also stores information about the tracks' color in the tracklist and if the track's beatgrid is locked.

The tag contains a two-byte tag header, followed by base64-encoded binary data.
If the content is very long, a linefeed character (`0a`) is inserted into the base64 string every 72 bytes.
For some unknown reason, Serato may produce a base64 string that is 1 byte longer than a multiple of 4 (i.e. an invalid base64 string).
In that case, you can just append an `A` (of `A==` if you use padding) before decoding it.

The minimum length of this tag seems to be 470 bytes, and shorter contents are padded with null bytes.

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `02` | `01 01`                   |               | *?* (2 bytes)           | Tag Header
|   `02` |   `28` | `41 51` ... `41 41`       | *see below*   | base64-encoded data     | Data
|   `2a` |  `1ac` | `00`                      |               |                         | Padding

The base64-encoded content starts with `01 01`, followed by multiple marker entries.

    $ grep -Poaz '[\w/]*' Serato\ Markers2.octet-stream | tr -d '\0' | base64 -d | hexdump -C
    00000000  01 01 43 4f 4c 4f 52 00  00 00 00 04 00 ff ff ff  |..COLOR.........|
    00000010  42 50 4d 4c 4f 43 4b 00  00 00 00 01 00 00        |BPMLOCK.......|
    0000001e

The base64-encoded content ends with a single null byte (`00`).

## Marker Entries

Each entry is described by a header that contains type and length.
The type is a null-terminated ASCII string.

The length of the entry's data depends heavily on the entry type.
`BPMLOCK` entries contain only a single byte of data, while `FLIP` might become quite large.
By storing the length explicitly instead of deriving it from the type, a parser could ignore unknown entry types and still be able to parse known ones.

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `08` | `42 50 4d 4c 4f 43 4b 00` | `BPMLOCK`     | ASCII (null-terminated) | Type
|   `08` |   `04` | `00 00 00 01`             | 1             | `uint32_t`              | Length in bytes
|   `0c` |   `01` | `01`                      |               | See below               | Data


### `BPMLOCK` entries

`BPMLOCK` entries contain a single boolean value that determines if [Beatgrid is locked](https://support.serato.com/hc/en-us/articles/235214887-Lock-Beatgrids).

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `01` | `00`                      | False         | `uint8_t` (boolean)     | Beatgrid locked


### `COLOR` entries

`COLOR` entries describe a track's color inside the tracklist.

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `01` | `00`                      |               |                         |
|   `01` |   `03` | `99 ff 99`                | `#99FF99`     | 3-byte RGB value        | Tracklist color


### `CUE` entries

Each `CUE` entry contains information about a [cue point](https://support.serato.com/hc/en-us/articles/360000067696-Cue-Points).

| Offset | Length | Raw Value                 | Decoded Value | Type                                | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------------------- | -----------
|   `00` |   `01` | `00`                      |               |                                     |
|   `01` |   `01` | `00`                      | 0             | `uint8_t`                           | Index
|   `02` |   `04` | `00 00 00 00`             | 0             | `uint32_t`                          | Position in milliseconds
|   `06` |   `01` | `00`                      |               |                                     |
|   `07` |   `03` | `cc 00 00`                | `#CC0000`     | 3-byte RGB value                    | Color
|   `0a` |   `02` | `00 00`                   |               |                                     |
|   `0c` |   `01` | `00`                      | ``            | UTF-8 (max. 50 bytes + null byte)   | Name


### `LOOP` entries

`LOOP` entries are used to store [saved loops](https://serato.com/latest/blog/17885/pro-tip-trigger-saved-loops).

| Offset | Length | Raw Value                 | Decoded Value | Type                                | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------------------- | -----------
|   `00` |   `01` | `00`                      |               |                                     |
|   `01` |   `01` | `00`                      | 0             | `uint8_t`                           | Index
|   `02` |   `04` | `00 00 00 00`             | 0             | `uint32_t`                          | Start Position in milliseconds
|   `06` |   `04` | `00 00 08 26`             | 2086          | `uint32_t`                          | End Position in milliseconds
|   `0a` |   `01` | `00`                      |               |                                     |
|   `0b` |   `01` | `00`                      | False         | `uint8_t` (boolean)                 | Locked
|   `0c` |   `01` | `00`                      | ``            | UTF-8 (max. 32747 bytes + nullbyte) | Name


### `FLIP` entries

`FLIP` entries are used for storing [Serato Flip](https://serato.com/dj/pro/expansions/flip) performances.

| Offset | Length | Raw Value                 | Decoded Value | Type                                | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------------------- | -----------
|   `00` |   `01` | `00`                      |               |                                     |
|   `01` |   `01` | `00`                      | 0             | `uint8_t`                           | Index
|   `02` |   `01` | `00`                      | False         | `uint8_t` (boolean)                 | Enabled
|   `03` |   `0b` | `41 41`... `41 41 00`     | `AA` .. `AA`  | UTF-8 (max. 10 bytes + null byte)   | Name
|   `0e` |   `01` | `00`                      | False         | `uint8_t` (boolean)                 | Loop
|   `0f` |   `04` | `00 00 00 08`             |               | `uint32_t`                          | Number of subentries
|   `13` |   `a8` | `00 00` .. `04 7c`        |               | See below                           | Subentries


#### Subentries of `FLIP entries`

Each subentry starts with a header that contains its type and length.
It's unknown if type `0x00` is an actual single-byte value or if it's an empty, null-terminated string.

| Offset | Length | Raw Value                 | Decoded Value | Type                                | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------------------- | -----------
|   `00` |   `01` | `00`                      | 0             | `uint8_t` (?)                       | Type (?)
|   `01` |   `04` | `00 00 00 10`             | 16            | `uint32_t`                          | Length
|   `05` |   `10` | `40 35` .. `7a e1`        |            .  | See below                           | Data


##### Subentries of type `0`

Subentries of type `0` are 16 bytes long and consist of two `double` precision floating point values.
The first values denotes the absolute position in the track where a jump occurs, the second value is the jump target.

| Offset | Length | Raw Value                 | Decoded Value | Type                                | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------------------- | -----------
|   `00` |   `08` | `40 35 30 04 85 6e 43 e2` | 21.187568...  | `double` (binary64)                 | Source position in seconds
|   `08` |   `08` | `40 4b 51 47 ae 14 7a e1` | 54.635        | `double` (binary64)                 | Target position in seconds

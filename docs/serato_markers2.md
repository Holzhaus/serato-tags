# Serato Markers2

This tag stores various kinds of track "markers" like Cue Points, Saved Loops, Flips.
It also stores information about the tracks' color in the tracklist and if the track's beatgrid is locked.

Note that some of this information is also stored in [`Serato Markers_`](serato_markers_.md), and Serato
will prefer that data over the information stored in `Serato Markers2` if it is present.

The tag contains a two-byte tag header, followed by base64-encoded binary data.
If the content is very long, a linefeed character (`0a`) is inserted into the base64 string every 72 bytes.
For some unknown reason, Serato may produce a base64 string that is 1 byte longer than a multiple of 4 (i.e. an invalid base64 string).
In that case, you can just append an `A` (of `A==` if you use padding) before decoding it.

The minimum length of this tag seems to be 470 bytes, and shorter contents are padded with null bytes.

| Offset   |            Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ----------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |              `02` | `01 01`                   |               | *?* (2 bytes)           | Tag Header
| `02`     |                 X | `41 51` ... `41 41`       | *see below*   | base64-encoded data     | Data
| `02` + X |                 Y | `00`                      |               | Null bytes              | Padding

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

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |           `01` <= X | `42 50 4d 4c 4f 43 4b 00` | `BPMLOCK`     | ASCII (null-terminated) | Type
| X        |                `04` | `00 00 00 01`             | 1             | `uint32_t`              | Length in bytes
| `04` + X |                   Y | `01`                      |               | See below               | Data


### `BPMLOCK` entries

`BPMLOCK` entries contain a single boolean value that determines if [Beatgrid is locked](https://support.serato.com/hc/en-us/articles/235214887-Lock-Beatgrids).

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `01` | `00`                      | False         | `uint8_t` (boolean)     | Beatgrid locked

###   `COLOR` entries

`COLOR` entries describe a track's color.

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `01` | `00`                      |               |                         |
| `01`     |                `03` | `99 ff 99`                | `#99FF99`     | 3-byte RGB value        | Track Color

### `CUE` entries

Each `CUE` entry contains information about a [cue point](https://support.serato.com/hc/en-us/articles/360000067696-Cue-Points).

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `01` | `00`                      |               |                         |
| `01`     |                `01` | `00`                      | 0             | `uint8_t`               | Index
| `02`     |                `04` | `00 00 00 00`             | 0             | `uint32_t`              | Position in milliseconds
| `06`     |                `01` | `00`                      |               |                         |
| `07`     |                `03` | `cc 00 00`                | `#CC0000`     | 3-byte RGB value        | Color
| `0a`     |                `02` | `00 00`                   |               |                         |
| `0c`     |   `01` <= X <= `33` | `00`                      | ``            | UTF-8 (null-terminated) | Name


### `LOOP` entries

`LOOP` entries are used to store [saved loops](https://serato.com/latest/blog/17885/pro-tip-trigger-saved-loops).

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `01` | `00`                      |               |                         |
| `01`     |                `01` | `00`                      | 0             | `uint8_t`               | Index
| `02`     |                `04` | `00 00 00 00`             | 0             | `uint32_t`              | Start Position in milliseconds
| `06`     |                `04` | `00 00 08 26`             | 2086          | `uint32_t`              | End Position in milliseconds
| `0a`     |                `04` | `ff ff ff ff`             |               |                         |
| `0e`     |                `04` | `00 27 aa e1`             | `#27aae1`     | 4-byte ARGB value       | Color
| `12`     |                `03` | `00`                      |               |                         |
| `13`     |                `01` | `00`                      | False         | `uint8_t` (boolean)     | Locked
| `14`     | `01` <= X <= `7fec` | `00`                      | ``            | UTF-8 (null-terminated) | Name


### `FLIP` entries

`FLIP` entries are used for storing [Serato Flip](https://serato.com/dj/pro/expansions/flip) performances.

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `01` | `00`                      |               |                         |
| `01`     |                `01` | `00`                      | 0             | `uint8_t`               | Index
| `02`     |                `01` | `00`                      | False         | `uint8_t` (boolean)     | Enabled
| `03`     |   `01` <= X <= `0b` | `41 41`... `41 41 00`     | `AA` .. `AA`  | UTF-8 (null-terminated) | Name
| `03` + X |                `01` | `00`                      | False         | `uint8_t` (boolean)     | Loop
| `04` + X |                `04` | `00 00 00 08`             |               | `uint32_t`              | Number of subentries
| `08` + X |                   Y | `00 00` .. `04 7c`        |               | See below               | Subentries


#### Subentries of `FLIP` entries

Each subentry starts with a header that contains its type and length.

The last entry is always a jump entry where the source position is the time when the Flip recording was stopped.
If looping is enabled, it's target position is the source position of the first entry.
If not, the target position of that last entry is the same as its source position.


| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `01` | `00`                      | 0             | `uint8_t`               | Type
| `01`     |                `04` | `00 00 00 10`             | 16            | `uint32_t`              | Length
| `05`     |                `10` | `40 35` .. `7a e1`        |            .  | See below               | Data


##### Subentries of type `0` (Jumps)

Subentries of type `0` are 16 bytes long and consist of two `double` precision floating point values.
The first value denotes the absolute position in the track where a jump occurs, the second value is the jump target.

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `08` | `40 35 30 04 85 6e 43 e2` | 21.187568...  | `double` (binary64)     | Source position in seconds
| `08`     |                `08` | `40 4b 51 47 ae 14 7a e1` | 54.635        | `double` (binary64)     | Target position in seconds

##### Subentries of type `1` (Playback/Censor)

Subentries of type `1` are 24 bytes long and consist of three `double` precision floating point values.
The first value denotes the absolute position in the track where playback starts, the second value is the playback ends.
The third value is the playback speed factor.
Subentries of this type are used for censoring (playback speed factor is -1.0) and are followed with a jump subentry from the censoring entry's end position to the play position that the track would be at without the reverse playback.

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `08` | `40 12 18 1b ad d5 28 b0` | 4.44800000... | `double` (binary64)     | Source position in seconds
| `08`     |                `08` | `40 07 fc 55 65 38 56 3d` | 3.09333333... | `double` (binary64)     | Target position in seconds
| `10`     |                `08` | `bf f0 00 00 00 00 00 00` | -1.0          | `double` (binary64)     | Playback speed factor

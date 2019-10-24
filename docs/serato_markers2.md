# Serato Markers2

This tag stores various kinds of track "markers" like Cue Points, Saved Loops, Flips.
It also stores information about the tracks' color in the tracklist and if the track's beatgrid is locked.

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

`COLOR` entries describe a track's color inside the tracklist.

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `01` | `00`                      |               |                         |
| `01`     |                `03` | `99 ff 99`                | `#99FF99`     | 3-byte RGB value        | Tracklist color

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
| `0a`     |                `08` | `ff ff ff ff 00 27 aa e1` |               |                         |
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
It's unknown if type `0x00` is an actual single-byte value or if it's an empty, null-terminated string.

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `01` | `00`                      | 0             | `uint8_t` (?)           | Type (?)
| `01`     |                `04` | `00 00 00 10`             | 16            | `uint32_t`              | Length
| `05`     |                `10` | `40 35` .. `7a e1`        |            .  | See below               | Data


##### Subentries of type `0`

Subentries of type `0` are 16 bytes long and consist of two `double` precision floating point values.
The first values denotes the absolute position in the track where a jump occurs, the second value is the jump target.

| Offset   |              Length | Raw Value                 | Decoded Value | Type                    | Description
| -------- | ------------------- | ------------------------- | ------------- | ----------------------- | -----------
| `00`     |                `08` | `40 35 30 04 85 6e 43 e2` | 21.187568...  | `double` (binary64)     | Source position in seconds
| `08`     |                `08` | `40 4b 51 47 ae 14 7a e1` | 54.635        | `double` (binary64)     | Target position in seconds


## Colors

The on-screen representation of hotcue colors present in the the `Serato Markers2` can differ slightly depending on wether Serato DJ Pro, Serato DJ Lite or Serato DJ Intro is used.
In contrast to Serato DJ Intro which just displays the colors unchanged, both Serato DJ Lite and Serato DJ Pro apply some kind of transformation or colorscheme, so that the actual color of the hotcue and the color show in the GUI are not the same.


### Serato DJ Intro

|  # | Hot Cue | Saved                                                              | Displayed                                                          |
| -- | ------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
|  1 |       1 | ![CC0000](http://dummyimage.com/20x20/CC0000/CC0000.gif) `#CC0000` | ![CC0000](http://dummyimage.com/20x20/CC0000/CC0000.gif) `#CC0000` |
|  2 |         | ![CC4400](http://dummyimage.com/20x20/CC4400/CC4400.gif) `#CC4400` | ![CC4400](http://dummyimage.com/20x20/CC4400/CC4400.gif) `#CC4400` |
|  3 |       2 | ![CC8800](http://dummyimage.com/20x20/CC8800/CC8800.gif) `#CC8800` | ![CC8800](http://dummyimage.com/20x20/CC8800/CC8800.gif) `#CC8800` |
|  4 |       4 | ![CCCC00](http://dummyimage.com/20x20/CCCC00/CCCC00.gif) `#CCCC00` | ![CCCC00](http://dummyimage.com/20x20/CCCC00/CCCC00.gif) `#CCCC00` |
|  5 |         | ![88CC00](http://dummyimage.com/20x20/88CC00/88CC00.gif) `#88CC00` | ![88CC00](http://dummyimage.com/20x20/88CC00/88CC00.gif) `#88CC00` |
|  6 |         | ![44CC00](http://dummyimage.com/20x20/44CC00/44CC00.gif) `#44CC00` | ![44CC00](http://dummyimage.com/20x20/44CC00/44CC00.gif) `#44CC00` |
|  7 |       5 | ![00CC00](http://dummyimage.com/20x20/00CC00/00CC00.gif) `#00CC00` | ![00CC00](http://dummyimage.com/20x20/00CC00/00CC00.gif) `#00CC00` |
|  8 |         | ![00CC44](http://dummyimage.com/20x20/00CC44/00CC44.gif) `#00CC44` | ![00CC44](http://dummyimage.com/20x20/00CC44/00CC44.gif) `#00CC44` |
|  9 |         | ![00CC88](http://dummyimage.com/20x20/00CC88/00CC88.gif) `#00CC88` | ![00CC88](http://dummyimage.com/20x20/00CC88/00CC88.gif) `#00CC88` |
| 10 |         | ![00CCCC](http://dummyimage.com/20x20/00CCCC/00CCCC.gif) `#00CCCC` | ![00CCCC](http://dummyimage.com/20x20/00CCCC/00CCCC.gif) `#00CCCC` |
| 11 |         | ![0088CC](http://dummyimage.com/20x20/0088CC/0088CC.gif) `#0088CC` | ![0088CC](http://dummyimage.com/20x20/0088CC/0088CC.gif) `#0088CC` |
| 12 |         | ![0044CC](http://dummyimage.com/20x20/0044CC/0044CC.gif) `#0044CC` | ![0044CC](http://dummyimage.com/20x20/0044CC/0044CC.gif) `#0044CC` |
| 13 |       3 | ![0000CC](http://dummyimage.com/20x20/0000CC/0000CC.gif) `#0000CC` | ![0000CC](http://dummyimage.com/20x20/0000CC/0000CC.gif) `#0000CC` |
| 14 |         | ![4400CC](http://dummyimage.com/20x20/4400CC/4400CC.gif) `#4400CC` | ![4400CC](http://dummyimage.com/20x20/4400CC/4400CC.gif) `#4400CC` |
| 15 |         | ![8800CC](http://dummyimage.com/20x20/8800CC/8800CC.gif) `#8800CC` | ![8800CC](http://dummyimage.com/20x20/8800CC/8800CC.gif) `#8800CC` |
| 16 |         | ![CC00CC](http://dummyimage.com/20x20/CC00CC/CC00CC.gif) `#CC00CC` | ![CC00CC](http://dummyimage.com/20x20/CC00CC/CC00CC.gif) `#CC00CC` |
| 17 |         | ![CC0088](http://dummyimage.com/20x20/CC0088/CC0088.gif) `#CC0088` | ![CC0088](http://dummyimage.com/20x20/CC0088/CC0088.gif) `#CC0088` |
| 18 |         | ![CC0044](http://dummyimage.com/20x20/CC0044/CC0044.gif) `#CC0044` | ![CC0044](http://dummyimage.com/20x20/CC0044/CC0044.gif) `#CC0044` |


### Serato DJ Lite

|  # | Hot Cue | Saved                                                              | Displayed                                                          |
| -- | ------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
|  1 |       1 | ![CC0000](http://dummyimage.com/20x20/CC0000/CC0000.gif) `#CC0000` | ![C02626](http://dummyimage.com/20x20/C02626/C02626.gif) `#C02626` |
|  2 |       2 | ![CC8800](http://dummyimage.com/20x20/CC8800/CC8800.gif) `#CC8800` | ![F8821A](http://dummyimage.com/20x20/F8821A/F8821A.gif) `#F8821A` |
|  3 |       3 | ![0000CC](http://dummyimage.com/20x20/0000CC/0000CC.gif) `#0000CC` | ![173BA2](http://dummyimage.com/20x20/173BA2/173BA2.gif) `#173BA2` |
|  4 |       4 | ![CCCC00](http://dummyimage.com/20x20/CCCC00/CCCC00.gif) `#CCCC00` | ![FAC313](http://dummyimage.com/20x20/FAC313/FAC313.gif) `#FAC313` |


### Serato DJ Pro

|  # | Hot Cue | Saved                                                              | Displayed                                                          |
| -- | ------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
|  1 |       1 | ![CC0000](http://dummyimage.com/20x20/CC0000/CC0000.gif) `#CC0000` | ![C02626](http://dummyimage.com/20x20/C02626/C02626.gif) `#C02626` |
|  2 |         | ![CC4400](http://dummyimage.com/20x20/CC4400/CC4400.gif) `#CC4400` | ![DB4E27](http://dummyimage.com/20x20/DB4E27/DB4E27.gif) `#DB4E27` |
|  3 |       2 | ![CC8800](http://dummyimage.com/20x20/CC8800/CC8800.gif) `#CC8800` | ![F8821A](http://dummyimage.com/20x20/F8821A/F8821A.gif) `#F8821A` |
|  4 |       4 | ![CCCC00](http://dummyimage.com/20x20/CCCC00/CCCC00.gif) `#CCCC00` | ![FAC313](http://dummyimage.com/20x20/FAC313/FAC313.gif) `#FAC313` |
|  5 |         | ![88CC00](http://dummyimage.com/20x20/88CC00/88CC00.gif) `#88CC00` | ![4EB648](http://dummyimage.com/20x20/4EB648/4EB648.gif) `#4EB648` |
|  6 |         | ![44CC00](http://dummyimage.com/20x20/44CC00/44CC00.gif) `#44CC00` | ![006838](http://dummyimage.com/20x20/006838/006838.gif) `#006838` |
|  7 |       5 | ![00CC00](http://dummyimage.com/20x20/00CC00/00CC00.gif) `#00CC00` | ![1FAD26](http://dummyimage.com/20x20/1FAD26/1FAD26.gif) `#1FAD26` |
|  8 |         | ![00CC44](http://dummyimage.com/20x20/00CC44/00CC44.gif) `#00CC44` | ![8DC63F](http://dummyimage.com/20x20/8DC63F/8DC63F.gif) `#8DC63F` |
|  9 |         | ![00CC88](http://dummyimage.com/20x20/00CC88/00CC88.gif) `#00CC88` | ![2B3673](http://dummyimage.com/20x20/2B3673/2B3673.gif) `#2B3673` |
| 10 |       7 | ![00CCCC](http://dummyimage.com/20x20/00CCCC/00CCCC.gif) `#00CCCC` | ![1DBEBD](http://dummyimage.com/20x20/1DBEBD/1DBEBD.gif) `#1DBEBD` |
| 11 |         | ![0088CC](http://dummyimage.com/20x20/0088CC/0088CC.gif) `#0088CC` | ![0F88CA](http://dummyimage.com/20x20/0F88CA/0F88CA.gif) `#0F88CA` |
| 12 |         | ![0044CC](http://dummyimage.com/20x20/0044CC/0044CC.gif) `#0044CC` | ![16308B](http://dummyimage.com/20x20/16308B/16308B.gif) `#16308B` |
| 13 |       3 | ![0000CC](http://dummyimage.com/20x20/0000CC/0000CC.gif) `#0000CC` | ![173BA2](http://dummyimage.com/20x20/173BA2/173BA2.gif) `#173BA2` |
| 14 |         | ![4400CC](http://dummyimage.com/20x20/4400CC/4400CC.gif) `#4400CC` | ![5C3F97](http://dummyimage.com/20x20/5C3F97/5C3F97.gif) `#5C3F97` |
| 15 |       8 | ![8800CC](http://dummyimage.com/20x20/8800CC/8800CC.gif) `#8800CC` | ![6823B6](http://dummyimage.com/20x20/6823B6/6823B6.gif) `#6823B6` |
| 16 |       6 | ![CC00CC](http://dummyimage.com/20x20/CC00CC/CC00CC.gif) `#CC00CC` | ![CE359E](http://dummyimage.com/20x20/CE359E/CE359E.gif) `#CE359E` |
| 17 |         | ![CC0088](http://dummyimage.com/20x20/CC0088/CC0088.gif) `#CC0088` | ![DC1D49](http://dummyimage.com/20x20/DC1D49/DC1D49.gif) `#DC1D49` |
| 18 |         | ![CC0044](http://dummyimage.com/20x20/CC0044/CC0044.gif) `#CC0044` | ![C71136](http://dummyimage.com/20x20/C71136/C71136.gif) `#C71136` |

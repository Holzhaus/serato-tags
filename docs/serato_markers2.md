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



### `BPMLOCK` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `08` | `42 50 4d 4c 4f 43 4b 00` | `BPMLOCK`     | ASCII (null-terminated) | Entry type
|   `08` |   `04` | `00 00 00 01`             | 1             | `uint32_t`              | Entry length
|   `0c` |   `01` | `00`                      | False         | `uint8_t` (boolean)     | [Beatgrid locked](https://support.serato.com/hc/en-us/articles/235214887-Lock-Beatgrids)

### `COLOR` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `06` | `43 4f 4c 4f 52 00`       | `COLOR`       | ASCII (null-terminated) | Entry type
|   `06` |   `04` | `00 00 00 04`             | 4             | `uint32_t`              | Entry length
|   `0a` |   `01` | `00`                      |               |                         |
|   `0c` |   `03` | `99 ff 99`                | `#99FF99`     | 3-byte RGB value        | Tracklist color


### `CUE` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                                | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------------------- | -----------
|   `00` |   `04` | `43 55 45 00`             | `CUE`         | ASCII (null-terminated)             | Entry type
|   `04` |   `04` | `00 00 00 0d`             | 13            | `uint32_t`                          | Entry length
|   `08` |   `01` | `00`                      |               |                                     |
|   `09` |   `01` | `00`                      | 0             | `uint8_t`                           | Hotcue index
|   `0a` |   `04` | `00 00 00 00`             | 0             | `uint32_t`                          | Position in milliseconds
|   `0e` |   `01` | `00`                      |               |                                     |
|   `0f` |   `03` | `cc 00 00`                | `#CC0000`     | 3-byte RGB value                    | Hotcue color
|   `12` |   `03` | `00 00`                   |               |                                     |
|   `14` |   `01` | `00`                      | ``            | UTF-8 (max. 50 bytes + nullbyte)    | Hotcue name

### `LOOP` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                                | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------------------- | -----------
|   `00` |   `05` | `4c 4f 4f 50 00`          | `LOOP`        | ASCII (null-terminated)             | Entry type
|   `05` |   `04` | `00 00 00 15`             | 21            | `uint32_t`                          | Entry length
|   `09` |   `01` | `00`                      |               |                                     |
|   `0a` |   `01` | `00`                      | 0             | `uint8_t`                           | Loop index
|   `0b` |   `04` | `00 00 00 00`             | 0             | `uint32_t`                          | Start Position in milliseconds
|   `0f` |   `04` | `00 00 08 26`             | 2086          | `uint32_t`                          | End Position in milliseconds
|   `13` |   `01` | `00`                      |               |                                     |
|   `14` |   `01` | `00`                      | False         | `uint8_t` (boolean)                 | Loop locked
|   `15` |   `01` | `00`                      | ``            | UTF-8 (max. 32747 bytes + nullbyte) | Loop name

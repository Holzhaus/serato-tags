# Serato Markers2

    $ hexdump -C Serato\ Markers2.octet-stream
    00000000  01 01 41 51 46 44 54 30  78 50 55 67 41 41 41 41  |..AQFDT0xPUgAAAA|
    00000010  41 45 41 50 2f 2f 2f 30  4a 51 54 55 78 50 51 30  |AEAP///0JQTUxPQ0|
    00000020  73 41 41 41 41 41 41 51  41 41 00 00 00 00 00 00  |sAAAAAAQAA......|
    00000030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    *
    000001d0  00 00 00 00 00 00                                 |......|
    000001d6

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `02` | `01 01`                   |               | *?* (2 bytes)           |
|   `02` |   `28` | `41 51` ... `41 41`       | *see below*   | base64-encoded data     | 
|   `2a` |  `1ac` | `00`                      |               | ASCII (null-terminated) |

## Base64-encoded Part

The base64-encoded content starts with `01 01`, followed by multiple data entries.

    $ grep -Poaz '[\w/]*' Serato\ Markers2.octet-stream | tr -d '\0' | base64 -d | hexdump -C
    00000000  01 01 43 4f 4c 4f 52 00  00 00 00 04 00 ff ff ff  |..COLOR.........|
    00000010  42 50 4d 4c 4f 43 4b 00  00 00 00 01 00 00        |BPMLOCK.......|
    0000001e

The content ends with a single null byte (`00`).

If the content is very long, a linefeed character (`0a`) is inserted into the base64 string every 76 bytes.
For some unknown reason, Serato may produce a base64 string that is 1 byte longer than a multiple of 4 (i.e. an invalid base64 string).
In that case, the last byte can be ignored, but the trailing null byte may be missing in the decoded data.

### `BPMLOCK` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `08` | `42 50 4d 4c 4f 43 4b 00` | `BPMLOCK`     | ASCII (null-terminated) | Entry type
|   `08` |   `04` | `00 00 00 01`             | 1             | `uint32_t`              | Entry length
|   `0C` |   `01` | `00`                      |               |                         |

### `COLOR` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `06` | `43 4f 4c 4f 52 00`       | `COLOR`       | ASCII (null-terminated) | Entry type
|   `06` |   `04` | `00 00 00 04`             | 4             | `uint32_t`              | Entry length
|   `0A` |   `01` | `00`                      |               |                         |
|   `0C` |   `03` | `99 ff 99`                | `#99FF99`     | 3-byte RGB value        | Tracklist color


### `CUE` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `04` | `43 55 45 00`             | `CUE`         | ASCII (null-terminated) | Entry type
|   `04` |   `04` | `00 00 00 0d`             | 13            | `uint32_t`              | Entry length
|   `08` |   `01` | `00`                      |               |                         |
|   `09` |   `01` | `00`                      | 0             | `uint8_t`               | Hotcue index
|   `0A` |   `04` | `00 00 00 00`             | 0             | `uint32_t`              | Position in milliseconds
|   `0E` |   `01` | `00`                      |               |                         |
|   `0F` |   `03` | `cc 00 00`                | `#CC0000`     | 3-byte RGB value        | Hotcue color
|   `12` |   `03` | `00 00`                   |               |                         |
|   `14` |   `01` | `00`                      | ``            | UTF-8 (null-terminated) | Hotcue name

### `LOOP` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `05` | `4c 4f 4f 50 00`          | `LOOP`        | ASCII (null-terminated) | Entry type
|   `05` |   `04` | `00 00 00 15`             | 21            | `uint32_t`              | Entry length
|   `09` |   `01` | `00`                      |               |                         |
|   `0A` |   `01` | `00`                      | 0             | `uint8_t`               | Loop index
|   `0B` |   `04` | `00 00 00 00`             | 0             | `uint32_t`              | Start Position in milliseconds
|   `0F` |   `04` | `00 00 08 26`             | 2086          | `uint32_t`              | End Position in milliseconds
|   `13` |   `01` | `00`                      |               |                         |
|   `14` |   `01` | `00`                      | False         | `uint8_t` (boolean)     | Loop Locked
|   `15` |   `01` | `00`                      | ``            | UTF-8 (null-terminated) | Loop name

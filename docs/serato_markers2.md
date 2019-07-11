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
|   `2a` |  `1ac` | `00`                      |               | ASCII (zero-terminated) |

## Base64-encoded Part

The base64-encoded content starts with `01 01`, followed by multiple data entries.

    $ grep -Poaz '[\w/]*' Serato\ Markers2.octet-stream | tr -d '\0' | base64 -d | hexdump -C
    00000000  01 01 43 4f 4c 4f 52 00  00 00 00 04 00 ff ff ff  |..COLOR.........|
    00000010  42 50 4d 4c 4f 43 4b 00  00 00 00 01 00 00        |BPMLOCK.......|
    0000001e

### `BPMLOCK` entries

|   `00` |   `08` | `42 50 4d 4c 4f 43 4b 00` | `BPMLOCK`     | ASCII (zero-terminated) |
|   `08` |   `06` | `00 00 00 01 00 00`       |               |                         |

### `COLOR` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `06` | `43 4f 4c 4f 52 00`       | `COLOR`       | ASCII (zero-terminated) |
|   `06` |   `08` | `00 00 00 04 00 ff ff ff` |               |                         |

#### `CUE` entries

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `04` | `43 55 45 00`             | `CUE`         | ASCII (zero-terminated) | Type name
|   `04` |   `05` | `00 00 00 0d 00`          |               |                         |
|   `09` |   `01` | `00`                      | 0             | `unsigned char`         | Hotcue index
|   `0A` |   `05` | `00 00 00 00 00`          |               |                         |
|   `0F` |   `03` | `cc 00 00`                | `#CC0000`     | 3-byte RGB value        | Hotcue color
|   `12` |   `03` | `00 00 00`                |               |                         |

# Serato Markers_

The `Serato Markers_` tag stores information about Cues and Loops.

The tag data consists of a header followed by 0 or more entries and a single footer byte.

Every entry is apparently 22 (= 0x16) bytes long.

    $ tail -c +7 data/hotcue-positions-00m00s0-03m38s4-01m00s0-00m00s1-00m01s0/Serato\ Markers_.octet-stream | hexdump -v -e '"%08.8_ax " 22/1 "%02x " "\n"'
    00000000 00 00 00 00 00 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 06 30 00 00 01 00
    00000016 00 00 0d 2a 58 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 06 32 10 00 01 00
    0000002c 00 00 03 54 64 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 01 4c 01 00
    00000042 00 00 00 00 6c 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 06 33 18 00 01 00
    00000058 00 00 00 07 77 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 03 18 00 01 00
    0000006e 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 00 00 03 00
    00000084 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 00 00 03 00
    0000009a 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 00 00 03 00
    000000b0 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 00 00 03 00
    000000c6 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 00 00 03 00
    000000dc 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 00 00 03 00
    000000f2 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 00 00 03 00
    00000108 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 00 00 03 00
    0000011e 7f 7f 7f 7f 7f 7f 7f 7f 7f 7f 00 7f 7f 7f 7f 7f 00 00 00 00 03 00
    00000134 07 7f 7f 7f

## Header

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `02` | `02 05`                   |               | *?* (2 bytes)           |
|   `02` |   `04` | `00 00 00 0e`             | 14            | `uint32_t`              | Number of Markers

## Marker Entries

Each entry has the same format. Labels for Cues and Loops are not supported and are loaded from [`Serato Markers2`](serato_markers2.md) instead.

| Offset   | Length | Raw Value                 | Decoded Value | Type                                      | Description
| -------- | ------ | ------------------------- | ------------- | ----------------------------------------- | -----------
| `00`     |   `01` | `00`                      | True          | `uint8_t` (`00` is True, `7f` is False`)  | Is Set
| `01`     |   `04` | `00 00 00 00`             | 0             | `uint32_t` (`7f 7f 7f 7f` if not set)     | Start Position in milliseconds
| `02`     |   `01` | `7f`                      |               |                                           |
| `06`     |   `04` | `7f 7f 7f 7f`             | None          | `uint32_t` (`7f 7f 7f 7f` if not set)     | End Position in milliseconds
| `0a`     |   `06` | `00 7f 7f 7f 7f 7f`       |               |                                           |
| `0e`     |   `04` | `06 30 00 00`             | `#cc0000`     | 4-byte color value (see below)            | Color
| `12`     |   `01` | `01`                      | Cue           | `uint8_t`                                 | Type
| `13`     |   `01` | `00`                      |               |                                           |

### `Serato Markers_` Entry Types

| ID | Type
| -- | ----
|  1 | Cue
|  3 | Loop

### `Serato Markers_` Color Format

The color format that Serato uses in the `Serato Markers_` entries is a bit
weird. Apparently they thought it was best to do sprinkle some unused bits into
the 3-byte RGB value. Hence, the resulting number becomes 4 bytes long:

    Serato Color |     Byte1     |     Byte2     |     Byte3     |     Byte4     |
                 | Nibb1 | Nibb2 | Nibb3 | Nibb4 | Nibb5 | Nibb6 | Nibb7 | Nibb8 |
    Bits         |A A A A B B B B C C C C D D D D E E E E F F F F G G G G H H H H|
    Ignored Bits |^ ^ ^ ^ ^       ^               ^               ^              |
    RGB          |||||||||||      Red        |      Green      |      Blue       |
                 |||||||||||  Nibb1  | Nibb2 |  Nibb3  | Nibb4 |  Nibb5  | Nibb6 |

Conversion is possible by doing some bitwise operations:

    # Converting 3-byte RGB into 4-byte Serato color
    z = b & 0x7F
    y = ((b >> 7) | (g << 1)) & 0xFF
    x = ((g >> 7) | (r << 2)) & 0xFF
    w = (r >> 5)
    color = (w << 24) | (x << 16) | (y << 8) | z

    # Converting 4-byte Serato color into 3-byte RGB
    b = (z & 0x7F) | ((y & 0x01) << 7)
    g = ((y & 0x7F) >> 1) | ((x & 0x03) << 6)
    r = ((x & 0x7F) >> 2) | ((w & 0x07) << 5)
    color = (r << 16) | (g << 8) | b

## Footer

The footer consists of 4 bytes that indicate the track color in the library view.

| Offset   | Length | Raw Value                 | Decoded Value | Type                                      | Description
| -------- | ------ | ------------------------- | ------------- | ----------------------------------------- | -----------
| `00`     | `04`   | `07 7f 7f 7f`             | #FFFFFF       | 4-byte color value (see above)            | Track Color Mask (e.g. `#FFFFF` mean black)

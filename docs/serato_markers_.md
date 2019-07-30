# Serato Markers_

The `Serato Markers_` tag stores information about the beatgrid (i.e. beatgrid markers).

The tag data consists of a header followed by 0 or more beatgrid markers and a single footer byte.

## Header

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `02` | `02 05`                   |               | *?* (2 bytes)           |
|   `02` |   `04` | `00 00 00 0e`             | 14            | `uint32_t`              | Number of Markers

## Markers

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

## Footer

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `04` | `07 7f 7f 7f`             |               |                         |

# Serato BeatGrid

    $ hexdump -C Serato\ BeatGrid.octet-stream
    00000000  01 00 00 00 00 01 3e 9c  28 38 42 e6 00 00 37     |......>.(8B...7|
    0000000f

The `Serato BeatGrid` tag stores information about the beatgrid (i.e. beatgrid markers).

The tag data consists of a header followed by 0 or more beatgrid markers and a single footer byte.

## Header

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `02` | `01 00`                   |               | *?* (2 bytes)           |
|   `02` |   `04` | `00 00 00 01`             | 1             | `uint32_t`              | Number of Markers

## Beatgrid Markers

There are two different types of beatgrid markers: terminal and non-terminal.

### Terminal

The last beatgrid marker always has to be a terminal one.
This is also the case if the tag only contain a single beatgrid marker.

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `04` | `3e 9c 28 38`             |               | `float` (binary32)      | Position
|   `04` |   `04` | `42 e6 00 00`             |               | `float` (binary32)      | BPM

### Non-terminal

All beatgrid markers before the last one are non-terminal beatgrid markers.
Instead of a floating point BPM value, they contain the number of beats till the next marker as an integer.

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `04` |                           |               | `float` (binary32)      | Position
|   `04` |   `04` | `00 00 00 04`             |               | `uint32_t`              | Beats till next marker


## Footer

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` | `01`   | `37`                      |               | *?* (1 byte)            | Apparently random (?)

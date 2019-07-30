# Serato Autotags

    $ hexdump -C ../shared/analyzed/Serato\ Autotags.octet-stream
    00000000  01 01 31 31 35 2e 30 30  00 2d 33 2e 32 35 37 00  |..115.00.-3.257.|
    00000010  30 2e 30 30 30 00                                 |0.000.|
    00000016

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `02` | `01 01`                   |               | *?* (2 bytes)           |
|   `02` |   `07` | `31 31 35 2e 30 30 00`    |      `115.00` | ASCII (zero-terminated) | BPM
|   `09` |   `07` | `2d 33 2e 32 35 37 00`    |      `-3.257` | ASCII (zero-terminated) | Auto Gain
|   `10` |   `06` | `30 2e 30 30 30 00`       |       `0.000` | ASCII (zero-terminated) | Gain dB


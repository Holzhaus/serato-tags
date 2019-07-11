# Serato Analysis

    $ hexdump -C ../shared/analyzed/Serato\ Analysis.octet-stream
    00000000  02 01                                             |..|
    00000002

Probably contains the Serato version number (*here:* Version 2.1.x).

| Offset | Length | Raw Value                 | Decoded Value | Type                    | Description
| ------ | ------ | ------------------------- | ------------- | ----------------------- | -----------
|   `00` |   `01` |                      `02` |           `2` | `unsigned char`         | Major Version of Serato that performed the analysis
|   `01` |   `01` |                      `01` |           `1` | `unsigned char`         | Minor Version of Serato that performed the analysis

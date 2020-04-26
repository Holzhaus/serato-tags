# File Formats

Serato DJ Pro [supports a variety of different file types](https://support.serato.com/hc/en-us/articles/204177974-Serato-DJ-Pro-Supported-File-Types):

- MP3
- OGG
- ALAC (mac & Windows 10 only)
- FLAC
- AIF
- WAV
- WL.MP3
- MP4
- M4A
- AAC (mac only)

## MP3 and AIFF

Data is stored inside [ID3v2.4 General encapsulated object (GEOB)](http://id3.org/id3v2.4.0-frames) frames:

- `Serato Overview`
- `Serato Analysis`
- `Serato Autotags`
- `Serato Markers_`
- `Serato Markers2`
- `Serato BeatGrid`
- `Serato Offsets_` (MP3 only)

## FLAC

Data is stored inside the [`VORBIS_COMMENT`](https://xiph.org/vorbis/doc/v-comment.html) block.
The fields used are as follows:

- `SERATO_ANALYSIS`
- `SERATO_AUTOGAIN`
- `SERATO_BEATGRID`
- `SERATO_MARKERS_V2`
- `SERATO_OVERVIEW`
- `SERATO_RELVOL`
- `SERATO_VIDEO_ASSOC`

The field data is base64-encoded without padding and linefeed `\n`
inserted after every 72 characters.

After decoding, the data contains:

- the null-terminated string `application/octet-stream`
- a null-byte (`\0`)
- a null-terminated field name (e.g. `Serato Markers_` or `Serato Markers2`)
- the actual data (e.g. `\x01\01AQFDT...`)

## MP4/M4A (AAC, ALAC)

Data is stored as custom MP4 atoms using the *type* `----` and the
*mean* `com.serato.dj`:

- `----:com.serato.dj:analysisVersion`
- `----:com.serato.dj:autgain`
- `----:com.serato.dj:beatgrid`
- `----:com.serato.dj:markers`
- `----:com.serato.dj:markersv2`
- `----:com.serato.dj:overview`
- `----:com.serato.dj:relvol`
- `----:com.serato.dj:videoassociation`

Field data is base64-encoded without padding. Both fields `markers` and
`markersv2` contain linefeeds after every 72 characters while all other
fields don't (i.e. *no* linefeeds). The decoded data matches the format
used for FLAC files.

In the special case of MP4/M4A files, Serato only reads the first 5 cue points and all loops when these are also in the `markers` field. This field has a fixed length and even when cue points or loops are not in use, they should still be filled.

## Ogg Vorbis

Data is stored as `VorbisComment` metadata with the following field names:

- `serato_analysis_ver`
- `serato_overview`
- `serato_beatgrid`
- `serato_markers`
- `serato_markers2`

For unknown reasons, the data format in Ogg Vorbis files seems differ significantly from other file types.

## AAC

Data is stored in XML format inside the `_Serato_/M̀etadata` directory.

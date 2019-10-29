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

Data is stored inside the `VORBIS_COMMENT` block. The fields used are as follows:

- `SERATO_ANALYSIS`
- `SERATO_AUTOGAIN`
- `SERATO_BEATGRID`
- `SERATO_MARKERS_V2`
- `SERATO_OVERVIEW`
- `SERATO_RELVOL`
- `SERATO_VIDEO_ASSOC`

The field data is base64 encoded (without padding, linefeed [`\n`[ after every 72 characters).
After decoding, the data contains 
- the null-terminated string `application/octet-stream`
- a null-byte (`\0`)
- a null-terminated field name (e.g. `Serato Markers2`)
- the actual data (e.g. `\x01\01AQFDT...`)


# MP4/M4A

Data is stored as Apple iTunes metadata fields:

- `----:com.serato.dj:analysisVersion`
- `----:com.serato.dj:autgain`
- `----:com.serato.dj:beatgrid`
- `----:com.serato.dj:markers`
- `----:com.serato.dj:markersv2`
- `----:com.serato.dj:overview`
- `----:com.serato.dj:relvol`
- `----:com.serato.dj:videoassociation`

The field data is base64-encoded (without padding, *no* linefeeds).
After decoding, the data is the same as in FLAC files.


## Ogg Vorbis

Data is stored as `VorbisComment` metadata with the following field names:

- `serato_analysis_ver`
- `serato_overview`
- `serato_beatgrid`
- `serato_markers`
- `serato_markers2`

For unknown reasons, the data format in Ogg Vorbis files seems differ significantly from other files types.


## AAC

Data is stored in XML format inside the `_Serato_/M̀etadata` directory.

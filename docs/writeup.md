# Music

As example file I used [Perséphone - Retro Funky (SUNDANCE remix)](https://soundcloud.com/sundancemusic/pers-phone-retro-funky), which is licensed under the term of the [Creative Commons Attribution 3.0 Unported (CC BY 3.0) license](https://creativecommons.org/licenses/by/3.0/).

    $ lame -b 320 Perséphone\ -\ Retro\ Funky\ \(SUNDANCE\ remix\).wav
    LAME 3.100 64bits (http://lame.sf.net)
    Using polyphase lowpass filter, transition band: 20094 Hz - 20627 Hz
    Encoding Perséphone - Retro Funky (SUNDANCE remix).wav
        to Perséphone - Retro Funky (SUNDANCE remix).mp3
    Encoding as 44.1 kHz j-stereo MPEG-1 Layer III (4.4x) 320 kbps qval=3
        Frame          |  CPU time/estim | REAL time/estim | play/CPU |    ETA
    8170/8170  (100%)|    0:03/    0:03|    0:03/    0:03|   68.457x|    0:00
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    kbps        LR    MS  %     long switch short %
    320.0       99.1   0.9        87.8   6.3   5.8
    Writing LAME Tag...done
    ReplayGain: -10.6dB

Initially, there are no tags in the resulting MP3 file:

    $ eyeD3 -v original.mp3
    .../original.mp3 [ 8.14 MB ]
    -------------------------------------------------------------------------------
    Time: 03:33	MPEG1, Layer III	[ 320 kb/s @ 44100 Hz - Joint stereo ]
    -------------------------------------------------------------------------------
    No ID3 v1.x/v2.x tag found!

Next, I'm starting up a Windows 10 VM with Serato DJ Pro 2.1.1 installed.
For some reason Serato causes my CPU usage to go up to 100%, but that can be ignored since we're not doing anything latency-critical.

To make testing easier, I'll just put the MP3 file into a separate directory on my host system and create a Samba network share to access it from inside the VM.
Serato does not list network shares in the sidebar, but it's still possible to load tracks from network shares into a deck directly by using drag and drop from a file explorer window.

First, let's just load the tack into deck 1, wait until Serato is done with analyzing it and then ejecting it to make sure that ID3 tag changes are written to the file.

We can see that the file has indeed changed by comparing it to the original file:

    $ sha1sum original.mp3 analyzed.mp3
    521974eb217ef001e6df426d1e2908cd80c39b6b  original.mp3
    46e7f16f735758b4d85730b639c908850860537b  analyzed.mp3

    $ eyeD3 -v analyzed.mp3
    eyed3.id3.frames:WARNING: Frame 'RVAD' is not yet supported, using raw Frame to parse
    .../analyzed.mp3                 [ 8.16 MB ]
    -------------------------------------------------------------------------------
    Time: 03:33	MPEG1, Layer III	[ 320 kb/s @ 44100 Hz - Joint stereo ]
    -------------------------------------------------------------------------------
    ID3 v2.3:
    title: Perséphone - Retro Funky (SUNDANCE remix)
    artist:
    album:
    album artist: None
    track:
    BPM: 115
    GEOB: [Size: 3842 bytes] [Type: application/octet-stream]
    Description: Serato Overview
    Filename:


    GEOB: [Size: 2 bytes] [Type: application/octet-stream]
    Description: Serato Analysis
    Filename:


    GEOB: [Size: 22 bytes] [Type: application/octet-stream]
    Description: Serato Autotags
    Filename:


    GEOB: [Size: 318 bytes] [Type: application/octet-stream]
    Description: Serato Markers_
    Filename:


    GEOB: [Size: 470 bytes] [Type: application/octet-stream]
    Description: Serato Markers2
    Filename:


    GEOB: [Size: 15 bytes] [Type: application/octet-stream]
    Description: Serato BeatGrid
    Filename:


    GEOB: [Size: 16401 bytes] [Type: application/octet-stream]
    Description: Serato Offsets_
    Filename:


    -------------------------------------------------------------------------------
    6 ID3 Frames:
    TIT2 (52 bytes)
    TCON (11 bytes)
    TKEY (13 bytes)
    RVAD (20 bytes)
    TBPM (14 bytes)
    GEOB x 7 (21441 bytes)
    512 bytes unused (padding)
    -------------------------------------------------------------------------------

The `GEOB` tags look interesting, so let's dump them to individual files for further analysis:

    $ eyeD3 --write-objects analyzed analyzed.mp3
    eyed3.id3.frames:WARNING: Frame 'RVAD' is not yet supported, using raw Frame to parse
    .../analyzed.mp3                 [ 8.16 MB ]
    -------------------------------------------------------------------------------
    Time: 03:33	MPEG1, Layer III	[ 320 kb/s @ 44100 Hz - Joint stereo ]
    -------------------------------------------------------------------------------
    ID3 v2.3:
    title: Perséphone - Retro Funky (SUNDANCE remix)
    artist:
    album:
    album artist: None
    track:
    BPM: 115
    GEOB: [Size: 3842 bytes] [Type: application/octet-stream]
    Description: Serato Overview
    Filename:


    Writing analyzed/Serato Overview.octet-stream...
    GEOB: [Size: 2 bytes] [Type: application/octet-stream]
    Description: Serato Analysis
    Filename:


    Writing analyzed/Serato Analysis.octet-stream...
    GEOB: [Size: 22 bytes] [Type: application/octet-stream]
    Description: Serato Autotags
    Filename:


    Writing analyzed/Serato Autotags.octet-stream...
    GEOB: [Size: 318 bytes] [Type: application/octet-stream]
    Description: Serato Markers_
    Filename:


    Writing analyzed/Serato Markers_.octet-stream...
    GEOB: [Size: 470 bytes] [Type: application/octet-stream]
    Description: Serato Markers2
    Filename:


    Writing analyzed/Serato Markers2.octet-stream...
    GEOB: [Size: 15 bytes] [Type: application/octet-stream]
    Description: Serato BeatGrid
    Filename:


    Writing analyzed/Serato BeatGrid.octet-stream...
    GEOB: [Size: 16401 bytes] [Type: application/octet-stream]
    Description: Serato Offsets_
    Filename:


    Writing analyzed/Serato Offsets_.octet-stream...
    -------------------------------------------------------------------------------

# A first look

Now let's have a look at the tag data and see if we can determine the meaning of it.
The `Serato Analysis` tag only contains 2 bytes, so let's look at that one first.

    $ hexdump -C ../shared/analyzed/Serato\ Analysis.octet-stream
    00000000  02 01                                             |..|
    00000002

It's just a suspicion, but the numbers `02 01` look like the major/minor part of the version number of Serato that was used for analysis (2.1.1).

The hexdump of next larger tag (in terms of byte length), `Serato BeatGrid`, is inconclusive at the moment, but `Serato Autotags` contains recognizable data:

    $ hexdump -C ../shared/analyzed/Serato\ Autotags.octet-stream
    00000000  01 01 31 31 35 2e 30 30  00 2d 33 2e 32 35 37 00  |..115.00.-3.257.|
    00000010  30 2e 30 30 30 00                                 |0.000.|
    00000016

We can easily see that the tag contains the string `115.00`, which is also the BPM value that is displayed by Serato.
There are two more ASCII strings in there, but I'm not sure what they are for.

Next, let's have a look at hexdump of `Serato Markers2`:

    $ hexdump -C Serato\ Markers2.octet-stream
    00000000  01 01 41 51 46 44 54 30  78 50 55 67 41 41 41 41  |..AQFDT0xPUgAAAA|
    00000010  41 45 41 50 2f 2f 2f 30  4a 51 54 55 78 50 51 30  |AEAP///0JQTUxPQ0|
    00000020  73 41 41 41 41 41 41 51  41 41 00 00 00 00 00 00  |sAAAAAAQAA......|
    00000030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
    *
    000001d0  00 00 00 00 00 00                                 |......|
    000001d6

The ASCII data in that file certainly looks like it has been base64-encoded.
Let's verify that that assumption and see what's inside:

    $ grep -Poaz '[\w/]*' Serato\ Markers2.octet-stream | tr -d '\0' | base64 -d | hexdump -C
    00000000  01 01 43 4f 4c 4f 52 00  00 00 00 04 00 ff ff ff  |..COLOR.........|
    00000010  42 50 4d 4c 4f 43 4b 00  00 00 00 01 00 00        |BPMLOCK.......|
    0000001e

The `Serato Overview` tag is almost 4 KB in size. The ASCII representation that is generated by hexdump -C looks quite familiar:

![Serato Overview](serato-overview-hexdump.png)

This tag obviously contains the data for the track overview in Serato.

The remaining tags, `Serato Markers_` and `Serato Offsets_` contain a lot of repeating data, but it's uncertain what it means.

# GC-AudioImporter

Small tool for fixing the start-lag when you add your own MP3s to Gunman Contracts.

If your custom music freezes or glitches for a few seconds when it starts and then plays fine, this is for you. It checks the MP3, strips the tags and headers that tend to cause it (ID3 tags, cover art, VBR/Xing header), and re-encodes it as a clean OGG or WAV.

> Fan-made. Not affiliated with the Gunman Contracts developers.

## How to use

1. Run `GC-AudioImporter.exe`
2. Click **Add MP3s** and pick your songs
3. Pick the output folder (wherever you normally put custom music for the game)
4. Hit **Fix my audio**

It remembers your output folder for next time.

## Command line

```
GC-AudioImporter.exe -o "D:\GameMusic" song1.mp3 song2.mp3
GC-AudioImporter.exe -o "D:\GameMusic" -f wav song.mp3
```

## OGG or WAV?

Try OGG first, it's much smaller. If you still get lag, switch to WAV. It's the most boring format there is, so it's the safest, just bigger.

## Building it yourself

1. Install Python 3.9+
2. Put `ffmpeg.exe` in the project folder
3. Run `build.bat`

The exe shows up in `dist/`.

## Notes

- Your original files are never touched. The fixed copies go in the output folder.
- Only the first audio stream is kept, and all metadata (title, artist, art) is removed, so the game won't show song names.

## Contributing

Found a file that still lags? Open an issue and mention the file's bitrate and where it came from (YouTube rip, bought, etc.), that helps narrow it down.

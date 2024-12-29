# Download youtube sound effect
yt-dlp -x --audio-format mp3 $1 -o "resources/%(title)s.%(ext)s"
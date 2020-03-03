import youtube_dl
import sys

if len(sys.argv) != 3:
    print('Usage: link name')
    sys.exit(-1)

link = sys.argv[1]
name = sys.argv[2]
print('Url:', link)
print('Name:', name)

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'music/' + name + '.%(ext)s'
}


with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([link])



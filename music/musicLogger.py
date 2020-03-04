import os
import sys
import json
import subprocess

path = ''

#TODO make a shuffler
def shuffle(arr):
    pass

def logMusic():
    print('Logging music to %smusicList.json' % path)

    dir = os.listdir(path)
    songs = []

    for i in dir:
        if i[-3:] == 'mp3':
            songs.append(i)

    shuffle(songs)

    musicList = {"cur": None, "songs": songs, 'past': []}

    with open(path + 'musicList.json', 'w') as outFile:
        outFile.write(json.dumps(musicList, indent=4, sort_keys=True))


def prime():
    print('Making the queue, %squeue.json' % path)

    with open(path + 'musicList.json', 'r') as inFile:
        jsonData = json.load(inFile)

    song = jsonData['songs']
    cur = song[0]
    jsonData['cur'] = cur
    song.pop(0)
    jsonData['songs'] = song

    with open(path + 'queue.json', 'w') as outFile:
        outFile.write(json.dumps(jsonData, indent=4, sort_keys=True))

# adds a link to the link list
# makes new urlhistory if none found
def url(link, name):
    print('Adding:', link)
    jsonData = []

    if 'urlhistory.json' in os.listdir(path):
        with open(path + 'urlhistory.json', 'r') as inFile:
            jsonData = json.load(inFile)


    if not link in jsonData:
        jsonData.append(link)

        with open(path + 'urlhistory.json', 'w') as outFile:
            outFile.write(json.dumps(jsonData, indent=4, sort_keys=True))

        subprocess.call(['python3', path + 'musicDownloader.py', link, name])

        sys.exit(1)
    else:
        print('Duplicate found')
        sys.exit(-1)


def main(args):
    global path
    #print('args:', args)
    if args[0].find('/') != -1:
        path = args[0].split('/')[0] + '/'
    else:
        path = './'
    #print('path:', path)

    if len(args) == 1:
        logMusic()

    elif args[1] == 'log':
        logMusic()

    elif args[1] == 'queue':
        prime()

    elif args[1] == 'url':
        url(args[2], args[3])

    else:
        print(args, "Bad args")


main(sys.argv)

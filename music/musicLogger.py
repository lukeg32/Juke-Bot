import os
import sys
import json

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

def url(link):
    print('Adding:', link)

    with open(path + 'urlhistory', 'r') as inFile:
        jsonData = json.load(inFile)

    jsonData.append(link)

    with open(path + 'urlhistory', 'w') as inFile:
        outFile.write(json.dumps(jsonData, indent=4, sort_keys=True))


def main(args):
    global path
    if len(args) == 3:
        path = args[2]

    if len(args) == 1:
        logMusic()
    elif args[1] == 'log':
        logMusic()
    elif args[1] == 'queue':
        prime()
    elif args[1] == 'url':
        url(args[3])
    else:
        print(args, "Bad args")


main(sys.argv)

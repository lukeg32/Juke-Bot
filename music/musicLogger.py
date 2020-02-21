import os
import sys
import json

def logMusic():
    print('Logging music to musicList.json')

    dir = os.listdir()
    songs = []

    for i in dir:
        if i[-3:] == 'mp3':
            songs.append(i)

    musicList = {"cur": None, "songs": songs, 'past': []}

    with open('musicList.json', 'w') as outFile:
        outFile.write(json.dumps(musicList, indent=4, sort_keys=True))


def prime():
    print('Making the queue, queue.json')

    with open('musicList.json', 'r') as inFile:
        jsonData = json.load(inFile)

    with open('queue.json', 'w') as outFile:
        outFile.write(json.dumps(jsonData, indent=4, sort_keys=True))


def main(args):
    if len(args) == 1:
        logMusic()
    elif args[1] == 'log':
        logMusic()
    elif args[1] == 'queue':
        prime()
    else:
        print(args, "Bad args")

main(sys.argv)

import os
import sys
import json
import discord
import subprocess
from discord.ext import commands
from dotenv import load_dotenv

#discord.opus.load_opus('opus')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PREFIX = os.getenv('PREFIX')
client = commands.Bot(command_prefix = PREFIX)

channel = None
path = './music/'
#print(os.listdir(path))
song = []
for i in os.listdir(path):
    if i[-3:] == 'mp3':
        song.append(i)
#print(song)

def loadQueue():
    with open(path + 'queue.json', 'r') as inFile:
        queue = json.load(inFile)

    return queue

def writeQueue(queue):
    with open(path + 'queue.json', 'w') as outFile:
        outFile.write(json.dumps(queue, indent=4, sort_keys=True))

def loadMusic():
    subprocess.call(['python3', 'music/musicLogger.py', 'log', 'music/'])

def makeQueue():
    subprocess.call(['python3', 'music/musicLogger.py', 'queue', 'music/'])


def getSong():
    queue = loadQueue()

    return queue['cur']

def nextSong():
    again = True

    queue = loadQueue()

    past = queue['past']
    cur = queue['cur']
    songs = queue['songs']

    if len(songs) == 0:
        again = False

    else:
        past.append(cur)
        cur = songs[0]
        songs.pop(0)

        queue['past'] = past
        queue['cur'] = cur
        queue['songs'] = songs

        writeQueue(queue)

    return again



#client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    sutats = discord.Status.online
    game = discord.Game('music')
    await client.change_presence(status=sutats, activity=game)
    print(
        f'{client.user} has connected to Discord!\n'
        f'{guild.name}(id : {guild.id})'
    )

#@client.event
#async def on_message(message):
#    if message.author == message.author.bot:
#        return
#    if not message.content.startswith(PREFIX):
#        return
#
#    msg = message.content[1:]
#    print(msg)
#
#    if msg == 'ping':
#        await message.channel.send('pong')
#    elif msg == 'kill':
#        await message.channel.send('Thou hast smote me')
#        sys.exit("I have become deaded.")

@client.command()
async def read(ctx):
    loadMusic()

@client.command()
async def write(ctx):
    makeQueue()

@client.command()
async def kill(ctx):
    await ctx.channel.send('Thou hast smote me.')
    sys.exit("I have become deaded")

@client.command()
async def next(ctx):
    print(ctx.voice_client)
    again = nextSong()
    if again:
        #ctx.voice_client.stop()
        if channel.is_playing():
            channel.stop()
        print(channel.is_playing())
        await play(ctx)

    else:
        await ctx.send("Queue ended")



@client.command()
async def isP(ctx):
    await ctx.send(channel.is_playing())

@client.command()
async def join(ctx):
    global channel
    channel = await ctx.author.voice.channel.connect()

@client.command()
async def play(ctx):
    if channel != None:
        source = path + getSong()
        print('::::playing: ' + source)
        source = discord.FFmpegPCMAudio(source)
        source = discord.PCMVolumeTransformer(source)
        #print(os.listdir(path))

        print(channel.is_playing())
        channel.play(source, after=lambda e: print("done", e))
        channel.source = discord.PCMVolumeTransformer(channel.source)

    else:
        print('not connected')

@client.command()
async def pause(ctx):
    vc = ctx.voice_client

    if vc.is_paused():
        ctx.send("Already paused")
        return

    vc.pause()
    await ctx.send(f'**`{ctx.author}`**: Paused song!')

@client.command()
async def add(ctx):
    print("TODO")
    #download a youtube link

@client.command()
async def stream(ctx):
    print('TODO')
    #stream a youtube link

@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

client.run(TOKEN)

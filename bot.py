import os
import sys
import json
import discord
import subprocess
from discord.ext import commands
from dotenv import load_dotenv

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
    with open('queue.json', 'r') as inFile:
        queue = json.load(inFile)

    return queue

def writeQueue(queue):
    with open('queue.json', 'w') as outFile:
        outFile.write(json.dumps(queue, indent=4, sort_keys=True))

def loadMusic():
    subprocess.call(['python3', 'music/musicLogger.py', 'log'])

def makeQueue():
    subprocess.call(['python3', 'music/musicLogger.py', 'queue'])


#client = discord.Client()
@client.command
async def read():
    loadMusic()

@client.command
async def write():
    makeQueue()

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
async def kill(ctx):
    await ctx.channel.send('Thou hast smote me.')
    sys.exit("I have become deaded")

@client.command()
async def join(ctx):
    global channel
    channel = ctx.author.voice.channel
    await channel.connect()

@client.command()
async def play(ctx):
    if channel != None:
        source = path + song[0]
        print(os.listdir(path))
        ctx.voice_client.play(discord.FFmpegPCMAudio(source), after=lambda e:
            print('done', e))
    else:
        print('not connected')

@client.command()
async def pause(ctx):
    vc = ctx.voice_client

    if vc.is_paused():
        ctx.send("Already paused")
        return

    vc.pause()
    ctx.send(f'**`{ctx.author}`**: Paused song!')

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

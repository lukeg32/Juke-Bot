import os
import asyncio
import sys
import json
import discord
import youtube_dl
import subprocess
from discord.ext import commands
from dotenv import load_dotenv

if not discord.opus.is_loaded():
    #discord.opus.load_opus('opus')
    pass

ytdl_format_options = {'format': 'bestaudio/best',
                       'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                       'restrictfilenames': True,
                       'noplaylist': True,
                       'nocheckcertificate': True,
                       'ignoreerrors': False,
                       'logtostderr': False,
                       'quiet': True,
                       'no_warnings': True,
                       'default_search': 'auto',
                       'source_address': '0.0.0.0'}

ffmpeg_options = {'before_options': '-nostdin', 'options': '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

load_dotenv()
if (len(sys.argv) > 1):
    TOKEN = os.getenv('DISCORD_TOKEN_TWO')
    PREFIX  = os.getenv('PREFIX_TWO')
else:
    TOKEN = os.getenv('DISCORD_TOKEN')
    PREFIX = os.getenv('PREFIX')

GUILD = os.getenv('DISCORD_GUILD')
client = commands.Bot(command_prefix = PREFIX)

voiceChannel = None
textChannel = None
RUNNING = True
done = False
path = './music/'
#print(os.listdir(path))
# song = []
# for i in os.listdir(path):
#     if i[-3:] == 'mp3':
#         song.append(i)

songs = asyncio.Queue()
play_next_song = asyncio.Event()


async def audio_player_task():
    global done
    while True:
        print('Go')
        play_next_song.clear()
        current = await songs.get()

        if current[1] == "None":
            await playSong(textChannel)
        elif current[1] == 'url':
            await textChannel.send('TODO')
            pass
        else:
            print(current)

        if current[0][:-4] != "":
            await textChannel.send('Now playing: {}'.format(current[0][:-4]))

        print('Playing and wating')
        await play_next_song.wait()
        await nextSong()

def toggle_next():
    client.loop.call_soon_threadsafe(play_next_song.set)


@client.command()
async def play(ctx):
    await addToQueue(getSong(), "None")

@client.command()
async def addToQueue(song, url):
    await songs.put([song, url])


# stream TODO Replace with stream
@client.command()
async def Play(ctx, url):
    if voiceChannel == None:
        await join(ctx)

    #player = self.players[ctx.guild.id]

   #player = await from_url(url, loop=client.loop, stream=True)
    player = await voiceChannel.create_ytdl_player(url, after=toggle_next())
    await songs.put(player)
    #source = await YTDLSource.create_source(ctx, search, loop=bot.loop, download=False)
    #await songs.queue.put(source)

# read write updating the queue
# reads the queue and returns it
def loadQueue():
    with open(path + 'queue.json', 'r') as inFile:
        queue = json.load(inFile)

    return queue

# writes to the queue.json the new queue
def writeQueue(queue):
    with open(path + 'queue.json', 'w') as outFile:
        outFile.write(json.dumps(queue, indent=4, sort_keys=True))

# runs the music logger to log the mp3 files
def loadMusic():
    subprocess.call(['python3', 'music/musicLogger.py', 'log', 'music/'])

# runs the music logger to make queue
def makeQueue():
    subprocess.call(['python3', 'music/musicLogger.py', 'queue', 'music/'])

# gets the cur song from queue
def getSong():
    queue = loadQueue()

    return queue['cur']

def done():
    # TODO add a queue ended msg
    again = True

    queue = loadQueue()

    if len(queue['songs']) == 0:
        again = False

    return again


async def nextSong():
    again = done()

    queue = loadQueue()

    #print(queue)

    past = queue['past']
    cur = queue['cur']
    songs = queue['songs']

    #print(json.dumps(queue, indent=4, sort_keys=True))

    #print(songs)

    if again:
        if cur != "":
            past.append(cur)
        cur = songs[0]
        songs.pop(0)

        queue['past'] = past
        queue['cur'] = cur
        queue['songs'] = songs

        writeQueue(queue)
        #print(json.dumps(queue, indent=4, sort_keys=True))

        await addToQueue(cur, 'None')


    return again

async def changeActivity(activity):
    sutats = discord.Status.online
    game = discord.Game(activity)
    await client.change_presence(status=sutats, activity=game)

#client = discord.Client()

# on ready
@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    sutats = discord.Status.dnd
    activity = discord.Game(" nothing")
    await client.change_presence(status=sutats, activity=activity)
    print(
        f'{client.user} has connected to Discord!\n'
        f'{guild.name}(id : {guild.id})'
    )

# on message do stuff
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

# Start controls
@client.command()
async def start(ctx):
    global voiceChannel
    global textChannel
    if voiceChannel == None:
        await join(ctx)

    await play(ctx)
    await ctx.send("Starting")

# reads the directory and writes the songs to json
@client.command()
async def read(ctx):
    loadMusic()

# reads song json and loads to queue json
@client.command()
async def write(ctx):
    makeQueue()

# should kill the bot
@client.command()
async def kill(ctx):
    await leave(ctx)
    await ctx.channel.send('Thou hast smote me.')
    sys.exit("I have become deaded")
    sys.exit("I should be dead rn")
    sys.exit("LIke really why is this showing")

# REMOVE, equivalent to skip
@client.command()
async def next(ctx):
    print(ctx.voice_client)
    again = done()

    print(again)
    if again:
        if voiceChannel.is_playing():
            voiceChannel.stop()
        print(voiceChannel.is_playing())
        #await playSong(ctx)

    else:
        await ctx.send("Queue ended")

# sends the current song or none
@client.command()
async def cur(ctx):
    txt = "Not Playing"
    if voiceChannel.is_playing():
        txt = "Playing " + getSong()[:-4]

    await ctx.send(txt)

# joins the voice channel user is in, saves textchannel for future msgs
@client.command()
async def join(ctx):
    global voiceChannel
    global textChannel
    voiceChannel = await ctx.author.voice.channel.connect()
    textChannel = ctx

# plays a song from queue
#@client.command()
async def playSong(ctx):
    if voiceChannel != None:
        source = path + getSong()
        print('::::playing: ' + source)
        source = discord.FFmpegPCMAudio(source)
        source = discord.PCMVolumeTransformer(source)
        #print(os.listdir(path))

        #voiceChannel.play(source, after=lambda e: finish(e))
        voiceChannel.play(source, after=lambda e: toggle_next())
        voiceChannel.source = discord.PCMVolumeTransformer(voiceChannel.source)
        voiceChannel.source.volume = 100000
        await changeActivity(getSong()[:-4])

    else:
        print('not connected')
def previous(queue):

    cur = queue['cur']
    past = queue['past']
    songs = queue['songs']
    #print(cur)
    #print(past)
    #print(songs)

    #print(json.dumps(queue, indent=4, sort_keys=True))

    if len(past) == 0:
        print('no past')
        songs.insert(0, cur)
        queue['cur'] = ''
        queue['past'] = []

    elif cur != '':
        print("cur isn't null")
        songs.insert(0, cur)

        print(past[-1])
        queue['cur'] = past[-1]
        past.pop(-1)

    #print(json.dumps(queue, indent=4, sort_keys=True))

    return queue


@client.command()
async def last(ctx):
    queue = loadQueue()

    print('going back')
    if len(queue['past']) > 0:
        queue = previous(queue)
        queue = previous(queue)

        writeQueue(queue)

        voiceChannel.stop()
    else:
        print('trying to do the impossible')
        await ctx.send('Your at the begining')


# resumes a paused song
@client.command()
async def resume(ctx):
    vc = ctx.voice_client

    if not vc.is_paused():
        await ctx.send("Not paused")
        return

    vc.resume()
    await ctx.send(f'**`{ctx.author}`**: Resumed song!')

# pauses a playing song
@client.command()
async def pause(ctx):
    vc = ctx.voice_client

    if vc.is_paused():
        await ctx.send("Already paused")
        return

    vc.pause()
    await ctx.send(f'**`{ctx.author}`**: Paused song!')

# downloads a yt song, update music
@client.command()
async def add(ctx):
    print("TODO")
    #download a youtube link

# play yt link without downloading
@client.command()
async def stream(ctx):
    print('TODO')
    #stream a youtube link

# leave the voice channel
@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


# add main loop to the list thing, run bot
client.loop.create_task(audio_player_task())
client.run(TOKEN)

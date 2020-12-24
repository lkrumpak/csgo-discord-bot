import subprocess
import rcon
import discord
from discord.ext import commands, tasks

IP = 'iphere'
PASSWORD = 'passwordhere'
CHANNEL_ID = -1
TOKEN = 'TOKENHERE'
message_id = -1
reactions = ["▶️", "⏹️", "🔁"]
client = commands.Bot(command_prefix='.')


def retrieve_status():
    try:
        conn = rcon.RCONConnection(IP, password=PASSWORD)
        response = conn.exec_command('status')
        response = response.split('\n')

        output = response[0] + '\n' + response[2].split('(')[1][:-1] + '\n' + response[5] + '\n' + response[6] + '\n'
    except:
        output = 'Offline'
    return output


@client.event
async def on_ready():
    global message_id
    channel = client.get_channel(CHANNEL_ID)
    embed = discord.Embed(title="Server [ Counter Strike : Global Offensive ]",
                          description="Connecting...",
                          color=discord.Color.orange())
    msg = await channel.send(embed=embed)
    message_id = msg.id
    for name in reactions:
        await msg.add_reaction(name)
    change_status.start()

@client.event
async def on_reaction_add(reaction, user):
    if user != client.user:
        if reaction.emoji == "▶️":
            subprocess.run(["./csgoserver", "start"])
            description = 'Starting Server...'
        elif reaction.emoji == "⏹️":
            subprocess.run(["./csgoserver", "stop"])
            description = 'Stopping Server...'
        elif reaction.emoji == "🔁":
            subprocess.run(["./csgoserver", "restart"])
            description = 'Restarting Server...'

        if reaction.emoji in reactions:
            color = discord.Color.orange()
            embed = discord.Embed(title="Server [ Counter Strike : Global Offensive ]",
                                  description=description,
                                  color=color)
            await reaction.message.edit(embed=embed)
        await reaction.remove(user)


@tasks.loop(seconds=5)
async def change_status():
    global message_id
    channel = client.get_channel(CHANNEL_ID)
    msg = await channel.fetch_message(message_id)
    status_response = retrieve_status()

    if status_response == "Offline":
        color = discord.Color.red()
    else:
        color = discord.Color.green()

    embed = discord.Embed(title="Server [ Counter Strike : Global Offensive ]",
                          description=status_response,
                          color=color)
    await msg.edit(embed=embed)

client.run(TOKEN)

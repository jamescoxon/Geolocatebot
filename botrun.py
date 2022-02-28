#TODO
# edit title command
# update status command
# update geolocation command
# help

import discord
import settings

bot = discord.Bot()

from pysondb import db
a=db.getDb('db.json')

archive_duration = 1440
guild_id = 947954303438573638


def get_seq(incr_bool):
    sequential_count = a.getBy({"type":"seq"})
    print(sequential_count)
    sequence = 0

    print('Seq: {}'.format(sequence))

    if len(sequential_count) == 0:
        print('First Run')
        id_name = a.add({"seq":0,"type":"seq", "user":"admin", "link":"link", "status":"admin"})

    else:
        sequence = int(sequential_count[0]['seq'])
        if incr_bool == True:
            a.updateById(sequential_count[0]['id'],{"seq": (sequence + 1)})

    print('Seq: {}'.format(sequence))
    return int(sequence)

@bot.slash_command(
    name="add",
    description="Add link to database",
    guild_ids=[guild_id]
)
async def hello(ctx, link: str = None):
    name = ctx.author.name

    if link == None:
        await ctx.respond('Error - no link')
    else:
        seq = get_seq(True)

        id_name = a.add({"user":name,"type":"link","link": link, "status":"OPEN", "seq":int(seq)})

        message = await ctx.send("Here is a research thread: #{} for {} setup by @{}".format(seq, link, name))
        await message.create_thread(name='#{}'.format(seq), auto_archive_duration=archive_duration)

        await ctx.respond('Thanks {}'.format(name))

@bot.slash_command(
    name="list",
    description="list database",
    guild_ids=[guild_id]
)
async def list_command(ctx):
    all_db = a.getAll()
    print(all_db)
    if len(all_db) <= 1: 
        print('Empty DB')
        await ctx.respond('Empty DB')

    else:
        response = ""
        for entry in all_db:
            print(entry['type'])
            if entry['type'] == "link":
                response = '{}\n#{}: {}, {}'.format(response, entry['seq'],  entry['link'], entry['status'])

        print(response)
        await ctx.respond('{}'.format(response))

get_seq(False)

bot.run(settings.bot_token)

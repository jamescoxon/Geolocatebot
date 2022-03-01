#TODO
# edit title command
# update status command
# update geolocation command

import discord
import settings
import logging

logging.basicConfig(level=logging.DEBUG)

bot = discord.Bot()

from pysondb import db
a=db.getDb('db.json')

archive_duration = settings.archive_duration
guild_id = settings.guild_id
status_options = ['OPEN', 'ARCHIVED', 'COMPLETE']

def get_seq(incr_bool):
    sequential_count = a.getBy({"type":"seq"})
    print(sequential_count)
    sequence = 0

    print('Seq: {}'.format(sequence))

    if len(sequential_count) == 0:
        print('First Run')
        id_name = a.add({"seq":0,"type":"seq", "user":"admin", "link":"link", "status":"admin", "title":"admin", "thread_id":0})

    else:
        sequence = int(sequential_count[0]['seq'])
        if incr_bool == True:
            a.updateById(sequential_count[0]['id'],{"seq": (sequence + 1)})

    print('Seq: {}'.format(sequence))
    return int(sequence)

####### HELP
@bot.slash_command(
    name="help",
    description="Help Description",
    guild_ids=[guild_id]
)
async def help_command(ctx):
        await ctx.respond('Help\n Commands:\nAdd New Project: `/add <research link>` e.g. twitter or imgur link\nList Current Projects: `/list` ')

####### ADD
@bot.slash_command(
    name="add",
    description="Add link to database",
    guild_ids=[guild_id]
)
async def add_command(ctx, link: str = None):
    name = ctx.author.name

    if link == None:
        await ctx.respond('Error - no link')
    else:
        seq = get_seq(True)
        title = '{}_{}'.format(seq, 'uuid')

        message = await ctx.send("Here is a research thread: #{} for {} setup by @{}".format(seq, link, name))
        thread_info = await message.create_thread(name='#{}'.format(title), auto_archive_duration=archive_duration)

        print(thread_info.id)
        id_name = a.add({"user":name,"type":"link","link": link, "status":"OPEN", "seq":int(seq), "title":title, "thread_id": thread_info.id})

        await ctx.respond('Thanks {}'.format(name))

####### UPDATE_TITLE
@bot.slash_command(
    name="update_title",
    description="Update geolocation database",
    guild_ids=[guild_id]
)
async def update_title_command(ctx, new_title: str =None):
    name = ctx.author.name

    new_title = new_title.replace(" ", "_")

    title = str(ctx.channel)
    details = a.getBy({"title": title })
    if len(details) == 0:
        return

    print(details[0]['thread_id'])
    thread_details = bot.get_channel(int(details[0]['thread_id']))
    print(thread_details.id)
    print(thread_details.type)
    if str(thread_details.type) == 'public_thread':
        await thread_details.edit(name='#{}_{}'.format(details[0]['seq'], new_title))

        seq = details[0]['seq']
        update_title = '{}_{}'.format(seq, new_title)
        a.updateById(details[0]['id'], {"title":update_title})
        await ctx.respond('Thanks {}'.format(name))

####### UPDATE_STATUS
@bot.slash_command(
    name="update_status",
    description="Update geolocation database",
    guild_ids=[guild_id]
)
async def update_status_command(ctx, new_status: str =None):
    name = ctx.author.name

    title = str(ctx.channel)
    print(title)
    details = a.getBy({"title": title })
    if len(details) == 0:
        return

    thread_details = bot.get_channel(int(details[0]['thread_id']))
    print(thread_details.id)
    print(thread_details.type)
    if str(thread_details.type) == 'public_thread':
        if new_status.upper() in status_options:
            a.updateById(details[0]['id'], {"status":new_status.upper()})
            await ctx.respond('Thanks {}'.format(name))
        else:
            await ctx.respond('Error - incorrect status, options are {}'.format(status_options))


####### LIST
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

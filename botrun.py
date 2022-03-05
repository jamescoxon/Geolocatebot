
from pysondb import db
import discord
import settings
import logging
import sys
import time
import shortuuid
import re

logging.basicConfig(level=logging.DEBUG)

bot = discord.Bot()

a = db.getDb('db.json')

archive_duration = settings.archive_duration
guild_id = settings.guild_id

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    #        r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

if guild_id == 0 or settings.bot_token == '':
    print('Error - please update settings.py')
    sys.exit()

status_options = ['OPEN', 'ARCHIVED', 'COMPLETE']


def get_seq(incr_bool):
    sequential_count = a.getBy({"type": "seq"})
    print(sequential_count)
    sequence = 0

    print('Seq: {}'.format(sequence))

    if len(sequential_count) == 0:
        print('First Run')
        id_name = a.add({"seq": 0,
                         "type": "seq",
                         "user": "admin",
                         "link": "link",
                         "status": "admin",
                         "title": "admin",
                         "thread_id": 0,
                         "time": int(time.time()),
                         "uuid": '0'})

    else:
        sequence = int(sequential_count[0]['seq'])
        if incr_bool:
            a.updateById(sequential_count[0]['id'], {"seq": (sequence + 1)})

    print('Seq: {}'.format(sequence))
    return int(sequence)

# HELP


@bot.slash_command(
    name="help",
    description="Help Description",
    guild_ids=[guild_id]
)
async def help_command(ctx):
    await ctx.respond("Help - a bot to help organise research, when a new source link is add the bot makes a new thread allowing groups to work on geolocating and fact checking together\n"
                      "Commands:\n"
                      "Add New Research Thread: `/add <research link>` e.g. twitter or imgur link\n"
                      "List Open Research Threads: `/list_open`\n"
                      "List all Research Threads: `/list_all`\n"
                      "Update Thread Title: `/update_title <title>` only works inside a thread\n"
                      "Update Thread Status: `/update_status <status>` options: OPEN, ARCHIVED, COMPLETE, only works inside a thread", ephemeral=True)

# ADD


@bot.slash_command(
    name="add",
    description="Add link to database",
    guild_ids=[guild_id]
)
async def add_command(ctx, link: str = None):
    name = ctx.author.name

    if link is None:
        await ctx.respond('Error - no link', ephemeral=True)
    else:
        if re.match(regex, link) is None:
            await ctx.respond('Error - malformed link', ephemeral=True)
            return
        if len(link) > 256:
            await ctx.respond('Error - link to long', ephemeral=True)
            return

        seq = get_seq(True)
        uuid = shortuuid.uuid()
        title = '{}_{}'.format(seq, uuid)

        details = a.getBy({"link": link})
        if len(details) > 0:
            await ctx.respond('Error - this link is already being researched: <https://discord.com/channels/{}/{}>'.format(guild_id, details[0]['thread_id']))
            return

        message = await ctx.send("Here is a research thread: #{} for {} setup by @{}".format(seq, link, name))
        thread_info = await message.create_thread(name='#{}'.format(title), auto_archive_duration=archive_duration)

        print(thread_info.id)
        id_name = a.add({"user": name,
                         "type": "link",
                         "link": link,
                         "status": "OPEN",
                         "seq": int(seq),
                         "title": title,
                         "thread_id": thread_info.id,
                         "time": int(time.time()),
                         "uuid": uuid})

        await ctx.respond('Thanks {}'.format(name), ephemeral=True)

# UPDATE_TITLE


@bot.slash_command(
    name="update_title",
    description="Update geolocation database",
    guild_ids=[guild_id]
)
async def update_title_command(ctx, new_title: str = None):
    name = ctx.author.name

    new_title = new_title.replace(" ", "_")

    title = str(ctx.channel)
    details = a.getBy({"title": title})
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
        a.updateById(details[0]['id'], {"title": update_title})
        await ctx.respond('Thanks {}'.format(name), ephemeral=True)

# UPDATE_STATUS


@bot.slash_command(
    name="update_status",
    description="Update geolocation database",
    guild_ids=[guild_id]
)
async def update_status_command(ctx, new_status: str = None):
    name = ctx.author.name

    title = str(ctx.channel)
    print(title)
    details = a.getBy({"title": title})
    if len(details) == 0:
        return

    thread_details = bot.get_channel(int(details[0]['thread_id']))
    print(thread_details.id)
    print(thread_details.type)
    if str(thread_details.type) == 'public_thread':
        if new_status.upper() in status_options:
            a.updateById(details[0]['id'], {"status": new_status.upper()})
            await ctx.respond('Thanks {}'.format(name), ephemeral=True)

            if new_status.upper() == 'COMPLETE':
                update_title = '{}_{}'.format(details[0]['title'], 'COMPLETE')
                await thread_details.edit(archived=True, name='#{}'.format(update_title))
                a.updateById(details[0]['id'], {"title": update_title})

            if new_status.upper() == 'ARCHIVED':
                update_title = '{}_{}'.format(details[0]['title'], 'ARCHIVED')
                await thread_details.edit(archived=True, name='#{}'.format(update_title))
                a.updateById(details[0]['id'], {"title": update_title})

            if new_status.upper() == 'OPEN':
                update_title = '{}'.format(
                    details[0]['title'].replace(
                        '_ARCHIVED', ''))
                update_title = '{}'.format(
                    details[0]['title'].replace(
                        '_COMPLETE', ''))
                await thread_details.edit(archived=False, name='#{}'.format(update_title))
                a.updateById(details[0]['id'], {"title": update_title})

        else:
            await ctx.respond('Error - incorrect status, options are {}'.format(status_options), ephemeral=True)


# LIST_OPEN
@bot.slash_command(
    name="list_open",
    description="list database",
    guild_ids=[guild_id]
)
async def list_open_command(ctx):
    all_db = a.getAll()
    print(all_db)
    if len(all_db) <= 1:
        print('Empty DB')
        await ctx.respond('Empty DB')

    else:
        response = ""
        for entry in all_db:
            if entry['type'] == "link" and entry['status'] == 'OPEN':
                response = '{}\n----------\n`{}`: <https://discord.com/channels/{}/{}>, <{}>, {}'.format(
                    response, entry['title'], guild_id, entry['thread_id'], entry['link'], entry['status'])

        print(response)
        await ctx.respond('{}'.format(response), delete_after=60, ephemeral=True)

# LIST_ALL


@bot.slash_command(
    name="list_all",
    description="list database",
    guild_ids=[guild_id]
)
async def list_all_command(ctx):
    all_db = a.getAll()
    print(all_db)
    if len(all_db) <= 1:
        print('Empty DB')
        await ctx.respond('Empty DB')

    else:
        response = ""
        for entry in all_db:
            if entry['type'] == "link" and int(
                    entry['time']) + 86400 > int(time.time()):
                response = '{}\n----------\n`{}`: <https://discord.com/channels/{}/{}>, <{}>, {}'.format(
                    response, entry['title'], guild_id, entry['thread_id'], entry['link'], entry['status'])

        print(response)
        await ctx.respond('{}'.format(response), delete_after=60, ephemeral=True)

get_seq(False)

bot.run(settings.bot_token)

# Geolocatebot
A simple discord bot which allows you to organise OSINT research into threads, has a simple json based database to help keep track.

### Install Requirements
* pycord 2.0 -  https://github.com/Pycord-Development/pycord
* pysondb - https://github.com/pysonDB/pysonDB
* shortuuid
* autopep8
* bandit
* prospector
* mypy

### Installation
* copy `settings.py.example` to `settings.py`
* update `settings.py` with your bot token and guild_id (your discord server id)
* run the bot

### Commands

```
Help - a bot to help organise research, when a new source link is add the bot makes a new thread allowing groups to work on geolocating and fact checking together
Commands:
Add New Research Thread: /add <research link> e.g. twitter or imgur link
List Open Research Threads: /list_open
List all Research Threads: /list_all
Update Thread Title: /update_title <title> only works inside a thread
Update Thread Status: /update_status <status> options: OPEN, ARCHIVED, COMPLETE, only works inside a thread
```

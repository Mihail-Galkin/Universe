import nextcord
import http.client
import json
import settings
from nextcord.ext import commands

intents = nextcord.Intents().all()
client = commands.Bot(command_prefix=settings.prefix, case_insensitive=True, intents=intents)
client.remove_command('help')


@client.event
async def on_ready():
    print('Bot online')
    channel = client.guilds[0].get_channel(settings.channel)
    hooks = await channel.webhooks()
    for i in hooks:
        await i.delete()


@client.event
async def on_message(mes):
    if mes.channel.id != int(settings.channel):
        return
    elif mes.author.bot:
        return

    channel = mes.channel
    name = mes.author.display_name
    hook = await channel.create_webhook(name=name)

    if mes.reference is not None:
        emb = nextcord.Embed(title=settings.reply, url=mes.reference.jump_url, description=mes.content,
                             color=settings.color)
    else:
        emb = nextcord.Embed(description=mes.content, color=settings.color)
    emb.set_footer(text=mes.author.name, icon_url=mes.author.avatar.url)

    if mes.attachments:
        emb.set_image(url=mes.attachments[0].url)

    m = await hook.send(wait=True, embed=emb, username=name,
                        avatar_url="https://crafatar.com/renders/head/{}?overlay".format(getUUID(None, name)))
    await mes.delete()
    emojis = settings.reactions
    for i in emojis:
        await m.add_reaction(i)

    await hook.delete()


def getUUID(timestamp=None, nickname: str = None):
    get_args = "" if timestamp is None else "?at=" + str(timestamp)

    http_conn = http.client.HTTPSConnection("api.mojang.com")
    http_conn.request("GET", "/users/profiles/minecraft/" + str(nickname) + str(get_args),
                      headers={'User-Agent': 'Minecraft Username -> UUID', 'Content-Type': 'application/json'})
    response = http_conn.getresponse().read().decode("utf-8")

    if not response and timestamp is None:  # No response & no timestamp
        return getUUID(0)  # Let's retry with the Unix timestamp 0.
    if not response:  # No response (player probably doesn't exist)
        return ""

    json_data = json.loads(response)
    try:
        uuid = json_data['id']
    except KeyError as e:
        print("KeyError raised:", e)

    return uuid


client.run(settings.token)

import discord
from discord.ext import commands, tasks
import json
from datetime import datetime, timedelta
import os

TOKEN = os.getenv("TOKEN")

VIP_ROLE_ID = 1375846595727331368
EXPIRED_ROLE_ID = 1390480462572683306

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_data():
    try:
        with open("subs.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("subs.json", "w") as f:
        json.dump(data, f)

@bot.command()
async def vip(ctx, member: discord.Member, dias: int = 30):
    vip_role = ctx.guild.get_role(VIP_ROLE_ID)
    expired_role = ctx.guild.get_role(EXPIRED_ROLE_ID)

    await member.add_roles(vip_role)
    if expired_role in member.roles:
        await member.remove_roles(expired_role)

    data = load_data()
    expire = (datetime.now() + timedelta(days=dias)).timestamp()
    data[str(member.id)] = expire
    save_data(data)

    await ctx.send(f"{member.mention} VIP por {dias} dias.")

@tasks.loop(hours=12)
async def check_expired():
    await bot.wait_until_ready()
    data = load_data()
    now = datetime.now().timestamp()

    for guild in bot.guilds:
        vip_role = guild.get_role(VIP_ROLE_ID)
        expired_role = guild.get_role(EXPIRED_ROLE_ID)

        for user_id, expire in list(data.items()):
            if now > expire:
                member = guild.get_member(int(user_id))
                if member:
                    if vip_role in member.roles:
                        await member.remove_roles(vip_role)
                    await member.add_roles(expired_role)
                del data[user_id]
                save_data(data)

@bot.event
async def on_ready():
    check_expired.start()
    print("Bot online")

bot.run(TOKEN)

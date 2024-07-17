import discord
from discord.ext import commands, tasks
import os
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv
from jp_database import fetch_and_save_json_to_jp_db, get_jp_entries_to_process, update_jp_message_sent
from en_database import fetch_and_save_json_to_en_db, get_en_entries_to_process, update_en_message_sent
from jp_cards import fetch_and_save_cards_to_jp_db, get_jp_cards_entries_to_process, update_jp_cards_message_sent

# Load environment variables from .env file
load_dotenv()

# Get the bot token and prefix from environment variables
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
BOT_PREFIX = os.getenv('BOT_PREFIX')
JP_CHANNEL_ID = int(os.getenv('JP_CHANNEL_ID'))
EN_CHANNEL_ID = int(os.getenv('EN_CHANNEL_ID'))
CARD_CHANNEL_ID = int(os.getenv('CARD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=BOT_PREFIX, intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# Background task to check for updates periodically
@tasks.loop(minutes=1)  # Check every minute
async def check_for_jp_updates():
    json_url = 'https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/userInformations.json'
    fetch_and_save_json_to_jp_db(json_url)
    print("JSON data fetched and saved to the JP database")
    await process_jp_updates()  # Call process_updates() after fetching data
@tasks.loop(minutes=1)  # Check every minute
async def check_for_en_updates():
    json_url = 'https://raw.githubusercontent.com/Sekai-World/sekai-master-db-en-diff/main/userInformations.json'
    fetch_and_save_json_to_en_db(json_url)
    print("JSON data fetched and saved to the EN database")
    await process_en_updates()  # Call process_updates() after fetching data
@tasks.loop(minutes=1)
async def check_for_new_jp_cards():
    json_url = 'https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/cards.json'
    fetch_and_save_cards_to_jp_db(json_url)
    print("JP cards data fetched and saved to the database")
    await process_new_cards()

@bot.event
async def on_ready():
    # Print login confirmation
    print(f'Logged in as {bot.user}')
    # Start the loop
    check_for_jp_updates.start()
    check_for_en_updates.start()
    check_for_new_jp_cards.start()
    # Sync bot commands
    await bot.tree.sync()

# Load all command files from the commands directory
async def load_extensions():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py') and filename != '__init__.py':  # Exclude __init__.py if present
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
            except Exception as e:
                print(f'Failed to load extension {filename}: {type(e).__name__} - {e}')

# Function to post jp embeds and update messageSent flag
async def process_jp_updates():
    entries = get_jp_entries_to_process()
    for entry in entries:
        id, informationTag, browseType, platform, title, path, startAt, bannerAssetbundleName = entry
        print(entry)
        await post_jp_embed(id, informationTag, browseType, platform, title, path, startAt, bannerAssetbundleName)
        print("JP embed posted")
        update_jp_message_sent(id)
        print("1 JP entry updated")

async def post_jp_embed(id, informationTag, browseType, platform, title, path, startAt, bannerAssetbundleName):
    channel = bot.get_channel(JP_CHANNEL_ID)
    print(JP_CHANNEL_ID)
    if bannerAssetbundleName != None:
        embed_image = f"https://production-web.sekai.colorfulpalette.org/images/information/{bannerAssetbundleName}.png".replace(" ", "%20")
    else:
        embed_image = None
        
    print(embed_image)

    if browseType == 'internal':
        embed_url = f"https://production-web.sekai.colorfulpalette.org/{path}".replace(" ", "%20")
    if browseType == 'external':
        embed_url = path

    print(embed_url)

    # If statement for informationTag to determine embed color and thumbnail
    if informationTag == 'bug':
            embed_color = 0x999999
            file = discord.File("images/jp/icon_failure.png", filename="icon_failure.png")
            embed_thumbnail = "attachment://icon_failure.png"
    if informationTag == 'campaign':
            embed_color = 0x00ffdd
            file = discord.File("images/jp/icon_campaign.png", filename="icon_campaign.png")
            embed_thumbnail = "attachment://icon_campaign.png"
    if informationTag == 'event':
            embed_color = 0xfc59ab
            file = discord.File("images/jp/icon_event.png", filename="icon_event.png")
            embed_thumbnail = "attachment://icon_event.png"
    if informationTag == 'gacha':
            embed_color = 0xfc59ab
            file = discord.File("images/jp/icon_gacha.png", filename="icon_gacha.png")
            embed_thumbnail = "attachment://icon_gacha.png"
    if informationTag == 'information':
            embed_color = 0x00ffdd
            file = discord.File("images/jp/icon_notice.png", filename="icon_notice.png")
            embed_thumbnail = "attachment://icon_notice.png"
    if informationTag == 'music':
            embed_color = 0xe3a41b
            file = discord.File("images/jp/icon_song.png", filename="icon_song.png")
            embed_thumbnail = "attachment://icon_song.png"
    if informationTag == 'update':
            embed_color = 0xfc5889
            file = discord.File("images/jp/icon_update.png", filename="icon_update.png")
            embed_thumbnail = "attachment://icon_update.png"

    print(embed_color)

    embed = discord.Embed(
    title=title,
    url=embed_url, 
    description=f"<t:{int(startAt/1000)}>",
    color=embed_color,  
    timestamp=datetime.now(),
    )
    if embed_image != None:
        embed.set_image(url=embed_image)
    embed.set_thumbnail(url=embed_thumbnail)
    embed.set_footer(text=f"platform: {platform}")
    await channel.send(file=file, embed=embed)
    print(f"JP Embed posted for ID: {id}")


# Function to post en embeds and update messageSent flag
async def process_en_updates():
    entries = get_en_entries_to_process()
    for entry in entries:
        id, informationTag, browseType, platform, title, path, startAt, bannerAssetbundleName = entry
        print(entry)
        await post_en_embed(id, informationTag, browseType, platform, title, path, startAt, bannerAssetbundleName)
        print("EN embed posted")
        update_en_message_sent(id)
        print("1 EN entry updated")

async def post_en_embed(id, informationTag, browseType, platform, title, path, startAt, bannerAssetbundleName):
    channel = bot.get_channel(EN_CHANNEL_ID)
    print(EN_CHANNEL_ID)
    if bannerAssetbundleName != None:
        embed_image = f"https://n-production-web.sekai-en.com/images/information/{bannerAssetbundleName}.png".replace(" ", "%20")
    else:
        embed_image = None

    print(embed_image)

    if browseType == 'internal':
        embed_url = f"https://n-production-web.sekai-en.com/{path}".replace(" ", "%20")
    if browseType == 'external':
        embed_url = path

    print(embed_url)

    # If statement for informationTag to determine embed color and thumbnail
    if informationTag == 'bug':
            embed_color = 0x999999
            file = discord.File("images/en/icon_failure.png", filename="icon_failure.png")
            embed_thumbnail = "attachment://icon_failure.png"
    if informationTag == 'campaign':
            embed_color = 0x00ffdd
            file = discord.File("images/en/icon_campaign.png", filename="icon_campaign.png")
            embed_thumbnail = "attachment://icon_campaign.png"
    if informationTag == 'event':
            embed_color = 0xfc59ab
            file = discord.File("images/en/icon_event.png", filename="icon_event.png")
            embed_thumbnail = "attachment://icon_event.png"
    if informationTag == 'gacha':
            embed_color = 0xfc59ab
            file = discord.File("images/en/icon_gacha.png", filename="icon_gacha.png")
            embed_thumbnail = "attachment://icon_gacha.png"
    if informationTag == 'information':
            embed_color = 0x00ffdd
            file = discord.File("images/en/icon_notice.png", filename="icon_notice.png")
            embed_thumbnail = "attachment://icon_notice.png"
    if informationTag == 'music':
            embed_color = 0xe3a41b
            file = discord.File("images/en/icon_song.png", filename="icon_song.png")
            embed_thumbnail = "attachment://icon_song.png"
    if informationTag == 'update':
            embed_color = 0xfc5889
            file = discord.File("images/en/icon_update.png", filename="icon_update.png")
            embed_thumbnail = "attachment://icon_update.png"

    print(embed_color)

    embed = discord.Embed(
    title=title,
    url=embed_url, 
    description=f"<t:{int(startAt/1000)}>",
    color=embed_color,  
    timestamp=datetime.now(),
    )
    if embed_image != None:
        embed.set_image(url=embed_image)
    embed.set_thumbnail(url=embed_thumbnail)
    embed.set_footer(text=f"platform: {platform}")
    await channel.send(file=file, embed=embed)
    print(f"EN Embed posted for ID: {id}")

# Function to post new cards and update messageSent flag
async def process_new_cards():
    entries = get_jp_cards_entries_to_process()
    for entry in entries:
        id, characterId, cardRarityType, attr, supportUnit, skillId, cardSkillName, prefix, assetbundleName, releaseAt = entry
        print(entry)
        await post_new_cards(id, characterId, cardRarityType, attr, supportUnit, skillId, cardSkillName, prefix, assetbundleName, releaseAt)
        print('New cards posted')
        update_jp_cards_message_sent(id)
        print('1 New card entry updated')

async def check_image_exists(url):
    response = requests.head(url)
    return response.status_code == 200

async def post_new_cards(id, characterId, cardRarityType, attr, supportUnit, skillId, cardSkillName, prefix, assetbundleName, releaseAt):
    channel = bot.get_channel(CARD_CHANNEL_ID)
    print(CARD_CHANNEL_ID)
    while True:
        try:
            # If statement to determine character name and color
            if characterId == 1:
                chara_name = '星乃一歌'
                chara_color = 0x33AAEE
            if characterId == 2:
                chara_name = '天馬咲希'
                chara_color = 0xFFDD44
            if characterId == 3:
                chara_name = '望月穂波'
                chara_color = 0xEE6666
            if characterId == 4:
                chara_name = '日野森志歩'
                chara_color = 0xBBDD22
            if characterId == 5:
                chara_name = '花里みのり'
                chara_color = 0xFFCCAA
            if characterId == 6:
                chara_name = '桐谷遥'
                chara_color = 0x99CCFF
            if characterId == 7:
                chara_name = '桃井愛莉'
                chara_color = 0xFFAACC
            if characterId == 8: 
                chara_name = '日野森雫'
                chara_color = 0x99EEDD
            if characterId == 9:
                chara_name = '小豆沢こはね'
                chara_color = 0xFF6699
            if characterId == 10:
                chara_name = '白石杏'
                chara_color = 0x00BBDD
            if characterId == 11:
                chara_name = '東雲彰人'
                chara_color = 0xFF7722
            if characterId == 12:
                chara_name = '青柳冬弥'
                chara_color = 0x0077DD
            if characterId == 13:
                chara_name = '天馬司'
                chara_color = 0xFFBB00
            if characterId == 14:
                chara_name = '鳳えむ'
                chara_color = 0xFF66BB
            if characterId == 15:
                chara_name = '草薙寧々'
                chara_color = 0x33DD99
            if characterId == 16:
                chara_name = '神代類'
                chara_color = 0xBB88EE
            if characterId == 17:
                chara_name = '宵崎奏'
                chara_color = 0xBB6688
            if characterId == 18:
                chara_name = '朝比奈まふゆ'
                chara_color = 0x8888CC
            if characterId == 19:
                chara_name = '東雲絵名'
                chara_color = 0xCCAA88
            if characterId == 20:
                chara_name = '暁山瑞希'
                chara_color = 0xDDAACC
            if characterId == 21:
                chara_name = '初音ミク'
                chara_color = 0x33CCBB
            if characterId == 22:
                chara_name = '鏡音リン'
                chara_color = 0xFFCC11
            if characterId == 23:
                chara_name = '鏡音レン'
                chara_color = 0xFFEE11
            if characterId == 24:
                chara_name = '巡音ルカ'
                chara_color = 0xFFBBCC
            if characterId == 25:
                chara_name = 'MEIKO'
                chara_color = 0xDD4444
            if characterId == 26:
                chara_name = 'KAITO'
                chara_color = 0x3366CC

            # If statement to determine card rarity
            if cardRarityType == 'rarity_1':
                rarity = '★1'
            if cardRarityType == 'rarity_2':
                rarity = '★2'
            if cardRarityType == 'rarity_3':
                rarity = '★3'
            if cardRarityType == 'rarity_4':
                rarity = '★4'
            if cardRarityType == 'rarity_birthday':
                rarity = 'BD'

            # If statement to determine attribute emoji
            if attr == 'cool':
                attribute = '<:AttrCool:1262788363522539723>'
            if attr == 'cute':
                attribute = '<:AttrCute:1262788381595795456>'
            if attr == 'happy':
                attribute = '<:AttrHappy:1262788403204849724>'
            if attr == 'mysterious':
                attribute = '<:AttrMysterious:1262788421190160404>'
            if attr == 'pure':
                attribute = '<:AttrPure:1262788439967793345>'

            # If statement to determine support unit if applicable
            if supportUnit != 'none':
                if supportUnit == 'light_sound':
                    subunit = '<:UnitLN:1262790965459026071>' 
                if supportUnit == 'idol':
                    subunit = '<:UnitMMJ:1262790991715373146>'
                if supportUnit == 'street':
                    subunit = '<:UnitVBS:1262791074498482226>'
                if supportUnit == 'theme_park':
                    subunit = '<:UnitWXS:1262791090810126386>'
                if supportUnit == 'school_refusal':
                    subunit = '<:UnitN25:1262791008408571944>'
            else:
                subunit = ''

            # If statement to determine max card skill
            if skillId == 1:
                skill = '5秒間 スコアが40%UPする'
            elif skillId == 2:
                skill = '5秒間 スコアが50%UPする'
            elif skillId == 3:
                skill = '5秒間 スコアが80%UPする'
            elif skillId == 4:
                skill = '5秒間 スコアが120%UPする'
            elif skillId == 5:
                skill = '6秒間 GREATがPERFECTになり、5秒間 スコアが30％UPする'
            elif skillId == 6:
                skill = '6.5秒間 GOOD以上がPERFECTになり、5秒間 スコアが60％UPする'
            elif skillId == 7:
                skill = '7秒間 BAD以上がPERFECTになり、5秒間 スコアが100％UPする'
            elif skillId == 8:
                skill = 'ライフが300回復し、5秒間 スコアが30%UPする'
            elif skillId == 9:
                skill = 'ライフが400回復し、5秒間 スコアが60%UPする'
            elif skillId == 10:
                skill = 'ライフが500回復し、5秒間 スコアが100%UPする'
            elif skillId == 11:
                skill = '5秒間 PERFECTのときのみスコアが130%UPする'
            elif skillId == 12:
                skill = '5秒間 発動時ライフが800未満ならスコアが90%UP、 800以上ならスコアが120%UP、更にライフが10増加毎に+1%UPする（最大140%)'
            elif skillId == 13:
                skill = '5秒間 スコアが90％UP、 GOOD以下を出すまではスコアが140％UPする'
            elif skillId == 14:
                skill = 'ライフが850回復し、5秒間 PERFECTのときのみスコアが80%UPする'
            elif skillId == 15:
                skill = '5秒間 スコアが100%UPする 自身を除き「Leo/need」メンバーを1人編成する毎にスコアが10%UPし、全員一致で更に10%UPする（最大150%)'
            elif skillId == 16:
                skill = '5秒間 スコアが100%UPする 自身を除き「MORE MORE JUMP！」メンバーを1人編成する毎にスコアが10%UPし、全員一致で更に10%UPする（最大150%)'
            elif skillId == 17:
                skill = '5秒間 スコアが100%UPする 自身を除き「Vivid BAD SQUAD」メンバーを1人編成する毎にスコアが10%UPし、全員一致で更に10%UPする（最大150%)'
            elif skillId == 18:
                skill = '5秒間 スコアが100%UPする 自身を除き「ワンダーランズ×ショウタイム」メンバーを1人編成する毎にスコアが10%UPし、全員一致で更に10%UPする（最大150%)'
            elif skillId == 19:
                skill = '5秒間 スコアが100%UPする 自身を除き「25時、ナイトコードで。」メンバーを1人編成する毎にスコアが10%UPし、全員一致で更に10%UPする（最大150%)'
            elif skillId == 22:
                skill = '*crscorer*'
            elif skillId == 23:
                skill = '*rngscorer*'
            elif skillId == 24:
                skill = '*mixedscorer*'
            else:
                skill = 'unknown'

            # Get card image from sekai.best and send Discord embed
            if cardRarityType == 'rarity_1' or cardRarityType == 'rarity_2' or cardRarityType == 'rarity_birthday':
                embed_image = f"https://storage.sekai.best/sekai-jp-assets/character/member/{assetbundleName}_rip/card_normal.png"
                embed_thumbnail = f"https://storage.sekai.best/sekai-jp-assets/thumbnail/chara_rip/{assetbundleName}_normal.png"

                if not (await check_image_exists(embed_image) and await check_image_exists(embed_thumbnail)):
                    print(f"Images not found for card ID: {id}. Retrying in 10 seconds...")
                    await asyncio.sleep(10)
                    continue

                embed = discord.Embed(
                title=f"{rarity} {attribute} [{prefix}] {chara_name}{subunit}",
                description=f"<t:{int(releaseAt/1000)}>",
                color=chara_color,
                timestamp=datetime.now(),
                )
                embed.set_image(url=embed_image)
                embed.set_thumbnail(url=embed_thumbnail)
                embed.set_footer(text='card_normal')
                embed.add_field(
                    name=cardSkillName,
                    value=skill,
                    inline=False
                )
                await channel.send(embed=embed)
                print(f"Card Embed sent for card ID: {id}")
                break

            elif cardRarityType == 'rarity_3' or cardRarityType == 'rarity_4':
                embed_image_normal = f"https://storage.sekai.best/sekai-jp-assets/character/member/{assetbundleName}_rip/card_normal.png"
                embed_thumbnail_normal = f"https://storage.sekai.best/sekai-jp-assets/thumbnail/chara_rip/{assetbundleName}_normal.png"
                embed_image_after_training = f"https://storage.sekai.best/sekai-jp-assets/character/member/{assetbundleName}_rip/card_after_training.png"
                embed_thumbnail_after_training = f"https://storage.sekai.best/sekai-jp-assets/thumbnail/chara_rip/{assetbundleName}_after_training.png"

                if not (await check_image_exists(embed_image_normal) and await check_image_exists(embed_thumbnail_normal)):
                    print(f"Normal images not found for card ID: {id}. Retrying in 10 seconds...")
                    await asyncio.sleep(10)
                    continue
                if not (await check_image_exists(embed_image_after_training) and await check_image_exists(embed_thumbnail_after_training)):
                    print(f"After Training images not found for card ID: {id}. Retrying in 10 seconds...")
                    await asyncio.sleep(10)
                    continue

                embed_normal = discord.Embed(
                title=f"{rarity} {attribute} [{prefix}] {chara_name}{subunit}",
                description=f"<t:{int(releaseAt/1000)}>",
                color=chara_color,
                timestamp=datetime.now(),
                )
                embed_normal.set_image(url=embed_image_normal)
                embed_normal.set_thumbnail(url=embed_thumbnail_normal)
                embed_normal.set_footer(text='card_normal')
                embed_normal.add_field(
                    name=cardSkillName,
                    value=skill,
                    inline=False
                )
                await channel.send(embed=embed_normal)
                print(f"Card Normal Embed sent for card ID: {id}")

                embed_after_training = discord.Embed(
                title=f"{rarity} {attribute} [{prefix}] {chara_name}{subunit}",
                description=f"<t:{int(releaseAt/1000)}>",
                color=chara_color,
                timestamp=datetime.now(),
                )
                embed_after_training.set_image(url=embed_image_after_training)
                embed_after_training.set_thumbnail(url=embed_thumbnail_after_training)
                embed_after_training.set_footer(text='card_after_training')
                embed_after_training.add_field(
                    name=cardSkillName,
                    value=skill,
                    inline=False
                )
                await channel.send(embed=embed_after_training)
                print(f"Card After Training Embed sent for card ID: {id}")
                break

        except Exception as e:
            print(f"An error occurred: {e}. Retrying in 10 seconds...")
            await asyncio.sleep(10)
            continue

# Start the bot
async def run_bot():
    await load_extensions()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(run_bot())

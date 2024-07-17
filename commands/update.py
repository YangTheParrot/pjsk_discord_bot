import discord
from discord import app_commands
from discord.ext import commands
import os
from bot import check_for_en_updates, check_for_jp_updates

class UpdateDatabase(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def owner_only(interaction: discord.Interaction):
        return interaction.user.id == int(os.getenv('BOT_OWNER'))

    @app_commands.command(name='update', description='Force a database update in case it stops doing it by itself idk (Owner Only)')
    @app_commands.describe(lang='game version')
    @app_commands.choices(lang=[
        app_commands.Choice(name="EN", value="EN"),
        app_commands.Choice(name="JP", value="JP"),
    ])
    @app_commands.check(owner_only)
    async def update(self, interaction: discord.Interaction, lang: str):
        if lang == 'EN':
            await check_for_en_updates()
        elif lang == 'JP':
            await check_for_jp_updates()
        await interaction.response.send_message(f"Database manually updated for {lang}", ephemeral=True)
        print(f"Database manually updated for {lang}")
    
    @update.error
    async def update_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("Only the bot owner can run this command.", ephemeral=True)
            print("Only the bot owner can run this command.")

async def setup(bot):
    await bot.add_cog(UpdateDatabase(bot))
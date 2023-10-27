import asyncio
import datetime
import inspect
import os

from src.bot import DiscordBot
from nextcord import Color
from nextcord import Interaction, Embed, slash_command
from nextcord.ext import commands
from .components.scripts.leaderboard import create_leaderboard_display
from .components.scripts.profile import create_profile_display
from .components.scripts.session import Session

from src.extra.scripts.colored_printing import colorized_print


class StarCitCog(commands.Cog):
    def __init__(self, bot: DiscordBot):

        self.active_sessions: list[Session] = []
        self.bot: DiscordBot = bot
        self.name = "Star Citizen"

        colorized_print("COG", "SCCog connected")


    async def update(self):
        pass


    @slash_command(dm_permission=False, name="leaderboard", description=f"Star Citizen: View the profits leaderboard")
    async def leaderboard(self, interaction: Interaction):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")
        await interaction.response.send_message(embed=await create_leaderboard_display(self.bot))


    @slash_command(dm_permission=False, name="profile", description=f"Star Citizen: View your profile info")
    async def profile(self, interaction: Interaction):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")
        await interaction.response.send_message(embed=await create_profile_display(self.bot, interaction.user))


    @slash_command(dm_permission=False, name="new_session", description=f"Star Citizen: Create a new session")
    async def session_starter(self, interaction: Interaction):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")

        new_session = Session(interaction, self.bot)
        await new_session.startup()

        self.active_sessions.append(new_session)


    @slash_command(dm_permission=False, name="sc_settings", description=f"Star Citizen: Display the current Star Citizen related settings")
    async def sc_settings(self, interaction: Interaction):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")
        guild_settings = await self.bot.get_settings(interaction.guild.id, "sc_settings")
        embed = Embed(title=f"{interaction.guild.name} SC Settings", color=Color.blurple())
        embed.set_thumbnail(url=interaction.guild.icon.url)
        
        highlighter = "➖➖➖"
        cargo_settings = ""
        cargo_settings += f" • Max Crew Size: `{guild_settings[1]}`\n"
        cargo_settings += f" • Max Session Count: `{guild_settings[2]}`\n"
        cargo_settings += f" • Bonus Rate: `{guild_settings[3]}`\n"
        embed.add_field(name=f"{highlighter}{'Cargo Sessions'}{highlighter}", value=cargo_settings, inline=False)
        
        additional_settings = ""
        additional_settings += f" • AutoRank: `{False}`\n"
        additional_settings += f" • Debug: `{False}`\n"
        embed.add_field(name=f"{highlighter}{'Additional Settings'}{highlighter}", value=additional_settings, inline=False)

        await interaction.response.send_message(embed=embed)


    @slash_command(dm_permission=False, name="set_crew_size", description=f"Star Citizen: Set the crew size limit default is `0, (no limit)`")
    async def set_crew_size(self, interaction: Interaction, limit: int):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")

        guild_settings = await self.bot.get_settings(interaction.guild.id, "sc_settings")
        if limit >= 0:
            await  DiscordBot.sql.execute("UPDATE sc_settings SET MaxCrewSize = ? WHERE GuildID = ?", limit, interaction.guild.id)
            if limit == 0:
                embed = Embed(title="Max crew size set", description=f"Max crew size: `UNLIMITED`", color=Color.green())
            else:
                embed = Embed(title="Max crew size set", description=f"Max crew size: `{limit}`", color=Color.green())
        else:
            embed = Embed(title="Max crew size Not Set", description=f"Max crew size: `{guild_settings[1]}`", color=Color.red())

        await interaction.response.send_message(embed=embed)


    @slash_command(dm_permission=False, name="set_session_size", description=f"Star Citizen: Set the session size limit default is `0, (no limit)`")
    async def set_session_size(self, interaction: Interaction, limit: int):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")

        guild_settings = await self.bot.get_settings(interaction.guild.id, "sc_settings")
        if limit >= 0:
            await  DiscordBot.sql.execute("UPDATE sc_settings SET MaxSessionCount = ? WHERE GuildID = ?", limit, interaction.guild.id)
            if limit == 0:
                embed = Embed(title="Max session count set", description=f"Max session count: `UNLIMITED`", color=Color.green())
            else:
                embed = Embed(title="Max session count set", description=f"Max session count: `{limit}`", color=Color.green())
        else:
            embed = Embed(title="Max session count Not Set", description=f"Max session count: `{guild_settings[2]}`", color=Color.red())

        await interaction.response.send_message(embed=embed)


    @slash_command(dm_permission=False, name="set_bonus", description=f"Star Citizen: Set the bonus payout rate for the session owner")
    async def set_bonus(self, interaction: Interaction, rate: float):
        colorized_print("COMMAND", f"{interaction.user.name} used {self.__cog_name__}.{inspect.currentframe().f_code.co_name} at {datetime.datetime.now()}")

        if rate >= 0 and rate <= 1:
            await  DiscordBot.sql.execute("UPDATE sc_settings SET BonusRate = ? Where GuildID = ?", rate, interaction.guild.id)
            embed = Embed(title="Bonus Rate Set", description=f"Bonus rate: {rate * 100: .1f}%", color=Color.green())
        else:
            guild_settings = await self.bot.get_settings(interaction.guild.id, "sc_settings")
            embed = Embed(title="Bonus Rate Not Set", description=f"Bonus rate: {guild_settings[3]}%", color=Color.red())

        await interaction.response.send_message(embed=embed)


def setup(bot: DiscordBot):
    os.makedirs(f'{DiscordBot.paths["temp"]}/sc', exist_ok=True)
    asyncio.run( DiscordBot.sql.executescript("src/cogs/COG_starCitizen/components/sql/SCtables.sql"))
    cog = StarCitCog(bot)
    bot.add_cog(cog)
    bot.global_task_list.append((cog.update, ))
    

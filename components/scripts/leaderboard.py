from src.bot import DiscordBot
from nextcord import Color
from nextcord import Embed
from nextcord import User



async def create_leaderboard_display(bot:DiscordBot):
    result = await  DiscordBot.sql.execute("SELECT DisplayName, LifetimeProfit FROM users ORDER BY LifetimeProfit DESC")
    embed = Embed(title="Profits", description="Date range: `` - ``")
    
    member_str = ""
    for member in result:
        member_str += f" • {member[0]}: `{member[1]}`\n"

    embed.add_field(name="Members", value=member_str)
    return embed
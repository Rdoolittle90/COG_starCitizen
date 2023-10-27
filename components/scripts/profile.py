from nextcord import Color
from nextcord import Embed
from nextcord import User
import datetime
from src.cogs.starCitizen.components.scripts.plotter import plot_data

from src.bot import DiscordBot
from src.cogs.starCitizen.components.scripts.crew_member import CrewMember
from collections import defaultdict



async def create_profile_display(bot:DiscordBot, user: User):
    user_name = user.display_name
    title = f"{user.display_name}'s"
    if user_name.endswith("s"):
        title = f"{user.display_name}'"
    crew_member = CrewMember(bot, user)
    await crew_member.get_player_file()
    history = await  DiscordBot.sql.execute("SELECT Profits, DateOfProfit FROM profits WHERE DUID = ?", user.id)

     # Group by date and sum profits
    grouped_data = defaultdict(int)
    for profit, date in history:
        day = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f").date()
        grouped_data[day] += profit

    dates = list(grouped_data.keys())
    profit_values = list(grouped_data.values())
    cumulative_profit_values = [sum(profit_values[:i+1]) for i in range(len(profit_values))]

    img_url = plot_data(dates, cumulative_profit_values, user, title="Lifetime Profits over time", title_size=24, xlabel="Date", ylabel="aUEC")

    # Embed in discord
    embed = Embed(title=f"{title} profile", description=f"Rank: {None}", color=Color.brand_green())
    embed.set_author(name=user.display_name, icon_url=user.avatar.url)
    embed.set_image(url=img_url)
    embed.add_field(name="Life Profits", value=crew_member.life_profits, inline=True)
    embed.add_field(name="Best Session", value=crew_member.session_record, inline=True)

    return embed

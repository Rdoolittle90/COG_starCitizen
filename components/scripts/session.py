import asyncio
import datetime
from nextcord import Interaction, Embed, User, ButtonStyle, Color
import nextcord
from nextcord.ui import View, Button
from src.cogs.starCitizen.components.scripts.crew_roster import CrewRoster
from src.cogs.starCitizen.components.scripts.crew_member import CrewMember
from src.cogs.starCitizen.components.scripts.aUEC import aUEC
from src.bot import DiscordBot
from src.extra.scripts.easy_modal import EasyModal

from src.extra.scripts.colored_printing import colorized_print

 

class Session:
    session_id = 0
    button_id_counter = 0
    def __init__(self, interaction: Interaction, bot: DiscordBot) -> None:
        self.id = Session.session_id
        self.interaction = interaction
        self.bot = bot

        self.start = datetime.datetime.now()
        self.settings = None

        self.total_profit = 0
        
        self.owner: User = interaction.user
        self.crew_roster = CrewRoster(self.bot, interaction.guild.id)
        self.crew_logged = []
        self.view = View(timeout=None)
        self.final_view = View(timeout=None)

        self.trips = []

        self.create_buttons()


    def create_buttons(self):
        self.button_add_crew = Button(style=ButtonStyle.blurple, label="⏱️In", custom_id=f"Session_crew_add_{Session.button_id_counter}")
        self.view.add_item(self.button_add_crew)

        self.button_remove_crew = Button(style=ButtonStyle.red, label="⏱️Out", custom_id=f"Session_crew_remove_{Session.button_id_counter}")
        self.view.add_item(self.button_remove_crew)

        self.button_new_trip = Button(style=ButtonStyle.green, label="🖥️ Sell", custom_id=f"Session_trip_{Session.button_id_counter}")
        self.view.add_item(self.button_new_trip)

        # self.button_cash_out = Button(style=ButtonStyle.green, label="💵 Cash Out", custom_id=f"Session_cash_out_{Session.button_id_counter}", disabled=True)
        # self.view.add_item(self.button_cash_out)


    async def startup(self):
        self.settings = await self.bot.get_settings(self.interaction.guild.id, "sc_settings")
        Session.session_id += 1
        Session.button_id_counter += 1

        await self.crew_roster.add_active_crew(self.owner)
        
        crew_str = self.crew_roster.get_crew_str(self.crew_roster.active)
        embed = Embed(
            title=f"Session #{self.id}", 
            description=f"Seller bonus rate is set to: `{self.settings[3] * 100: .1f}% `", 
            color=Color.blurple(), 
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=self.owner.display_name, icon_url=self.owner.avatar.url)
        embed.add_field(name="Crew", value=crew_str, inline=False)

        colorized_print("INFO", f"Starting new session: #{self.session_id}")
        await self.interaction.send(content="", embed=embed, view=self.view)


        async def update(interaction: Interaction, warnings=None):
            embed = Embed(
                title=f"Session #{self.id}", 
                description=f"Seller bonus rate is set to: `{self.settings[3] * 100: .1f}% `", 
                color=Color.blurple(), 
                timestamp=datetime.datetime.now()
            )
            embed.set_author(name=self.owner.display_name, icon_url=self.owner.avatar.url)

            if len(self.trips) > 0:
                embed.add_field(name="Total Profits", value=f"`{aUEC(self.total_profit)}`")
                embed.add_field(name="Latest Profits", value=f"`{aUEC(self.trips[-1][0])}`")

            active_crew_str = self.crew_roster.get_crew_str(self.crew_roster.active)
            embed.add_field(name="Crew", value=active_crew_str, inline=False)

            if len(self.crew_roster.inactive) > 0:
                inactive_crew_str = self.crew_roster.get_crew_str(self.crew_roster.inactive)
                embed.add_field(name="Inactive Crew", value=inactive_crew_str, inline=False)

            try:
                await interaction.response.edit_message(content=warnings, embed=embed, view=self.view)
            except nextcord.errors.InteractionResponded:
                colorized_print("WARNING", "This interaction has already been responded to before")


        async def join_callback(interaction: Interaction):
            self.settings = await self.bot.get_settings(interaction.guild.id, "sc_settings")
            await self.crew_roster.add_active_crew(interaction.user)
            await update(interaction)


        async def leave_callback(interaction: Interaction):
            self.settings = await self.bot.get_settings(interaction.guild.id, "sc_settings")
            if interaction.user == self.owner:
                colorized_print("FAIL", f"{interaction.user.name} tried to leave but is the owner of the session {datetime.datetime.now()}")
                return
            self.crew_roster.remove_active_crew(interaction.user)
            await update(interaction, "Must transfer session before leaving!")


        async def new_trip_callback(interaction: Interaction):
            self.settings = await self.bot.get_settings(interaction.guild.id, "sc_settings")
            if interaction.user != self.owner:
                colorized_print("FAIL", f"{interaction.user.name} tried to initiate a sale but is not the session owner {datetime.datetime.now()}")
                return
            await interaction.response.send_modal(modal=EasyModal(f"Trip #{len(self.trips) + 1}", profit_modal_callback, Profit=0))
            await update(interaction)


        async def profit_modal_callback(interaction: Interaction, entries):
            trip = await self.crew_roster.pay_crew(self.owner, entries)
            self.trips.append(trip)
            self.total_profit += trip[0]
            await update(interaction)


        async def cash_out_callback(interaction: Interaction):
            if interaction.user != self.owner:
                colorized_print("COMMAND", f"{interaction.user.name} tried to cash out but is not the session owner {datetime.datetime.now()}")
                return
            
            await update(interaction)


        self.button_add_crew.callback = join_callback
        self.button_remove_crew.callback = leave_callback
        self.button_new_trip.callback = new_trip_callback
        # self.button_cash_out.callback = cash_out_callback

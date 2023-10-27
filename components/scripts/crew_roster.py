from src.bot import DiscordBot
from src.cogs.starCitizen.components.scripts.aUEC import aUEC
from src.cogs.starCitizen.components.scripts.crew_member import CrewMember
from nextcord import User


class CrewRoster:
    def __init__(self, bot:DiscordBot, guildID) -> None:
        self.bot = bot
        self.guildID = guildID
        self.active: list[CrewMember] = []
        self.inactive: list[CrewMember] = []
        self.max_crew_size = 0


    def find_crew_member(self, user: User, crew_list: list[CrewMember]):
        for crew_member in crew_list:
            if crew_member.id == user.id:
                return crew_member
        return None


    def remove_active_crew(self, user: User):
        crew_in_active = self.find_crew_member(user, self.active)
        if crew_in_active:
            self.active.remove(crew_in_active)
            self.inactive.append(crew_in_active)


    async def add_active_crew(self, user: User):
        await self.get_settings()
        crew_in_inactive = self.find_crew_member(user, self.inactive)
        if crew_in_inactive:
            self.inactive.remove(crew_in_inactive)
            self.active.append(crew_in_inactive)
        else:
            crew_in_active = self.find_crew_member(user, self.active)
            if not crew_in_active:
                new_crew = CrewMember(self.bot, user)
                await new_crew.get_player_file()
                await new_crew.increment_session()
                self.active.append(new_crew)


    async def calculate_payment(self, entries):
        await self.get_settings()
        bonusRate = self.settings[3]
        total = 0
        for item in entries:
            if item.label == "Profit":
                profit = int(item.value)
                total += profit

        bonus = profit * bonusRate
        profit -= bonus
        
        split = profit / len(self.active)
        split_change = split % 1
        split -= split_change

        bonus += (split_change * len(self.active))

        return total, split, bonus


    async def pay_crew(self, seller: User, entries):
        total, split, bonus = await self.calculate_payment(entries)

        for member in self.active:
            payment = split
            if member.id == seller.id:
                payment += bonus
            await member.pay(payment)

        crew_str = self.get_crew_str(self.active)
        return total, crew_str


    async def get_settings(self):
        self.settings = await self.bot.get_settings(self.guildID, "sc_settings")
        self.max_crew_size = self.settings[1]


    def get_crew_str(self, crew_list: list[CrewMember]):
        crew_str = ""
        for crew in crew_list:
            crew_str += str(crew)
        return crew_str

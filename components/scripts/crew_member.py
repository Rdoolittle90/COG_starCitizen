import datetime
from nextcord import User
from src.cogs.starCitizen.components.scripts.aUEC import aUEC
from src.extra.scripts.colored_printing import colorized_print
from src.bot import DiscordBot



class CrewMember:
    def __init__(self, bot: DiscordBot, user: User) -> None:
        self.bot = bot

        self.id = user.id
        self.display_name = user.display_name
        self.avatar_url = user.avatar.url

        self.life_profits:aUEC = aUEC(0)
        self.session_record:aUEC = aUEC(0)
        self.session_counter = 0
        self.trip_counter = 0

        self.session_profits = aUEC(0)
        

    async def get_player_file(self):
        # Checking if user already exists in the database
        exists = await  DiscordBot.sql.execute("SELECT * FROM users WHERE DUID = ?", self.id)
        if exists:
            result = await  DiscordBot.sql.execute("SELECT LifetimeProfit, SessionRecord, SessionCounter FROM users WHERE DUID = ?", self.id)
            result = result[0]
            self.life_profits = aUEC(result[0])
            self.session_record = aUEC(result[1])
            self.session_counter = result[2]
        else:
            await self.new_player_file()
    

    async def save_player_file(self):
        # Checking if user already exists in the database
        exists = await  DiscordBot.sql.execute("SELECT DisplayName FROM users WHERE DUID = ?", self.id)
        if exists:
            # Updating user details if they already exist
            await  DiscordBot.sql.execute(
                "UPDATE users SET LifetimeProfit = ?, SessionRecord = ?, SessionCounter = ? WHERE DUID = ?", 
                int(self.life_profits),
                int(self.session_record),
                self.session_counter,
                self.id
            )
        else:
            # Inserting new user details if they don't exist
            await  DiscordBot.sql.execute(
                "INSERT INTO users (DUID, DisplayName, AvatarURL, LifetimeProfit, SessionRecord, SessionCounter) VALUES (?, ?, ?, ?, ?, ?)",
                self.id,
                self.display_name,
                self.avatar_url,
                int(self.life_profits),
                int(self.session_record),
                self.session_counter
            )
    

    async def new_player_file(self):
        await  DiscordBot.sql.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", 
            self.id, 
            self.display_name,
            None,
            self.avatar_url,
            int(self.life_profits),
            int(self.session_record), 
            self.session_counter
        )
        self.life_profits = aUEC(0)
        self.session_record = aUEC(0)
        self.session_counter = 0
        await self.save_player_file()


    async def increment_session(self):
        """Increment the session counter by 1 and save the changes."""
        if self.session_counter is None:
            self.session_counter = 0
        self.session_counter += 1
        await self.save_player_file()
  

    async def update_profits(self, earnings):
        await  DiscordBot.sql.execute(
            "INSERT INTO profits VALUES (?, ?, ?, ?, ?)", 
            self.id,
            self.session_counter,
            self.trip_counter,
            earnings, 
            datetime.datetime.now()
        )
        self.trip_counter += 1
        

    async def pay(self, earnings):
        colorized_print("CONN", f"Paying {self.display_name}: {earnings}")
        self.life_profits += earnings
        self.session_profits += earnings
        if not self.session_record or earnings > self.session_record:
            self.session_record = earnings
        await self.update_profits(earnings)
        await self.save_player_file()


    def __eq__(self, other):
        if self.id == other.id:
            return True
        else:
            return False


    def __int__(self):
        return self.id


    def __str__(self):
        return f" • {self.display_name}: `{aUEC(self.session_profits)}`\n"

CREATE TABLE IF NOT EXISTS sc_settings (
    GuildID INTEGER PRIMARY KEY NOT NULL,
    MaxCrewSize INTEGER DEFAULT 0,
    MaxSessionCount INT DEFAULT 3,
    BonusRate FLOAT DEFAULT 0.05
);

CREATE TABLE IF NOT EXISTS users (
    DUID INTEGER NOT NULL,
    DisplayName VARCHAR(64),
    Handle VARCHAR(64),
    AvatarURL VARCHAR(128),
    LifetimeProfit INTEGER DEFAULT 0,
    SessionRecord INTEGER DEFAULT 0,
    SessionCounter INTEGER DEFAULT 0,
    PRIMARY key (DUID)
);

CREATE TABLE IF NOT EXISTS profits (
    DUID INTEGER NOT NULL,
    SessionNum INTEGER NOT NULL,
    TripNum INTEGER NOT NULL,
    Profits INTEGER NOT NULL,
    DateOfProfit DATE,
    PRIMARY key (DUID, SessionNum, TripNum)
);

CREATE TABLE IF NOT EXISTS buyers (
    LocationName VARCHAR(64) NOT NULL,
    ItemName VARCHAR(64) NOT NULL,
    Price INTEGER NOT NULL,
    PRIMARY key (LocationName, ItemName)
);
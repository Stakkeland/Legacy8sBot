
--create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    mp INTEGER,
    mp_wins INTEGER,
    mp_losses INTEGER,
    sr INTEGER,
    rank TEXT NOT NULL CHECK(rank IN ('Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'Grandmaster', 'Overlord')),
    location TEXT NOT NULL CHECK(location IN ('west', 'central', 'east', 'eu', 'china', 'australia', 'south america', 'africa', 'unknown'))
);


drop table users;

select * from users;

-- update my account rank from Bronze to Overlord
UPDATE users
SET rank = 'Overlord'
WHERE id = 375491129598148608;
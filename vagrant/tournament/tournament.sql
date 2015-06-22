-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE matches (
    id serial PRIMARY KEY,
    winner_id int references players,
    challenger_id int references players,
    tie boolean default NULL
);

-- table of player's id and played opponent's id
CREATE VIEW opponents AS (
    SELECT players.id, matches.challenger_id
    FROM players
    JOIN matches
        ON matches.winner_id = players.id
    UNION
    SELECT players.id, matches.winner_id AS challenger_id
    FROM players
    JOIN matches
        ON matches.challenger_id = players.id
);

-- table of player's number of wins, matches, and ties
CREATE VIEW standings AS (
    SELECT
        players.id,
        players.name,
        COUNT(
            CASE WHEN matches.tie IS NULL
              AND matches.winner_id = players.id
                THEN 1
                ELSE NULL
            END) AS wins,
        COUNT(matches.id) AS matches,
        COUNT(
            CASE WHEN matches.tie IS NOT NULL
                THEN 1
                ELSE NULL
            END) AS ties
    FROM players
    LEFT JOIN matches
        ON matches.winner_id = players.id
        OR matches.challenger_id = players.id
    GROUP BY players.id
    ORDER BY wins DESC, ties DESC, matches, players.id
);

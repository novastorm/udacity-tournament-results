#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    dbh = connect()
    sth = dbh.cursor()
    sth.execute("TRUNCATE TABLE matches")
    dbh.commit()
    dbh.close()


def deletePlayers():
    """Remove all the player records from the database."""
    dbh = connect()
    sth = dbh.cursor()
    sth.execute("TRUNCATE TABLE players CASCADE")
    dbh.commit()
    dbh.close()


def countPlayers():
    """Returns the number of players currently registered."""
    dbh = connect()
    sth = dbh.cursor()
    sth.execute("SELECT count(players) FROM players")
    result = sth.fetchone()
    dbh.commit()
    dbh.close()

    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    dbh = connect()
    sth = dbh.cursor()
    query = "INSERT INTO players (name) VALUES (%s)"
    values = [name]
    sth.execute(query, values)
    dbh.commit()
    dbh.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    dbh = connect()
    sth = dbh.cursor()
    query = '''
        SELECT
            players.id,
            players.name,
            COUNT(CASE WHEN matches.winner_id = players.id THEN 1 ELSE NULL END) AS wins,
            COUNT(matches.id) AS matches
        FROM players
        LEFT JOIN matches
            ON matches.winner_id = players.id
            OR matches.challenger_id = players.id
        GROUP BY players.id
        '''
    sth.execute(query)
    result = sth.fetchall()
    dbh.commit()
    dbh.close()
    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    dbh = connect()
    sth = dbh.cursor()
    query = "INSERT INTO matches (winner_id, challenger_id) VALUES (%s, %s)"
    values = [winner, loser]
    sth.execute(query, values)
    dbh.commit()
    dbh.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """



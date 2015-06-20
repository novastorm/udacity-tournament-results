#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import pprint

pp = pprint.PrettyPrinter(indent=4)


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
        '''
    sth.execute(query)
    result = sth.fetchall()
    dbh.commit()
    dbh.close()
    return result


def reportMatch(winner, loser, tied=None):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    dbh = connect()
    sth = dbh.cursor()
    query = "INSERT INTO matches (winner_id, challenger_id, tie) VALUES (%s, %s, %s)"
    values = [winner, loser, tied]
    sth.execute(query, values)
    dbh.commit()
    dbh.close()

def __getPlayerOpponents():
    """Returns list of opponents for all players
    """
    dbh = connect()
    sth = dbh.cursor()
    query = '''
        WITH opponents AS (
            SELECT players.id, players.name, challenger_id
            FROM players
            JOIN matches
                ON matches.winner_id = players.id
            UNION
            SELECT players.id, players.name, winner_id AS challenger_id
            FROM players
            JOIN matches
                ON matches.challenger_id = players.id
        )
        SELECT
            opponents.id,
            opponents.name,
            array_agg(challenger_id) AS challenger_id_list
        FROM opponents
        GROUP BY opponents.id, opponents.name
        '''
    sth.execute(query)
    result = sth.fetchall()
    dbh.commit()
    dbh.close()

    return result

def __getStandingGroups():
    """Returns a list of standings grouped by win, tie, loss

    Assuming standings are provided ordered by win, tie, loss, each standings
    group contains players with equivalent standings

    Returns:
      A list of sets, each of which contains ()
    """
    standings = playerStandings()

    standings_groups = []
    group = set()
    # set initial standings
    (win, tie, loss) = standings[0][2:5]
    for player in standings:
        # test if player standings does not match current standings
        if ((win, tie, loss) != player[2:5]):
            # append current player group to the standings group
            standings_groups.append(group.copy())
            # set new standings
            (win, tie, loss) = player[2:5]
            # reset group
            group.clear()
        # add (player id, player name) to group of players
        group.add(player[0:2])
    # add last group to standings_groups
    standings_groups.append(group.copy())

    return standings_groups

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

    # reduce opponents to a dictionary of player_id and the set of their
    # previously played opponent_id
    opponents = {}
    for (id, name, cid_list) in __getPlayerOpponents():
        opponents[id] = set(cid_list)

    print("opponents")
    pp.pprint(opponents)

    standings_groups = __getStandingGroups()
    print("standings_groups")
    pp.pprint(standings_groups)

    pending_players = set()
    pending_players.update(set(standings_groups.pop(0)))
    pairs = []
    player = None
    challenger = None
    while len(pending_players) > 0:
        print "pending_players"
        pp.pprint(pending_players)
        player = pending_players.pop()
        # if pending players == 1 add players from next group
        if len(pending_players) == 0 and len(standings_groups) > 0:
                pending_players.update(set(standings_groups.pop(0)))
        challenger = pending_players.pop()
        if len(pending_players) == 0 and len(standings_groups) > 0:
                pending_players.update(set(standings_groups.pop(0)))

        print "player info", player
        print opponents[player[0]]
        if challenger[0] in opponents[player[0]]:
            print "*** find new challenger ***"
            new_challenger = pending_players.pop()
            pending_players.add(challenger)
            challenger = new_challenger

        print "player, challenger", (player, challenger)
        pairs.append((player[0], player[1], challenger[0], challenger[1]))
        print "pairs"
        pp.pprint(pairs)

    # pairing every other record by spliting standings into two lists,
    # one of even elements, the other of odd elements. zip together the
    # results and map to create the output format
    # result = map(lambda (x, y) : (x[0], x[1], y[0], y[1]),
    #     zip(standings[0::2],standings[1::2]))


    return pairs


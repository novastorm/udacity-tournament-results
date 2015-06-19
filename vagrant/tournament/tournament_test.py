#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *
import pprint

pp = pprint.PrettyPrinter(indent=4)

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 5:
        raise ValueError("Each playerStandings row should have five columns.")
    [(id1, name1, wins1, matches1, ties1), (id2, name2, wins2, matches2, ties2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    registerPlayer("Gillian Jewelsteel")
    registerPlayer("Donner Greystalker")
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    reportMatch(id5, id6, True)
    standings = playerStandings()
    # pp.pprint(standings)
    for (i, n, w, m, t) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and t == 0 and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        if i in (id2, id4) and t == 0 and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
        elif i in (id5, id6) and t != 1:
            raise ValueError("Each tied match player should have one tie recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    registerPlayer("Daimbert Oxcloud")
    registerPlayer("Elaisse Gemkiss")
    registerPlayer("Swift Felblade")
    registerPlayer("Stella Icewind")
    standings = playerStandings()
    # pp.pprint(standings)
    pairings = swissPairings()
    # pp.pprint(pairings)
    [id1, id2, id3, id4, id5, id6, id7, id8] = [row[0] for row in standings]
    pairings = swissPairings()
    pp.pprint(pairings)
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    reportMatch(id5, id6, True)
    reportMatch(id7, id8, True)
    standings = playerStandings()
    # pp.pprint(standings)

    reportMatch(id1, id3)
    pairings = swissPairings()
    pp.pprint(pairings)


    if len(pairings) != 4:
        raise ValueError(
            "For eight players, swissPairings should return four pairs.")
    [
        (pid1, pname1, pid2, pname2),
        (pid3, pname3, pid4, pname4),
        (pid5, pname5, pid6, pname6),
        (pid7, pname7, pid8, pname8)
    ] = pairings
    correct_pairs = set([
        frozenset([id1, id3]),
        frozenset([id5, id6]),
        frozenset([id7, id8]),
        frozenset([id2, id4])
        ])
    actual_pairs = set([
        frozenset([pid1, pid2]),
        frozenset([pid3, pid4]),
        frozenset([pid5, pid6]),
        frozenset([pid7, pid8])
        ])
    pp.pprint(correct_pairs)
    pp.pprint(actual_pairs)
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success!  All tests pass!"



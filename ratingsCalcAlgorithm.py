import math

#formulas from http://math.bu.edu/people/mg/ratings/rs/rs2.html

#creates player object for testing (can be overhauled later)
class player:
    def __init__(self, name, rating, n, age, peak, allWins, WSRS, USCF, FIDE, CFC, score):
        self.name = name
        self.rating = rating
        self.n = n
        self.peak = peak
        self.allWins = allWins
        self.WSRS = WSRS
        self.USCF = USCF
        self.FIDE = FIDE
        self.CFC = CFC
        self.age = age
        self.score = score

#number of games in the event (m)
m = 4

#creates example players for testing
playerList = []
playerList.append(player("Khalil, Tayseer", 1829, 45, 15, 0, 0, 0, 0, 0, 0, ["W3","W4","L2","W5"]))
playerList.append(player("Doncaster, Cannon", 1718, 64, 15, 0, 0, 0, 0, 0, 0, ["L4","W5","W1","B"]))
playerList.append(player("Chung, Ethan", 1618, 296, 15, 0, 0, 0, 0, 0, 0, ["L1","B","L5","W4"]))
playerList.append(player("Carman, Leif", 1537, 263, 15, 0, 0, 0, 0, 0, 0, ["W2","L1","B","L3"]))
playerList.append(player("Palm, Caleb", 1500, 156, 15, 0, 0, 0, 0, 0, 0, ["B","L2","W3","L1"]))

#set initial rating for unrated players
def unratedRating(player):
    if (player.FIDE > 0):
        if(player.FIDE > 2150):
            player.n = 10
        if(player.FIDE <= 2150):
            player.n = 5
        return player.FIDE + 50
    if (player.CFC > 0):
        if (player.CFC > 1500):
            player.n = 5
            return (player.CFC * 1.1) - 240
        if (player.CFC <= 1500):
            player.n = 0
            return player.CFC - 90
    #fix: need to add QC ratings to set players rating = QC rating if international unavailable
    #fix: need to add check to set player rating to 750 if no international rating or age info
    else:
        if(player.age <= 4 and player.age <= 20):
            return 300 + 50 * player.age
        else:
            return 1300
#calculates N
def effectiveGames(player):
    if (player.rating > 2200):
        return min(50, player.n)
    else:
        return min(50/(math.sqrt(1 + (2200.0 - player.rating)**2/100000)), player.n)

#formula for finding K (note: the formula changes when finding full or half K)
def calculateK(N, M):
    #fix: need to determine when to use full or half K (not specified in report)
    if (M < 3):
        return 400/(N+M/2.0)
    else:
        return 800/(N+M)

#formula for win expectancy of player with rating R and opponent with rating R2
def winningE(R, R2):
    return 1/(1+10.0**(-(R - R2)/400.0))

#calculate provisional winning expectancy
def pWE(R, R2):
    if (R <= R2 - 400):
        return 0
    if (R > R2 - 400 and R < R2 + 400):
        return .5 + (R - R2)/800.0
    if (R >= R2 - 400):
        return 1

#adjusts rating for floor based on highest rating
def ratingFloor(i):
    floor = 100
    if(i >= 1600 and i <= 2300):
        floor = (i/100)*100-200
    return floor

def main():
    # loops through all players in the tournament and calculates their new ratings
    for player in playerList:
        M = m
        print(player.name)
        #rates unrated players
        if (player.rating == 0):
            player.rating = unratedRating(player)
        newRating = player.rating
        #calculates number of effective games (N)
        N = effectiveGames(player)
        #runs through all of the player's games and generates new rating
        if (N > 8):
            #S is the players score and E is the sum of the total winning expectancy against all opponents
            S = 0
            E = 0
            #adjusts S and E by running through all of a player's games
            for z in range(m):
                if (player.score[z][0:1] == "W"):
                    S = S + 1
                if (player.score[z][0:1] == "D"):
                    S = S+.5
                if (player.score[z][0:1] != "B"):
                    E = E + winningE(player.rating, playerList[(int(player.score[z][1:2])) - 1].rating)
                if (player.score[z][0:1] == "B"):
                    M = M - 1
            #calculates K
            K = calculateK(N, M)
            #fix: need to add a check that that makes this TRUE if any player plays the same opponent more than twice
            if (M < 3):
                newRating = player.rating + K*(S-E)
            if (M >= 3):
                newRating = player.rating + K*(S-E) + max(0, K*(float(S-E)) - 10.0*math.sqrt(max(M, 4.0)))
            #final rating needs to be rounded up to integer if player gained rating or down if player lost points
            if (newRating > player.rating):
                newRating = int(math.ceil(newRating))
            if (newRating < player.rating):
                newRating = int(math.floor(newRating))
        
        #for players without an established rating
        if (N <= 8 or player.allWins == 1 or player.allWins == 2):
            S = 0
            E = 0
            R2 = 0
            S2 = 0
            for z in range(m):
                if (player.score[z][0:1] == "W"):
                    S = S + 1
                if (player.score[z][0:1] == "D"):
                    S = S+.5
                if (player.score[z][0:1] != "B"):
                    E = E + pWE(player.rating, playerList[(int(player.score[z][1:2])) - 1].rating)
                if (player.score[z][0:1] == "B"):
                    M = M - 1
            if(player.allWins == 1):
                R2 = player.rating - 400
                S2 = S + N
            if(player.allWins == 2):
                R2 = player.rating + 400
                S2 = S
            if (player.allWins == 0):
                R2 = player.rating
                S2 = S + N/2.0
            #fix: still working on implementing the function iteratively as described in the paper
            newRating = N * pWE(player.rating, R2) + E - S2
        #calls rating floor method to determine if the current rating would be below the player's floor
        if (newRating < ratingFloor(player.peak)):
            newRating = ratingFloor(player.peak)
        print(player.rating, newRating)
        print("")

if __name__ == "__main__":
    main()
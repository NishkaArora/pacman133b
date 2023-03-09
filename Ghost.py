
import numpy as np
import time

class Ghost:
    def __init__(self, map, spawnPoint, pingTime, id) -> None:
        self.position = spawnPoint
        self.map = map
        self.prevMove = None
        self.lastPing = time.time()
        self.pingTime = pingTime
        self.pingAvailable = False
        self.id = id

    def update(self):
        validMoves = self.map.getValidMoves(self.position)
        x, y = self.position

        if len(validMoves) == 1:
            self.prevMove = validMoves[0]
            self.position = x + validMoves[0][0], y + validMoves[0][1]
            return validMoves[0]
        
        if not self.prevMove is None:
            # Don't go backwards if there is another option
            backwards = self.prevMove[0] * -1, self.prevMove[1] * -1
            if backwards in validMoves:
                validMoves.remove(backwards)

        if len(validMoves) == 1:
            self.position = x + validMoves[0][0], y + validMoves[0][1]
            self.prevMove = validMoves[0]
            return validMoves[0]
        
        possibleFutures = [(x + dx, y + dy) for (dx, dy) in validMoves]
        self.targetTile = self.map.getPacmanLocation()
        tx, ty = self.targetTile

        bestFuture = min(possibleFutures, key=lambda p: (p[0] - tx) ** 2 + (p[1] - ty) ** 2)
        bestIdx = possibleFutures.index(bestFuture)
        bestMove = validMoves[bestIdx]

        self.position = x + bestMove[0], y + bestMove[1]
        self.prevMove = bestMove

        return bestMove

    def updatePingStatus(self):
        self.pingAvailable = time.time() - self.lastPing > self.pingTime

    def getPing(self):
        self.lastPing = time.time()
        self.updatePingStatus()

        return (self.id, self.position) # Need to translate and add some varience
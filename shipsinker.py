#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, copy
from gameboard.board import Board
from gameboard.coordinate import Coordinate

class ShipSinker:
    """This is the class where all the magic happens. Given a board you should decide on a position to shoot at."""
    def make_move(self, board):
        intelligent_move = self.getIntelligentMove(board)
        if (intelligent_move):
            return intelligent_move
        else:
            return self.getIntelligentRandom(board)

    def getIntelligentMove(self, board):
        for y in range(board.size()):
            for x in range(board.size()):
                position = self.get(board, x, y)
                if (position and position["state"] == "Seaworthy"):
                    return self.sinkShip(board, position["coordinates"]["x"], position["coordinates"]["y"])

        return None

    def sinkShip(self, board, x, y):
        for neighbourX in [x-1, x, x+1]:
            for neighbourY in [y-1, y, y+1]:
                if (neighbourX >= 0 and neighbourY >= 0 
                    and neighbourX < board.size() and neighbourY < board.size()
                    and (neighbourX == x or neighbourY == y)
                    and not (neighbourY == y and neighbourX == x)):
                    position = self.get(board, neighbourX, neighbourY)
                    if (position and position["state"] == "Seaworthy"):
                        nextMove = self.pickNextMoveWhenWeKnowTwoSeaworthy(board, x, y, neighbourX, neighbourY)
                        if (nextMove):
                            return nextMove        
        return self.pickNeighbour(board, x, y)

    def weightBoard(self, board):
        weights = []
        for y in range(board.size()):
            weights.append([])
            for x in range(board.size()):
                weights[y].append(0)
        
        for y in range(board.size()):
            for x in range(board.size()):
                for ship in board.ships():
                    self._tryPlaceShipSouth(board, weights, ship, x, y)
                    self._tryPlaceShipEast(board, weights, ship, x, y)

        return weights
        
    def _tryPlaceShipSouth(self, board, weights, ship, x, y):
        for lookForY in range(y, y + ship["length"]):
            if (lookForY == board.size()):
                return
            if (self.get(board, x, lookForY)):
                return
        for shipY in range(y, y + ship["length"]):
            weights[x][shipY] += 1

    def _tryPlaceShipEast(self, board, weights, ship, x, y):
        for lookForX in range(x, x + ship["length"]):
            if (lookForX == board.size()):
                return
            if (self.get(board, lookForX, y)):
                return
        for shipX in range(x, x + ship["length"]):
            weights[shipX][y] += 1

    def pickNeighbour(self, board, x, y):
        potential = []
        for neighbourX in [x-1, x, x+1]:
            for neighbourY in [y-1, y, y+1]:
                if (neighbourX >= 0 and neighbourY >= 0 
                    and neighbourX < board.size() and neighbourY < board.size()
                    and (neighbourX == x or neighbourY == y)
                    and not self.get(board, neighbourX, neighbourY)):
                    potential.append(Coordinate(neighbourX, neighbourY))
        return potential.pop(random.randrange(len(potential)))

    def pickNextMoveWhenWeKnowTwoSeaworthy(self, board, x1, y1, x2, y2):
        potential = []
        first = self.getNextPotentialPosition(board, x1, y1, x2, y2, 1)
        if (first):
            potential.append(first)
        second = self.getNextPotentialPosition(board, x1, y1, x2, y2, -1)
        if (second):
            potential.append(second)
        if (len(potential) == 0):
            return None
        if (random.randrange(2) == 0):
            potential.reverse()
        return potential.pop(random.randrange(len(potential)))

    def getNextPotentialPosition(self, board, x1, y1, x2, y2, step):
        if (x1 == x2):
            stepX = 0
            stepY = step
        if (y1 == y2):
            stepX = step
            stepY = 0

        y = y1
        x = x1
        while True:
            x += stepX
            y += stepY
            if ((stepY > 0 and y == y2) or (stepX > 0 and x == x2)):
                continue
            if (x < 0 or y < 0 or x == board.size() or y == board.size()):
                return None
            position = self.get(board, x, y)
            if (not position):
                return Coordinate(x, y)
            if (position["state"] == "Seaworthy"):
                continue
            return None

    def getIntelligentRandom(self, board):
        weights = self.weightBoard(board)

        positions = self._getTopPositionsFromWeigths(weights)
        if (positions and len(positions) >= 1):
            return positions[random.randrange(len(positions))]

        while True:
            x = random.randrange(board.size())
            y = random.randrange(board.size())
            if (not self.get(board, x, y) and self._canActuallyContainAliveShip(board, x, y)):
                return Coordinate(x, y)

    def _getTopPositionsFromWeigths(self, weights):
        top = 0
        positions = []
        for y in range(len(weights)):
            for x in range(len(weights[y])):
                if (weights[x][y] > top):
                    top = weights[x][y]
                    positions = []
                
                if (weights[x][y] == top):
                    positions.append(Coordinate(x, y))
        return positions

    def _canActuallyContainAliveShip(self, board, x, y):
        smallestShip = 5
        for ship in board.ships():
            if (smallestShip > ship["length"]):
                smallestShip = ship["length"]

        horizontal = 1 + self._findPotentialShipPositions(board, x, y, 1, 0) + self._findPotentialShipPositions(board, x, y, -1, 0)
        vertical = 1 + self._findPotentialShipPositions(board, x, y, 0, 1) + self._findPotentialShipPositions(board, x, y, 0, -1)

        return (horizontal >= smallestShip or vertical >= smallestShip)

    def _findPotentialShipPositions(self, board, x, y, stepX, stepY):
        newX = x + stepX
        newY = y + stepY
        positions = 0
        while (newX >= 0 and newY >= 0
                and newX < board.size() and newY < board.size()
                and not self.get(board, newX, newY)):
            positions += 1
            newX = newX + stepX
            newY = newY + stepY
        return positions

    def get(self, board, x, y):
        for shot in board.shots():
            if (shot["coordinates"]["x"] == x and shot["coordinates"]["y"] == y):
                return shot
        return None
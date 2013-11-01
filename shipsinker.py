#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from gameboard.board import Board
from gameboard.coordinate import Coordinate

class ShipSinker:
    """This is the class where all the magic happens. Given a board you should decide on a position to shoot at."""
    def make_move(self, board):
        # You get a board-object.

        # Your job is to return a Position
        return Coordinate(random.randrange(board.size()), random.randrange(board.size()))
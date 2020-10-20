#!/usr/bin/env python3
"""
Core routines to solve sudoku

These use a 2 d array for the board with None for unknown cells and and 1 - 9 for the known (or under test)
values.

2 different classes with similar interfaces are provided,

Both classes use a contructor that defines the inital board, and a function that is called to solve the board.

When a valid solution is found, it is passed to a callback function

The method used allows all valid solutions to be found.
"""
import time

class sudoboardbrute():
    """
    A very simple pure brute force solver for sudoku.
    
    The solver scans the board for an unknown value cell, puts a test value in and calls itself. A solution is
    found when the board is valid and there are no unknown cells.
    """
    def __init__(self, board, dfunc, callall):
        self.board=board
        self.dfunc=dfunc
        self.callall=callall
        self.breakout=False
        self.startat=time.time()
        self.soltimes=[]

    def findEmpty(self):
        """find the first unknown value position"""
        for r, row in enumerate(self.board):
            try:
                c=row.index(None)
                return r,c
            except ValueError:
                pass
        return None

    def testValid(self, row, col, val):
        """
        return True if val is legal in current board at row, col
        """
        board=self.board
        if val in board[row]:
            return False
        for x in range(9):
            if board[x][col] == val:
                return False
        rbase=(row)//3*3
        cbase=(col)//3*3
        for r in range(rbase,rbase+3):
            if r != row:
                arow=board[r][cbase:cbase+3]
                if val in arow:
                    return False
        return True

    def sudsearch(self, nest):
        """
        given a game board it attempts to resolve unknown squares. It is used recursively
        It calls dfunc as each solution is found, and (if callall is True) as each value is tested
        """ 
        if self.breakout:
            return       
        rc=self.findEmpty()
        if rc is None:
            self.soltimes.append(time.time() - self.startat)
            if self.dfunc(self.board, btype='solution', nest=nest) is False:
                self.breakout=True
        else:
            testr, testc=rc
            for testv in range(1,10):
                if self.testValid(testr, testc, testv):
                    if self.callall:
                        if self.dfunc(self.board, btype='partial', nest=nest+1) is False:
                            self.breakout=True
                    self.board[testr][testc]=testv
                    self.sudsearch(nest+1)
            self.board[testr][testc]=None

class sudoboardsmart():
    """
    This is still primarily a brute force solver, but includes some simple optimizations.
    
    On each pass it creates a sorted list of unknown cells, sorted on the number of valid values
    (given the current board) for each unknown cell.
    
    If there are any cells that have only 1 possible value, then these values are set.
    
    If the board is still valid it recursively calls the solver
    
    If the board is now invalid it backtracks as an earlier test value must be wrong
    
    If there are no cells with only a single possible value it picks a cell with the fewest
    possible valid values and sets each value in turn and recursively calls itself.
    
    Once there are no unknown cells and the board is valid, we have a solution.
    """
    def __init__(self, board, dfunc, callall):
        self.board=board
        self.dfunc=dfunc
        self.callall=callall
        self.breakout=False
        self.startat=time.time()
        self.soltimes=[]
        self.freerowvals = [set([x for x in range(1,10) if not x in row]) for row in self.board]
        colordered = list(zip(*self.board))
        self.freecolvals = [set([x for x in range(1,10) if not x in col]) for col in colordered]
        self.freegroupvals=[]
        for yb in range(3):
            freegrouprow=[]
            for xb in range(3):
                niner=[]
                for yi in range(3):
                    niner += [self.board[yb*3+yi][xb*3+xi] for xi in range(3)]
                freegrouprow.append(set([x for x in range(10) if not x in niner]))
            self.freegroupvals.append(freegrouprow)

    def freelists(self):
        freecounts=[[] for _ in range(10)]
        count=0
        for y in range(9):
            for x in range(9):
                if self.board[y][x] is None:
                    freenums=self.freerowvals[y] & self.freecolvals[x] & self.freegroupvals[y//3][x//3]
                    freecounts[len(freenums)].append((y,x, freenums))
                    count += 1
        return None if count==0 else freecounts

    def setcell(self, row, col, val):
        try:
            self.freerowvals[row].remove(val)
        except KeyError:
            return False
        try:
            self.freecolvals[col].remove(val)
        except KeyError:
            self.freerowvals[row].add(val)
            return False
        try:
            self.freegroupvals[row//3][col//3].remove(val)
        except KeyError:
             self.freerowvals[row].add(val)
             self.freecolvals[col].add(val)
             return False
        self.board[row][col]=val
        return True

    def clearcell(self, row, col, val):
        self.board[row][col]=None
        self.freerowvals[row].add(val)
        self.freecolvals[col].add(val)
        self.freegroupvals[row//3][col//3].add(val)
        
    def sudsearch(self, nest):
        if self.breakout:
            return
        freecounts=self.freelists()
        if freecounts is None:
            self.soltimes.append(time.time()-self.startat)
            if self.dfunc(self.board, btype='solution', nest=nest+1) is False:
                self.breakout-True
            return
        if len(freecounts[0]) > 0:
            return
        if len(freecounts[1]) > 0:
            restore=[]
            for fix, fce in enumerate(freecounts[1]):
                fy, fx, freevals = fce
                val=freevals.pop()
                if not self.setcell(fy, fx, val):
                    for y,x,val in restore:
                        self.clearcell(y,x,val)
                    return
                restore.append((fy, fx, val))
            self.sudsearch(nest+1)
            for y,x,val in restore:
                self.clearcell(y,x,val)
            return
        for fc in range(2,10):
            if len(freecounts[fc]) > 0:
                break
        else:
            self.soltimes.append(time.time()-self.startat)
            if self.dfunc(self.board, btype='solution', nest=nest) is False:
                self.breakout=True
            return
        ty, tx, tfree=freecounts[fc].pop()
        for tryval in tfree:
            if self.setcell(ty,tx, tryval):
                self.sudsearch(nest+1)
                self.clearcell(ty,tx, tryval)

"""
housekeeping routines
"""
import os
def validgrid(grid):
    OK=True
    for rbase in range(0,9,3):
        for cbase in range(0,9,3): #cycle through the blocks of 9 numbers
            tdata=[]
            for r in range(rbase,rbase+3):
                for c in range(cbase,cbase+3): 
                    if not grid[r][c] is None:
                        tdata.append(grid[r][c])
            rc=[0]*10
            for v in tdata:
                if 0<v<10:
                    if rc[v] == 0:
                        rc[v] = 1
                    else:
                        print('########### %d duplicated in block row %d, col %d ' %(v, rbase+1, cbase+1))
                        OK=False
                else:
                    print('duff value', v)
                    return False                         
    for r in range(9):
        arow = grid[r]
        rc=[0]*10
        for v in arow:
            if not v is None:
                if 0 < v < 10:
                    if rc[v] == 0:
                        rc[v] = 1
                    else:
                        print('########### %d duplicated in row %d' %(v, r+1))
                        OK=False
                else:
                    print('duff value', v)
                    return False
        acol = [grid[c][r] for c in range(9)]
        rc=[0]*10
        for v in acol:
            if not v is None:
                if 0 < v < 10:
                    if rc[v] == 0:
                        rc[v] = 1
                    else:
                        print('########### %d duplicated in col %d' %(v, r+1))
                        OK=False
                else:
                    print('duff value',v)
                    return False
    return OK

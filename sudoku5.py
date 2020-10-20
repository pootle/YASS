#!/usr/bin/env python3
"""
Core routines to solve sudoku
"""
def findEmpty(grid):
    """find the first unknown value position"""
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v is None:
                return r,c
    return None

def testValid(grid, row, col, val):
    """
    return True if val is legal in current board at row, col
    """
    for x in range(9):
        if row != x and grid[x][col] == val:
            return False
        if col != x and grid[row][x] == val:
            return False
    rbase=(row)//3*3
    cbase=(col)//3*3
    for r in range(rbase,rbase+3):
        for c in range(cbase,cbase+3):
            if not(r == row and c == col) and grid[r][c] == val:
                return False
    return True

def sudsearch(grid, dfunc, nest):
    """
    given a game board it attempts to resolve unknown squares. It is used recursively
    It calls dfunc as each solution is found, and as each value is tested
    """
    svtotal=0
    rc=findEmpty(grid)
    if rc is None:
        dfunc(grid, btype='solution')
    else:
        testr, testc=rc
        for testv in range(1,10):
            if testValid(grid, testr, testc, testv):
                dfunc(grid, btype='partial', nest=nest+1)
                grid[testr][testc]=testv
                sudsearch(grid, dfunc, nest+1)
        grid[testr][testc]=None

"""
housekeeping routines
"""
import os
from colorama import Fore, Back, Style, Cursor
def formatBoard(grid, title, colormap, clr=Back.BLUE):
    """
    pretty format the board with row and column numbers - returns an array of strings padded with spaces to the
    length of 34 chars
    """
    linelen=34
    if len(title) >= linelen:
        title = title[:34]
    else:
        title=' '*((linelen-len(title))//2) + title
        title=title+' '*(linelen-len(title))
    lines=[clr + title + Style.RESET_ALL,
           clr + '     1  2  3   4  5  6   7  8  9  ',
           clr + "   \u250c" + '\u2500'*9 +'\u252c' + '\u2500'*9 + '\u252c'+ '\u2500'*9 + '\u2510']
    setcols=[
        ('',''),
        (Back.BLACK, clr),
        (Back.RED, clr)
    ]
    for rc, row in enumerate(grid):
        if rc % 3 == 0 and rc != 0:
            lines.append(clr + "   \u251c" + '\u2500'*9 + '\u253c' + '\u2500'*9 + '\u253c' + '\u2500'*9 + '\u2524')
        rowcolors=colormap[rc]
        chars=[setcols[rowcolors[vi]][0] + (' '  if v is None else '%d' % v) + setcols[rowcolors[vi]][1] for vi, v in enumerate(row)]
        lines.append(clr + ' %d \u2502' % (rc+1) + ' %s  %s  %s \u2502 %s  %s  %s \u2502 %s  %s  %s \u2502' % (
                chars[0],chars[1],chars[2],chars[3],chars[4],chars[5],chars[6],chars[7],chars[8]))
    lines.append(clr + "   \u2514" + '\u2500'*9 +'\u2534' + '\u2500'*9 + '\u2534'+ '\u2500'*9 + '\u2518')
    return lines

def makesgrid(rows):
    """
    takes a 9 x 9 grid of values and returns a grid with the values set (and None for unknown values).
    (list of 9 9 character strings)
    """
    assert len(rows) == 9
    grid=[]
    colors=[]
    for rx, rowch in enumerate(rows):
        assert len(rowch)==9
        for ch in rowch:
            assert ch in (' ','0','1','2','3','4','5','6','7','8','9')
        grid.append([None if ch in (' ','0') else int(ch) for ch in rowch])    
        colors.append([1 if ch in (' ','0') else 0 for ch in rowch])
    return grid, colors

def validgrid(grid):
    OK=True
    for rbase in range(0,9,3):
        for cbase in range(0,9,3):
            tdata=[]
            for r in range(rbase,rbase+3):
                for c in range(cbase,cbase+3):
                    if not grid[r][c] is None:
                        tdata.append(grid[r][c])
            rc=[0]*10
            for v in tdata:
                if rc[v] == 0:
                    rc[v] = 1
                else:
                    print('########### %d duplicated in block row %d, col %d ' %(v, rbase+1, cbase+1))
                    OK=False
                                    
    for r in range(9):
        arow = grid[r]
        rc=[0]*10
        for v in arow:
            if not v is None:
                if rc[v] == 0:
                    rc[v] = 1
                else:
                    print('########### %d duplicated in row %d' %(v, r+1))
                    OK=False
        acol = [grid[c][r] for c in range(9)]
        rc=[0]*10
        for v in acol:
            if not v is None:
                if rc[v] == 0:
                    rc[v] = 1
                else:
                    print('########### %d duplicated in col %d' %(v, r+1))
                    OK=False
    return OK

class printer():
    boarddef={
        'input'     : (0, 0, Back.BLUE),
        'partial'   : (1, 0, Back.GREEN),
        'solution'  : (0, 1, Back.RED),
        'invalid'   : (1, 1, ''),
    }
    def __init__(self, solutions, skip, colormap):
        self.solutions=solutions
        self.skip=skip
        self.curskips=0
        self.skipped=0
        self.partials=0
        self.depth=0
        rows, cols = os.popen('stty size', 'r').read().split()
        if int(rows) < 32:
            raise ValueError('I need more terminal lines - make the window taller!')
        self.sctr=0
        self.thisset=0
        self.outrows=None
        self.colormap=colormap
        self.input=None
        self.setboardposns()
        self.solcount=0
        self.solset=[]

    def setboardposns(self):
        rows, cols = os.popen('stty size', 'r').read().split()
        cols=int(cols)
        rows=int(rows)
        maxx=(cols+1)//35
        maxy=(rows+1)//16
        rowlocs=[]
        for y in range(maxy):
            row=[]
            for x in range(maxx):
                yv=rows-(maxy-y)*16
                row.append(Cursor.POS(x=x*35+1,y=yv))
            rowlocs.append(row)
        self.poslocs=rowlocs

    def oneprint(self, aboard, btype, nest=1):
        """
        prints a board at board position controlled by btype
        """
        bx, by, clr = self.boarddef[btype]
        if btype=='solution':
            self.solcount += 1
            self.solset.append((self.solcount, [arow.copy() for arow in aboard]))
            if len(self.solset) > len(self.poslocs[by]):
                self.solset.pop(0)
            for si,s in enumerate(self.solset):
                title= '=== solution %d ===' % s[0]
                print(self.poslocs[by][si], end='')
                for aline in formatBoard(s[1], title, colormap, clr=clr):
                    print(aline + Cursor.DOWN() + Cursor.BACK(34), end='')
            print(end='', flush=True)
            if self.solutions != 0 and self.solcount >= self.solutions:
                self.done()
                return False
        elif btype=='invalid':
            for aline in formatBoard(aboard, "??? invalid board ???", colormap, clr=clr):
                print(aline)
        else:
            doprint=True
            if btype=='partial':
                if nest < self.printdepth:
                    doprint=False
                    self.skipped+=1
                else:
                    self.partials += 1
                    title='testing at depth %2d' % nest
            else:
                maxdepth=sum([sum([1 for c in row if c is None]) for row in aboard])
                self.printdepth=maxdepth-self.skip
                title='%d cells unknown in this board' % maxdepth 
            if doprint:
                print(self.poslocs[by][bx], end='')
                for aline in formatBoard(aboard, title, colormap, clr=clr):
                    print(aline + Cursor.DOWN() + Cursor.BACK(34), end='')
                print(end='', flush=True)
        return True

    def done(self, msg=''):
        print(self.poslocs[-1][0] + Cursor.DOWN(16) + Style.RESET_ALL, end='')
        if self.solcount == 0:
            print(msg + "There don't appear to be any valid solutions!")
        else:
            print(msg + '%d solutions found, %d partial prints skipped, %d printed.' % (self.solcount, self.skipped, self.partials)) 

import solver as sudsolv

if __name__ == '__main__':
    import argparse, sys, time
    ntext="""
    Enter the 9 rows as 9 digits each with space between them.

    Use '0' for unknown / blank values
    
    For example:
./sudoku.py -m 5 150700489 420080050 003049006 200800500 830090060 001007004 300900600 040000000 000000000
    """
    parser = argparse.ArgumentParser(description='find sudoku solutions.', epilog=ntext, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-m', "--solutions", type=int, default=5, help='maximum number of solutions to print')
    parser.add_argument('-s', "--skipcount", type=int, default=1, help='only print every nth test - 1 => print every one, 0 => show none')
    parser.add_argument('-c', "--compute", type=int, default=0, help='pure brute force => 0, optimized brute force => 1')
    parser.add_argument('rows', type=str, nargs='+')
    
    args = parser.parse_args()
    if isinstance(args.rows, list):
        if len (args.rows) !=    9:
            print('I only found %d rows, I need 9' % len(args.rows))
            sys.exit(1)
        good=True
        for i, n in enumerate(args.rows):
            if len(n) != 9:
                print('row %d does not have 9 numbers: >%s<' % (i,n))
                good=False
        if not good:
             sys.exit(1)
        aboard, colormap=makesgrid(args.rows)
        pagent=printer(solutions=args.solutions, skip=args.skipcount, colormap=colormap)
        if not aboard is None and validgrid(aboard):
            os.system('clear')
            pagent.oneprint(aboard, 'input')
            startat=time.time()
            solv=(sudsolv.sudoboardbrute if args.compute == 0 else sudsolv.sudoboardsmart)(aboard, dfunc=pagent.oneprint, callall=not args.skipcount==0)
            try:
                solv.sudsearch(nest=0)
                msg=''
            except KeyboardInterrupt:
                msg='Aborted by keybaordinterrupt. '
            pagent.done(msg)
            for i, atime in enumerate(solv.soltimes):
                print('%3d: solved at %5.4f' % (i,atime))
            print('complete in %5.4f' % (time.time()-startat))
        else:
            print('input board was not valid')
            if not aboard is None:
                pagent.oneprint(aboard, 'invalid')

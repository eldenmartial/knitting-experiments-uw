import numpy as np
import math


VERBOSE = False
#---------------------------------------------
#--- CUSTOMIZABLE VARIABLES FOR EXTENSIONS ---
#---------------------------------------------
default_specs = {
    'swgn2': {
        'stitchNumber': 63,
        'speedNumber': 0, # 10, # Valid speeds are 0-15
        'wasteSpeedNumber': 0, #10,
        'wasteStitchNumber': 63,
        #for xfers
        'xferSpeedNumber': 7, #1,
    },
    'kniterate': {
        'stitchNumber': 5,
        'speedNumber': 300,
        'wasteSpeedNumber': 400,
        'wasteStitchNumber': 5,
        'rollerAdvance': 300,
        #for xfers
        'xferSpeedNumber': 300,
        'xferStitchNumber': 3,
        'xferRollerAdvance': 0,
        #for splits
        'splitSpeedNumber': 100,
        'splitStitchNumber': 4,
        'splitRollerAdvance': 0
    }
}


class KnitoutSpecs:
    def __init__(self):
        self.machine = 'swgn2'

        #for main section
        self.speedNumber = 0
        self.stitchNumber = 63
        self.rollerAdvance = None

        #for waste section
        self.wasteSpeedNumber = 0 #10 #400
        self.wasteStitchNumber = 63 #5

        # #for xfers
        self.xferSpeedNumber = 1
        self.xferStitchNumber = None
        self.xferRollerAdvance = None

    def set_ext(self, ext, val):
        if ext == 'machine' and ext != self.machine: # make sure default specs like up with machine if changing machine
            print(f'WARNING: reseting all spec values to match defaults for {ext}.')

            for spec, default_val in default_specs[val].items():
                self.__dict__[spec] = default_val

            specs_NA = [key for key in self.__dict__.keys() if key not in default_specs[val].keys()]

            for spec in specs_NA:
                self.__dict__[spec] = None
        
        self.__dict__[ext] = val

    def defaults(self):
        self.__init__()


specs = KnitoutSpecs()

# ------------------------
# --- HELPER FUNCTIONS ---
# ------------------------
def resetSettings(k):
    k.speedNumber(specs.speedNumber)
    k.stitchNumber(specs.stitchNumber)
    if specs.rollerAdvance is not None: k.rollerAdvance(specs.rollerAdvance)


def xferSettings(k, alterations={}):
    xSpeed = specs.xferSpeedNumber
    xStitch = specs.xferStitchNumber
    xRoll = specs.xferRollerAdvance

    if 'speedNumber' in alterations: xSpeed = alterations['speedNumber']
    if 'stitchNumber' in alterations: xStitch = alterations['stitchNumber']
    if 'rollerAdvance' in alterations: xRoll = alterations['rollerAdvance']

    if xSpeed is not None: k.speedNumber(xSpeed)
    if xStitch is not None: k.stitchNumber(xStitch)
    if xRoll is not None: k.rollerAdvance(xRoll)


def includeNSecureSides(n, secureNeedles={}, knitBed=None):
    '''
    * n is the number associated with the needle we're checking
    * secureNeedles is dict with needle numbers as key and bed as value (valid values are 'f', 'b', or 'both')
    * knitBed is the bed that is currently knitting, if applicable (because this is only checking if we can't xfer it, so if it was unable to be xferred from a certain bed, it should still be knitted on that bed); value of None indicates we are just check for xfer
    '''
    if n in secureNeedles:
        if knitBed is None: return False
        else: #for knitting
            if knitBed == secureNeedles[n]: return True
            else: return False
    else: return True


def sortBedNeedles(bnList=[], direction='+'):
    sortedBnList = list(set(bnList.copy()))
    if direction == '-': sortedBnList.sort(key=lambda bn: int(bn[1:]), reverse=True)
    else: sortedBnList.sort(key=lambda bn: int(bn[1:]))
    return sortedBnList


def convertToBN(needles, sort=True, gauge=2):
    try:
        int(needles)
        return f'b{needles}' if (needles % gauge != 0) else f'f{needles}'
    except Exception:
        if type(needles) == str: return needles
        else: # list of lists of range
            needles = [convertToBN(n) for sublist in needles for n in ([sublist] if isinstance(sublist, (str, int, float)) else sublist)]

    if sort: sortBedNeedles(needles)
    return needles #otherwise, just return original list


def tuckPattern(k, firstN, direction, c=None, bed='f'): #remember to drop after (aka pass `c=None`)
    if direction == '+':
        for n in range(firstN-1, firstN-6, -1):
            if c is None: k.drop(f'{bed}{n}')
            elif n % 2 == 0: k.tuck('-', f'{bed}{n}', c)
            elif n == firstN-5: k.miss('-', f'{bed}{n}', c)
            
        
        if c is not None:
            for n in range(firstN-5, firstN):
                if n % 2 != 0: k.tuck('+', f'{bed}{n}', c)
                elif n == firstN-1: k.miss('+', f'{bed}{n}', c)
    else:
        if c is not None and specs.machine.lower() == 'swgn2': #do it twice so always starting in negative direction
            for n in range(firstN+5, firstN, -1):
                if n % 2 == 0: k.tuck('-', f'{bed}{n}', c)
                elif n == firstN+1: k.miss('-', f'{bed}{n}', c)

        for n in range(firstN+1, firstN+6):
            if c is None: k.drop(f'{bed}{n}')
            elif n % 2 != 0: k.tuck('+', f'{bed}{n}', c)
            elif n == firstN+5: k.miss('+', f'{bed}{n}', c)

        if c is not None:
            for n in range(firstN+5, firstN, -1):
                if n % 2 == 0: k.tuck('-', f'{bed}{n}', c)
                elif n == firstN+1: k.miss('-', f'{bed}{n}', c)

        
def knitPass(k, startN, endN, c, bed='f', gauge=1, emptyNeedles=[]):
    if endN > startN: #pass is pos
        for n in range(startN, endN+1):
            if f'{bed}{n}' not in emptyNeedles:
                if (bed == 'f' and n % gauge == 0) or (bed == 'b' and (gauge == 1 or n % gauge != 0)): k.knit('+', f'{bed}{n}', c) 
                elif n == endN: k.miss('+', f'{bed}{n}', c)
            elif n == endN: k.miss('+', f'{bed}{n}', c)
    else: #pass is neg
        for n in range(startN, endN-1, -1):
            if f'{bed}{n}' not in emptyNeedles:
                if (bed == 'f' and n % gauge == 0) or (bed == 'b' and (gauge == 1 or n % gauge != 0)): k.knit('-', f'{bed}{n}', c)
                elif n == endN: k.miss('-', f'{bed}{n}', c)
            elif n == endN: k.miss('-', f'{bed}{n}', c)


def altTuckTubeCaston(k, startN, endN, c, gauge=1, inhook=False, releasehook=False):
    k.comment('begin alternating tuck tube cast-on')
    if inhook: k.inhook(c)

    if endN > startN: #first pass is pos
        dir1 = '+'
        dir2 = '-'
        needleRange1 = range(startN, endN+1)
        needleRange2 = range(endN, startN-1, -1)
    else: #first pass is neg
        dir1 = '-'
        dir2 = '+'
        needleRange1 = range(startN, endN-1, -1)
        needleRange2 = range(endN, startN+1)

    for n in needleRange1:
        if n % gauge == 0 and (((n/gauge) % 2) == 0):
            k.knit(dir1, f'f{n}', c)
        elif n == endN: k.miss(dir1, f'f{n}', c)
    for n in needleRange2:
        if (gauge == 1 or n % gauge != 0) and ((((n-1)/gauge) % 2) == 0):
            k.knit(dir2, f'b{n}', c)
        elif n == startN: k.miss(dir2, f'b{n}', c)

    if releasehook: k.releasehook(c)

    for n in needleRange1:
        if n % gauge == 0 and (((n/gauge) % 2) != 0):
            k.knit(dir1, f'f{n}', c)
        elif n == endN: k.miss(dir1, f'f{n}', c)
    for n in needleRange2:
        if (gauge == 1 or n % gauge != 0) and ((((n-1)/gauge) % 2) != 0):
            k.knit(dir2, f'b{n}', c)
        elif n == startN: k.miss(dir2, f'b{n}', c)

    k.comment('end alternating tuck tube cast-on')


# for sheet:
def altTuckCaston(k, startN, endN, c, bed, gauge=1, inhook=False, releasehook=False):
    k.comment('begin alternating tuck cast-on')
    if inhook: k.inhook(c)

    if endN > startN: #first pass is pos
        dir1 = '+'
        dir2 = '-'
        needleRange1 = range(startN, endN+1)
        needleRange2 = range(endN, startN-1, -1)
    else: #first pass is neg
        dir1 = '-'
        dir2 = '+'
        needleRange1 = range(startN, endN-1, -1)
        needleRange2 = range(endN, startN+1)

    if bed == 'f':
        for n in needleRange1:
            if n % gauge == 0 and (((n/gauge) % 2) == 0):
                k.knit(dir1, f'f{n}', c)
            elif n == endN: k.miss(dir1, f'f{n}', c)

        for n in needleRange2:
            if n % gauge == 0 and (((n/gauge) % 2) != 0):
                k.knit(dir2, f'f{n}', c)
            elif n == endN: k.miss(dir2, f'f{n}', c)
    else:
        for n in needleRange1:
            if (gauge == 1 or n % gauge != 0) and ((((n-1)/gauge) % 2) == 0):
                k.knit(dir1, f'b{n}', c)
            elif n == startN: k.miss(dir1, f'b{n}', c)
        
        for n in needleRange2:
            if (gauge == 1 or n % gauge != 0) and ((((n-1)/gauge) % 2) != 0):
                k.knit(dir2, f'b{n}', c)
            elif n == startN: k.miss(dir2, f'b{n}', c)

    if releasehook: k.releasehook(c)
    k.comment('end alternating tuck cast-on')


def drawThread(k, leftN, rightN, drawC, finalDir='-', finalBed='f', circular=False, missDraw=None, gauge=1):
    if finalBed == 'f': initBed = 'b'
    else: initBed = 'f'

    def posDraw(bed='f', addMiss=True):
        for n in range(leftN, rightN+1):
            if (n % gauge == 0 and bed=='f') or ((gauge == 1 or n % gauge != 0) and bed=='b'): k.knit('+', f'{bed}{n}', drawC)
            elif n == rightN: k.miss('+', f'{bed}{n}', drawC)
        if addMiss and missDraw is not None: k.miss('+', f'{bed}{missDraw}', drawC)

    def negDraw(bed='f', addMiss=True):
        for n in range(rightN, leftN-1, -1):
            if (n % gauge == 0 and bed=='f') or ((gauge == 1 or n % gauge != 0) and bed=='b'):  k.knit('-', f'{bed}{n}', drawC)
            elif n == leftN: k.miss('-', f'{bed}{n}', drawC)
        if addMiss and missDraw is not None: k.miss('-', f'{bed}{missDraw}', drawC)

    k.comment('begin draw thread')

    if finalDir == '+':
        if circular: negDraw(initBed, False)
        posDraw(finalBed)
    else:
        if circular: posDraw(initBed, False)
        negDraw(finalBed)

    k.comment('end draw thread')


def interlock(k, startN, endN, length, c, gauge=1, startCondition=1, emptyNeedles=[], currentBed=None, homeBed=None, secureStartN=False, secureEndN=False, inhook=False, releasehook=False):
    '''
    Knits on every needle interlock starting on side indicated by which needle value is greater.
    In this function length is the number of total passes knit so if you want an interlock segment that is 20 courses long on each side set length to 40. Useful if you want to have odd amounts of interlock.
    '''
    k.comment('begin interlock')
    if inhook: k.inhook(c)

    if releasehook and length < 2: raise ValueError("not safe to releasehook with less than 2 passes.")

    emptyNeedles = convertToBN(emptyNeedles)
        
    length *= 2
    length = int(length) #incase doing e.g. .5 length (only a pass)

    if endN > startN: #first pass is pos
        beg = 0
        leftN = startN
        rightN = endN
    else: #first pass is neg
        beg = 1
        length += 1
        leftN = endN
        rightN = startN
        if startCondition == 1: startCondition = 2 #switch since starting at 1
        else: startCondition = 1
    
    if homeBed is not None:
        if homeBed == 'f':
            homeCondition = lambda n: (n % gauge == 0)
            travelBed = 'b'
        else:
            homeCondition = lambda n: ((n-1) % gauge == 0)
            travelBed = 'f'
    
    def frontBed1(n, direction):
        if ((n == startN and secureStartN) or (n == endN and secureEndN)) and currentBed == 'b': return False

        if f'f{n}' not in emptyNeedles and n % gauge == 0 and (((n//gauge) % 2) == 0):
            k.knit(direction, f'f{n}', c)
            return True
        else: return False
    
    def backBed1(n, direction):
        if ((n == startN and secureStartN) or (n == endN and secureEndN)) and currentBed == 'f': return False

        if f'b{n}' not in emptyNeedles and (gauge == 1 or n % gauge != 0) and ((((n-1)//gauge) % 2) == 0):
            k.knit(direction, f'b{n}', c)
            return True
        else: return False
    
    def frontBed2(n, direction):
        if ((n == startN and secureStartN) or (n == endN and secureEndN)) and currentBed == 'b': return False

        if f'f{n}' not in emptyNeedles and n % gauge == 0 and (((n//gauge) % 2) != 0):
            k.knit(direction, f'f{n}', c)
            return True
        else: return False
    

    def backBed2(n, direction):
        if ((n == startN and secureStartN) or (n == endN and secureEndN)) and currentBed == 'f': return False

        if f'b{n}' not in emptyNeedles and (gauge == 1 or n % gauge != 0) and ((((n-1)//gauge) % 2) != 0):
            k.knit(direction, f'b{n}', c)
            return True
        else: return False


    if currentBed is not None: #currentBed indicates that we need to start by xferring to proper spots
        xferSettings(k)

        if currentBed == 'f':
            otherBed = 'b'
            currCondition = lambda n: (n % gauge == 0)
        else:
            otherBed = 'f'
            currCondition = lambda n: ((n-1) % gauge == 0)

        for n in range(leftN, rightN+1):
            if (n == startN and secureStartN) or (n == endN and secureEndN): continue

            if currCondition(n) and f'{currentBed}{n}' not in emptyNeedles and (((n//gauge) % (2*gauge)) % gauge) != 0: k.xfer(f'{currentBed}{n}', f'{otherBed}{n}')
        resetSettings(k)

    #for if home bed
    def homeBed1(n, direction):
        if homeCondition(n) and f'{homeBed}{n}' not in emptyNeedles and ((n//gauge) % (2*gauge) == 0):
            k.knit(direction, f'{homeBed}{n}', c)
            return True
        else: return False

    def travelBed1(n, direction):
        if (n == startN and secureStartN) or (n == endN and secureEndN):
            if homeCondition(n):
                k.knit(direction, f'{homeBed}{n}', c)
                return True
            else: return False

        if homeCondition(n) and f'{travelBed}{n}' not in emptyNeedles and ((n//gauge) % (2*gauge) == (gauge+1)):
            k.knit(direction, f'{travelBed}{n}', c)
            return True
        else: return False
    
    def homeBed2(n, direction):
        if homeCondition(n) and f'{homeBed}{n}' not in emptyNeedles and ((n//gauge) % (2*gauge) == gauge):
            k.knit(direction, f'{homeBed}{n}', c)
            return True
        else: return False

    def travelBed2(n, direction):
        if (n == startN and secureStartN) or (n == endN and secureEndN):
            if homeCondition(n):
                k.knit(direction, f'{homeBed}{n}', c)
                return True
            else: return False

        if homeCondition(n) and f'{travelBed}{n}' not in emptyNeedles and ((n//gauge) % (2*gauge) == (gauge-1)):
            k.knit(direction, f'{travelBed}{n}', c)
            return True
        else: return False

    #--- the knitting ---
    for h in range(beg, length):
        if releasehook and h-beg == 2: k.releasehook(c)
        if h % 2 == 0:
            for n in range(leftN, rightN+1):
                if startCondition == 1: #first pass of interlock will knit on 0, 1, 4, 5, etc.
                    if homeBed is None or gauge == 1:
                        if frontBed1(n, '+'): continue
                        elif backBed1(n, '+'): continue
                        elif n == rightN: k.miss('+', f'f{n}', c)
                    else:
                        if homeBed1(n, '+'): continue
                        elif travelBed1(n, '+'): continue
                        elif n == rightN: k.miss('+', f'f{n}', c)
                else: #first pass of interlock will knit on 2, 3, 6, 7, etc.
                    if homeBed is None or gauge == 1:
                        if frontBed2(n, '+'): continue
                        elif backBed2(n, '+'): continue
                        elif n == rightN: k.miss('+', f'f{n}', c)
                    else:
                        if homeBed2(n, '+'): continue
                        elif travelBed2(n, '+'): continue
                        elif n == rightN: k.miss('+', f'f{n}', c)
        else:
            for n in range(rightN, leftN-1, -1):
                if startCondition == 2:
                    if homeBed is None or gauge == 1:
                        if frontBed1(n, '-'): continue
                        elif backBed1(n, '-'): continue
                        elif n == leftN: k.miss('-', f'f{n}', c)
                    else:
                        if homeBed1(n, '-'): continue
                        elif travelBed1(n, '-'): continue
                        elif n == leftN: k.miss('-', f'f{n}', c)
                else:
                    if homeBed is None or gauge == 1:
                        if frontBed2(n, '-'): continue
                        elif backBed2(n, '-'): continue
                        elif n == leftN: k.miss('-', f'f{n}', c)
                    else:
                        if homeBed2(n, '-'): continue
                        elif travelBed2(n, '-'): continue
                        elif n == leftN: k.miss('-', f'f{n}', c)
    
    if homeBed is not None and (gauge != 1 or startCondition != 1):
        xferSettings(k)
        for n in range(leftN, rightN+1):
            if gauge == 1:
                if n % 2 == 0: k.xfer(f'b{n}', f'f{n}')
                else: k.xfer(f'f{n}', f'b{n}')
            else:
                if (n == startN and secureStartN) or (n == endN and secureEndN): continue

                if currCondition(n) and f'{homeBed}{n}' not in emptyNeedles and (((n//gauge) % (2*gauge)) % gauge) != 0: k.xfer(f'{travelBed}{n}', f'{homeBed}{n}')
        resetSettings(k)

    k.comment('end interlock')


#--- FUNCTION FOR DOING THE MAIN KNITTING OF CIRCULAR, OPEN TUBES ---
def circular(k, startN, endN, length, c, gauge=1):
    '''
    Knits on every needle circular tube starting on side indicated by which needle value is greater.
    In this function length is the number of total passes knit so if you want a tube that
    is 20 courses long on each side set length to 40.
    '''
    if endN > startN: #first pass is pos
        beg = 0
        leftN = startN
        rightN = endN
    else: #first pass is neg
        beg = 1
        length += 1
        leftN = endN
        rightN = startN

    for h in range(beg, length):
        if h % 2 == 0:
            for n in range(leftN, rightN+1):
                if n % gauge == 0: k.knit('+', f'f{n}', c)
                elif n == rightN: k.miss('+', f'f{n}', c)
        else:
            for n in range(rightN, leftN-1, -1):
                if gauge == 1 or n % gauge != 0: k.knit('-', f'b{n}', c)
                elif n == leftN: k.miss('-', f'b{n}', c)


def wasteSection(k, leftN, rightN, closedCaston=True, wasteC='1', drawC='2', inCs=[], gauge=1, initDirs={}, endOnRight=[], firstNeedles={}, catchMaxNeedles=False, initial=True, drawMiddle=False, interlockLength=40):
    '''
    Does everything to prepare for knitting prior to (and not including) the cast-on.
        - bring in carriers
        - (if kniterate) catch the yarns to make them secure
        - knit waste section for the rollers to catch
        - add draw thread
    Can also be used to produce a waste section to go in-between samples.
    '''
    carrierLocations = {}

    k.stitchNumber(specs.stitchNumber)
    if specs.rollerAdvance is not None: k.rollerAdvance(specs.rollerAdvance)
    
    missWaste = None
    missDraw = None
    missOtherCs = {}

    if len(firstNeedles):
        if wasteC in firstNeedles:
            if wasteC in endOnRight:
                missWaste = firstNeedles[wasteC][1]
                carrierLocations[wasteC] = firstNeedles[wasteC][1]
            else:
                missWaste = firstNeedles[wasteC][0]
                carrierLocations[wasteC] = firstNeedles[wasteC][0]
        
        if drawC in firstNeedles:
            if drawC in endOnRight:
                missDraw = firstNeedles[drawC][1]
                carrierLocations[drawC] = firstNeedles[drawC][1]
            else:
                missDraw = firstNeedles[drawC][0]
                carrierLocations[drawC] = firstNeedles[drawC][0]

        if len(inCs):
            for c in range(0, len(inCs)):
                if inCs[c] in firstNeedles:
                    if inCs[c] in endOnRight:
                        missOtherCs[inCs[c]] = firstNeedles[inCs[c]][1]
                        carrierLocations[inCs[c]] = firstNeedles[inCs[c]][1]
                    else:
                        missOtherCs[inCs[c]] = firstNeedles[inCs[c]][0]
                        carrierLocations[inCs[c]] = firstNeedles[inCs[c]][0]

    carriers = [wasteC, drawC]
    carriers.extend(inCs)
    carriers = list(set(carriers))

    carriers = [x for x in carriers if x is not None]

    if len(carriers) != len(carrierLocations):
        for c in carriers:
            if c not in carrierLocations:
                if c in endOnRight: carrierLocations[c] = rightN
                else: carrierLocations[c] = leftN

    if initial:
        catchEndOnRight = endOnRight.copy()

        if closedCaston:
            if not drawMiddle:
                if drawC in endOnRight:
                    catchEndOnRight.remove(drawC)
                    if drawC in missOtherCs: missOtherCs[drawC] = firstNeedles[drawC][0] 
                else:
                    catchEndOnRight.append(drawC)
                    if drawC in missOtherCs: missOtherCs[drawC] = firstNeedles[drawC][1] 
        elif drawC is not None and specs.machine.lower() == 'swgn2' and not drawC in initDirs and not len(endOnRight):
            endOnRight.append(drawC)
        elif wasteC in inCs: k.inhook(wasteC)

    k.comment('begin waste section')
    k.speedNumber(specs.wasteSpeedNumber)
    k.stitchNumber(specs.wasteStitchNumber)

    if drawMiddle: interlockLength //= 2
    
    if drawC in endOnRight: drawFinalDir = '+'# side it ends on (could also do from `finalDirs` or `endDirs`)
    else: drawFinalDir = '-'

    # init dir for draw thread:
    if drawC in initDirs:
        drawInitDir = initDirs[drawC]
    elif drawC in inCs: # meaning we are bringing it in for the first time
        if specs.machine.lower() == 'kniterate': drawInitDir = '+'
        else: drawInitDir = '-'
    elif (drawFinalDir == '+' and closedCaston) or (drawFinalDir == '-' and not closedCaston): drawInitDir = '+'
    else: drawInitDir = '-'
    
    if wasteC in endOnRight:
        if specs.machine.lower() == 'kniterate' and initial and interlockLength > 24:
            interlock(k, rightN, leftN, 24, wasteC, gauge)
            k.pause('cut yarns')
            interlock(k, rightN, leftN, interlockLength-24, wasteC, gauge)
        else: interlock(k, rightN, leftN, interlockLength, wasteC, gauge, releasehook=(specs.machine.lower() == 'swgn2' and wasteC in inCs))

        if drawMiddle:
            if drawC is not None:
                if specs.machine.lower() == 'swgn2' and drawC in inCs:
                    k.inhook(drawC)
                    tuckPattern(k, firstN=(leftN if drawInitDir=='+' else rightN), direction=drawInitDir, c=drawC)
                    
                if drawInitDir == drawFinalDir: # we need to tuck to get it in the correct position
                    n_range = range(leftN, rightN+1)
                    if drawInitDir == '-': n_range = n_range[::-1] #reverse it
                    for n in n_range:
                        if n % 2 == 0: k.tuck(drawInitDir, f'b{n}', drawC)
                        elif n == n_range[-1]: k.miss(drawInitDir, f'b{n}', drawC)
                    
                    # this is essentially circular
                    drawThread(k, leftN, rightN, drawC, finalDir=('-' if drawFinalDir == '+' else '+'), finalBed='f', circular=False, missDraw=missDraw, gauge=gauge)
                    for n in n_range:
                        if n % 2 == 0: k.drop(f'b{n}')
                    drawThread(k, leftN, rightN, drawC, finalDir=drawFinalDir, finalBed='b', circular=False, missDraw=missDraw, gauge=gauge)
                else: drawThread(k, leftN, rightN, drawC, finalDir=drawFinalDir, circular=True, missDraw=missDraw, gauge=gauge) 

                if specs.machine.lower() == 'swgn2' and drawC in inCs:
                    k.releasehook(drawC)
                    tuckPattern(k, firstN=(leftN if drawInitDir=='+' else rightN), direction=drawInitDir, c=None) # drop it

            if initial and interlockLength > 12:
                if interlockLength < 24:
                    pauseAfter = 24-interlockLength
                    interlock(k, rightN, leftN, pauseAfter, wasteC, gauge)
                    if specs.machine.lower() == 'kniterate': k.pause('cut yarns')
                    interlock(k, rightN, leftN, interlockLength-pauseAfter, wasteC, gauge)
                else: interlock(k, rightN, leftN, interlockLength, wasteC, gauge)
            else:
                interlock(k, rightN, leftN, interlockLength, wasteC, gauge)
                if specs.machine.lower() == 'kniterate' and initial: k.pause('cut yarns')
        else:
            if specs.machine.lower() == 'kniterate' and initial and interlockLength <= 24: k.pause('cut yarns')
            circular(k, rightN, leftN, 8, wasteC, gauge)
        if missWaste is not None: k.miss('+', f'f{missWaste}', wasteC)
    else:
        if specs.machine.lower() == 'kniterate' and initial and interlockLength > 24:
            interlock(k, leftN, rightN, 24, wasteC, gauge)
            k.pause('cut yarns')
            interlock(k, leftN, rightN, interlockLength-24, wasteC, gauge)
        else:
            if specs.machine.lower() == 'swgn2' and initial:
                interlock(k, rightN, leftN, 1.5, wasteC, gauge, releasehook=(wasteC in inCs))
                interlockLength -= 2
            interlock(k, leftN, rightN, interlockLength, wasteC, gauge)

        if drawMiddle:
            if drawC is not None:
                if specs.machine.lower() == 'swgn2' and drawC in inCs:
                    k.inhook(drawC)
                    tuckPattern(k, firstN=(leftN if drawInitDir=='+' else rightN), direction=drawInitDir, c=drawC)
                
                if drawInitDir == drawFinalDir: # we need to tuck to get it in the correct position
                    n_range = range(leftN, rightN+1)
                    if drawInitDir == '-': n_range = n_range[::-1] #reverse it
                    for n in n_range:
                        if n % 2 == 0: k.tuck(drawInitDir, f'b{n}', drawC)
                        elif n == n_range[-1]: k.miss(drawInitDir, f'b{n}', drawC)
                    
                    # this is essentially circular
                    drawThread(k, leftN, rightN, drawC, finalDir=('-' if drawFinalDir == '+' else '+'), finalBed='f', circular=False, missDraw=missDraw, gauge=gauge)
                    for n in n_range:
                        if n % 2 == 0: k.drop(f'b{n}')
                    drawThread(k, leftN, rightN, drawC, finalDir=drawFinalDir, finalBed='b', circular=False, missDraw=missDraw, gauge=gauge)
                else: drawThread(k, leftN, rightN, drawC, finalDir=drawFinalDir, circular=True, missDraw=missDraw, gauge=gauge)

                if specs.machine.lower() == 'swgn2' and drawC in inCs:
                    k.releasehook(drawC)
                    tuckPattern(k, firstN=(leftN if drawInitDir=='+' else rightN), direction=drawInitDir, c=None) # drop it

            if initial and interlockLength > 12:
                if interlockLength < 24:
                    pauseAfter = 24-interlockLength
                    interlock(k, leftN, rightN, pauseAfter, wasteC, gauge)
                    if specs.machine.lower() == 'kniterate': k.pause('cut yarns')
                    interlock(k, leftN, rightN, interlockLength-pauseAfter, wasteC, gauge)
                else: interlock(k, leftN, rightN, interlockLength, wasteC, gauge)
            else:
                interlock(k, leftN, rightN, interlockLength, wasteC, gauge)
                if initial: k.pause('cut yarns')
        else:
            if specs.machine.lower() == 'kniterate' and initial  and interlockLength <= 24: k.pause('cut yarns')
            circular(k, leftN, rightN, 8, wasteC, gauge)
        if missWaste is not None: k.miss('-', f'f{missWaste}', wasteC)

    if closedCaston and not drawMiddle:
        for n in range(leftN, rightN+1):
            if (n + 1) % gauge == 0: k.drop(f'b{n}')

    if not drawMiddle and drawC is not None:
        if specs.machine.lower() == 'swgn2' and drawC in inCs:
            k.inhook(drawC)
            tuckPattern(k, firstN=(leftN if drawInitDir=='+' else rightN), direction=drawInitDir, c=drawC)

        if (closedCaston and drawInitDir != drawFinalDir) or (not closedCaston and drawInitDir == drawFinalDir): # we need to tuck to get it in the correct position
            n_range = range(leftN, rightN+1)
            if drawInitDir == '-': n_range = n_range[::-1] # reverse it

            for n in n_range:
                if n % 2 == 0: k.tuck(drawInitDir, f'b{n}', drawC)
                elif n == n_range[-1]: k.miss(drawInitDir, f'b{n}', drawC)

            if closedCaston: drawFinalDir1 = drawFinalDir
            else: drawFinalDir1 = ('-' if drawFinalDir == '+' else '+')

            drawThread(k, leftN, rightN, drawC, finalDir=drawFinalDir1, finalBed='f', circular=False, missDraw=missDraw, gauge=gauge)

            if not closedCaston: # aka circular
                # this + above drawThread call is essentially circular
                for n in n_range:
                    if n % 2 == 0: k.drop(f'b{n}')
                drawThread(k, leftN, rightN, drawC, finalDir=drawFinalDir, finalBed='b', circular=False, missDraw=missDraw, gauge=gauge)
            else:
                for n in n_range:
                    if n % 2 == 0: k.drop(f'b{n}')
        else: drawThread(k, leftN, rightN, drawC, finalDir=drawFinalDir, circular=(not closedCaston), missDraw=missDraw, gauge=gauge)

        if specs.machine.lower() == 'swgn2' and drawC in inCs:
            k.releasehook(drawC)
            tuckPattern(k, firstN=(leftN if drawInitDir=='+' else rightN), direction=drawInitDir, c=None) # drop it

    resetSettings(k)

    k.comment('end waste section')
    return carrierLocations


#--- FINISH BY DROP FUNCTION ---
def dropFinish(k, frontNeedleRanges=[], backNeedleRanges=[], carriers=[], rollOut=True, emptyNeedles=[], direction='+', borderC=None, borderLength=16, gauge=1):
    '''
    Finishes knitting by dropping loops (optionally knitting 16 rows of waste yarn prior with `borderC`, and optionally taking carriers listed in `carriers` param out afterwards).
    '''

    k.comment('begin drop finish')

    outCarriers = carriers.copy()

    if specs.machine.lower() == 'kniterate': out_func = k.outcarrier
    else: out_func = k.outhook

    if len(carriers):
        if borderC is not None and borderC in carriers: outCarriers.remove(borderC) # remove so can take it out at end instead
        
        for c in outCarriers:
            out_func(c)

    def knitBorder(posNeedleRange, posBed, negNeedleRange, negBed): #v
        # NOTE: if specified `borderStPat`, assumes `posNeedleRange` and `negNeedleRange` are the same
        beg = 0
        length = borderLength #rows of waste # parameter is

        if direction == '-':
            beg += 1
            length += 1
            side = 'r'
        else: side = 'l'

        def knitBorderPos(needleRange, bed):
            for n in range(needleRange[0], needleRange[1]+1):
                if f'{bed}{n}' not in emptyNeedles: k.knit('+', f'{bed}{n}', borderC)
        
        def knitBorderNeg(needleRange, bed):
            for n in range(needleRange[1], needleRange[0]-1, -1):
                if f'{bed}{n}' not in emptyNeedles: k.knit('-', f'{bed}{n}', borderC)
    
        for r in range(beg, length):
            if r % 2 == 0: knitBorderPos(posNeedleRange, posBed)
            else: knitBorderNeg(negNeedleRange, negBed)
    #--- end knitBorder func ---#^


    if borderC is not None:
        if len(frontNeedleRanges) and len(backNeedleRanges):
            needleRanges1 = frontNeedleRanges
            bed1 = 'f'
            needleRanges2 = backNeedleRanges
            bed2 = 'b'
        else:
            if len(frontNeedleRanges):
                needleRanges1 = frontNeedleRanges
                bed1 = 'f'
                needleRanges2 = frontNeedleRanges
                bed2 = 'f'
            else:
                needleRanges1 = backNeedleRanges
                bed1 = 'b'
                needleRanges2 = backNeedleRanges
                bed2 = 'b'

        if type(needleRanges1[0]) == int: #just one range (one section)
            knitBorder(needleRanges1, bed1, needleRanges2, bed2)
        else:
            for nr in range(0, len(needleRanges1)):
                knitBorder(needleRanges1[nr], bed1, needleRanges2[nr], bed2)

    def dropOnBed(needleRanges, bed): #v
        if type(needleRanges[0]) == int: #just one range (one section)
            if rollOut and specs.machine.lower() == 'kniterate' and (needleRanges is backNeedleRanges or not len(backNeedleRanges)): k.addRollerAdvance(2000)
            for n in range(needleRanges[0], needleRanges[1]+1):
                if f'{bed}{n}' not in emptyNeedles: k.drop(f'{bed}{n}')
        else: #multiple ranges (multiple sections, likely shortrowing)
            for nr in needleRanges:
                if rollOut and specs.machine.lower() == 'kniterate' and needleRanges.index(nr) == len(needleRanges)-1 and (needleRanges is backNeedleRanges or not len(backNeedleRanges)): k.addRollerAdvance(2000)
                for n in range(nr[0], nr[1]+1):
                    if f'{bed}{n}' not in emptyNeedles: k.drop(f'{bed}{n}')
    #--- end dropOnBed func ---#^

    if len(frontNeedleRanges): dropOnBed(frontNeedleRanges, 'f')
    if len(backNeedleRanges): dropOnBed(backNeedleRanges, 'b')

    if borderC is not None and borderC in carriers: out_func(borderC)

    k.comment('end drop finish')


# --------------------------------
# --- STITCH PATTERN FUNCTIONS ---
# --------------------------------
# if doing gauge == 2, want width to be odd so *actually* have number of stitches
def jersey(k, startN, endN, length, c, bed='f', gauge=1, emptyNeedles=[], inhook=False, releasehook=False, tuck_pattern=True):

    k.comment('begin jersey')
    if endN > startN: init_dir = '+'
    else: init_dir = '-'
    
    if inhook:
        k.inhook(c)
        if tuck_pattern: tuckPattern(k, firstN=startN, direction=init_dir, c=c)

    width = abs(endN-startN)+1

    for p in range(0, length):
        if releasehook and p == 2:
            k.releasehook(c)
            if tuck_pattern: tuckPattern(k, firstN=startN, direction=init_dir, c=None) # drop it

            releasehook = False

        if p % 2 == 0:
            passStartN = startN
            passEndN = endN
        else:
            passStartN = endN
            passEndN = startN
        knitPass(k, startN=passStartN, endN=passEndN, c=c, bed=bed, gauge=gauge, emptyNeedles=emptyNeedles)
    
    if releasehook: # still hasn't happened
        k.releasehook(c)
        if tuck_pattern: tuckPattern(k, firstN=startN, direction=init_dir, c=None) # drop it
        releasehook = False
    
    k.comment('end jersey')

    if length % 2 == 0:
        if endN > startN: return '+'
        else: return '-'
    else:
        if endN > startN: return '-'
        else: return '+'


def rib(k, startN, endN, length, c, bed=None, bedLoops={'f': [], 'b': []}, sequence='fb', gauge=1, inhook=False, releasehook=False, tuck_pattern=True):
    k.comment(f'begin rib ({sequence})')

    if releasehook and length < 2: raise ValueError("not safe to releasehook with less than 2 passes.")

    if not 'f' in bedLoops: bedLoops['f'] = []
    if not 'b' in bedLoops: bedLoops['b'] = []

    if gauge > 1:
        gaugedSequence = ''
        for char in sequence:
            gaugedSequence += char * gauge
        sequence = gaugedSequence
    
    width = abs(endN-startN)+1

    def bedConditions(n):
        if bed == 'f':
            if n % gauge == 0: return True
            else: return False
        else:
            if (n+1) % gauge == 0: return True
            else: return False


    if endN > startN: #first pass is pos
        dir1 = '+'
        dir2 = '-'

        ranges = {dir1: range(startN, endN+1), dir2: range(endN, startN-1, -1)}
    else: #first pass is neg
        dir1 = '-'
        dir2 = '+'

        ranges = {dir1: range(startN, endN-1, -1), dir2: range(endN, startN+1)}

    if inhook:
        k.inhook(c)
        if tuck_pattern: tuckPattern(k, firstN=startN, direction=dir1, c=c)

    if bed == 'f': otherBed = 'b'
    else: otherBed = 'f'

    if len(bedLoops['f']) or len(bedLoops['b']): # indicates that we might need to start by xferring to proper spots
        xferSettings(k)

        for n in ranges[dir1]:
            if bedConditions(n):
                if sequence[n % len(sequence)] == otherBed and n in bedLoops[bed]: k.xfer(f'{bed}{n}', f'{otherBed}{n}')
                elif sequence[n % len(sequence)] == bed and n in bedLoops[otherBed]: k.xfer(f'{otherBed}{n}', f'{bed}{n}')
            
        resetSettings(k)

    for p in range(0, length):
        if releasehook and p == 2:
            k.releasehook(c)
            if tuck_pattern: tuckPattern(k, firstN=startN, direction=dir1, c=None) # drop it
        if p % 2 == 0:
            direction = dir1
            lastN = endN
        else:
            direction = dir2
            lastN = startN

        for n in ranges[direction]:
            if sequence[n % len(sequence)] == 'f':
                if bedConditions(n):
                    k.knit(direction, f'f{n}', c) #xferred it or bed == 'f', ok to knit
                elif n == lastN: k.miss(direction, f'f{n}', c)
            else: #sequence == 'b'
                if bedConditions(n):
                    k.knit(direction, f'b{n}', c) #xferred it or bed == 'b', ok to knit
                elif n == lastN: k.miss(direction, f'b{n}', c)
    
    # return the loops:
    if len(bedLoops['f']) or len(bedLoops['b']):
        xferSettings(k)

        for n in ranges[dir1]:
            if bedConditions(n):
                if sequence[n % len(sequence)] == otherBed and n in bedLoops[bed]: k.xfer(f'{otherBed}{n}', f'{bed}{n}')
                elif sequence[n % len(sequence)] == bed and n in bedLoops[otherBed]: k.xfer(f'{bed}{n}', f'{otherBed}{n}')
            
        resetSettings(k)

    k.comment('end rib')

    if length % 2 == 0:
        if endN > startN: return '+'
        else: return '-'
    else:
        if endN > startN: return '-'
        else: return '+'


def altKnitTuck(k, startN, endN, length, c, bed='f', gauge=1, sequence='kt', tuckSequence='mt', inhook=False, releasehook=False, tuck_pattern=True):
    k.comment(f'begin alt knit/tuck ({sequence})')

    if endN > startN: init_dir = '+'
    else: init_dir = '-'
    
    if inhook:
        k.inhook(c)
        if tuck_pattern: tuckPattern(k, firstN=startN, direction=init_dir, c=c)

    if releasehook and length < 2: raise ValueError("not safe to releasehook with less than 2 passes.")

    for p in range(0, length):
        if releasehook and p == 2:
            k.releasehook(c)
            if tuck_pattern: tuckPattern(k, firstN=startN, direction=init_dir, c=None) # drop it

        if p % 2 == 0:
            passStartN = startN
            passEndN = endN
        else:
            passStartN = endN
            passEndN = startN
        if sequence[p % len(sequence)] == 'k':
            knitPass(k, startN=passStartN, endN=passEndN, c=c, bed=bed, gauge=gauge)
        else:
            if passEndN > passStartN: #pass is pos
                for n in range(passStartN, passEndN+1):
                    if n == passEndN and (gauge == 1 or (bed == 'f' and passEndN % gauge == 0) or (bed == 'b' and passEndN % gauge != 0)): #v
                        k.miss('+', f'{bed}{n}', c) #^
                    elif (bed == 'f' and n % gauge == 0 and (((n//gauge) % 2) == 0)) or (bed == 'b' and (gauge == 1 or n % gauge != 0) and ((((n-1)//gauge) % 2) == 0)):
                        k.tuck('+', f'{bed}{n}', c)
                    elif n == passEndN: k.miss('+', f'{bed}{n}', c)
            else: #pass is neg
                for n in range(passStartN, passEndN-1, -1):
                    if n == passEndN and (gauge == 1 or (bed == 'f' and passEndN % gauge == 0) or (bed == 'b' and passEndN % gauge != 0)): #v
                        k.miss('-', f'{bed}{n}', c) #^
                    elif (bed == 'f' and n % gauge == 0 and (((n//gauge) % 2) != 0)) or (bed == 'b' and (gauge == 1 or n % gauge != 0) and ((((n-1)//gauge) % 2) != 0)):
                        k.tuck('-', f'{bed}{n}', c)
                    elif n == passEndN: k.miss('-', f'{bed}{n}', c)

    k.comment('end alt knit/tuck')

    if passEndN > passStartN: return '-' #just knit a pos pass
    else: return '+'


def garter(k, startN, endN, length, c, bed='f', bedLoops={'f': [], 'b': []}, sequence='fb', secureStartN=True, secureEndN=True, gauge=1, inhook=False, releasehook=False, tuck_pattern=True):
    patternRows = {
        'f': sequence.count('f'),
        'b': sequence.count('b')
    }

    k.comment(f'begin {patternRows["f"]}x{patternRows["b"]} garter')

    if releasehook and length < 2: raise ValueError("not safe to releasehook with less than 2 passes.")

    secureNeedles = {'f': [], 'b': []}

    if bed == 'b':
        otherBed = 'f'
        condition = lambda n: (n % gauge != 0 or gauge == 1)
    else:
        otherBed = 'b'
        condition = lambda n: n % gauge == 0

    if endN > startN: #first pass is pos
        dir1 = '+'
        dir2 = '-'

        range1 = range(startN, endN+1)
        range2 = range(endN, startN-1, -1)

        if gauge == 2:
            if secureStartN:
                if startN % 2 == 0:
                    secureNeedles['f'].append(startN)
                    secureNeedles['b'].append(startN+1)
                else:
                    secureNeedles['b'].append(startN)
                    secureNeedles['f'].append(startN+1)
            
            if secureEndN:
                if endN % 2 == 0:
                    secureNeedles['f'].append(endN)
                    secureNeedles['b'].append(endN-1)
                else:
                    secureNeedles['b'].append(endN)
                    secureNeedles['f'].append(endN-1)
        else:
            if secureStartN: secureNeedles[bed].append(startN)
            if secureEndN: secureNeedles[bed].append(endN)
    else: #first pass is neg
        dir1 = '-'
        dir2 = '+'

        range1 = range(startN, endN-1, -1)
        range2 = range(endN, startN+1)

        if gauge == 2:
            if secureStartN:
                if startN % 2 == 0:
                    secureNeedles['f'].append(startN)
                    secureNeedles['b'].append(startN-1)
                else:
                    secureNeedles['b'].append(startN)
                    secureNeedles['f'].append(startN-1)
            
            if secureEndN:
                if endN % 2 == 0:
                    secureNeedles['f'].append(endN)
                    secureNeedles['b'].append(endN+1)
                else:
                    secureNeedles['b'].append(endN)
                    secureNeedles['f'].append(endN+1)
        else:
            if secureStartN: secureNeedles[bed].append(startN)
            if secureEndN: secureNeedles[bed].append(endN)

    if inhook:
        k.inhook(c)
        if tuck_pattern: tuckPattern(k, firstN=startN, direction=dir1, c=c)
    
    # for now: (will be reset)
    direction = dir1
    needleRange = range1

    if type(patternRows) != dict:
        pat_rows = {}
        pat_rows['f'] = patternRows
        pat_rows['b'] = patternRows
        patternRows = pat_rows
    
    b = sequence[0]
    b2 = 'f' if b == 'b' else 'b'

    if len(bedLoops['f']) or len(bedLoops['b']):
        for n in range1:
            if n in bedLoops[b2] and condition(n) and n not in secureNeedles[b2]: k.xfer(f'{b2}{n}', f'{b}{n}')
    
    for p in range(0, length):
        if p % 2 == 0:
            direction = dir1
            needleRange = range1
        else:
            direction = dir2
            needleRange = range2

        if p > 0 and b != sequence[p % len(sequence)]: # transfer
            xferSettings(k)
            
            for n in range1:
                if condition(n) and n not in secureNeedles[b]: k.xfer(f'{b}{n}', f'{sequence[p % len(sequence)]}{n}')

            resetSettings(k)

        b = sequence[p % len(sequence)]

        b2 = 'f' if b == 'b' else 'b'

        if releasehook and p == 2:
            k.releasehook(c)
            if tuck_pattern: tuckPattern(k, firstN=startN, direction=dir1, c=None) # drop it

        for n in needleRange:
            if condition(n):
                if n in secureNeedles[b2]: k.knit(direction, f'{b2}{n}', c)
                else: k.knit(direction, f'{b}{n}', c)
            elif n == endN: k.miss(direction, f'{b}{n}', c)

    if len(bedLoops['f']) or len(bedLoops['b']):
        b2 = 'f' if b == 'b' else b

        if n in bedLoops[b2] and condition(n) and n not in secureNeedles[b2]: k.xfer(f'{b}{n}', f'{b2}{n}')
        
    if type(patternRows) == dict: k.comment(f'end {patternRows["f"]}x{patternRows["b"]} garter')
    else: k.comment(f'end {patternRows}x{patternRows} garter')

    next_direction = '-' if direction == '+' else '+'
    return next_direction # direction #return the direction that the next pass should be, so know which to use next


def tuckGarter(k, startN, endN, length, c, bed='f', sequence='ffb', secureStartN=True, secureEndN=True, gauge=1, inhook=False, releasehook=False, tuck_pattern=True):
    patternRows = {
        'f': sequence.count('f'),
        'b': sequence.count('b')
    }

    if type(patternRows) == dict: k.comment(f'begin {patternRows["f"]}x{patternRows["b"]} garter')
    else: k.comment(f'begin {patternRows}x{patternRows} garter')

    if releasehook and length < 2: raise ValueError("not safe to releasehook with less than 2 passes.")

    secureNeedles = {}

    if bed == 'b':
        bed2 = 'f'
        condition = lambda n: (n % gauge != 0 or gauge == 1)
    else:
        bed2 = 'b'
        condition = lambda n: n % gauge == 0

    if endN > startN: #first pass is pos
        dir1 = '+'
        dir2 = '-'

        range1 = range(startN, endN+1)
        range2 = range(endN, startN-1, -1)

        if gauge == 2:
            if secureStartN:
                if startN % 2 == 0:
                    secureNeedles[startN] = 'f'
                    secureNeedles[startN+1] = 'b'
                else:
                    secureNeedles[startN] = 'b'
                    secureNeedles[startN+1] = 'f'
            
            if secureEndN:
                if endN % 2 == 0:
                    secureNeedles[endN] = 'f'
                    secureNeedles[endN-1] = 'b'
                else:
                    secureNeedles[endN] = 'b'
                    secureNeedles[endN-1] = 'f'
        else:
            if secureStartN: secureNeedles[startN] = bed
            if secureEndN: secureNeedles[endN] = bed
    else: #first pass is neg
        dir1 = '-'
        dir2 = '+'

        range1 = range(startN, endN-1, -1)
        range2 = range(endN, startN+1)

        if gauge == 2:
            if secureStartN:
                if startN % 2 == 0:
                    secureNeedles[startN] = 'f'
                    secureNeedles[startN-1] = 'b'
                else:
                    secureNeedles[startN] = 'b'
                    secureNeedles[startN-1] = 'f'
            
            if secureEndN:
                if endN % 2 == 0:
                    secureNeedles[endN] = 'f'
                    secureNeedles[endN+1] = 'b'
                else:
                    secureNeedles[endN] = 'b'
                    secureNeedles[endN+1] = 'f'
        else:
            if secureStartN: secureNeedles[startN] = bed
            if secureEndN: secureNeedles[endN] = bed

    if inhook:
        k.inhook(c)
        if tuck_pattern: tuckPattern(k, firstN=startN, direction=dir1, c=c)
    
    # for now: (will be reset)
    direction = dir1
    needleRange = range1

    width = abs(endN-startN)+1

    if type(patternRows) != dict:
        pat_rows = {}
        pat_rows['f'] = patternRows
        pat_rows['b'] = patternRows
        patternRows = pat_rows
    
    patternRows['f'] += 1 #for the tucks

    passCt = 0
    for l in range(0, length):
        if l % 2 == 0:
            b1 = bed
            b2 = bed2
        else:
            b1 = bed2
            b2 = bed

        for r in range(0, patternRows[b1]):
            if releasehook and passCt == 2:
                k.releasehook(c)
                if tuck_pattern: tuckPattern(k, firstN=startN, direction=dir1, c=None) # drop it
            
            if b1 == 'f' and r == 0:
                for n in needleRange:
                    if n % (gauge*2) == 0 and includeNSecureSides(n, secureNeedles=secureNeedles, knitBed=None): k.tuck(direction, f'{b1}{n}', c)
                    elif n == endN: k.miss(direction, f'{b1}{n}', c)
            else:
                for n in needleRange:
                    if condition(n) and includeNSecureSides(n, secureNeedles=secureNeedles, knitBed=b1): k.knit(direction, f'{b1}{n}', c)
                    elif condition(n): k.knit(direction, f'{bed}{n}', c)
                    elif n == endN: k.miss(direction, f'{b1}{n}', c)

            if direction == dir1:
                direction = dir2
                needleRange = range2
            else:
                direction = dir1
                needleRange = range1

            passCt += 1
            if passCt == length: break

        if passCt == length and b1 == bed: break #don't need to return it

        xferSettings(k)
            
        for n in range1:
            if condition(n) and includeNSecureSides(n, secureNeedles=secureNeedles): k.xfer(f'{b1}{n}', f'{b2}{n}')

        resetSettings(k)

        if passCt == length: break

    if type(patternRows) == dict: k.comment(f'end {patternRows["f"]-1}x{patternRows["b"]} garter')
    else: k.comment(f'end {patternRows}x{patternRows} garter')

    return direction #return the direction that the next pass should be, so know which to use next


def seed(k, startN, endN, length, c, bed='f', bedLoops={'f': [], 'b': []}, sequence='fb', secureStartN=True, secureEndN=True, gauge=1, inhook=False, releasehook=False, tuck_pattern=True):
    k.comment(f'begin seed ({sequence})')

    if releasehook and length < 2: raise ValueError("not safe to releasehook with less than 2 passes.")

    if not 'f' in bedLoops: bedLoops['f'] = []
    if not 'b' in bedLoops: bedLoops['b'] = []

    secureNeedles = {}

    if gauge == 2:
        if secureStartN:
            if startN % 2 == 0:
                secureNeedles[startN] = 'f'
                secureNeedles[startN-1] = 'b'
            else:
                secureNeedles[startN] = 'b'
                secureNeedles[startN-1] = 'f'
        
        if secureEndN:
            if endN % 2 == 0:
                secureNeedles[endN] = 'f'
                secureNeedles[endN+1] = 'b'
            else:
                secureNeedles[endN] = 'b'
                secureNeedles[endN+1] = 'f'
    else:
        if secureStartN: secureNeedles[startN] = bed
        if secureEndN: secureNeedles[endN] = bed


    if gauge > 1:
        gauged_sequence = ''
        for char in sequence:
            gauged_sequence += char * gauge
        sequence = gauged_sequence


    def bedConditions(n):
        if bed == 'f':
            if n % gauge == 0: return True
            else: return False
        else:
            if (n+1) % gauge == 0: return True
            else: return False


    if endN > startN: #first pass is pos
        dir1 = '+'
        dir2 = '-'

        ranges = {dir1: range(startN, endN+1), dir2: range(endN, startN-1, -1)}
    else: #first pass is neg
        dir1 = '-'
        dir2 = '+'

        ranges = {dir1: range(startN, endN-1, -1), dir2: range(endN, startN+1)}

    if inhook:
        k.inhook(c)
        if tuck_pattern: tuckPattern(k, firstN=startN, direction=dir1, c=c)
    
    if bed == 'f': otherBed = 'b'
    else: otherBed = 'f'

    if len(bedLoops['f']) or len(bedLoops['b']): # indicates that we might need to start by xferring to proper spots
        xferSettings(k)

        for n in ranges[dir1]:
            if n not in secureNeedles and bedConditions(n):
                if sequence[n % len(sequence)] == otherBed and n in bedLoops[bed]: k.xfer(f'{bed}{n}', f'{otherBed}{n}')
                elif sequence[n % len(sequence)] == bed and n in bedLoops[otherBed]: k.xfer(f'{otherBed}{n}', f'{bed}{n}')
            
        resetSettings(k)

    for p in range(0, length):
        if releasehook and p == 2:
            k.releasehook(c)
            if tuck_pattern: tuckPattern(k, firstN=startN, direction=dir1, c=None) # drop it
        
        if p % 2 == 0:
            direction = dir1
            lastN = endN

            for n in ranges[direction]:
                if n in secureNeedles:
                    if bedConditions(n):
                        k.knit(direction, f'{secureNeedles[n]}{n}', c) #xferred it or bed == 'f', ok to knit
                    elif n == lastN: k.miss(direction, f'{secureNeedles[n]}{n}', c)
                else:
                    if sequence[n % len(sequence)] == 'f':
                        if bedConditions(n):
                            k.knit(direction, f'f{n}', c) #xferred it or bed == 'f', ok to knit
                        elif n == lastN: k.miss(direction, f'f{n}', c)
                    else: #sequence == 'b'
                        if bedConditions(n):
                            k.knit(direction, f'b{n}', c) #xferred it or bed == 'b', ok to knit
                        elif n == lastN: k.miss(direction, f'b{n}', c)
            
            xferSettings(k)
            if p < length-1:
                for n in ranges[direction]:
                    if n not in secureNeedles and bedConditions(n):
                        if sequence[n % len(sequence)] == 'f': k.xfer(f'f{n}', f'b{n}')
                        else: k.xfer(f'b{n}', f'f{n}')
            else:
                for n in ranges[direction]:
                    if n not in secureNeedles and bedConditions(n):
                        if sequence[n % len(sequence)] == 'f' and n in bedLoops['b']: k.xfer(f'f{n}', f'b{n}')
                        elif sequence[n % len(sequence)] == 'b' and n in bedLoops['f']: k.xfer(f'b{n}', f'f{n}')

            resetSettings(k)
        else:
            direction = dir2
            lastN = startN

            for n in ranges[direction]:
                if n in secureNeedles:
                    if bedConditions(n):
                        k.knit(direction, f'{secureNeedles[n]}{n}', c) #xferred it or bed == 'f', ok to knit
                    elif n == lastN: k.miss(direction, f'{secureNeedles[n]}{n}', c)
                else:
                    if sequence[n % len(sequence)] == 'f':
                        if bedConditions(n):
                            k.knit(direction, f'b{n}', c) #xferred it or bed == 'f', ok to knit
                        elif n == lastN: k.miss(direction, f'b{n}', c)
                    else: #sequence == 'b'
                        if bedConditions(n):
                            k.knit(direction, f'f{n}', c) #xferred it or bed == 'b', ok to knit
                        elif n == lastN: k.miss(direction, f'f{n}', c)

            xferSettings(k)
            if p < length-1:
                for n in ranges[direction]:
                    if n not in secureNeedles and bedConditions(n):
                        if sequence[n % len(sequence)] == 'f': k.xfer(f'b{n}', f'f{n}')
                        else: k.xfer(f'f{n}', f'b{n}')
            else:
                for n in ranges[direction]:
                    if n not in secureNeedles and bedConditions(n):
                        if sequence[n % len(sequence)] == 'f' and n in bedLoops['f']: k.xfer(f'b{n}', f'f{n}')
                        elif sequence[n % len(sequence)] == 'b' and n in bedLoops['b']: k.xfer(f'f{n}', f'b{n}')
            resetSettings(k)

    k.comment(f'end seed ({sequence})')

    if length % 2 == 0:
        if endN > startN: return '+'
        else: return '-'
    else:
        if endN > startN: return '-'
        else: return '+'


def tuckStitch(k, startN, endN, length, c, bed='f', gauge=1, sequence='kt', inhook=False, releasehook=False, tuck_pattern=True):

    k.comment(f'begin tuck stitch ({sequence})')

    if endN > startN:
        init_dir = '+'
        other_dir = '-'
        needle_range0 = range(startN, endN+1)
        needle_range1 = range(endN, startN-1, -1)
    else:
        init_dir = '-'
        other_dir = '+'
        needle_range0 = range(startN, endN-1, -1)
        needle_range1 = range(endN, startN+1)
    
    if inhook:
        k.inhook(c)
        if tuck_pattern: tuckPattern(k, firstN=startN, direction=init_dir, c=c)

    if releasehook and length < 2: raise ValueError("not safe to releasehook with less than 2 passes.")

    for p in range(0, length):
        if releasehook and p == 2:
            k.releasehook(c)
            if tuck_pattern: tuckPattern(k, firstN=startN, direction=init_dir, c=None) # drop it

        if p % 2 == 0:
            needle_range = needle_range0
            do_knit = 'k'
            d = init_dir
            passStartN = startN
            passEndN = endN
        else:
            needle_range = needle_range1
            do_knit = 't'
            d = other_dir
            passStartN = endN
            passEndN = startN

        for n in needle_range:
            if n % (gauge*2) == 0 or n % (gauge*2) == gauge:
                if sequence[(n*gauge) % len(sequence)] == do_knit or n == passStartN or n == passEndN: k.knit(d, f'{bed}{n}', c)
                else: k.tuck(d, f'{bed}{n}', c)
            elif n == passEndN: k.miss(d, f'{bed}{n}', c)

    k.comment('end tuck stitch')

    if passEndN > passStartN: return '-' #just knit a pos pass
    else: return '+'

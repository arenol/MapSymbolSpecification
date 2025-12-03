# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 07:57:07 2025

@author: agnar
"""

import re
import math

def ParseSvgPath(canvas,d):
    '''
    Creates a reportlab path object from an SVG path element

    Parameters
    ----------
    canvas : reportlab canvas
    d : string
        holds the "d" attribute of an SVG path element.

    Returns
    -------
    canvas path object.

    '''

    thePath = canvas.beginPath()

    # Tokenize: commands or numbers
    token_re = re.compile(r"""
        ([MLCZmlcz])              # SVG command
        |([-+]?[0-9]*\.?[0-9]+)   # Number
    """, re.VERBOSE)

    tokens = token_re.findall(d)
    # Flatten: each match gives (command, number)
    tokens = [t[0] or t[1] for t in tokens]

    i = 0

    def get_number():
        nonlocal i
        val = float(tokens[i])
        i += 1
        return val

    current_cmd = None

    x = y = 0   # Current position

    while i < len(tokens):
        t = tokens[i]

        # If token is a command letter, advance and set it
        if re.match(r'[MLCZmlcz]', t):
            current_cmd = t
            i += 1
        # Else the command repeats

        cmd = current_cmd.upper()
        is_rel = current_cmd.islower()

        if cmd == 'M':  # moveto
            # First pair is moveto, subsequent pairs are implicit lineto
            while i < len(tokens) and not re.match(r'[MLCZmlcz]', tokens[i]):
                nx = get_number()
                ny = get_number()
                if is_rel:
                    nx += x
                    ny += y

                if cmd == "M" and i > 2:
                    thePath.moveTo( nx, ny)
                else:
                    thePath.lineTo( nx, ny)

                x, y = nx, ny

        elif cmd == 'L':  # lineto
            while i < len(tokens) and not re.match(r'[MLCZmlcz]', tokens[i]):
                nx = get_number()
                ny = get_number()
                if is_rel:
                    nx += x
                    ny += y
                thePath.lineTo( nx, ny)
                x, y = nx, ny

        elif cmd == 'C':  # cubic curveto
            # groups of 6 numbers
            while i < len(tokens) and not re.match(r'[MLCZmlcz]', tokens[i]):
                x1 = get_number()
                y1 = get_number()
                x2 = get_number()
                y2 = get_number()
                nx = get_number()
                ny = get_number()

                if is_rel:
                    x1 += x; y1 += y
                    x2 += x; y2 += y
                    nx += x; ny += y

                thePath.curveTo( x1, y1, x2, y2, nx, ny)
                x, y = nx, ny

        elif cmd == 'Z':  # closepath
            thePath.close()
            # SVG closes back to subpath start; we could track it if needed
    return thePath

def AdjustDashArray( dashArray, dashOffset, lineLength):
    '''
    Given a the length of a line, this will return adjusted dashArray and dashOffset
    so the line will be drawn with full (or offseted) dash at the start, and a full (or offseted)
    dash at the end

    Parameters
    ----------
    dashArray : [float]
        array of floats
    dashOffset : float
        dash offset at the ends
    lineLength : float
        the length of the line

    Returns
    -------
    [float]
        Adjusted dasharray
    float
        Adjusted offset

    '''
    
    # TODO: This function is not tested, it was just drawn out of my head, so 
    # it's probably not working as intended.
        
    
    if (len(dashArray) == 0):
        return dashArray, dashOffset
    lastGap = dashArray[-1]
    dashLength = sum( dashArray)
    count = int((lineLength+lastGap)/dashLength)
    nominalLength = dashLength / (count * dashLength)
    scaling = nominalLength / lineLength
    
    outArray = [x*scaling for x in dashArray]
    outOffset = dashOffset * scaling
    
    return outArray, outOffset

def CalcLineLengthFromDash( dashArray, dashOffset, maxLen):
    '''
    Calulate the longest line length that will fit a complete number of
    dashes, <dashOffset> taken into account on a line shorter than <maxLen>

    Parameters
    ----------
    dashArray : [float]
    dashOffset : float
    maxLen : float

    Returns
    -------
    float

    '''
    
    dashLen = sum( dashArray)
    offset2x = 2*dashOffset
    if (dashLen == 0):
        return maxLen
    dashCount = math.floor((maxLen + dashArray[-1] + offset2x)/dashLen)
    return (dashLen * dashCount - dashArray[-1]) - offset2x

def CreatePolyFromRect( xc, yc, w, h):

    llx = xc - w/2
    lly = yc - h/2
    urx = llx + w
    ury = lly + h

    return CreatePolyFromBounds( llx, lly, urx, ury)

def CreatePolyFromBounds( llx, lly, urx, ury):

    return [(llx, lly),(urx, lly),(urx,ury),(llx,ury)]


def RotatePoly( poly, angle):
    angle *= math.pi / 180

    result = []
    for (x,y) in poly:
        x0 = x * math.cos(angle) - y * math.sin(angle)
        y0 = x * math.sin(angle) + y * math.cos(angle)

        result.append( (x0, y0))

    return result

def CalcPolyBounds( poly):
    (x,y) = poly[0]
    xMin = x
    xMax = x
    yMin = y
    yMax = y

    for (x,y) in poly:
        xMin = min( x, xMin)
        xMax = max( x, xMax)
        yMin = min( y, yMin)
        yMax = max( y, yMax)

    return (xMin, yMin, xMax, yMax)

def CreatePathFromPoly( canvas, poly, closePath):

    p = canvas.beginPath()

    firstPoint = True
    for (x,y) in poly:
        if firstPoint:
            p.moveTo( x, y)
            firstPoint = False
        else:
            p.lineTo( x, y)
    if (closePath):
        p.close()
    return p


# -*- coding: utf-8 -*-
"""
Created on Sun Dec  7 19:10:25 2025

@author: agnar
"""

import re

def DrawShape( canvas, xmlElement):
    if (xmlElement.tag == 'path'):
        DrawPath( canvas, xmlElement)
    elif (xmlElement.tag == 'rect'):
        DrawRect( canvas, xmlElement)
    elif (xmlElement.tag == 'circle'):
        DrawCircle( canvas, xmlElement)



def DrawPath( canvas, xmlPath):
    
    p = _ParseSvgPath( canvas, xmlPath.attrib['d'])

    doFill = 1 if "fill" in xmlPath.attrib else 0
    doStroke = 1 if "stroke" in xmlPath.attrib else 0

    canvas.drawPath( p, fill = doFill, stroke=doStroke)
    
    

def DrawCircle( canvas, xmlCircle):
    
    cx = float( xmlCircle.attrib['cx'])
    cy = float( xmlCircle.attrib['cy'])
    r = float( xmlCircle.attrib['r'])

    doFill = 1 if "fill" in  xmlCircle.attrib else 0
    doStroke = 1 if "stroke" in  xmlCircle.attrib else 0
    
    canvas.circle( cx, cy, r, fill=doFill, stroke=doStroke)
    
def DrawRect( canvas, xmlRect):

    llx = float( xmlRect.attrib['x'])
    lly = float( xmlRect.attrib['y'])
    w = float( xmlRect.attrib['width'])
    h = float( xmlRect.attrib['height'])

    doFill = 1 if "fill" in xmlRect.attrib else 0
    doStroke = 1 if "stroke" in xmlRect.attrib else 0
    
    canvas.rect( llx, lly, w, h, fill=doFill, stroke=doStroke)
    

def _ParseSvgPath(canvas,d):


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

    

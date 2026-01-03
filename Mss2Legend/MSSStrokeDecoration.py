# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 07:57:07 2025

@author: agnar
"""

import math
from  MSSPath import *
from MSSDrawShapes import DrawShape

def CalcLineLengthFromDecoration( strokeDecoration, maxLen):
    offset = float(strokeDecoration.attrib['offset'])
    spacing = float(strokeDecoration.attrib['spacing'])

    count = math.floor((maxLen - offset*2) / spacing)
    return round(spacing*count + 2*offset, 3)
    
def _DrawDecoration( canvas, decParts, layerId):
    for part in decParts:
        if ("fill" in part.attrib):
            fillColor = part.attrib["fill"]
            if (fillColor == layerId):
                DrawShape( canvas, part)
        if ("stroke" in part.attrib):
            strokeColor =  part.attrib["stroke"]
            if (strokeColor == layerId):
                DrawShape( canvas, part)


def DrawRegularStrokeDecoration( canvas, xs, ys, layerId, lineLen, strokeDecoration ):
    offset = float(strokeDecoration.attrib['offset'])
    spacing = float(strokeDecoration.attrib['spacing'])
    x0 = xs - (lineLen * 0.5) + offset
    x1 = xs + (lineLen * 0.5)
    canvas.saveState()
    canvas.translate( x0, ys)
    while (x0<x1):
        _DrawDecoration( canvas, strokeDecoration, layerId)
        x0 += spacing
        canvas.translate( spacing,0)
    canvas.restoreState()

def DrawDashPointrStrokeDecoration( canvas, xs, ys, layerId, lineLen, strokeDecoration ):
    spaceCount = 3  # will draw 3 elements
    spacing = lineLen / (spaceCount+1)   
    x0 = xs - lineLen / 2 + spacing
    canvas.saveState()
    canvas.translate( x0, ys)
    _DrawDecoration( canvas, strokeDecoration, layerId)

    for i in range(spaceCount):
        _DrawDecoration( canvas, strokeDecoration, layerId)
        canvas.translate( spacing,0)
    canvas.restoreState()

def DrawStartPointStrokeDecoration( canvas, xs, ys, layerId, lineLen, strokeDecoration ):
    canvas.saveState()
    canvas.translate( xs - lineLen/2, ys)
    _DrawDecoration( canvas, strokeDecoration, layerId)
    canvas.restoreState()

def DrawEndPointStrokeDecoration( canvas, xs, ys, layerId, lineLen, strokeDecoration ):
    canvas.saveState()
    canvas.translate( xs + lineLen/2, ys)
    _DrawDecoration( canvas, strokeDecoration, layerId)
    canvas.restoreState()




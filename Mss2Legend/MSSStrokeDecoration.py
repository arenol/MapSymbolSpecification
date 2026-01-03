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

    count = math.floor(maxLen - offset*2) / spacing
    return spacing*count + 2*offset
    

def DrawRegularStrokeDecoration( canvas, xs, ys, layerId, lineLen, strokeDecoration ):
    offset = float(strokeDecoration.attrib['offset'])
    spacing = float(strokeDecoration.attrib['spacing'])
    x0 = xs - (lineLen * 0.5) + offset
    x1 = xs + (lineLen * 0.5)
    canvas.saveState()
    canvas.translate( x0, ys)
    while (x0<x1):
        for part in strokeDecoration:
            if ("fill" in part.attrib):
                fillColor = part.attrib["fill"]
                if (fillColor == layerId):
                    DrawShape( canvas, part)
            if ("stroke" in part.attrib):
                strokeColor =  part.attrib["stroke"]
                if (strokeColor == layerId):
                    DrawShape( canvas, part)
        x0 += spacing
        canvas.translate( spacing,0)
    canvas.restoreState()

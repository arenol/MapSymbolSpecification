# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 07:57:07 2025

@author: agnar
"""

import math
from  MSSPath import *

def DrawHatch( canvas, hatch, poly):
    # This method relies that the canvase have saved its state before calling
    # this function, and will resore it aftewards

    sWidth = float(hatch.attrib['stroke-width'])
    spacing = float(hatch.attrib['spacing'])    
    angle = 0
    if ('rotation' in hatch.attrib):
        angle = float(hatch.attrib['rotation'])
        
    offset = 0.0
    if ('offset' in hatch.attrib):
        offset = float(hatch.attrib['offset'])

    canvas.rotate(angle)

    rotatedPoly = RotatePoly( poly, -angle)
    (xMin, yMin, xMax, yMax) = CalcPolyBounds( rotatedPoly)

    yMin -= sWidth
    yMax += sWidth

    y = math.floor(yMin / spacing) * spacing - offset
    while y < yMax:
        p = canvas.beginPath()
        p.moveTo( xMin, y)
        p.lineTo( xMax, y)
        canvas.drawPath( p, stroke=1, fill=0)
        y += spacing
    
    
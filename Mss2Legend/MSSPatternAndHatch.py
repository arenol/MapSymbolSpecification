# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 07:57:07 2025

@author: agnar
"""

import math
from  MSSPath import *
from MSSLegendDrawing import *

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

    if ('stroke-dasharray' in hatch.attrib):
        # adjust left start so dashes will align across the map
        dashArray = [float(x) for x in hatch.attrib['stroke-dasharray'].split(',')]
        dashTotal = sum( dashArray)
        xMin = math.floor( xMin / dashTotal) * dashTotal


    yMin -= sWidth
    yMax += sWidth


    y = math.floor(yMin / spacing) * spacing - offset
    while y < yMax:
        p = canvas.beginPath()
        p.moveTo( xMin, y)
        p.lineTo( xMax, y)
        canvas.drawPath( p, stroke=1, fill=0)
        y += spacing
    
def DrawPattern( legend, layer, pattern, poly):
    x0 = float(pattern.attrib['x'])
    y0 = float(pattern.attrib['y'])
    tileWidth = float(pattern.attrib['width'])
    tileHeight = float(pattern.attrib['height'])
    
    angle = 0
            
    if ('rotation' in pattern.attrib):
        angle = float(pattern.attrib['rotation'])
    
    legend.canvas.rotate( angle)
    rotatedPoly = RotatePoly( poly, -angle)
    (xMin, yMin, xMax, yMax) = CalcPolyBounds( rotatedPoly)


    y = math.floor(yMin / tileHeight) * tileHeight
    xMin = math.floor(xMin / tileWidth) * tileWidth
    while y < yMax:
        x = xMin
        while x < xMax:
            legend.canvas.saveState()
            legend.canvas.translate( x, y)

            clipPoly = CreatePolyFromBounds( x0, y0, x0+tileWidth, y+tileHeight)
            clipPath = CreatePathFromPoly( legend.canvas, clipPoly, True)
            legend.canvas.clipPath( clipPath, fill=0, stroke=0)
            legend.DrawPointSymbol(x0,y0,layer,pattern)
            legend.canvas.restoreState()
            
            x += tileWidth
        y+= tileHeight
    
                      
        

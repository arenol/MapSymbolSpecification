#---------------------------------------------------------------------------
#  MMS2Legend:   Create a Legend from an MSS file
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#---------------------------------------------------------------------------


from reportlab.lib.units import mm
from MSSPath import *
from MSSPatternAndHatch import *
from MSSDrawShapes import *
from MSSStrokeDecoration import *
from MSSError import BailOut



class MSSLegendDrawer(object):
    '''
        Given a Map Symbol Specification (MSS) fil, this class will
        draw a Legend onto a canvas.
    '''
    
    # height and width of graphical legend elements
    legend_width = 14   # mm
    legend_height = 5   # mm
    
    # the vertical spacing between each line
    legend_vspacing = 6.5 # mm
    legend_hspacing = 80
    
    def __init__( self, theCanvas, xmlBaseColors, xmlColorLayers, xmlSymbols):
        '''
   
        Parameters
        ----------
        theCanvas : reportlab.pdfgen.canvas
            a reportlab canvas element, shall be prepared to accept mm as unit
        xmlBaseColors : xml.etree.ElementTree "BaseColors" element
            Holds the base colours of the MSS file.
        xmlColorLayers : xml.etree.ElementTree "ColorLayers" element
            Holds the colour layers of the MMS file.
        xmlSymbols : xml.etree.ElementTree "Symbols" element
            Holds the symbol definitions of the MMS file.

        Returns
        -------
        None.

        '''
        self.canvas = theCanvas
        self.baseColors = xmlBaseColors
        self.colorLayers = xmlColorLayers
        self.symbols = xmlSymbols
        
        # convert into millimiter
        self.pageWidth, self.pageHeight = theCanvas._pagesize
        self.pageWidth /= mm
        self.pageHeight /= mm

        print( "Page size", self.pageWidth, self.pageHeight)

    def DrawSymbols( self):
        '''
        Draws all the legend entries into its canvas.
        This is the main function of this class.

        Returns
        -------
        None.

        '''
        margin = 20
        x0 = margin
        y0 = self.pageHeight - margin
        dy = self.legend_vspacing

        # draw symbols, color layer by color layer:
        for layer in reversed(self.colorLayers):
            print( "LAYER:", layer.attrib['id'])
            self.SetLayerStyle( layer)
            xs = x0
            ys = y0
            for symbol in self.symbols:
                symbolType = symbol.attrib['type']

                if (symbolType == 'point'):
                    self.DrawPointSymbol( xs, ys, layer, symbol)
                elif (symbolType == 'area'):
                    self.DrawAreaSymbol( xs, ys, layer, symbol)
                elif (symbolType == 'line'):
                    self.DrawStrokeSymbol( xs, ys, layer, symbol)
                ys -= dy
                if ys < margin:
                    ys = self.pageHeight  - margin
                    xs += self.legend_hspacing


                    
        self.DrawNames( x0+10, y0, dy)
        

    def SetLayerStyle( self, xmlLayer):
        '''
            Sets the stroke color and fill color according to layer specification
            before drawing anything associated with this layers
            The <layer> is an xml element.
        '''
        
        tint = 1.0
        opacity = 1.0
        blend = 'normal'
        overprint = False

        colorId = xmlLayer.attrib['color']
        baseColor = self.baseColors.find(".//color[@id='%s']" % colorId)
        cmyk = baseColor.attrib['cmyk']
        c, m, y, k = cmyk.split(',')       
        
        if ('tint') in xmlLayer.attrib:
            tint = float(xmlLayer.attrib['tint'])
            
        c = float(c) * tint
        m = float(m) * tint
        y = float(y) * tint
        k = float(k) * tint
        
        if ('opacity' in xmlLayer.attrib):
            opacity = float( xmlLayer.attrib['opacity'])
            
        if ('blend' in xmlLayer.attrib):
            blend = xmlLayer.attrib['blend']
            # not supported by reportlab?

        if ('overprint' in xmlLayer.attrib):
            if xmlLayer.attrib['overprint'] == "yes":
                overprint = True
            
        
        self.canvas.setStrokeColorCMYK( c, m, y, k)
        self.canvas.setFillColorCMYK( c, m, y, k)
        
        self.canvas.setStrokeOverprint( overprint)
        self.canvas.setFillOverprint( overprint)
        
        self.canvas.setStrokeAlpha( opacity)
        self.canvas.setFillAlpha( opacity)
        
        # self.canvas,setBlendMode( blend)
    
    def SetStrokeStyle( self, xmlElement):
        '''
        Provided an xmlElement containing a strok style, sets the style
        before drawing any element
        '''

        lineLen = self.legend_width
       
        sWidth = float( xmlElement.attrib['stroke-width'])
        sCap = 0
        sJoin = 0
        sMiterLimit = 4
        
        

        sDash, sDashOffset = ParseStrokeDash( xmlElement)
        if ('stroke-linecap' in xmlElement.attrib):
            sCap = ['but','round','square','pointed'].index( xmlElement.attrib['stroke-linecap'])
        if ('stroke-linejoin' in xmlElement.attrib):
            sJoin = ['miter','bevel','round'].index( xmlElement.attrib['stroke-linejoin'])
        if ('stroke-miterlimit' in xmlElement.attrib):
            sMiterLimit = float( xmlElement.attrib['stroke-miterlimit'])

        if (sCap == 3):
            sCap = 0    # pointed line caps is not legal in PDF and must be handled specially.

        self.canvas.setLineWidth( sWidth)
        self.canvas.setDash( sDash, sDashOffset)
        self.canvas.setLineCap( sCap)
        self.canvas.setLineJoin( sJoin)
        self.canvas.setMiterLimit( sMiterLimit)
           
                
    def DrawPointSymbol( self, xs, ys, layer, xmlSymbol):
        '''
        Draws a point symbol based on its specification centered on xs, ys.
        Only draw if the fill or stroke attribute of the symbol matches the current <layer>

        '''
        
        layerId = layer.attrib['id']
        for part in xmlSymbol:
            
            fill = part.attrib.get('fill')
            stroke = part.attrib.get('stroke')
            
            doThisLayer = False
            if (fill == layerId):
                doThisLayer = True
                
            if (stroke == layerId):
                self.SetStrokeStyle(part)
                doThisLayer = True
                
            if doThisLayer:
                self.canvas.saveState()
                self.canvas.translate( xs, ys)

                DrawShape( self.canvas, part)

                self.canvas.restoreState()
                        
    def DrawAreaSymbol( self, xs, ys, layer, symbol):
        '''
        Draws a square and fills it accroding to the symbol specification
        '''
        layerId = layer.attrib['id']
        for part in symbol:
            if (part.tag == 'path'):
                if ('fill' in part.attrib):
                    fill = part.attrib['fill']
                    if (fill == layerId):
                        self.DrawLegendArea( xs, ys)
                if ('stroke' in part.attrib):
                    stroke = part.attrib['stroke']
                    if (stroke == layerId):
                        self.SetStrokeStyle( part)
                        self.DrawLegendAreaOutline(xs, ys)
            if (part.tag == 'hatch'):
                stroke = part.attrib['stroke']
                if (stroke == layerId):
                    self.DrawLegendHatch( xs, ys, part)
            if (part.tag == 'pattern'):
                self.DrawLegendPattern( xs, ys, layer, part)
                
            # TODO: add pattern
            

                    
    def DrawStrokeSymbol( self, xs, ys, layer, symbol):
        '''
        Draws a line symbol according to symbol specification

        Parameters
        ----------
        xs, ys : float
            The center ot the legend symbol field.
        layer : xml layer element
            The layer currently being drawn. Will only draw anything if the specific
            symbol has a color on this layer
        symbol : xml symbol element
            Contains the symbol specification

        Returns
        -------
        None.

        '''
        layerId = layer.attrib['id']
        lineLen = self.CalcLineLength( symbol)
        for part in symbol:
            # print( "LINE LEN = ", lineLen, "of", symbol.attrib['id'])
            if (part.tag == 'path'):
                stroke = part.attrib['stroke']
                if (stroke == layerId):
                    self.SetStrokeStyle( part)
                    strokeOffset = 0.0
                    if ('stroke-offset' in part.attrib):
                        strokeOffset = float(part.attrib['stroke-offset'])
                    self.DrawLegendLine( xs, ys+strokeOffset, lineLen)
#                    if ('stroke-linecap' in part.attrib) and (part.attrib['stroke-linecap'] == 'pointed'):
#                        self.DrawPointedLineCaps( xs, ys, lineLen, part)
            if (part.tag == 'stroke-decoration'):
                decorationType = part.attrib['type']
                if (decorationType == 'regular'):
                    DrawRegularStrokeDecoration( self, xs, ys, layerId, lineLen, part)
                elif (decorationType == 'dash-point'):
                    DrawDashPointStrokeDecoration( self, xs, ys, layerId, lineLen, part)
                elif (decorationType == 'start-point'):
                    DrawStartPointStrokeDecoration( self, xs, ys, layerId, lineLen, part)
                elif (decorationType == 'end-point'):
                    DrawEndPointStrokeDecoration( self, xs, ys, layerId, lineLen, part)

            # TODO: Add stroke decaration

  

    def CalcLineLength( self, xmlSymbol):
        # Calculates the length of the line so that dash pattern and/or stroke decoration
        # matches exactly.
        lineLen = self.legend_width
        decorLen = lineLen
        dashLen = lineLen
 #       capLen = 0
        for part in xmlSymbol:
            if (part.tag == 'stroke-decoration'):
                if (part.attrib['type'] == 'regular'):
                    decorLen = CalcLineLengthFromDecoration( part, lineLen)
            if (part.tag == 'path'):
                if ('stroke-dasharray' in part.attrib):
                    dashLen = CalcLineLengthFromDash( part, lineLen)
#                if ('stroke-linecap' in part.attrib) and part.attrib['stroke-linecap'] == 'pointed':
#                    if ('stroke-caplength' in part.attrib):
#                        capLen = float(part.attrib['stroke-caplength'])
#                    else:
#                        capLen = float(part.attrib['stroke-width'])
#                    lineLen -= (capLen * 2)
            if (decorLen != lineLen) and (dashLen != lineLen) and (dashLen != decorLen):
                BailOut( "Error in symbol %s. Dash array do not match stroke decoration spacing", xmlSymbol.attrib['id'])

        if (decorLen < lineLen):
            return decorLen
        return min( dashLen, lineLen)
        

                    
    def GetLayerColor( self, layer):
        '''
        Gets

        Parameters
        ----------
        layer : layer
            an xml color layer element.

        Returns
        -------
        c, m, y, k : float
            The CMYK colours of the specific layer. Will be in the range 0 to 1
        opacity : float
            The opacity of the layer. Will be in the range 0.1
        blend : string
            Any blending mode accepted in the SVG file format

        '''
        
        tint = 1.0
        opacity = 1.0
        blend = 'normal'

        colorId = layer.attrib['color']
        baseColor = self.baseColors.find(".//color[@id='%s']" % colorId)
        cmyk = baseColor.attrib['cmyk']
        c, m, y, k = cmyk.split(',')       
        
        if ('tint') in layer.attrib:
            tint = float(layer.attrib['tint'])
            
        c = float(c) * tint
        m = float(m) * tint
        y = float(y) * tint
        k = float(k) * tint
        
        if ('opacity' in layer.attrib):
            opacity = float( layer.attrib['opacity'])
            
        if ('blend' in layer.attrib):
            blend = layer.attrib['blend']
            
        return c, m, y, k, opacity, blend

       
        
    def DrawLegendArea( self, x, y):
        '''
        Draws a filled square using the current fill style centered at x, y
        '''
        
        width = self.legend_width
        height = self.legend_height
        self.canvas.rect( x-width*0.5, y-height*0.5, width, height, fill=1, stroke=0)
    

    def DrawLegendAreaOutline( self, x, y):
        width = self.legend_width
        height = self.legend_height
        self.canvas.rect( x-width*0.5, y-height*0.5, width, height, fill=0, stroke=1)
        

    def DrawLegendHatch( self, xs, ys, hatch):
        '''
        Draws a hatched area centered at x, y
        '''
        self.SetStrokeStyle( hatch)
        self.canvas.saveState()
        
        rectPoly = CreatePolyFromRect( xs, ys, self.legend_width, self.legend_height)
        path = CreatePathFromPoly( self.canvas, rectPoly, True)
        self.canvas.clipPath( path, stroke=0, fill=0)
        
        DrawHatch( self.canvas, hatch, rectPoly)

        self.canvas.restoreState()

    def DrawLegendPattern(self, xs, ys, layer, pattern):
        self.canvas.saveState()

        rectPoly = CreatePolyFromRect( xs, ys, self.legend_width, self.legend_height)
        path = CreatePathFromPoly( self.canvas, rectPoly, True)
        self.canvas.clipPath( path, stroke=0, fill=0)
        
        DrawPattern( self, layer, pattern, rectPoly)
        
        self.canvas.restoreState()
        
        

    def DrawLegendLine( self, x, y, lineLen):
        '''
        Draws a line using the current line style centered at x, y
        In order to draw a complete number of dashes, a <lineLen> is precalculated
        so we do not end up with half a dash at the end.
        '''
        
        p = self.canvas.beginPath()
        p.moveTo( x - lineLen*0.5, y)
        p.lineTo( x + lineLen*0.5, y)
        self.canvas.drawPath( p)
        
        # TODO: This is just a straght line. Draw a more complex line to better
        # test stroke decorations.
        
    def DrawPointedLineCaps( self, xs, ys, lineLen, xmlPath):
        strokeWidth = float( xmlPath.attrib['stroke-width'])
        if ('stroke-caplength' in xmlPath.attrib):
            capLen = float( xmlPath.attrib['stroke-caplength'])
        else:
            capLen = strokeWidth
        self._DrawPointedCap( xs - lineLen*0.5, ys, -1, capLen, strokeWidth)
        self._DrawPointedCap( xs + lineLen*0.5, ys, 1, capLen, strokeWidth)

    def _DrawPointedCap( self, x, y, dir, capLen, strokeWidth):
        p = self.canvas.beginPath()
        yu = y + strokeWidth*0.5    # upper y
        yl = yu - strokeWidth       # lower y
        p.moveTo( x, yu)
        p.curveTo( x + capLen*0.25*dir, yu, x + capLen*0.5*dir, yu, x + capLen*dir, y)
        p.curveTo( x + capLen*0.5*dir, yl,  x + capLen*0.25*dir, yl, x, yl)
        p.close()
        self.canvas.drawPath(p, stroke=0, fill=1)


    def DrawNames( self, x, starty, dy):
        '''
        Draw all the symbol names

        Parameters
        ----------
        x : float
            the x coordinate of all name texts
        starty : flaot
            The y coordiante of the first entry
        dy : float
            The line spacing between each entry

        Returns
        -------
        None.

        '''
        y = starty - 1.0
        
        self.canvas.setFillColorCMYK(0,0,0,1)
        self.canvas.setFont( "Helvetica", 3)
        
        for symbol in self.symbols:
            symbolName = symbol.attrib['id'] + " " + symbol.attrib['name'] 
            (  symbolName)
            self.canvas.drawString( x, y, symbolName)
            print( symbolName)

            y -= dy

        
                               
            
        

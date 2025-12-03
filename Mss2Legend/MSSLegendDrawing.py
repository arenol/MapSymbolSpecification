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
    legend_hspacing = 50
    
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
        x0 = 20
        y0 = self.pageHeight - 20
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
                    
        self.DrawNames( x0+10, y0, dy)

    def SetLayerStyle( self, layer):
        tint = 1.0
        opacity = 1.0
        blend = 'normal'
        overprint = False

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
            # not supported by reportlab?

        if ('overprint' in layer.attrib):
            if layer.attrib['overprint'] == "yes":
                overprint = True
            
        
        self.canvas.setStrokeColorCMYK( c, m, y, k)
        self.canvas.setFillColorCMYK( c, m, y, k)
        
        self.canvas.setStrokeOverprint( overprint)
        self.canvas.setFillOverprint( overprint)
        
        self.canvas.setStrokeAlpha( opacity)
        self.canvas.setFillAlpha( opacity)
        
        # self.setBlendMode( blend)
                    
    def DrawPointSymbol( self, xs, ys, layer, symbol):
        '''
        Draws a point symbol based on its specification centered on xs, ys.

        Parameters
        ----------
        xs, ys : float
            center coordinate of the symbol to draw
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
        for part in symbol:
            
            fill = part.attrib.get('fill')
            stroke = part.attrib.get('stroke')
            
            doThisLayer = False
            if (fill == layerId):
                doThisLayer = True
                
            if (stroke == layerId):
                self.SetStrokeStyle(part)
                doThisLayer = True
                
            if doThisLayer:
                if (part.tag == 'circle'):
                    self.DrawCircle( xs, ys, part)
                elif (part.tag == 'rect'):
                    self.DrawRect( xs, ys, part)
                elif (part.tag == 'path'):
                    self.DrawPath(xs, ys, part)
                        
    def DrawAreaSymbol( self, xs, ys, layer, symbol):
        '''
        Draws a square and fills it accroding to the symbol specification

        Parameters
        ----------
        xs,ys : float
            Center of the sqaure
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
        for part in symbol:
            if (part.tag == 'path'):
                fill = part.attrib['fill']
                if (fill == layerId):
                    self.DrawLegendArea( xs, ys)
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
        for part in symbol:
            if (part.tag == 'path'):
                stroke = part.attrib['stroke']
                if (stroke == layerId):
                    lineLen = self.SetStrokeStyle( part)
                    self.DrawLegendLine( xs, ys, lineLen)
            # TODO: Add stroke decaration
                    
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


    def SetStrokeStyle( self, path):
        '''
        Sets up the basic stroke style before drawing a stroked path

        Parameters
        ----------
        path : xml path element
            holds stroke attributes to set up before drawing
        layer : xml layer element
            hols the color information for the specific symbol

        Returns
        -------
        The length of the line to be drawn in the legend such that complete
        dashes are shown at the end..

        '''

        lineLen = self.legend_width
       
        sWidth = float( path.attrib['stroke-width'])
        sCap = 0
        sJoin = 0
        sMiterLimit = 4
        
        

        sDashLen = 0
        sDash = []
        sDashOffset = 0
        if ('stroke-dasharray' in path.attrib):
            sDash = [float(x) for x in path.attrib['stroke-dasharray'].split(',')]
        if ('stroke-dashoffset' in path.attrib):
            sDashOffset = float( path.attrib['stroke-dashoffset'])
        if ('stroke-linecap' in path.attrib):
            sCap = ['but','round','square'].index( path.attrib['stroke-linecap'])
        if ('stroke-linejoin' in path.attrib):
            sJoin = ['miter','bevel','round'].index( path.attrib['stroke-linejoin'])
        if ('stroke-miterlimit' in path.attrib):
            sMiterLimit = float( path.attrib['stroke-miterlimit'])

        lineLen = CalcLineLengthFromDash( sDash, sDashOffset, lineLen)


        self.canvas.setLineWidth( sWidth)
        self.canvas.setDash( sDash, sDashOffset)
        self.canvas.setLineCap( sCap)
        self.canvas.setLineJoin( sJoin)
        self.canvas.setMiterLimit( sMiterLimit)
           
        # the dashes and and offset must be adjusted for each path, so the path will always
        # end in a complete dashed (with a possible offset). Not sure how to communicate this
        # to the drawing function, as I cannot find a getCurrentDash method in the canvas class
        
        # TODO: add stroke-linecap, stroke-linejoion
        
        return lineLen

        
        
    def DrawLegendArea( self, x, y):
        '''
        Draws a filled square using the current fill style centered at x, y

        Parameters
        ----------
        x, y : float

        Returns
        -------
        None.

        '''
        
        width = self.legend_width
        height = self.legend_height
        self.canvas.rect( x-width*0.5, y-height*0.5, width, height, fill=1, stroke=0)
    
    def DrawLegendHatch( self, xs, ys, hatch):
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

        Parameters
        ----------
        x, y: float

        Returns
        -------
        None.

        '''
        
        p = self.canvas.beginPath()
        p.moveTo( x - lineLen*0.5, y)
        p.lineTo( x + lineLen*0.5, y)
        self.canvas.drawPath( p)
        
        # TODO: This is just a straght line. Draw a more complex line to better
        # test stroke decorations.
        
        
    def DrawPath( self, xs, ys, path):
        '''
        Draw a path centered on xs, ys

        Parameters
        ----------
        xs, ys : float
            Centerpoint where to draw the path.
        path : xml/svg path element

        Returns
        -------
        None.

        '''
        self.canvas.saveState()
        self.canvas.translate( xs, ys)
        
        p = ParseSvgPath( self.canvas, path.attrib['d'])

        fill = 1 if "fill" in path.attrib else 0
        stroke = 1 if "stroke" in path.attrib else 0

        self.canvas.drawPath( p, fill = fill, stroke=stroke)
        self.canvas.restoreState()
        
        
    
    def DrawCircle( self, xs, ys, circle):
        '''
        Draws a circle centered at xs, ys.

        Parameters
        ----------
        xs, ys : float
            Center point for symbol
        circle : xml(svg) circle element
            holds x, y (offset) and radius

        Returns
        -------
        None.

        '''
    
        
        cx = xs + float(circle.attrib['cx'])
        cy = ys + float(circle.attrib['cy'])
        r = float(circle.attrib['r'])
        fill = 1 if "fill" in circle.attrib else 0
        stroke = 1 if "stroke" in circle.attrib else 0
        
        self.canvas.circle( cx, cy, r, fill=fill, stroke=stroke)
        
    def DrawRect( self, xs, ys, rect):
        '''
        Draws a rectangle at xs, ys

        Parameters
        ----------
        xs, ys : float
            Center point for the symbol
        rect : xml(svg) rect element
            holds position and style of rect

        Returns
        -------
        None.

        '''
        llx = xs + float(rect.attrib['x'])
        lly = ys + float(rect.attrib['y'])
        w = float( rect.attrib['width'])
        h = float( rect.attrib['height'])
        fill = 1 if "fill" in rect.attrib else 0
        stroke = 1 if "stroke" in rect.attrib else 0
        
        self.canvas.rect( llx, lly, w, h, fill=fill, stroke=stroke)
        


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

        
                               
            
        

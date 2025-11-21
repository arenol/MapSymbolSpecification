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
import math


class MSSLegendDrawer(object):
    '''
        Given a Map Symbol Specification (MSS) fil, this class will
        draw a Legend onto a canvas.
    '''
    
    # height and width of graphical legend elements
    legend_width = 14   # mm
    legend_height = 5   # mm
    
    # the vertical spacing between each line
    legend_vspacing = 8 # mm
    
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
                self.SetFillStyle( layer)
                doThisLayer = True
                
            if (stroke == layerId):
                self.SetStrokeStyle(part, layer)
                doThisLayer = True
                
            if doThisLayer:
                if (part.tag == 'circle'):
                    self.DrawCircle( xs, ys, part)
                elif (part.tag == 'rect'):
                    self.DrawRect( xs, ys, part)
            # TODO: add path and rect elements
                        
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
                    self.SetFillStyle( layer)
                    self.DrawLegendArea( xs, ys)
            # TODO: add hatch and pattern
                    
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
                    lineLen = self.SetStrokeStyle( part, layer)
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


    def SetStrokeStyle( self, path, layer):
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
        
        c, m, y, k, opacity, blend = self.GetLayerColor( layer)
        self.canvas.setStrokeColorCMYK( c, m, y, k)
        
        sWidth = float( path.attrib['stroke-width'])
        self.canvas.setLineWidth( sWidth)

        sDash = []
        sDashOffset = 0
        if ('stroke-dasharray' in path.attrib):
            sDash = [float(x) for x in path.attrib['stroke-dasharray'].split(',')]
        if ('stroke-dashoffset' in path.attrib):
            sDashOffset = float( path.attrib['stroke-dashoffset'])

        lineLen = self.CalcLineLengthFromDash( sDash, sDashOffset, lineLen)

    
        self.canvas.setDash( sDash, sDashOffset)
        # the dashes and and offset must be adjusted for each path, so the path will always
        # end in a complete dashed (with a possible offset). Not sure how to communicate this
        # to the drawing function, as I cannot find a getCurrentDash method in the canvas class
        
        # TODO: add stroke-linecap, stroke-linejoion
        
        return lineLen

    def SetFillStyle( self, layer):
        '''
        Sets the basic fill style for an area sumbol

        Parameters
        ----------
        layer : xml layer element
            holds the color and opcaity

        Returns
        -------
        None.

        '''
        
        c, m, y, k, opacity, blend = self.GetLayerColor( layer)
        
        self.canvas.setFillColorCMYK(c, m, y, k)
        
        # TODO: opacity and blend mode
        
        
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
        
        self.canvas.setFont( "Helvetica", 3)
        
        for symbol in self.symbols:
            symbolName = symbol.attrib['id'] + " " + symbol.attrib['name'] 
            print(  symbolName)
            self.canvas.drawString( x, y, symbolName)
            y -= dy
            
    def CalcLineLengthFromDash( self, dashArray, dashOffset, maxLen):
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
        
        
        
        
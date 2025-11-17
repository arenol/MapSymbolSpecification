import sys
import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from MSSLegendDrawing import *


def BailOut( errorMessage, params=None):
    '''
    Prints an error message and exits the program.
    The errorMessage may contain %-place holders, 
    and the params is a tuple with entries to insert.
    '''

    if params:
        errorMessage = errorMessage % params
        
    print( "ERROR:", errorMessage)
    sys.exit( 1)



def main():
    xmlFileName = "test-file.mms"
    
    xmlDom = ET.parse( xmlFileName)
    
    # check whether we have the correct element of the root of hte XML file
    xmlRoot = xmlDom.getroot()
    if (xmlRoot.tag != "MapSymbolsSpec"):
        BailOut("Element <MapSymbolsSpec> not found")
                
    xmlBaseColors = xmlRoot.find("BaseColors")
    if (xmlBaseColors == None):
        BailOut("Element <BaseColors> not found")
        
    xmlColorLayers = xmlRoot.find("ColorLayers")
    if (xmlColorLayers == None):
        BailOut("Element <ColorLayers> not found")

    xmlSymbols = xmlRoot.find("Symbols")
    if (xmlSymbols == None):
        BailOut("Element <Symbols> not found")

    # pageSize is A4 in points
    pdfFileName = "Legend.pdf"

    theCanvas = canvas.Canvas( pdfFileName, pagesize=A4)
    theCanvas.scale(mm, mm)
    
    legendDrawer = MSSLegendDrawer( theCanvas, xmlBaseColors, xmlColorLayers, xmlSymbols)
    legendDrawer.DrawSymbols()
    
    theCanvas.showPage()

    
    theCanvas.save();
    
    print( "Done! Result printed to", pdfFileName)
    

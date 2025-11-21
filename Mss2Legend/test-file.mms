<?xml version="1.0" encoding="utf-8"?>
<MapSymbolsSpec id="ISOM2017-2" version="6" language="en" issued-date="2024-15-01" valid-date="2025-01-01" mapscale="15000">
    <BaseColors>
        <color id="BLACK" cmyk="0,0,0,1"/>
        <color id="BROWN" cmyk="0.25,0.75,1,0"/>
    </BaseColors>
    <ColorLayers>
        <layer id="black100" color="BLACK"/>
        <layer id="brown100" color="BROWN"/>
        <layer id="black35" color="BLACK" tint="0.35" />
    </ColorLayers>
    <Symbols>
        <symbol type="line" id="103" name="Form line">
            <path stroke="brown100" stroke-width="0.1" stroke-dasharray="2,0.2" stroke-dashoffset="1"/>
        </symbol>
		<symbol type="point" id="204" name="Boulder">
            <description>A distinct boulder (should be higher than 1 m)</description>
            <circle cx="0" cy="0" r="0.2" fill="black100" />
        </symbol>
        <symbol type="area" id="214" name="Bare rock">
            <path fill="black35"/>
        </symbol>
        <symbol type="line" id="505" name="Footpath">
            <path stroke="black100" stroke-width="0.25" stroke-dasharray="2.0, 0.25" />
        </symbol>
        <symbol type="point" id="523" name="Ruin">
            <rect stroke="black100" stroke-width="0.16" x="-0.32" y="-0.32" width="0.64" height="0.64" />
        </symbol>
            
    </Symbols>
</MapSymbolsSpec>

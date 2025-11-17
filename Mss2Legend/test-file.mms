<?xml version="1.0" encoding="utf-8"?>
<MapSymbolsSpec id="ISOM2017-2" version="6" language="en" issued-date="2024-15-01" valid-date="2025-01-01" mapscale="15000">
    <BaseColors>
        <color id="BLACK" cmyk="0,0,0,1"/>
    </BaseColors>
    <ColorLayers>
        <layer id="black100" color="BLACK"/>
        <layer id="black35" color="BLACK" tint="0.35" />
    </ColorLayers>
    <Symbols>
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
            
    </Symbols>
</MapSymbolsSpec>

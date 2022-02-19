
class NMScenarioMixin(object):
    terrain='asbuilt'
    
class NMScenario1Mixin(NMScenarioMixin):
    """
    Low Footprint

    1. Remove main culverts and replace levee. Add 1-2 12”-24” culverts
    above MHHW to allow freshwater into the NM during high lagoon
    stand. For modeling purposes these will be open. MHHW taken as 5.9' NAVD
    (=1.80m) per ESA QCM memo. Place invert of the new culverts at MHHW+1ft
    (=2.10m), with 2 12" culverts.

    2. Remove/fill culvert that drains south drainage ditch

    3. Remove tidal influence in the ditch on the north side of North Marsh.
    The scenario description discusses removing the levee and using that dirt
    to fill the ditch in the vicinity of the existing culvert. For modeling
    purposes just close/remove the culvert.

    4. Lower the upstream-most portion of the levee separating Pescadero Creek
    and North Marsh down to 3.25m, near level of adjacent marsh
    """
    tag='nm1'

    
class NMScenario2Mixin(NMScenarioMixin):
    """
    Medium Footprint

    Lower the levee to 2.75m:
     - from downstream side of turtle bend
       to the east to the dune rise on the west,
     - upstream of turtle bend (same as in scenario 1)   
    (goal is above MHHW and near elevation of surrounding marsh).

    Remove main culverts and fill to same level, 2.75m.

    Remove culvert from south drainage ditch and fill.

    Remove the low levee

    Fill main channel to MHHW (1.80m), from the main culverts to the 
    culverts on the north side.
    """
    tag='nm2'
    
class NMScenario3Mixin(NMScenarioMixin):
    """
    Large Footprint

    Same as 2

    Also lower levee at turtle bend, to 3.0m (slightly higher than
    adjacent sections since the surrounding surface is higher).

    Widen the main tidal channel at the same time as filling to
    MHHW.

    Fill portions of north and south drainage ditches to surrounding
    marsh elevation.
    """


    

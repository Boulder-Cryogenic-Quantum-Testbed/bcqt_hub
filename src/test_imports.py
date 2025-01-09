"""
    Used for testing the package import

    listing all __init__.py's:
    
    ** bcqt_hub
        -- src
            -- drivers
                -- instruments
                    -->> Spectrum Analyzers, Signal Gens, VNA, etc.
                -- misc
                    -->> minicircuits circuits, cryoswitch controller
            -- modules
                    -->> BaseConfig.py, DataXYZ.py
"""

import sys

sys.path.append(r"C:\\Users\\Lehnert Lab\\GitHub")

import bcqt_hub

def ddir(module):
    ddir = [x for x in dir(module) if "__" not in x]
    return f"{module.__name__}  -> {ddir}"


display(ddir(bcqt_hub))
display(ddir(bcqt_hub.modules))
display(ddir(bcqt_hub.drivers))



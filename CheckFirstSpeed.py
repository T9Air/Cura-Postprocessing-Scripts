#------------------------------------------------------------------------------------------------------------------------------------
#
# Cura PostProcessing Script
# Author:   5axes
# Date:     January 06, 2024
#
# Description:  postprocessing script to modifiy the first layer infill and Check the first Wall Speed Bug Cura 5.6 
#
#------------------------------------------------------------------------------------------------------------------------------------
#
#   Version 1.0 06/01/2024
#
#------------------------------------------------------------------------------------------------------------------------------------

from ..Script import Script
from UM.Logger import Logger
from UM.Application import Application
import re # To perform the search
from enum import Enum

__version__ = '1.0'

class Section(Enum):
    """Enum for section type."""

    NOTHING = 0
    SKIRT = 1
    INNER_WALL = 2
    OUTER_WALL = 3
    INFILL = 4
    SKIN = 5
    SKIN2 = 6

def is_begin_layer_line(line: str) -> bool:
    """Check if current line is the start of a layer section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a layer section
    """
    return line.startswith(";LAYER:")

def is_begin_type_line(line: str) -> bool:
    """Check if current line is the start of a new type section.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of a new type section
    """
    return line.startswith(";TYPE:")
    
def is_retract_line(line: str) -> bool:
    """Check if current line is a retract segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a retract segment
    """
    return "G1" in line and "F" in line and "E" in line and not "X" in line and not "Y" in line and not "Z" in line
    
def is_extrusion_line(line: str) -> bool:
    """Check if current line is a standard printing segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a standard printing segment
    """
    return "G1" in line and "X" in line and "Y" in line and "E" in line

def is_not_extrusion_line(line: str) -> bool:
    """Check if current line is a rapid movement segment.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is a standard printing segment
    """
    return "G0" in line and "X" in line and "Y" in line and not "E" in line

def is_begin_skin_segment_line(line: str) -> bool:
    """Check if current line is the start of an skin.

    Args:
        line (str): Gcode line

    Returns:
        bool: True if the line is the start of an skin section
    """
    return line.startswith(";TYPE:SKIN")
    
class CheckFirstSpeed(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Check First Speed",
            "key": "CheckFirstSpeed",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "infillspeed":
                {
                    "label": "First layer infill speed",
                    "description": "First layer infill speed value.",
                    "type": "float",
                    "unit": "mm/s",
                    "default_value": 30,
                    "minimum_value": 1,
                    "maximum_value": 100,
                    "maximum_value_warning": 50
                },
                "checkwallspeed":
                {
                    "label": "Check Wall Speed",
                    "description": "Option to test wall speed on first layer (Cura 5.6 bug fix).",
                    "type": "bool",
                    "default_value": true
                }                
            }
        }"""

    def execute(self, data):

        InfillSpeed = float(self.getSettingValueByKey("infillspeed")) * 60
        CheckFirestWallSpeed = bool(self.getSettingValueByKey("checkwallspeed"))


        idl=0
        
        for layer in data:
            layer_index = data.index(layer)
            
            lines = layer.split("\n")
            for line in lines:                  
               
                if is_begin_layer_line(line):
                    # Logger.log('d', 'layer_index : {:d}'.format(layer_index))
                    # Logger.log('d', 'layer_lines : {}'.format(line))
                    if line.startswith(";LAYER:0"):
                        idl=1
                    else :
                        idl=0
                
                if is_begin_type_line(line) and idl > 0:
                    if is_begin_skin_segment_line(line):
                        idl=2
                        ReplaceSpeedInstruction="F" + str(InfillSpeed)
                    elif is_begin_inner_wall_segment_line(line) and  :
                        idl=2
                        ReplaceSpeedInstruction="F" + str(speed_print_layer_0)                        
                    elif is_begin_outer_wall_segment_line(line) and  :
                        idl=2
                        ReplaceSpeedInstruction="F" + str(speed_print_layer_0)                       
                    else :
                        idl=1
                
                if idl >= 2 and is_extrusion_line(line):
                    searchF = re.search(r"F(\d*\.?\d*)", line)
                    if searchF:
                        line_index = lines.index(line)
                        save_F=float(searchF.group(1)) 
                        instructionF="F"+str(searchF.group(1))
                        Logger.log('d', 'save_F       : {:f}'.format(save_F))
                        Logger.log('d', 'line : {}'.format(line))
                        Logger.log('d', 'line replace : {}'.format(line.replace(instructionF,ReplaceSpeedInstruction)))
                        lines[line_index]=line.replace(instructionF,ReplaceSpeedInstruction)
                        
            result = "\n".join(lines)
            data[layer_index] = result

        return data

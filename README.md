# Krita Separate Brush and Eraser
Makes Krita treat the brush and eraser as if they're separate tools. The brush and eraser keep track of presets, size, opacity, flow, etc separately.
All added functions can be found under Tools > Separate Brush and Eraser in the shortcuts menu.
- Activate Eraser: Turns the eraser on for the current tool and switches over to the current eraser preset
- Activate Brush: Turns the brush on for the current tool and switches over to the current brush preset
- Toggle Eraser: Toggles the eraser for the current tool without switching brush presets.
- Switch to Brush: Switches to the brush tool in brush mode and switches over to the current brush preset
- Switch to Eraser: Switches to the brush tool in erase mode and switches over to the current eraser preset

If you click the eraser in the top bar, the eraser will toggle on/off for the current tool without changing presets (ie. what Krita does by default).

If you switch from the brush tool to another tool the eraser will automatically be deactivated unless you're holding shift.

**Input adapter library taken from shortcuts composer**

## Installation

Download [separatebrusheraser.zip](http://github.com/dninosores/krita-separate-brush-eraser/releases/latest/download/separatebrusheraser.zip) and install by going to `Tools > Scripts > Import Python Plugin From File...` in Krita and selecting the zip file.

If you're having issues, more information on plugin installation can be found [here](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html).

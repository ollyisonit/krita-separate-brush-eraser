# Krita Export Region
Adds an "Export Region..." option to the file menu that allows you to only export the contents of a selected region. If no region is selected, then it will crop the image to fit the bounds of the currently selected layer.

## Examples
Running "Export Region..." with an area selected will export an image cropped to the selected area. For example, the following selection:

![image](./resources/face-selected.PNG)

Would export this:

![image](./resources/face-region.png)

If you don't have an area selected, the image will be cropped to whatever layer is currently selected. For example, if we have the BoundingBox layer selected:

![image](./resources/face-no-selection.PNG)

Then the exported image would be this:

![image](./resources/box-region.png)

## Installation

Download [krita-export-region.zip](http://github.com/dninosores/krita-export-region/releases/latest/download/krita-export-region.zip) and install by going to `Tools > Scripts > Import Python Plugin From File...` in Krita and selecting the zip file. Once the plugin is installed, you can manage shortcuts in the shortcuts menu under `Scripts > Export Region`. 

If you're having issues, more information on plugin installation can be found [here](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html).

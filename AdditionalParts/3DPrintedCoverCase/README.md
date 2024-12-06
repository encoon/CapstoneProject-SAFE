This folder contains the following files:

Authors: Taehoon Kim, Nicholas Eloff, Thomas Green, and Inhyup Lee
Date: December 06, 2024

(Explanations of the files)
Design files for cover case will be saved in this folder. (Additional explanation down here.)

1. Circuit_case.stl (generated from "Fusion 360"): It contains the 3D geometry of the circuit case in STL format. It provides detailed information about the model, including its dimensions, volume, surface area, and mesh details. The model is watertight, making it suitable for 3D printing, but it contains some concave features.

2. Circuit_Case.gcode (generated from "PrusaSlicer"): It is the G-code file with specific machine instructions for 3D printing the circuit case. This file includes paths for extrusion, travel movements, and layer-by-layer instructions optimized for FDM printers. It is ready to be used directly with a compatible 3D printer (Marriott library 3d printer).


After slicing the stl file in slicer software, must ensure the G-code file is compatible with specific 3D printer model and adjust settings based on the material being used or set the bundle file which is designed to use with specific 3D printer.
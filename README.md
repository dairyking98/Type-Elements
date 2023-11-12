# 3D Printed Type Elements for Typewriters
## Downloading and Configuring OpenSCAD
Download a development snapshot of [OpenSCAD.](https://openscad.org/downloads.html#snapshot)
Open OpenSCAD and make the following changes:
- Edit > Preferences > Features
  - enable fast-csg
  - enable lazy-union

## Opening an OpenSCAD file
Upon opening an OpenSCAD file, a preview render will automatically take place which can take a few seconds to a minute. These models are highly complex and can take hours to render. Upon preview completion, uncheck `Automatic preview` in the top right under the Customizer window. Changes can now be made to the Customizer, and once the changes are made, another preview can be made with `(F5)` or the preview button.

## Creating a Custom Element
1. Install a custom font by right clicking on your font file > Install for all users.
2. Open `TypeHeightFinder.scad` and find the ideal Type Size for your particular font and specifications and note the value.
3. Open an element file and disable the Automatic preview. Update the Customizer with the font specifications and values.
4. Preview the element to ensure it looks successful. By default a `Debug No Minkowski` checkbox is placed in the customizer to save on preview times due to the CPU intensive draft angle calculation.

## Rendering a Custom Element
1. Once the preview is satisfactory, `Debug No Minkowski` may be unchecked, and `(F6)` or the render button may pressed to commence final rendering. This may take hours.
2. Upon rendering completion, save the 3D model as an STL using the STL button at the Editor toolbar. 
Some presets for certain fonts may exist and be saved in Customizer profiles.



//Shared Resin Support placement system (v2.0 lib) - cylinder machines only
//(Blick/Postal). Extracted from Blickensderfer2.scad / Postal.scad. Per
//docs/resin-supports.md this pattern (CutGroove breakaway, bottomZ
//sloped-surface calc) is specific to the cylinder machine family - do not
//include this from Hammond/IBM, which keep their own angle-aware rod
//systems. The single-rod primitive itself (ResinRod()) lives in
//resin_rod.scad (included below) since it's universal - Bennett/Mignon
//include just that file directly, without this placement layer.
//
//Include this AFTER the machine file has defined its own globals, same rule
//as glyph_pipeline.scad.
//
//Required from including machine file (beyond resin_rod.scad's own list):
//  Surface_Fn
//  Element_Diameter, Shaft_Diameter, Core_Chamfer, Core_Bottom_Offset, Wall_Min_Thickness, Wall_Chamfer
//  Speed_Hole_Qty, Speed_Hole_Radial, Speed_Hole_ID
//  Resin_Groove_OD, Resin_Groove_Thickness
//
//Optional (lib supplies a default if the machine file leaves these undefined):
//  Resin_Rod_Raft            - whether ResinRod() grows its own small raft disk.
//                            Default true (Blickensderfer2's behavior). Postal
//                            sets this false because its CutGroove() polygon
//                            extends to the element's center axis and forms
//                            one continuous shared raft instead - the two
//                            settings are a matched pair, not independent.
//  Cut_Groove_Inner_X          - inner-X coordinate of CutGroove()'s profile
//                            polygon, in the frame before the wall-radius
//                            translate. Default 0 (Blickensderfer2: thin ring
//                            at the wall only). Postal uses -Element_Diameter/2+Wall_Min_Thickness
//                            (extends the profile to X=0 absolute, i.e. the
//                            full center-to-wall raft disk described above).
//  Bottom_Support_Fractions   - list of fractions along [a,b] (core-chamfer-edge
//                            to outer-wall) at which BottomSupports() places a
//                            rod per sector. Default [.2] (Blickensderfer2:
//                            one rod at 20%). Postal uses [0,.25,.5,.75,1]
//                            (five rods spanning the full sloped floor).
//  Bottom_Support_Inner_Angle_Offset - angular offset (in sectors) for the
//                            near-core rod in BottomSupports(). Default .5
//                            (Blickensderfer2). Postal uses 0.

include <resin_rod.scad>

//function for obtaining z height of radial point X on the bottom sloped
//section of the element
Bottom_Slope=Core_Bottom_Offset/((Shaft_Diameter/2+Wall_Min_Thickness+Wall_Chamfer)-(Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer));
Bottom_Z_Offset=-Bottom_Slope*(Shaft_Diameter/2+Wall_Min_Thickness+Wall_Chamfer)+Core_Bottom_Offset;
function bottomZ(X)=Bottom_Slope*X+Bottom_Z_Offset;
function bottomX(Z)=(Z-Bottom_Z_Offset)/Bottom_Slope;

module CutGroove(){
    $fn=Surface_Fn;
    _innerX = is_undef(Cut_Groove_Inner_X) ? 0 : Cut_Groove_Inner_X;
    rotate_extrude()
    translate([Element_Diameter/2-Wall_Min_Thickness, 0, 0])
    difference(){
        polygon([[_innerX, -Resin_Min_Rod_Height-Resin_Raft_Thickness], [_innerX, -Resin_Min_Rod_Height], [Wall_Min_Thickness-Resin_Groove_OD-Resin_Groove_Thickness, -Resin_Groove_OD], [Wall_Min_Thickness-Resin_Groove_OD-Resin_Groove_Thickness, z], [Wall_Min_Thickness, z], [Wall_Min_Thickness, -Resin_Min_Rod_Height], [Wall_Min_Thickness+Resin_Raft_Thickness, -Resin_Min_Rod_Height], [Wall_Min_Thickness, -Resin_Min_Rod_Height-Resin_Raft_Thickness]]);
        translate([Wall_Min_Thickness, -Resin_Groove_OD/2])
        circle(d=Resin_Groove_OD);
        translate([Wall_Min_Thickness-Resin_Groove_OD-Resin_Groove_Thickness, -Resin_Groove_OD/2])
        circle(d=Resin_Groove_OD);
   }
}

module SpeedHoleSupport(){
    translate([Speed_Hole_Radial+Speed_Hole_ID/2+Resin_Tip_OD/2, 0, 0])
    ResinRod(bottomZ(Speed_Hole_Radial+Speed_Hole_ID/2+Resin_Tip_OD/2));
    translate([Speed_Hole_Radial-Speed_Hole_ID/2-Resin_Tip_OD/2, 0, 0])
    ResinRod(bottomZ(Speed_Hole_Radial-Speed_Hole_ID/2+-Resin_Tip_OD/2));
    translate([Speed_Hole_Radial, Speed_Hole_ID/2+Resin_Tip_OD/2, 0])
    ResinRod(bottomZ((Speed_Hole_Radial^2+(Speed_Hole_ID/2+Resin_Tip_OD/2)^2)^.5));
    translate([Speed_Hole_Radial, -Speed_Hole_ID/2-Resin_Tip_OD/2, 0])
    ResinRod(bottomZ((Speed_Hole_Radial^2+(-Speed_Hole_ID/2-Resin_Tip_OD/2)^2)^.5));
}

module SpeedHoleSupports(){
    for (n=[0:Speed_Hole_Qty-1])
    if (n!=0)
    rotate([0, 0, 360/Speed_Hole_Qty*n])
    SpeedHoleSupport();
}

//generic cardinal-point support around a rectangular (or, with equal half
//extents, circular) footprint at a given radial position - covers both
//Blickensderfer2's drive-pin countersink (circular, halfExtentX=halfExtentY)
//and Postal's drive pin (rectangular, halfExtentX=drivePinLength/2,
//halfExtentY=drivePinWidth/2). Machine file computes radius/halfExtents.
module DrivePinSupport(radius, halfExtentX, halfExtentY){
    translate([radius+halfExtentX+Resin_Tip_OD/2, 0, 0])
    ResinRod(bottomZ(radius+halfExtentX+Resin_Tip_OD/2));
    translate([radius-halfExtentX-Resin_Tip_OD/2, 0, 0])
    ResinRod(bottomZ(radius-halfExtentX-Resin_Tip_OD/2));
    translate([radius, halfExtentY+Resin_Tip_OD/2, 0])
    ResinRod(bottomZ((radius^2+(halfExtentY+Resin_Tip_OD/2)^2)^.5));
    translate([radius, -halfExtentY-Resin_Tip_OD/2, 0])
    ResinRod(bottomZ((radius^2+(-halfExtentY-Resin_Tip_OD/2)^2)^.5));
}

module BottomSupports(){
    _fractions = is_undef(Bottom_Support_Fractions) ? [.2] : Bottom_Support_Fractions;
    _innerAngleOffset = is_undef(Bottom_Support_Inner_Angle_Offset) ? .5 : Bottom_Support_Inner_Angle_Offset;
    for (n=[0:Speed_Hole_Qty-1]){
        rotate([0, 0, (n+.5)*360/Speed_Hole_Qty]){
            a=bottomX(Core_Bottom_Offset);
            b=Element_Diameter/2-Wall_Min_Thickness-Wall_Chamfer;
            for (f=_fractions)
            translate([a+(b-a)*f, 0, 0])
            ResinRod(bottomZ(a+(b-a)*f));
        }
        rotate([0, 0, (n+_innerAngleOffset)*360/Speed_Hole_Qty])
        translate([Shaft_Diameter/2+Core_Chamfer+Resin_Tip_OD/2, 0, 0])
        ResinRod(Core_Bottom_Offset);
    }
}

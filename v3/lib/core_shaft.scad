//Shared Core/Shaft Groove System (v2.0 lib)
//Extracted from Blickensderfer2.scad / Postal.scad / BennettElement.scad -
//all three use the exact same polygon/twist/chamfer formulas for the shaft
//bore's friction grooves and secondary-core taper, differing only in which
//two Z landmarks bound the region (and Bennett skips the top chamfer, which
//sits under a clip on Blick/Postal but Bennett has no clip).
//
//Include this AFTER the machine file has defined its own globals.
//
//Required from including machine file:
//  z, Surface_Fn, Groove_Fn
//  Core_Groove_Qty, Core_Groove_D, Core_Chamfer, Core_Contact_Length,
//  Core_Secondary_ID_Offset, Core_Web_Qty, Core_Web_Width, Core_Web_Length
//  Shaft_Diameter            - shaft/core diameter, same canonical name Bennett
//                             always used natively; Blick2/Postal's coreID
//                             (itself derived from coreIDin+coreIDOffset) bridges
//                             to this.
//  Core_Top_Z, Core_Bottom_Z     - the absolute top/bottom Z landmarks (Blick2/
//                             Postal: Element_Height+clipHeight and
//                             Core_Bottom_Offset; Bennett: Element_Height-
//                             Top_Countersink_Depth-1+s and Bottom_Countersink_Depth).
//                             Used for CoreGrooves' full extrude span and
//                             CoreChamfer's two chamfer positions.
//
//Optional (lib supplies a default if the machine file leaves these undefined):
//  Core_Taper_Top_Z              - the secondary-core taper's OWN top landmark,
//                             which is NOT always the same as Core_Top_Z: on
//                             Blick2/Postal this is plain Element_Height (i.e.
//                             Core_Top_Z minus clipHeight - the taper stops
//                             below the clip), while Bennett has no clip so
//                             its taper top coincides with the absolute top.
//                             Default: same as Core_Top_Z (Bennett's case).
//                             Blick2/Postal must set this explicitly to
//                             Element_Height.
//  Core_Chamfer_Top             - whether CoreChamfer() also chamfers the top
//                             (Blick2/Postal: true, under the clip). Default
//                             true. Bennett sets false (original had no top
//                             chamfer call at all).

module SecondaryCore(Offset){
    $fn=Surface_Fn;
    _taperTopZ = is_undef(Core_Taper_Top_Z) ? Core_Top_Z : Core_Taper_Top_Z;
    rotate_extrude(){
        polygon([[0, Core_Bottom_Z+Core_Contact_Length], [0, Core_Top_Z], [Shaft_Diameter/2+Offset/2+Core_Secondary_ID_Offset, Core_Top_Z], [Shaft_Diameter/2+Offset/2+Core_Secondary_ID_Offset, _taperTopZ], [Shaft_Diameter/2+Offset/2, _taperTopZ-Core_Secondary_ID_Offset], [Shaft_Diameter/2+Offset/2, _taperTopZ-Core_Contact_Length], [Shaft_Diameter/2+Offset/2+Core_Secondary_ID_Offset, _taperTopZ-Core_Contact_Length-Core_Secondary_ID_Offset], [Shaft_Diameter/2+Offset/2+Core_Secondary_ID_Offset, Core_Bottom_Z+Core_Contact_Length+Core_Secondary_ID_Offset], [Shaft_Diameter/2+Offset/2, Core_Bottom_Z+Core_Contact_Length]]);
    }
}

module CoreGrooves(Offset){
    //extrude height is measured from this module's own Z=0 (not from
    //Core_Bottom_Z) up to Core_Top_Z, matching the original Blick2/Postal/Bennett
    //modules exactly - verified this reduces to their literal cylHeight+
    //clipHeight+2*z / Element_Height-Top_Countersink_Depth-1+s+2*z expressions.
    for (n=[0:Core_Groove_Qty-1]){
        rotate([0, 0, 360/Core_Groove_Qty*n])
        linear_extrude(Core_Top_Z+2*z, twist=360*(Core_Top_Z-Core_Bottom_Z+2*z)/(PI*(Shaft_Diameter+Offset))*(n%2==0?1:-1), $fn=Surface_Fn)
        translate([Shaft_Diameter/2+Offset/2, 0, -z])
        translate([0, 0, -z])
        circle(d=Core_Groove_D, $fn=Groove_Fn);
    }
}

module CoreChamferShape(Offset){
    cylinder(d1=Shaft_Diameter+Offset+2*Core_Chamfer, d2=Shaft_Diameter+Offset, h=Core_Chamfer+z, $fn=Surface_Fn);
}

module CoreChamfer(Offset){
    _chamferTop = is_undef(Core_Chamfer_Top) ? true : Core_Chamfer_Top;
    translate([0, 0, Core_Bottom_Z-z])
    CoreChamferShape(Offset);
    if (_chamferTop)
    translate([0, 0, Core_Top_Z+z])
    rotate([180, 0, 0])
    CoreChamferShape(Offset+Core_Secondary_ID_Offset/2);
}

module CoreEllipses(){
    $fn=Surface_Fn;
    _taperTopZ = is_undef(Core_Taper_Top_Z) ? Core_Top_Z : Core_Taper_Top_Z;
    for (n=[0:Core_Web_Qty-1])
    rotate([0, 0, n*360/Core_Web_Qty])
    translate([0, 0, Core_Bottom_Z+(_taperTopZ-Core_Bottom_Z)/2-Core_Web_Length/2])
    rotate([90, 0, 90])
    hull(){
        translate([0, Core_Web_Width/2, 0])
        cylinder(d=Core_Web_Width, h=5);
        translate([0, Core_Web_Length-Core_Web_Width/2, 0])
        cylinder(d=Core_Web_Width, h=5);
    }
}

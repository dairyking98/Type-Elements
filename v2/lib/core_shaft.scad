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
//  z, surfaceFn, grooveFn
//  coreGrooveQty, coreGrooveD, coreChamfer, coreContactLength,
//  coreSecondaryIDOffset, coreWebQty, coreWebWidth, coreWebLength
//  Shaft_Diameter            - shaft/core diameter, same canonical name Bennett
//                             always used natively; Blick2/Postal's coreID
//                             (itself derived from coreIDin+coreIDOffset) bridges
//                             to this.
//  coreTopZ, coreBottomZ     - the absolute top/bottom Z landmarks (Blick2/
//                             Postal: Element_Height+clipHeight and
//                             coreBottomOffset; Bennett: Element_Height-
//                             Top_Countersink_Depth-1+s and Bottom_Countersink_Depth).
//                             Used for CoreGrooves' full extrude span and
//                             CoreChamfer's two chamfer positions.
//
//Optional (lib supplies a default if the machine file leaves these undefined):
//  coreTaperTopZ              - the secondary-core taper's OWN top landmark,
//                             which is NOT always the same as coreTopZ: on
//                             Blick2/Postal this is plain Element_Height (i.e.
//                             coreTopZ minus clipHeight - the taper stops
//                             below the clip), while Bennett has no clip so
//                             its taper top coincides with the absolute top.
//                             Default: same as coreTopZ (Bennett's case).
//                             Blick2/Postal must set this explicitly to
//                             Element_Height.
//  coreChamferTop             - whether CoreChamfer() also chamfers the top
//                             (Blick2/Postal: true, under the clip). Default
//                             true. Bennett sets false (original had no top
//                             chamfer call at all).

module SecondaryCore(Offset){
    $fn=surfaceFn;
    _taperTopZ = is_undef(coreTaperTopZ) ? coreTopZ : coreTaperTopZ;
    rotate_extrude(){
        polygon([[0, coreBottomZ+coreContactLength], [0, coreTopZ], [Shaft_Diameter/2+Offset/2+coreSecondaryIDOffset, coreTopZ], [Shaft_Diameter/2+Offset/2+coreSecondaryIDOffset, _taperTopZ], [Shaft_Diameter/2+Offset/2, _taperTopZ-coreSecondaryIDOffset], [Shaft_Diameter/2+Offset/2, _taperTopZ-coreContactLength], [Shaft_Diameter/2+Offset/2+coreSecondaryIDOffset, _taperTopZ-coreContactLength-coreSecondaryIDOffset], [Shaft_Diameter/2+Offset/2+coreSecondaryIDOffset, coreBottomZ+coreContactLength+coreSecondaryIDOffset], [Shaft_Diameter/2+Offset/2, coreBottomZ+coreContactLength]]);
    }
}

module CoreGrooves(Offset){
    //extrude height is measured from this module's own Z=0 (not from
    //coreBottomZ) up to coreTopZ, matching the original Blick2/Postal/Bennett
    //modules exactly - verified this reduces to their literal cylHeight+
    //clipHeight+2*z / Element_Height-Top_Countersink_Depth-1+s+2*z expressions.
    for (n=[0:coreGrooveQty-1]){
        rotate([0, 0, 360/coreGrooveQty*n])
        linear_extrude(coreTopZ+2*z, twist=360*(coreTopZ-coreBottomZ+2*z)/(PI*(Shaft_Diameter+Offset))*(n%2==0?1:-1), $fn=surfaceFn)
        translate([Shaft_Diameter/2+Offset/2, 0, -z])
        translate([0, 0, -z])
        circle(d=coreGrooveD, $fn=grooveFn);
    }
}

module CoreChamferShape(Offset){
    cylinder(d1=Shaft_Diameter+Offset+2*coreChamfer, d2=Shaft_Diameter+Offset, h=coreChamfer+z, $fn=surfaceFn);
}

module CoreChamfer(Offset){
    _chamferTop = is_undef(coreChamferTop) ? true : coreChamferTop;
    translate([0, 0, coreBottomZ-z])
    CoreChamferShape(Offset);
    if (_chamferTop)
    translate([0, 0, coreTopZ+z])
    rotate([180, 0, 0])
    CoreChamferShape(Offset+coreSecondaryIDOffset/2);
}

module CoreEllipses(){
    $fn=surfaceFn;
    _taperTopZ = is_undef(coreTaperTopZ) ? coreTopZ : coreTaperTopZ;
    for (n=[0:coreWebQty-1])
    rotate([0, 0, n*360/coreWebQty])
    translate([0, 0, coreBottomZ+(_taperTopZ-coreBottomZ)/2-coreWebLength/2])
    rotate([90, 0, 90])
    hull(){
        translate([0, coreWebWidth/2, 0])
        cylinder(d=coreWebWidth, h=5);
        translate([0, coreWebLength-coreWebWidth/2, 0])
        cylinder(d=coreWebWidth, h=5);
    }
}

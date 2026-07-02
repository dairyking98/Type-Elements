//Shared Resin Support System (v2.0 lib) - cylinder machines only (Blick/Postal)
//Extracted from Blickensderfer2.scad / Postal.scad. Per docs/resin-supports.md
//this pattern (CutGroove breakaway, bottomZ sloped-surface calc) is specific
//to the cylinder machine family - do not include this from Hammond/IBM, which
//keep their own angle-aware rod systems.
//
//Include this AFTER the machine file has defined its own globals, same rule
//as glyph_pipeline.scad.
//
//Required from including machine file:
//  z, resinFn, surfaceFn
//  Element_Diameter, Shaft_Diameter, coreChamfer, coreBottomOffset, wallMinThickness, wallChamfer
//  speedHoleQty, speedHoleRadial, speedHoleID
//  resinTipOD, resinTipL, resinRodOD, resinInset, resinMinRodHeight,
//  resinRaftOD, resinRaftThickness, resinGrooveOD, resinGrooveThickness
//
//Optional (lib supplies a default if the machine file leaves these undefined):
//  resinRodRaft            - whether ResinRod() grows its own small raft disk.
//                            Default true (Blickensderfer2's behavior). Postal
//                            sets this false because its CutGroove() polygon
//                            extends to the element's center axis and forms
//                            one continuous shared raft instead - the two
//                            settings are a matched pair, not independent.
//  cutGrooveInnerX          - inner-X coordinate of CutGroove()'s profile
//                            polygon, in the frame before the wall-radius
//                            translate. Default 0 (Blickensderfer2: thin ring
//                            at the wall only). Postal uses -Element_Diameter/2+wallMinThickness
//                            (extends the profile to X=0 absolute, i.e. the
//                            full center-to-wall raft disk described above).
//  bottomSupportFractions   - list of fractions along [a,b] (core-chamfer-edge
//                            to outer-wall) at which BottomSupports() places a
//                            rod per sector. Default [.2] (Blickensderfer2:
//                            one rod at 20%). Postal uses [0,.25,.5,.75,1]
//                            (five rods spanning the full sloped floor).
//  bottomSupportInnerAngleOffset - angular offset (in sectors) for the
//                            near-core rod in BottomSupports(). Default .5
//                            (Blickensderfer2). Postal uses 0.

//function for obtaining z height of radial point X on the bottom sloped
//section of the element
bottomSlope=coreBottomOffset/((Shaft_Diameter/2+wallMinThickness+wallChamfer)-(Element_Diameter/2-wallMinThickness-wallChamfer));
bottomZOffset=-bottomSlope*(Shaft_Diameter/2+wallMinThickness+wallChamfer)+coreBottomOffset;
function bottomZ(X)=bottomSlope*X+bottomZOffset;
function bottomX(Z)=(Z-bottomZOffset)/bottomSlope;

module ResinRod(h){
    $fn=resinFn;
    _raft = is_undef(resinRodRaft) ? true : resinRodRaft;
    hull(){
        translate([0, 0, -resinTipOD/2+resinInset+h]){
            sphere(d=resinTipOD);
            translate([0, 0, -resinTipL])
            sphere(d=resinRodOD);
        }
        translate([0, 0, -resinMinRodHeight-resinRaftThickness+resinRodOD/2+z])
        sphere(d=resinRodOD);
    }
    if (_raft)
    translate([0, 0, -resinMinRodHeight-resinRaftThickness])
    cylinder(d1=resinRaftOD, d2=resinRaftOD+1*resinRaftThickness, h=resinRaftThickness);
}

module CutGroove(){
    $fn=surfaceFn;
    _innerX = is_undef(cutGrooveInnerX) ? 0 : cutGrooveInnerX;
    rotate_extrude()
    translate([Element_Diameter/2-wallMinThickness, 0, 0])
    difference(){
        polygon([[_innerX, -resinMinRodHeight-resinRaftThickness], [_innerX, -resinMinRodHeight], [wallMinThickness-resinGrooveOD-resinGrooveThickness, -resinGrooveOD], [wallMinThickness-resinGrooveOD-resinGrooveThickness, z], [wallMinThickness, z], [wallMinThickness, -resinMinRodHeight], [wallMinThickness+resinRaftThickness, -resinMinRodHeight], [wallMinThickness, -resinMinRodHeight-resinRaftThickness]]);
        translate([wallMinThickness, -resinGrooveOD/2])
        circle(d=resinGrooveOD);
        translate([wallMinThickness-resinGrooveOD-resinGrooveThickness, -resinGrooveOD/2])
        circle(d=resinGrooveOD);
   }
}

module SpeedHoleSupport(){
    translate([speedHoleRadial+speedHoleID/2+resinTipOD/2, 0, 0])
    ResinRod(bottomZ(speedHoleRadial+speedHoleID/2+resinTipOD/2));
    translate([speedHoleRadial-speedHoleID/2-resinTipOD/2, 0, 0])
    ResinRod(bottomZ(speedHoleRadial-speedHoleID/2+-resinTipOD/2));
    translate([speedHoleRadial, speedHoleID/2+resinTipOD/2, 0])
    ResinRod(bottomZ((speedHoleRadial^2+(speedHoleID/2+resinTipOD/2)^2)^.5));
    translate([speedHoleRadial, -speedHoleID/2-resinTipOD/2, 0])
    ResinRod(bottomZ((speedHoleRadial^2+(-speedHoleID/2-resinTipOD/2)^2)^.5));
}

module SpeedHoleSupports(){
    for (n=[0:speedHoleQty-1])
    if (n!=0)
    rotate([0, 0, 360/speedHoleQty*n])
    SpeedHoleSupport();
}

//generic cardinal-point support around a rectangular (or, with equal half
//extents, circular) footprint at a given radial position - covers both
//Blickensderfer2's drive-pin countersink (circular, halfExtentX=halfExtentY)
//and Postal's drive pin (rectangular, halfExtentX=drivePinLength/2,
//halfExtentY=drivePinWidth/2). Machine file computes radius/halfExtents.
module DrivePinSupport(radius, halfExtentX, halfExtentY){
    translate([radius+halfExtentX+resinTipOD/2, 0, 0])
    ResinRod(bottomZ(radius+halfExtentX+resinTipOD/2));
    translate([radius-halfExtentX-resinTipOD/2, 0, 0])
    ResinRod(bottomZ(radius-halfExtentX-resinTipOD/2));
    translate([radius, halfExtentY+resinTipOD/2, 0])
    ResinRod(bottomZ((radius^2+(halfExtentY+resinTipOD/2)^2)^.5));
    translate([radius, -halfExtentY-resinTipOD/2, 0])
    ResinRod(bottomZ((radius^2+(-halfExtentY-resinTipOD/2)^2)^.5));
}

module BottomSupports(){
    _fractions = is_undef(bottomSupportFractions) ? [.2] : bottomSupportFractions;
    _innerAngleOffset = is_undef(bottomSupportInnerAngleOffset) ? .5 : bottomSupportInnerAngleOffset;
    for (n=[0:speedHoleQty-1]){
        rotate([0, 0, (n+.5)*360/speedHoleQty]){
            a=bottomX(coreBottomOffset);
            b=Element_Diameter/2-wallMinThickness-wallChamfer;
            for (f=_fractions)
            translate([a+(b-a)*f, 0, 0])
            ResinRod(bottomZ(a+(b-a)*f));
        }
        rotate([0, 0, (n+_innerAngleOffset)*360/speedHoleQty])
        translate([Shaft_Diameter/2+coreChamfer+resinTipOD/2, 0, 0])
        ResinRod(coreBottomOffset);
    }
}

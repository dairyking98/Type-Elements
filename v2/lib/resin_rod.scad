//Shared single resin-support-rod primitive (v2.0 lib). Extracted out of
//resin_support.scad so machines whose rod *placement* differs from the
//Blick/Postal cylinder-family pattern (Bennett, Mignon, ...) can still reuse
//the one universal rod shape: hull() of a small tip sphere into a
//shaft-diameter sphere (the tapered tip), hull()-continued down to a second
//shaft-diameter sphere (the straight rod - two equal spheres hulled is a
//capsule), then an optional separate frustum cylinder() for the raft.
//
//Include this AFTER the machine file has defined its own globals, same rule
//as every other v2 lib file.
//
//Required from including machine file:
//  z, Resin_Fn
//  Resin_Tip_OD, Resin_Tip_L, Resin_Rod_OD, Resin_Inset, Resin_Min_Rod_Height,
//  Resin_Raft_OD, Resin_Raft_Thickness
//
//Optional (lib supplies a default if the machine file leaves these undefined):
//  Resin_Rod_Raft - whether ResinRod() grows its own small raft disk.
//                   Default true. Set false if the machine file builds its
//                   own separate raft/groove ring instead (Postal's pattern -
//                   see resin_support.scad's header comment).

module ResinRod(h){
    $fn=Resin_Fn;
    _raft = is_undef(Resin_Rod_Raft) ? true : Resin_Rod_Raft;
    hull(){
        translate([0, 0, -Resin_Tip_OD/2+Resin_Inset+h]){
            sphere(d=Resin_Tip_OD);
            translate([0, 0, -Resin_Tip_L])
            sphere(d=Resin_Rod_OD);
        }
        translate([0, 0, -Resin_Min_Rod_Height-Resin_Raft_Thickness+Resin_Rod_OD/2+z])
        sphere(d=Resin_Rod_OD);
    }
    if (_raft)
    translate([0, 0, -Resin_Min_Rod_Height-Resin_Raft_Thickness])
    cylinder(d1=Resin_Raft_OD, d2=Resin_Raft_OD+1*Resin_Raft_Thickness, h=Resin_Raft_Thickness);
}

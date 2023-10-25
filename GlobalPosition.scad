module GlobalPosition (Radius, Baseline, Column, Theta){
    translate([cos(Theta)*Radius,sin(Theta)*Radius, Baseline])
    rotate([90, 0, 90+Theta])
    children();
}
start=3.9;
increment=.1;
end=4.5;
buildplatelength=30;
extrusion=20;
$fn=360;
    for (n=[0:1:(end-start)/increment-1]){
    
    d=start+increment*n;
    if (d<=end){
    translate([10*n-buildplatelength*floor(10*n/buildplatelength),20*floor(10*n/buildplatelength),0]){
    

        translate([0,10,0]){
        difference(){
            cylinder(d=d+2, h=extrusion);
            translate([0,0,-.01])
            cylinder(h=extrusion+.02, d=d);
            
    translate([3-.25, 0, extrusion/2])
    rotate([0, 90, 0])
    linear_extrude(2)
    #text(text=str(d), size=2, halign="center", valign="center");
            
        }}
        
            difference(){
            translate([-d/2-1, -d/2-1 -.01])
            cube([d+2, d+2, extrusion]);
            translate([-d/2, -d/2, -.01])
            cube([d, d, extrusion+.02]);
                translate([3-.25, 0, extrusion/2])
    rotate([0, 90, 0])
    linear_extrude(2)
    #text(text=str(d), size=2, halign="center", valign="center");
            }
        }
        }
}
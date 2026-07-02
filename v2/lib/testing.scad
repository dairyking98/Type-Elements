//Shared testing/calibration utilities (v2.0 lib)
//
//The one genuinely duplicated piece of every machine's Testing Stuff section
//is this linear sweep formula: "start + interval*n for n in [0,count)". It
//shows up as Blickensderfer2/Postal's cutoutTestArray/baselineTestArray, and
//(4 times over) as IBM's CUTOUT_TEST_ANGLE_ARRAY/DRAFTANGLE_TEST_ARRAY/
//MINK_LONG_OFFSET_TEST_ARRAY/PLATEN_DIAMETER_TEST_ARRAY - only the
//start/interval/count differ per machine/array.
//
//Bennett/Mignon/Helios Klimax/Hammond use a fixed literal array of
//already-measured calibration offsets instead of a uniform sweep
//(Testing_Offsets/baselineTestArray), so there's nothing for them to wire in
//here - a literal array is not duplicated logic, just per-machine data.
function testSweepArray(start, interval, count) = [for (n=[0:count-1]) start+interval*n];

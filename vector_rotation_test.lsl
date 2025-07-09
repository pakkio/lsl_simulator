
// Test script for vector and rotation functionality

default
{
    state_entry()
    {
        llSay(0, "--- Starting Vector & Rotation Tests ---");

        // 1. Vector Literal and Component Access
        vector v = <3.0, 4.0, 0.0>;
        llSay(0, "Vector is: " + (string)v);
        llSay(0, "Vector y component is: " + (string)v.y);

        // 2. Vector Math
        float mag = llVecMag(v); // Should be 5.0
        llSay(0, "Magnitude of v is: " + (string)mag);
        
        vector norm_v = llVecNorm(v); // Should be <0.6, 0.8, 0.0>
        llSay(0, "Normalized v is: " + (string)norm_v);

        // 3. Rotation Literal and Function
        rotation q = <0.0, 0.0, 0.707, 0.707>; // 90 degrees around Z axis
        vector euler_angles = llRot2Euler(q); // Should be approx <0, 0, 1.57> (pi/2)
        
        llSay(0, "Rotation q is: " + (string)q);
        llSay(0, "Euler angles are: " + (string)euler_angles);
        llSay(0, "Yaw (z-angle) is approx: " + (string)euler_angles.z);

        llSay(0, "--- Tests Complete ---");
    }
}

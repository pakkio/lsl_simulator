
// Test script for true LSL list functionality

default
{
    state_entry()
    {
        llSay(0, "--- Starting List Tests ---");

        // 1. List Literals and Concatenation
        list list_a = [ "a", 1, "b", 2 ];
        list list_b = [ "c", 3 ];
        list combined = list_a + list_b; // Should be [ "a", 1, "b", 2, "c", 3 ]
        
        llSay(0, "Combined list length: " + (string)llGetListLength(combined)); // Should be 6

        // 2. llList2String
        string item = llList2String(combined, 4); // Should be "c"
        llSay(0, "Item at index 4 is: " + item);

        // 3. llListFindList
        list sub = [ "b", 2, "c" ];
        integer index = llListFindList(combined, sub); // Should be 2
        llSay(0, "Index of sublist is: " + (string)index);

        // 4. llListSort
        list to_sort = [ "z", 10, "a", 5, "m", 15 ];
        list sorted_asc = llListSort(to_sort, 2, TRUE); // Stride of 2, ascending
        // Should be [ "a", 5, "m", 15, "z", 10 ]
        
        // We need to manually check the sorted list for now
        llSay(0, "Sorted list (asc) starts with: " + llList2String(sorted_asc, 0));

        llSay(0, "--- Tests Complete ---");
    }
}

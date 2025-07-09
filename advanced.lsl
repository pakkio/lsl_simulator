// Advanced LSL script for testing new features

string NOTECARD_NAME = "my_notecard";
key http_request_id;

default
{
    state_entry()
    {
        llSay(0, "Default state. Touch to begin.");
    }

    touch_start(integer total_number)
    {
        llSay(0, "Switching to waiting state.");
        state waiting;
    }
}

state waiting
{
    state_entry()
    {
        llSay(0, "Entered waiting state. Reading notecard and making HTTP request.");
        llGetNotecardLine(NOTECARD_NAME, 0);
        http_request_id = llHTTPRequest("https://example.com/", [], "");
        llSetTimerEvent(10.0); // Set a timer to return to default state
    }

    timer()
    {
        llSay(0, "Timer expired. Returning to default state.");
        state default;
    }

    dataserver(key queryid, string data)
    {
        llSay(0, "Notecard line received: " + data);
    }

    http_response(key request_id, integer status, list metadata, string body)
    {
        if (request_id == http_request_id)
        {
            llSay(0, "HTTP response received. Status: " + (string)status);
        }
    }
}

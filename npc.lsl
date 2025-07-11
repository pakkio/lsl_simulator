// Corona Agent - AI NPC Integration (VERIFICATO)
// Attachment point: Head (per massima visibilità)
// Integrazione con nexus AI RPG engine

// =================== CONFIGURATION ===================
// These settings define the core behavior of the NPC agent.
string NEXUS_BASE_URL = "http://localhost:5000/npc"; // URL of the AI backend.
string NOTECARD_NAME = "npc_profile"; // Name of the notecard containing the NPC's personality.
integer CHANNEL = 1; // Private channel for control commands.
integer HTTP_TIMEOUT = 30; // Seconds before an HTTP request times out.
integer SENSOR_RANGE = 8; // Meters to scan for nearby avatars.
float SENSOR_REPEAT = 2.0; // Seconds between sensor scans.

// =================== STATE VARIABLES ===================
// These variables track the script's current status.
integer is_npc = TRUE; // We assume this is always an NPC for the simulation.
key npc = NULL_KEY; // The key of the spawned NPC avatar.
key current_avatar = NULL_KEY; // The key of the avatar the NPC is currently interacting with.
string npc_profile_data = ""; // Stores the content of the profile notecard.
string conversation_state = ""; // Tracks the current point in the conversation (e.g., "greeting").
integer sensing_active = TRUE; // Flag to enable or disable the avatar sensor.
integer is_registered = FALSE; // Flag to indicate if the NPC has successfully registered with the Nexus server.
integer notecard_read_complete = FALSE;
integer notecard_line = 0; // Counter for reading the profile notecard line by line.

// HTTP request management
key current_http_request = NULL_KEY; // The ID of the last HTTP request sent.
string current_request_type = ""; // The type of the last request ("register", "hook", "talk").
integer http_request_count = 0; // Counter for HTTP requests to avoid throttling.
float last_http_time = 0.0; // Timestamp of the last HTTP request.

// Listener management
integer conversation_listener = -1; // Handle for the current conversation listener

// Visual states
// These vectors define the colors for the object's text display in different states.
vector COLOR_LOADING = <1,1,0>;     // Yellow - Loading
vector COLOR_READY = <0,1,0>;       // Green - Ready
vector COLOR_TALKING = <0,0,1>;     // Blue - In conversation
vector COLOR_ERROR = <1,0,0>;       // Red - Error
vector COLOR_STANDBY = <0.8,0.8,0.8>; // Gray - Standby (on avatar)

// =================== MAIN LOGIC ===================

default {
    state_entry() {
        llSay(0, "🚀 [DEBUG] state_entry STARTED!");
        // Initialize the visual appearance of the "corona" object.
        setup_corona_visual();

        // Set up listeners FIRST before starting async operations
        llSay(0, "🔧 [DEBUG] About to call llListen for private channel " + (string)CHANNEL);
        string handle1 = llListen(CHANNEL, "", NULL_KEY, "");
        llSay(0, "🔧 [DEBUG] Private channel llListen completed, handle=" + handle1);
        
        // Listen for public chat on channel 0 for general commands and conversation
        llSay(0, "🔧 [DEBUG] About to call llListen for public channel 0");
        string handle2 = llListen(0, "", NULL_KEY, "");
        llSay(0, "🔧 [DEBUG] Public channel llListen completed, handle=" + handle2);
        llSay(0, "👂 [LISTENER] Set up general public channel listening");
        
        llSay(0, "🏁 [DEBUG] state_entry LISTENERS SETUP COMPLETED!");

        // Start the NPC initialization process (this triggers many async dataserver events)
        llSetText("🤖 NPC Mode - Loading...", COLOR_LOADING, 1.0);
        llSay(0, "🔧 [DEBUG] About to call start_npc_initialization()");
        
        // Try inline initialization as a workaround
        llSay(0, "🔧 [DEBUG] INLINE: Checking inventory type for: " + NOTECARD_NAME);
        integer inv_type = llGetInventoryType(NOTECARD_NAME);
        llSay(0, "🔧 [DEBUG] INLINE: Inventory type result: " + (string)inv_type + " (INVENTORY_NOTECARD=7)");
        
        if (inv_type == INVENTORY_NOTECARD) {
            llSay(0, "🔧 [DEBUG] INLINE: ✅ Notecard found! Starting to read...");
            npc_profile_data = "";
            notecard_line = 0;
            notecard_read_complete = FALSE;
            llSay(0, "🔧 [DEBUG] INLINE: About to call llGetNotecardLine for: " + NOTECARD_NAME + ", line 0");
            llGetNotecardLine(NOTECARD_NAME, 0);
            llSay(0, "🔧 [DEBUG] INLINE: llGetNotecardLine call completed");
        } else {
            llSay(0, "🔧 [DEBUG] INLINE: ❌ Notecard not found!");
            llSetText("❌ Missing " + NOTECARD_NAME, COLOR_ERROR, 1.0);
            llSetTimerEvent(30.0);
        }
        
        llSay(0, "🔧 [DEBUG] start_npc_initialization() completed - state_entry finished!");
    }

    // =================== NOTECARD READING ===================
    dataserver(key query_id, string data) {
        // This event is triggered by llGetNotecardLine.
        llSay(0, "[DEBUG] dataserver: notecard_read_complete=" + (string)notecard_read_complete + ", data='" + data + "'");
        
        // Skip processing if already complete
        if (notecard_read_complete) {
            llSay(0, "[DEBUG] dataserver: skipping - already complete");
            return;
        }
        
        // Handle EOF - notecard reading is complete
        if (data == EOF) {
            llSay(0, "[DEBUG] dataserver: EOF reached, setting notecard_read_complete=TRUE");
            notecard_read_complete = TRUE;
            
            if (!is_registered) {
                llSay(0, "[DEBUG] dataserver: All notecard data read, registering with nexus");
                register_with_nexus();
            }
        }
        else {
            // Handle normal content - continue reading
            llSay(0, "[DEBUG] dataserver: Read line " + (string)notecard_line + ": " + data);
            npc_profile_data += data + "\n";
            notecard_line++;
            llGetNotecardLine(NOTECARD_NAME, notecard_line);
        }
    }

    // =================== HTTP RESPONSES ===================
    http_response(key request_id, integer status, list metadata, string body) {
        // This event is triggered when an HTTP request receives a response.
        llSay(0, "[DEBUG] http_response: request_id=" + (string)request_id + ", current_http_request=" + (string)current_http_request);
        llSay(0, "[DEBUG] http_response: current_request_type='" + current_request_type + "', status=" + (string)status);
        
        if (request_id != current_http_request) {
            llSay(0, "[DEBUG] http_response: ignoring - request_id mismatch");
            return; // Ignore responses from old requests.
        }

        current_http_request = NULL_KEY;

        // Handle the response based on the type of request that was sent.
        llSay(0, "[DEBUG] current_request_type length: " + (string)llStringLength(current_request_type));
        llSay(0, "[DEBUG] Comparing '" + current_request_type + "' with 'register'");
        
        // Use explicit substring checking as a workaround for comparison issues
        integer is_register = (llSubStringIndex(current_request_type, "register") == 0) && (llStringLength(current_request_type) == 8);
        integer is_hook = (llSubStringIndex(current_request_type, "hook") == 0) && (llStringLength(current_request_type) == 4);
        integer is_talk = (llSubStringIndex(current_request_type, "talk") == 0) && (llStringLength(current_request_type) == 4);
        
        llSay(0, "[DEBUG] is_register=" + (string)is_register + ", is_hook=" + (string)is_hook + ", is_talk=" + (string)is_talk);
        
        if (is_register) {
            llSay(0, "🔧 [HTTP] Processing REGISTRATION response");
            handle_register_response(status, body);
        } else if (is_hook) {
            llSay(0, "🎯 [HTTP] Processing GREETING/HOOK response");
            handle_hook_response(status, body);
        } else if (is_talk) {
            llSay(0, "💬 [HTTP] Processing CONVERSATION response");
            handle_talk_response(status, body);
        } else {
            llSay(0, "❓ [HTTP] Unknown request type: '" + current_request_type + "' (length: " + (string)llStringLength(current_request_type) + ")");
        }

        current_request_type = "";
    }

    // =================== SENSOR EVENTS ===================
    sensor(integer detected) {
        // This event is triggered by llSensorRepeat when avatars are detected.
        llSay(0, "[SENSOR DEBUG] sensor event triggered, detected=" + (string)detected + ", sensing_active=" + (string)sensing_active);
        if (!sensing_active) {
            llSay(0, "[SENSOR DEBUG] ❌ sensing_active is FALSE, returning early");
            return;
        }

        // Find the closest avatar that is not the owner and not already in conversation.
        integer i;
        float min_dist = SENSOR_RANGE + 1.0;
        key closest_avatar = NULL_KEY;

        for (i = 0; i < detected; i++) {
            key detected_key = llDetectedKey(i);
            llSay(0, "[SENSOR DEBUG] Checking avatar " + (string)i + ": key=" + (string)detected_key + ", current_avatar=" + (string)current_avatar);
            // Allow detection if no current conversation OR if this is a different avatar
            if (current_avatar == NULL_KEY || detected_key != current_avatar) {
                float dist = llDetectedDist(i);
                llSay(0, "[SENSOR DEBUG] Avatar distance: " + (string)dist);
                if (dist < min_dist && dist <= 3.0) {
                    min_dist = dist;
                    closest_avatar = detected_key;
                    llSay(0, "[SENSOR DEBUG] ✅ Set closest_avatar to: " + (string)closest_avatar);
                }
            } else {
                llSay(0, "[SENSOR DEBUG] ❌ Skipping avatar - already in conversation");
            }
        }

        // If a new avatar is found, start a conversation with them.
        if (closest_avatar != NULL_KEY) {
            llSay(0, "[SENSOR DEBUG] ✅ Found closest avatar: " + (string)closest_avatar + ", setting current_avatar");
            current_avatar = closest_avatar;
            llSay(0, "[SENSOR DEBUG] ✅ current_avatar set to: " + (string)current_avatar);
            initiate_conversation(closest_avatar);
        } else {
            llSay(0, "[SENSOR DEBUG] ❌ No closest avatar found");
        }
    }

    no_sensor() {
        // This event is triggered when no avatars are detected in the sensor range.
        // End the current conversation if one is active.
        if (current_avatar != NULL_KEY) {
            end_conversation();
        }
    }

    // =================== CHAT LISTENING ===================
    listen(integer channel, string name, key id, string user_message) {
        // This event is triggered by llListen when a chat message is heard.
        llSay(0, "[LISTEN DEBUG] Channel=" + (string)channel + ", Name='" + name + "', ID=" + (string)id + ", Message='" + user_message + "'");
        llSay(0, "[LISTEN DEBUG] current_avatar=" + (string)current_avatar + ", Match=" + (string)(id == current_avatar));
        
        if (channel == 0) {
            // Check if this is a control command (starts with /)
            if (llGetSubString(user_message, 0, 0) == "/") {
                // A control command was received on the public channel.
                string command = llGetSubString(user_message, 1, -1); // Remove the "/" prefix
                handle_control_command(command);
            }
            else if (id == current_avatar) {
                // An avatar in conversation has spoken. Send their message to the Nexus server.
                llSay(0, "[LISTEN DEBUG] ✅ MATCHED CURRENT AVATAR - Sending talk request");
                send_talk_request(id, user_message);
            }
            else {
                // Regular public chat from someone not in conversation
                llSay(0, "[LISTEN DEBUG] ❌ ID mismatch - ignoring message");
            }
        }
    }

    // =================== TIMER EVENTS ===================
    timer() {
        // This event is triggered by llSetTimerEvent.
        llSay(0, "[DEBUG] timer: current_avatar=" + (string)current_avatar + ", is_registered=" + (string)is_registered + ", notecard_read_complete=" + (string)notecard_read_complete);
        
        if (current_avatar != NULL_KEY) {
            // If a conversation has been idle for too long, end it.
            llSay(0, "[DEBUG] timer: ending conversation");
            end_conversation();
            llSetTimerEvent(0.0); // Stop the timer.
        } else if (!is_registered && npc_profile_data != "" && notecard_read_complete) {
            // If registration failed, retry it.
            llSay(0, "[DEBUG] timer: calling register_with_nexus");
            register_with_nexus();
            // Don't cancel timer here - let register_with_nexus handle it
        }
    }

    // =================== TOUCH EVENTS ===================
    touch_start(integer total_number) {
        // When the object is touched, send a status message to the toucher.
        key toucher = llDetectedKey(0);
        string status_msg = get_status_message();
        llInstantMessage(toucher, "🤖 Corona AI Agent Status:\n" + status_msg);
    }

    // =================== CHANGE EVENTS ===================
    changed(integer change) {
        // This event is triggered by various changes to the object or region.
        if (change & CHANGED_REGION_RESTART) {
            // If the region restarts, reset the script.
            llResetScript();
        } else if (change & CHANGED_OWNER) {
            // If the owner changes, reset the script.
            llResetScript();
        }
    }
}

// =================== CORE FUNCTIONS ===================

setup_corona_visual() {
    // Configures the visual appearance of the "corona" object.
    llSetAlpha(0.7, ALL_SIDES);
    llSetScale(<0.2, 0.2, 0.08>); // Crown-like proportions
    string crown_texture = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==";
    // A simple golden color is used for now.
}

start_npc_initialization() {
    // Begins the process of initializing the NPC.
    // It starts by reading the profile notecard.
    if (llGetInventoryType(NOTECARD_NAME) == INVENTORY_NOTECARD) {
        npc_profile_data = "";
        notecard_line = 0;
        notecard_read_complete = FALSE; // Reset the flag when starting to read
        llGetNotecardLine(NOTECARD_NAME, 0);
    } else {
        llSetText("❌ Missing " + NOTECARD_NAME, COLOR_ERROR, 1.0);
        llSetTimerEvent(30.0); // Retry reading the notecard after 30 seconds.
    }
}

// =================== HTTP FUNCTIONS ===================

register_with_nexus() {
    // Sends a registration request to the Nexus server.
    llSay(0, "[DEBUG] register_with_nexus: called, notecard_read_complete=" + (string)notecard_read_complete);
    llSay(0, "[DEBUG] register_with_nexus: About to check HTTP throttle");
    
    // Temporarily disable throttling for testing
    // if (!check_http_throttle()) {
    //     llSay(0, "[DEBUG] register_with_nexus: HTTP throttled, setting timer for 5 seconds");
    //     llSetTimerEvent(5.0); // Retry in 5 seconds if throttled.
    //     return;
    // }

    llSay(0, "[DEBUG] register_with_nexus: proceeding with registration");
    llSetText("🌐 Registering with Nexus...", COLOR_LOADING, 1.0);

    string url = NEXUS_BASE_URL + "/register";
    llSay(0, "[DEBUG] register_with_nexus: URL=" + url);
    
    string payload = llList2Json(JSON_OBJECT, [
        "profile", npc_profile_data,
        "region", llGetRegionName(),
        "position", llList2Json(JSON_ARRAY, [llGetPos().x, llGetPos().y, llGetPos().z]),
        "owner", llGetOwner(),
        "object_key", llGetKey(),
        "timestamp", llGetUnixTime()
    ]);
    
    llSay(0, "[DEBUG] register_with_nexus: About to call llHTTPRequest");
    current_http_request = llHTTPRequest(url, [
        HTTP_METHOD, "POST",
        HTTP_MIMETYPE, "application/json",
        HTTP_CUSTOM_HEADER, "X-Corona-Agent", "1.0"
    ], payload);
    
    llSay(0, "[DEBUG] register_with_nexus: llHTTPRequest returned: " + (string)current_http_request);

    if (current_http_request != NULL_KEY) {
        current_request_type = "register";
        update_http_stats();
    } else {
        llSetText("⚠️ HTTP Throttled", COLOR_ERROR, 1.0);
        llSetTimerEvent(20.0);
    }
}

initiate_conversation(key avatar_key) {
    // Sends a "hook" request to the Nexus server to start a conversation.
    if (!check_http_throttle()) return;

    llSetText("💬 Initiating contact...", COLOR_TALKING, 1.0);

    string url = NEXUS_BASE_URL + "/hook";
    string payload = llList2Json(JSON_OBJECT, [
        "avatar", avatar_key,
        "avatar_name", llKey2Name(avatar_key),
        "npc_profile", npc_profile_data,
        "region", llGetRegionName(),
        "position", llList2Json(JSON_ARRAY, [llGetPos().x, llGetPos().y, llGetPos().z])
    ]);

    current_http_request = llHTTPRequest(url, [
        HTTP_METHOD, "POST",
        HTTP_MIMETYPE, "application/json"
    ], payload);

    if (current_http_request != NULL_KEY) {
        current_request_type = "hook";
        update_http_stats();
    }
}

send_talk_request(key avatar_key, string user_message) {
    // Sends a "talk" request to the Nexus server with the user's message.
    if (!check_http_throttle()) return;

    string url = NEXUS_BASE_URL + "/talk";
    string payload = llList2Json(JSON_OBJECT, [
        "avatar", avatar_key,
        "avatar_name", llKey2Name(avatar_key),
        "message", user_message,
        "conversation_state", conversation_state,
        "npc_profile", npc_profile_data
    ]);

    current_http_request = llHTTPRequest(url, [
        HTTP_METHOD, "POST",
        HTTP_MIMETYPE, "application/json"
    ], payload);

    if (current_http_request != NULL_KEY) {
        current_request_type = "talk";
        update_http_stats();
    }
}

// =================== RESPONSE HANDLERS ===================

handle_register_response(integer status, string response) {
    // Handles the response from a "register" request.
    llSay(0, "🔧 [REGISTRATION] Response received, status=" + (string)status);
    if (status == 200) {
        llSay(0, "✅ [REGISTRATION] SUCCESS! NPC is now registered and active");
        is_registered = TRUE;
        llSetText("✅ AI Agent Ready", COLOR_READY, 1.0);
        
        // Parse and display server greeting if available
        if (response != "") {
            // Extract greeting or status message from server response
            llSay(0, "🤖 Server says: Registration successful! I'm now active and ready to help.");
        }
        
        // Announce listening channels to nearby users
        llSay(0, "💬 Chat with me on channel 0 (public) or use channel " + (string)CHANNEL + " for commands.");
        llSay(0, "📡 I'm listening for conversations and ready to assist visitors.");
        
        sensing_active = TRUE;
        llSay(0, "👁️ [SENSING] Now active - will detect approaching avatars");
        llSensorRepeat("", "", AGENT, SENSOR_RANGE, PI, SENSOR_REPEAT);
        create_crown_effect();
    } else {
        llSay(0, "❌ [REGISTRATION] FAILED with status: " + (string)status);
        llSetText("❌ Registration Failed: " + (string)status, COLOR_ERROR, 1.0);
        llSetTimerEvent(30.0); // Retry registration after 30 seconds.
    }
}

handle_hook_response(integer status, string response) {
    // Handles the response from a "hook" request.
    llSay(0, "🎯 [GREETING] Response received, status=" + (string)status);
    if (status != 200) {
        llSay(0, "❌ [GREETING] FAILED with status: " + (string)status);
        llSetText("❌ Hook Failed", COLOR_ERROR, 1.0);
        current_avatar = NULL_KEY;
        return;
    }

    llSay(0, "✅ [GREETING] SUCCESS! Processing server response and starting conversation");
    process_npc_actions(response);
    
    // Remove old listener and create new one for this conversation
    if (conversation_listener != -1) {
        llListenRemove(conversation_listener);
        llSay(0, "🔄 [LISTENER] Removed old conversation listener");
    }
    conversation_listener = llListen(0, "", current_avatar, ""); // Start listening to the avatar on the public channel.
    llSay(0, "👂 [LISTENER] Now listening for messages from " + llKey2Name(current_avatar));
    llSetTimerEvent(60.0); // Set a timeout for the conversation.
}

handle_talk_response(integer status, string response) {
    // Handles the response from a "talk" request.
    llSay(0, "💬 [CONVERSATION] Response received, status=" + (string)status);
    if (status != 200) {
        llSay(0, "❌ [CONVERSATION] FAILED with status: " + (string)status);
        llSetText("❌ Talk Failed", COLOR_ERROR, 1.0);
        return;
    }

    llSay(0, "✅ [CONVERSATION] SUCCESS! Processing server response");
    process_npc_actions(response);
    llSetTimerEvent(60.0); // Reset the conversation timeout.
}

// =================== ACTION PROCESSING ===================

process_npc_actions(string json_response) {
    // Parses the JSON response from the Nexus server and executes the specified actions.
    string say_text = llJsonGetValue(json_response, ["say"]);
    string look_target = llJsonGetValue(json_response, ["look_at"]);
    string display_text = llJsonGetValue(json_response, ["text_display"]);
    string animation = llJsonGetValue(json_response, ["animation"]);
    string emote = llJsonGetValue(json_response, ["emote"]);
    conversation_state = llJsonGetValue(json_response, ["conversation_state"]);

    if (say_text != JSON_INVALID && say_text != "") {
        osNpcSay(npc, say_text);
    }

    if (look_target == "player" && current_avatar != NULL_KEY) {
        look_at_avatar(current_avatar);
    }

    if (display_text != JSON_INVALID && display_text != "") {
        llSetText("💭 " + display_text, COLOR_TALKING, 1.0);
    }

    if (animation != JSON_INVALID && animation != "") {
        osNpcPlayAnimation(npc, animation);
    }
}

look_at_avatar(key avatar) {
    // Makes the NPC turn to look at the specified avatar.
    vector avatar_pos = llList2Vector(llGetObjectDetails(avatar, [OBJECT_POS]), 0);
    if (avatar_pos != ZERO_VECTOR) {
        vector npc_pos = osNpcGetPos(npc);
        rotation look_rot = llRotBetween(<1,0,0>, llVecNorm(avatar_pos - npc_pos));
        osNpcSetRot(npc, look_rot);
    }
}

// =================== CONTROL COMMANDS ===================

handle_control_command(string cmd) {
    // Handles control commands received on the private channel.
    if (cmd == "START_SENSING") {
        if (is_registered) {
            sensing_active = TRUE;
            llSensorRepeat("", "", AGENT, SENSOR_RANGE, PI, SENSOR_REPEAT);
            llSetText("👁️ Sensing Active", COLOR_READY, 1.0);
        }
    } else if (cmd == "STOP_SENSING") {
        sensing_active = FALSE;
        llSensorRemove();
        llSetText("💤 Sensing Paused", <0.5,0.5,0.5>, 1.0);
    } else if (llSubStringIndex(cmd, "CREATE_NPC:") == 0) {
        // Creates a new NPC. This command is typically sent by a controller object.
        string npc_name = llGetSubString(cmd, 11, -1);
        list name_parts = llParseString2List(npc_name, " ", []);
        if (llGetListLength(name_parts) >= 2) {
            npc = osNpcCreate(
                llList2String(name_parts, 0),
                llList2String(name_parts, 1),
                llGetPos() + <1,0,0>,
                llGetOwner()
            );
            if (npc != NULL_KEY) {
                llRegionSay(CHANNEL, "START_SENSING");
            }
        }
    }
}

// =================== UTILITY FUNCTIONS ===================

integer check_http_throttle() {
    // Prevents the script from exceeding LSL's HTTP request limits.
    float current_time = llGetTime();
    llSay(0, "[DEBUG] check_http_throttle: current_time=" + (string)current_time + ", last_http_time=" + (string)last_http_time);

    // Initialize last_http_time on first call
    if (last_http_time == 0.0) {
        last_http_time = current_time - 1.1; // Allow first request immediately
        llSay(0, "[DEBUG] check_http_throttle: Initialized last_http_time to " + (string)last_http_time);
    }

    if (current_time - last_http_time > 20.0) {
        http_request_count = 0; // Reset counter every 20 seconds.
    }

    if (http_request_count >= 20) {
        return FALSE; // LSL allows 25 requests per 20 seconds, but we stay safe.
    }

    if (current_time - last_http_time < 1.0) {
        llSay(0, "[DEBUG] check_http_throttle: current_time=" + (string)current_time + ", last_http_time=" + (string)last_http_time + ", diff=" + (string)(current_time - last_http_time));
        return FALSE; // Enforce a minimum of 1 second between requests.
    }

    return TRUE;
}

update_http_stats() {
    // Updates the HTTP request statistics.
    last_http_time = llGetTime();
    http_request_count++;
}

end_conversation() {
    // Ends the current conversation and resets the state.
    current_avatar = NULL_KEY;
    conversation_state = "";
    if (is_registered) {
        llSetText("✅ AI Agent Ready", COLOR_READY, 1.0);
    }
    llSetTimerEvent(0.0);
}

create_crown_effect() {
    // Creates an enhanced visual effect for the active NPC.
    llSetText("👑 AI AGENT ACTIVE 👑", COLOR_READY, 1.0);
    llSetAlpha(0.8, ALL_SIDES);
}

string get_status_message() {
    // Generates a status message with current script information.
    string msg = "";
    msg += "• Mode: NPC\n";
    
    if (npc_profile_data != "") {
        msg += "• Profile: Loaded\n";
    } else {
        msg += "• Profile: Missing\n";
    }
    
    if (is_registered) {
        msg += "• Registered: Yes\n";
    } else {
        msg += "• Registered: No\n";
    }
    
    if (sensing_active) {
        msg += "• Sensing: Active\n";
    } else {
        msg += "• Sensing: Inactive\n";
    }
    
    if (npc != NULL_KEY) {
        msg += "• NPC UUID: " + (string)npc + "\n";
    } else {
        msg += "• NPC UUID: None\n";
    }
    
    if (current_avatar != NULL_KEY) {
        msg += "• Current Chat: " + llKey2Name(current_avatar);
    } else {
        msg += "• Current Chat: None";
    }
    
    return msg;
}
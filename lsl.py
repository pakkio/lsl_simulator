import argparse
import threading
from lsl_antlr4_parser import LSLAntlr4Parser as LSLParser
from lsl_simulator import LSLSimulator
from lsl_dialect import LSLDialect, set_dialect, get_dialect, parse_dialect_flag

def main():
    # --- Command-Line Argument Parsing ---
    parser = argparse.ArgumentParser(description="Parse and simulate an LSL script.")
    parser.add_argument("filename", help="The LSL script file to run (e.g., sample.lsl)")
    parser.add_argument("--sl", action="store_true", help="Use Second Life dialect (default)")
    parser.add_argument("--os", action="store_true", help="Use OpenSimulator dialect")
    args = parser.parse_args()
    
    # Set dialect based on arguments
    if args.os:
        set_dialect(LSLDialect.OPENSIMULATOR)
    else:
        set_dialect(LSLDialect.SECONDLIFE)
    
    current_dialect = get_dialect()
    print(f"Using LSL dialect: {current_dialect.value.upper()}")

    # --- Read the LSL file ---
    try:
        with open(args.filename, "r") as f:
            lsl_code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{args.filename}'")
        return

    # --- 1. Parse the Script ---
    print(f"--- Parsing {args.filename} ---")
    lsl_parser = LSLParser()
    try:
        parsed_script = lsl_parser.parse(lsl_code)
        print("Parsing complete.")
    except Exception as e:
        print(f"A parsing error occurred: {e}")
        return

    # --- 2. Simulate the Script ---
    simulator = LSLSimulator(parsed_script)
    
    # Run the simulator in a separate thread
    sim_thread = threading.Thread(target=simulator.run)
    sim_thread.daemon = True
    sim_thread.start()

    # Give the simulator time to start and process state_entry + notecard reading + registration
    import time
    print("Waiting for NPC registration to complete...")
    
    # Wait up to 10 seconds for registration to complete
    max_wait = 10
    waited = 0
    while waited < max_wait:
        time.sleep(1)
        waited += 1
        
        # Check if registration completed (sensing_active should be True)
        sensing_active = simulator.global_scope.get("sensing_active")
        is_registered = simulator.global_scope.get("is_registered")
        
        if is_registered and sensing_active:
            print(f"✅ NPC registration completed after {waited} seconds")
            break
        elif waited % 5 == 0:
            print(f"⏳ Still waiting... ({waited}s)")
    
    if waited >= max_wait:
        print("⚠️ Registration may not have completed, continuing anyway...")

    # --- 3. Interactive Loop ---
    print("--- Interactive session started ---")
    print("Type 'help' or 'h' for available commands.")
    print("Type 'quit' or 'q' to exit.")
    try:
        while True:
            command = input("> ").strip().lower()
            if command in ['quit', 'q']:
                break
            
            cmd_parts = command.split()
            if not cmd_parts:
                continue
                
            cmd = cmd_parts[0]
            
            # Handle abbreviations and full commands
            if cmd in ['touch', 't']:
                simulator.event_queue.append(("touch_start", []))
            elif cmd in ['say', 's']:
                if len(cmd_parts) > 1:
                    # s john 1 hi  OR  s john hi
                    if len(cmd_parts) > 3 and cmd_parts[2].isdigit():
                        # s john 1 hi
                        speaker_name = cmd_parts[1]
                        channel = int(cmd_parts[2])
                        message = " ".join(cmd_parts[3:])
                        # Try to get the key for this avatar from the simulator
                        speaker_key = getattr(simulator, 'avatar_name_to_key', dict()).get(speaker_name)
                        if not speaker_key and hasattr(simulator, 'sensed_avatar_name') and simulator.sensed_avatar_name == speaker_name:
                            speaker_key = simulator.sensed_avatar_key
                        if not speaker_key:
                            speaker_key = "00000000-0000-0000-0000-000000000000"
                        simulator.say_on_channel(channel, message, speaker_name, speaker_key)
                    elif len(cmd_parts) > 2 and not cmd_parts[1].isdigit():
                        # s john hi
                        speaker_name = cmd_parts[1]
                        channel = 0
                        message = " ".join(cmd_parts[2:])
                        speaker_key = getattr(simulator, 'avatar_name_to_key', dict()).get(speaker_name)
                        if not speaker_key and hasattr(simulator, 'sensed_avatar_name') and simulator.sensed_avatar_name == speaker_name:
                            speaker_key = simulator.sensed_avatar_key
                        if not speaker_key:
                            speaker_key = "00000000-0000-0000-0000-000000000000"
                        simulator.say_on_channel(channel, message, speaker_name, speaker_key)
                    else:
                        # Existing logic: s <channel> <message> or s <message>
                        try:
                            if len(cmd_parts) > 2:
                                channel = int(cmd_parts[1])
                                message = " ".join(cmd_parts[2:])
                                simulator.say_on_channel(channel, message)
                            else:
                                channel = int(cmd_parts[1])
                                print("Usage: say <channel_number> <message> - message is required")
                        except ValueError:
                            # Second argument is not a number, treat as message on channel 0
                            message = " ".join(cmd_parts[1:])
                            simulator.say_on_channel(0, message)
                else:
                    print("Usage: say <channel_number> <message> or say <message> (defaults to channel 0) or say <avatar> <message> or say <avatar> <channel> <message>")
            elif cmd in ['sense']:
                if len(cmd_parts) > 1:
                    avatar_name = " ".join(cmd_parts[1:])
                    simulator.simulate_avatar_sense(avatar_name)
                else:
                    print("Usage: sense <avatar_name>")
            elif cmd in ['help', 'h']:
                print("\n=== Available Commands ===")
                print("help, h          - Show this help message")
                print("sense <name>     - Simulate avatar approaching (triggers greeting)")
                print("say, s <msg>     - Send message on channel 0 (public)")
                print("say, s <ch> <msg> - Send message on specific channel")
                print("touch, t         - Simulate touching the NPC object")
                print("quit, q          - Exit the simulator")
                print("\n=== Typical Conversation Flow ===")
                print("1. sense John    - John approaches → NPC greets via /hook")
                print("2. s hello       - John says 'hello' → NPC responds via /talk")
                print("3. s how are you - Continued conversation")
                print("4. s goodbye     - End conversation")
                print("\n=== Other Examples ===")
                print("sense Alice      - Avatar 'Alice' approaches (key: 000...002)")
                print("s 0 hello        - Say 'hello' on public channel (explicit)")
                print("s /START_SENSING - Send control command")
                print("t                - Touch the NPC")
                print("h                - Show this help")
                print("q                - Quit\n")
                print("💡 Pro Tip: Use 'sense <name>' first to simulate avatar")
                print("   approaching, then use 's <message>' to chat!")
            else:
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
    finally:
        simulator.stop()
        # Wait briefly for the simulator thread to finish
        sim_thread.join(timeout=0.5)
    
    print("--- Simulation Ended ---")


if __name__ == "__main__":
    main()

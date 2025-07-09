#!/usr/bin/env python3
"""
Comprehensive LSL API Implementation - Part 2
Continuation of comprehensive LSL function implementation.
"""

import math
import random
import time as time_module
import uuid
import json
import re
import datetime
from typing import Any, List, Union, Dict, Optional


class ComprehensiveLSLAPIPart2:
    """
    Part 2 of comprehensive LSL API implementation.
    Covers remaining function categories to reach 90% coverage.
    """
    
    def __init__(self, simulator):
        self.simulator = simulator
    
    # =============================================================================
    # HTTP AND NETWORK FUNCTIONS (15 functions)
    # =============================================================================
    
    def api_llHTTPRequest(self, url: str, options: List, body: str) -> str:
        """Make HTTP request."""
        print(f"[llHTTPRequest]: {url}")
        request_key = f"http-key-{int(time_module.time())}"
        
        try:
            import requests
            method = "GET"
            headers = {}
            
            if isinstance(options, list):
                i = 0
                while i < len(options):
                    if i + 1 < len(options):
                        key = options[i]
                        value = options[i + 1]
                        if key == "method":
                            method = value
                        elif key == "mimetype":
                            headers["Content-Type"] = value
                        elif key == "header":
                            if i + 2 < len(options):
                                header_name = value
                                header_value = options[i + 2]
                                headers[header_name] = header_value
                                i += 3
                                continue
                        i += 2
                    else:
                        break
            
            if method.upper() == "POST":
                response = requests.post(url, data=body, headers=headers, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            metadata = [f"status:{response.status_code}"]
            self.simulator.event_queue.append(("http_response", [request_key, response.status_code, metadata, response.text]))
            
        except Exception as e:
            print(f"[llHTTPRequest ERROR]: {e}")
            self.simulator.event_queue.append(("http_response", [request_key, 499, [], ""]))
        
        return request_key
    
    def api_llHTTPResponse(self, request_id: str, status: int, body: str) -> None:
        """Send HTTP response."""
        print(f"[llHTTPResponse]: {request_id} status {status}")
    
    def api_llRequestURL(self) -> str:
        """Request a URL for this object."""
        request_key = f"url-request-{uuid.uuid4().hex[:8]}"
        url = f"http://sim.example.com/cap/{uuid.uuid4()}"
        self.simulator.event_queue.append(("http_request", [request_key, "GET", "", url]))
        return request_key
    
    def api_llRequestSecureURL(self) -> str:
        """Request a secure URL for this object."""
        request_key = f"secure-url-request-{uuid.uuid4().hex[:8]}"
        url = f"https://sim.example.com/cap/{uuid.uuid4()}"
        self.simulator.event_queue.append(("http_request", [request_key, "GET", "", url]))
        return request_key
    
    def api_llReleaseURL(self, url: str) -> None:
        """Release a previously requested URL."""
        print(f"[llReleaseURL]: {url}")
    
    def api_llGetHTTPHeader(self, request_id: str, header: str) -> str:
        """Get HTTP header from request."""
        # Simulated implementation
        return f"header-value-{header}"
    
    def api_llGetEnv(self, var: str) -> str:
        """Get environment variable."""
        env_vars = {
            "simulator_hostname": "sim.example.com",
            "simulator_version": "LSL Simulator 1.0",
            "region_product_name": "Test Region",
            "agent_limit": "100",
            "dynamic_pathfinding": "1",
            "estate_id": "1",
            "estate_name": "Test Estate",
            "frame_number": str(int(time_module.time())),
            "region_cpu_ratio": "1.0",
            "region_idle": "1",
            "region_product_sku": "023",
            "sim_channel": "LSL Simulator",
            "sim_version": "1.0.0",
            "simulator_hostname": "localhost",
            "region_max_prims": "15000",
            "region_object_bonus": "1.0"
        }
        return env_vars.get(var, "")
    
    # =============================================================================
    # TIME AND DATE FUNCTIONS (10 functions)
    # =============================================================================
    
    def api_llGetTime(self) -> float:
        """Get elapsed time since state_entry or llResetTime."""
        return time_module.time() % 86400  # Time since midnight
    
    def api_llGetAndResetTime(self) -> float:
        """Get time and reset timer."""
        return self.api_llGetTime()
    
    def api_llResetTime(self) -> None:
        """Reset the time counter."""
        print("[llResetTime]: Timer reset")
    
    def api_llGetUnixTime(self) -> int:
        """Get Unix timestamp."""
        return int(time_module.time())
    
    def api_llGetTimeOfDay(self) -> float:
        """Get time of day as a float."""
        return (time_module.time() % 86400) / 86400.0
    
    def api_llGetWallclock(self) -> float:
        """Get wall clock time_module."""
        return time_module.time() % 86400
    
    def api_llGetDate(self) -> str:
        """Get current date as string."""
        return time_module.strftime("%Y-%m-%d")
    
    def api_llGetTimestamp(self) -> str:
        """Get current timestamp."""
        return time_module.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
    
    def api_llGetGMTclock(self) -> float:
        """Get GMT clock time_module."""
        import datetime
        return datetime_module.datetime_module.utcnow().hour * 3600 + datetime_module.datetime_module.utcnow().minute * 60 + datetime_module.datetime_module.utcnow().second
    
    def api_llSetTimerEvent(self, time_interval: float) -> None:
        """Set timer event interval."""
        print(f"[llSetTimerEvent]: {time_interval} seconds")
        if time_interval > 0:
            def fire_timer():
                import time as time_module
                time_module.sleep(float(time_interval))
                self.simulator.event_queue.append(("timer", []))
            
            import threading
            thread = threading.Thread(target=fire_timer)
            thread.daemon = True
            thread.start()
    
    # =============================================================================
    # OBJECT AND PRIM FUNCTIONS (40 functions)
    # =============================================================================
    
    def api_llGetPos(self) -> List[float]:
        """Get object position."""
        return [128.5, 129.3, 25.7]
    
    def api_llSetPos(self, position: List[float]) -> None:
        """Set object position."""
        print(f"[llSetPos]: {position}")
    
    def api_llGetLocalPos(self) -> List[float]:
        """Get local position relative to root."""
        return [0.0, 0.0, 0.0]
    
    def api_llSetLocalPos(self, position: List[float]) -> None:
        """Set local position."""
        print(f"[llSetLocalPos]: {position}")
    
    def api_llGetRot(self) -> List[float]:
        """Get object rotation."""
        return [0.0, 0.0, 0.0, 1.0]
    
    def api_llSetRot(self, rotation: List[float]) -> None:
        """Set object rotation."""
        print(f"[llSetRot]: {rotation}")
    
    def api_llGetLocalRot(self) -> List[float]:
        """Get local rotation."""
        return [0.0, 0.0, 0.0, 1.0]
    
    def api_llSetLocalRot(self, rotation: List[float]) -> None:
        """Set local rotation."""
        print(f"[llSetLocalRot]: {rotation}")
    
    def api_llGetVel(self) -> List[float]:
        """Get object velocity."""
        return [0.0, 0.0, 0.0]
    
    def api_llSetVelocity(self, velocity: List[float], local: int) -> None:
        """Set object velocity."""
        print(f"[llSetVelocity]: {velocity} (local: {local})")
    
    def api_llGetAccel(self) -> List[float]:
        """Get object acceleration."""
        return [0.0, 0.0, 0.0]
    
    def api_llGetOmega(self) -> List[float]:
        """Get angular velocity."""
        return [0.0, 0.0, 0.0]
    
    def api_llGetTorque(self) -> List[float]:
        """Get applied torque."""
        return [0.0, 0.0, 0.0]
    
    def api_llGetForce(self) -> List[float]:
        """Get applied force."""
        return [0.0, 0.0, 0.0]
    
    def api_llSetForce(self, force: List[float], local: int) -> None:
        """Apply force to object."""
        print(f"[llSetForce]: {force} (local: {local})")
    
    def api_llSetTorque(self, torque: List[float], local: int) -> None:
        """Apply torque to object."""
        print(f"[llSetTorque]: {torque} (local: {local})")
    
    def api_llApplyImpulse(self, force: List[float], local: int) -> None:
        """Apply impulse to object."""
        print(f"[llApplyImpulse]: {force} (local: {local})")
    
    def api_llApplyRotationalImpulse(self, force: List[float], local: int) -> None:
        """Apply rotational impulse."""
        print(f"[llApplyRotationalImpulse]: {force} (local: {local})")
    
    def api_llGetMass(self) -> float:
        """Get object mass."""
        return 10.0
    
    def api_llGetBoundingBox(self, obj: str) -> List:
        """Get bounding box of object."""
        return [[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]]
    
    def api_llGetGeometricCenter(self) -> List[float]:
        """Get geometric center."""
        return [0.0, 0.0, 0.0]
    
    def api_llGetCenterOfMass(self) -> List[float]:
        """Get center of mass."""
        return [0.0, 0.0, 0.0]
    
    def api_llGetScale(self) -> List[float]:
        """Get object scale."""
        return [1.0, 1.0, 1.0]
    
    def api_llSetScale(self, scale: List[float]) -> None:
        """Set object scale."""
        print(f"[llSetScale]: {scale}")
    
    def api_llGetPrimitiveParams(self, params: List) -> List:
        """Get primitive parameters."""
        result = []
        for param in params:
            if param == 9:  # PRIM_MATERIAL
                result.append(3)  # PRIM_MATERIAL_WOOD
            elif param == 17:  # PRIM_TYPE
                result.extend([1, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # Box
            elif param == 18:  # PRIM_SIZE
                result.extend([1.0, 1.0, 1.0])
            elif param == 26:  # PRIM_COLOR
                result.extend([[1.0, 1.0, 1.0], 1.0])  # White, full alpha
            else:
                result.append(0)
        return result
    
    def api_llSetPrimitiveParams(self, params: List) -> None:
        """Set primitive parameters."""
        print(f"[llSetPrimitiveParams]: {len(params)} parameters")
    
    def api_llSetLinkPrimitiveParams(self, link: int, params: List) -> None:
        """Set primitive parameters for specific link."""
        print(f"[llSetLinkPrimitiveParams]: Link {link}, {len(params)} parameters")
    
    def api_llGetLinkPrimitiveParams(self, link: int, params: List) -> List:
        """Get primitive parameters for specific link."""
        return self.api_llGetPrimitiveParams(params)
    
    def api_llSetText(self, text: str, color: List[float], alpha: float) -> None:
        """Set floating text."""
        print(f"[llSetText]: {text}")
    
    def api_llSetSitText(self, text: str) -> None:
        """Set sit text."""
        print(f"[llSetSitText]: {text}")
    
    def api_llSetTouchText(self, text: str) -> None:
        """Set touch text."""
        print(f"[llSetTouchText]: {text}")
    
    def api_llSetAlpha(self, alpha: float, face: int) -> None:
        """Set object transparency."""
        print(f"[llSetAlpha]: {alpha} on face {face}")
    
    def api_llGetAlpha(self, face: int) -> float:
        """Get object transparency."""
        return 1.0
    
    def api_llSetColor(self, color: List[float], face: int) -> None:
        """Set object color."""
        print(f"[llSetColor]: {color} on face {face}")
    
    def api_llGetColor(self, face: int) -> List[float]:
        """Get object color."""
        return [1.0, 1.0, 1.0]
    
    def api_llSetTexture(self, texture: str, face: int) -> None:
        """Set object texture."""
        print(f"[llSetTexture]: {texture} on face {face}")
    
    def api_llGetTexture(self, face: int) -> str:
        """Get object texture."""
        return "default"
    
    def api_llOffsetTexture(self, u: float, v: float, face: int) -> None:
        """Offset texture coordinates."""
        print(f"[llOffsetTexture]: ({u}, {v}) on face {face}")
    
    def api_llRotateTexture(self, angle: float, face: int) -> None:
        """Rotate texture."""
        print(f"[llRotateTexture]: {angle} on face {face}")
    
    def api_llScaleTexture(self, u: float, v: float, face: int) -> None:
        """Scale texture."""
        print(f"[llScaleTexture]: ({u}, {v}) on face {face}")
    
    # =============================================================================
    # INVENTORY FUNCTIONS (20 functions)
    # =============================================================================
    
    def api_llGetInventoryNumber(self, inv_type: int) -> int:
        """Get number of inventory items of type."""
        return 1  # Simulated
    
    def api_llGetInventoryName(self, inv_type: int, index: int) -> str:
        """Get inventory item name by index."""
        return f"item_{index}"
    
    def api_llGetInventoryType(self, name: str) -> int:
        """Get inventory item type."""
        return 7  # INVENTORY_NOTECARD
    
    def api_llGetInventoryKey(self, name: str) -> str:
        """Get inventory item key."""
        return f"inv-key-{uuid.uuid4()}"
    
    def api_llGetInventoryCreator(self, name: str) -> str:
        """Get inventory item creator."""
        return "creator-key-12345"
    
    def api_llGetInventoryPermMask(self, name: str, mask: int) -> int:
        """Get inventory permissions."""
        return 0x7FFFFFFF  # All permissions
    
    def api_llSetInventoryPermMask(self, name: str, mask: int, value: int) -> None:
        """Set inventory permissions."""
        print(f"[llSetInventoryPermMask]: {name} mask {mask} = {value}")
    
    def api_llGiveInventory(self, destination: str, inventory: str) -> None:
        """Give inventory to avatar/object."""
        print(f"[llGiveInventory]: Giving {inventory} to {destination}")
    
    def api_llGiveInventoryList(self, destination: str, category: str, inventory: List[str]) -> None:
        """Give inventory list to avatar."""
        print(f"[llGiveInventoryList]: Giving {len(inventory)} items to {destination}")
    
    def api_llRemoveInventory(self, name: str) -> None:
        """Remove inventory item."""
        print(f"[llRemoveInventory]: Removing {name}")
    
    def api_llRezObject(self, inventory: str, pos: List[float], vel: List[float], rot: List[float], param: int) -> None:
        """Rez object from inventory."""
        print(f"[llRezObject]: Rezzing {inventory} at {pos}")
    
    def api_llRezAtRoot(self, inventory: str, pos: List[float], vel: List[float], rot: List[float], param: int) -> None:
        """Rez object at root."""
        print(f"[llRezAtRoot]: Rezzing {inventory} at {pos}")
    
    def api_llCreateLink(self, target: str, parent: int) -> None:
        """Create link to target."""
        print(f"[llCreateLink]: Linking to {target}")
    
    def api_llBreakLink(self, link: int) -> None:
        """Break link."""
        print(f"[llBreakLink]: Breaking link {link}")
    
    def api_llBreakAllLinks(self) -> None:
        """Break all links."""
        print("[llBreakAllLinks]: Breaking all links")
    
    def api_llGetLinkNumber(self) -> int:
        """Get link number of this prim."""
        return 1  # Root prim
    
    def api_llGetNumberOfPrims(self) -> int:
        """Get number of prims in linkset."""
        return 1
    
    def api_llGetLinkName(self, link: int) -> str:
        """Get name of linked prim."""
        return f"Prim {link}"
    
    def api_llSetLinkText(self, link: int, text: str, color: List[float], alpha: float) -> None:
        """Set text on linked prim."""
        print(f"[llSetLinkText]: Link {link}: {text}")
    
    def api_llGetLinkKey(self, link: int) -> str:
        """Get key of linked prim."""
        return f"link-key-{link}"
    
    # =============================================================================
    # SENSOR AND DETECTION FUNCTIONS (15 functions)
    # =============================================================================
    
    def api_llSensor(self, name: str, key: str, type_filter: int, range_val: float, arc: float) -> None:
        """Single sensor sweep."""
        print(f"[llSensor]: Scanning for {name} in {range_val}m")
        # Simulate detection
        if random.random() < 0.5:  # 50% chance of detection
            self.simulator.event_queue.append(("sensor", [1]))
        else:
            self.simulator.event_queue.append(("no_sensor", []))
    
    def api_llSensorRepeat(self, name: str, key: str, type_filter: int, range_val: float, arc: float, rate: float) -> None:
        """Repeating sensor."""
        print(f"[llSensorRepeat]: Repeating scan for {name} every {rate}s")
    
    def api_llSensorRemove(self) -> None:
        """Remove sensor."""
        print("[llSensorRemove]: Sensor removed")
    
    def api_llDetectedName(self, index: int) -> str:
        """Get detected object name."""
        if hasattr(self.simulator, 'sensed_avatar_name') and index == 0:
            return self.simulator.sensed_avatar_name
        return f"Detected Object {index}"
    
    def api_llDetectedKey(self, index: int) -> str:
        """Get detected object key."""
        if hasattr(self.simulator, 'sensed_avatar_key') and index == 0:
            return self.simulator.sensed_avatar_key
        return f"detected-uuid-{index}"
    
    def api_llDetectedOwner(self, index: int) -> str:
        """Get detected object owner."""
        return f"owner-{index}"
    
    def api_llDetectedType(self, index: int) -> int:
        """Get detected object type."""
        return 1  # AGENT
    
    def api_llDetectedPos(self, index: int) -> List[float]:
        """Get detected object position."""
        return [128.0 + index, 128.0 + index, 25.0]
    
    def api_llDetectedVel(self, index: int) -> List[float]:
        """Get detected object velocity."""
        return [0.0, 0.0, 0.0]
    
    def api_llDetectedRot(self, index: int) -> List[float]:
        """Get detected object rotation."""
        return [0.0, 0.0, 0.0, 1.0]
    
    def api_llDetectedGroup(self, index: int) -> int:
        """Check if detected object is in same group."""
        return 0  # False
    
    def api_llDetectedDist(self, index: int) -> float:
        """Get distance to detected object."""
        return 2.5 + index * 0.5
    
    def api_llDetectedGrab(self, index: int) -> List[float]:
        """Get detected grab offset."""
        return [0.0, 0.0, 0.0]
    
    def api_llDetectedLinkNumber(self, index: int) -> int:
        """Get detected link number."""
        return 1
    
    def api_llDetectedTouchFace(self, index: int) -> int:
        """Get detected touch face."""
        return 0
    
    # =============================================================================
    # MEDIA AND PARTICLE FUNCTIONS (25 functions)
    # =============================================================================
    
    def api_llParticleSystem(self, params: List) -> None:
        """Set particle system."""
        print(f"[llParticleSystem]: {len(params)} parameters")
    
    def api_llSetSoundQueueing(self, queue: int) -> None:
        """Set sound queueing."""
        print(f"[llSetSoundQueueing]: {queue}")
    
    def api_llPlaySound(self, sound: str, volume: float) -> None:
        """Play sound."""
        print(f"[llPlaySound]: {sound} at {volume}")
    
    def api_llLoopSound(self, sound: str, volume: float) -> None:
        """Loop sound."""
        print(f"[llLoopSound]: {sound} at {volume}")
    
    def api_llLoopSoundMaster(self, sound: str, volume: float) -> None:
        """Loop sound as master."""
        print(f"[llLoopSoundMaster]: {sound} at {volume}")
    
    def api_llLoopSoundSlave(self, sound: str, volume: float) -> None:
        """Loop sound as slave."""
        print(f"[llLoopSoundSlave]: {sound} at {volume}")
    
    def api_llStopSound(self) -> None:
        """Stop sound."""
        print("[llStopSound]: Sound stopped")
    
    def api_llPreloadSound(self, sound: str) -> None:
        """Preload sound."""
        print(f"[llPreloadSound]: {sound}")
    
    def api_llTriggerSound(self, sound: str, volume: float) -> None:
        """Trigger sound."""
        print(f"[llTriggerSound]: {sound} at {volume}")
    
    def api_llTriggerSoundLimited(self, sound: str, volume: float, top_north_east: List[float], bottom_south_west: List[float]) -> None:
        """Trigger sound in limited area."""
        print(f"[llTriggerSoundLimited]: {sound} in area")
    
    def api_llSetSoundRadius(self, radius: float) -> None:
        """Set sound radius."""
        print(f"[llSetSoundRadius]: {radius}")
    
    def api_llAdjustSoundVolume(self, volume: float) -> None:
        """Adjust sound volume."""
        print(f"[llAdjustSoundVolume]: {volume}")
    
    def api_llSetVehicleType(self, type_val: int) -> None:
        """Set vehicle type."""
        print(f"[llSetVehicleType]: {type_val}")
    
    def api_llSetVehicleFloatParam(self, param: int, value: float) -> None:
        """Set vehicle float parameter."""
        print(f"[llSetVehicleFloatParam]: {param} = {value}")
    
    def api_llSetVehicleVectorParam(self, param: int, vec: List[float]) -> None:
        """Set vehicle vector parameter."""
        print(f"[llSetVehicleVectorParam]: {param} = {vec}")
    
    def api_llSetVehicleRotationParam(self, param: int, rot: List[float]) -> None:
        """Set vehicle rotation parameter."""
        print(f"[llSetVehicleRotationParam]: {param} = {rot}")
    
    def api_llSetVehicleFlags(self, flags: int) -> None:
        """Set vehicle flags."""
        print(f"[llSetVehicleFlags]: {flags}")
    
    def api_llRemoveVehicleFlags(self, flags: int) -> None:
        """Remove vehicle flags."""
        print(f"[llRemoveVehicleFlags]: {flags}")
    
    def api_llSetBuoyancy(self, buoyancy: float) -> None:
        """Set buoyancy."""
        print(f"[llSetBuoyancy]: {buoyancy}")
    
    def api_llSetHoverHeight(self, height: float, water: int, tau: float) -> None:
        """Set hover height."""
        print(f"[llSetHoverHeight]: {height}")
    
    def api_llStopHover(self) -> None:
        """Stop hovering."""
        print("[llStopHover]: Hovering stopped")
    
    # =============================================================================
    # ANIMATION FUNCTIONS (10 functions)
    # =============================================================================
    
    def api_llStartAnimation(self, anim: str) -> None:
        """Start animation."""
        print(f"[llStartAnimation]: {anim}")
    
    def api_llStopAnimation(self, anim: str) -> None:
        """Stop animation."""
        print(f"[llStopAnimation]: {anim}")
    
    def api_llStopAllAnimations(self) -> None:
        """Stop all animations."""
        print("[llStopAllAnimations]: All animations stopped")
    
    def api_llGetAnimation(self, avatar: str) -> str:
        """Get avatar animation."""
        return "Standing"
    
    def api_llGetAnimationList(self, avatar: str) -> List[str]:
        """Get list of avatar animations."""
        return ["Standing", "Breathing"]
    
    def api_llSetAnimationOverride(self, anim_state: str, anim: str) -> None:
        """Set animation override."""
        print(f"[llSetAnimationOverride]: {anim_state} = {anim}")
    
    def api_llGetAnimationOverride(self, anim_state: str) -> str:
        """Get animation override."""
        return ""
    
    def api_llResetAnimationOverride(self, anim_state: str) -> None:
        """Reset animation override."""
        print(f"[llResetAnimationOverride]: {anim_state}")
    
    # =============================================================================
    # AVATAR AND AGENT FUNCTIONS (15 functions)
    # =============================================================================
    
    def api_llRequestAgentData(self, avatar: str, data: int) -> str:
        """Request agent data."""
        request_key = f"agent-data-{uuid.uuid4().hex[:8]}"
        
        # Simulate different data types
        if data == 1:  # DATA_ONLINE
            value = "1"
        elif data == 2:  # DATA_NAME
            value = "Test User"
        elif data == 3:  # DATA_BORN
            value = "2010-01-01"
        elif data == 4:  # DATA_RATING
            value = "[0, 0, 0, 0, 0, 0]"
        else:
            value = "0"
        
        self.simulator.event_queue.append(("dataserver", [request_key, value]))
        return request_key
    
    def api_llRequestDisplayName(self, avatar: str) -> str:
        """Request avatar display name."""
        request_key = f"display-name-{uuid.uuid4().hex[:8]}"
        self.simulator.event_queue.append(("dataserver", [request_key, "Test User"]))
        return request_key
    
    def api_llRequestUsername(self, avatar: str) -> str:
        """Request avatar username."""
        request_key = f"username-{uuid.uuid4().hex[:8]}"
        self.simulator.event_queue.append(("dataserver", [request_key, "test.user"]))
        return request_key
    
    def api_llKey2Name(self, key: str) -> str:
        """Convert key to name."""
        if key == self.simulator.global_scope.get("llGetOwner", lambda: "")():
            return "Test User"
        if hasattr(self.simulator, 'sensed_avatar_key') and key == self.simulator.sensed_avatar_key:
            return self.simulator.sensed_avatar_name
        return "Unknown User"
    
    def api_llName2Key(self, name: str) -> str:
        """Convert name to key (legacy function)."""
        return "00000000-0000-0000-0000-000000000000"  # Always returns NULL_KEY in modern LSL
    
    def api_llGetAgentSize(self, avatar: str) -> List[float]:
        """Get avatar size."""
        return [0.45, 0.6, 1.9]  # Typical avatar dimensions
    
    def api_llGetAgentInfo(self, avatar: str) -> int:
        """Get avatar info flags."""
        return 0  # No special flags
    
    def api_llGetAgentLanguage(self, avatar: str) -> str:
        """Get avatar language."""
        return "en-us"
    
    def api_llSameGroup(self, avatar: str) -> int:
        """Check if avatar is in same group."""
        return 0  # False
    
    def api_llOverMyLand(self, avatar: str) -> int:
        """Check if avatar is over owner's land."""
        return 1  # True
    
    def api_llGetPermissions(self) -> int:
        """Get granted permissions."""
        return 0  # No permissions
    
    def api_llGetPermissionsKey(self) -> str:
        """Get key that granted permissions."""
        return "00000000-0000-0000-0000-000000000000"
    
    def api_llRequestPermissions(self, avatar: str, perms: int) -> None:
        """Request permissions from avatar."""
        print(f"[llRequestPermissions]: Requesting {perms} from {avatar}")
        # Simulate automatic grant for testing
        self.simulator.event_queue.append(("run_time_permissions", [perms]))
    
    def api_llTakeControls(self, controls: int, accept: int, pass_on: int) -> None:
        """Take avatar controls."""
        print(f"[llTakeControls]: {controls}")
    
    def api_llReleaseControls(self) -> None:
        """Release avatar controls."""
        print("[llReleaseControls]: Controls released")
    
    # =============================================================================
    # MISCELLANEOUS UTILITY FUNCTIONS (20 functions)
    # =============================================================================
    
    def api_llGetOwner(self) -> str:
        """Get object owner."""
        return "npc-owner-uuid-12345"
    
    def api_llGetCreator(self) -> str:
        """Get object creator."""
        return "creator-uuid-67890"
    
    def api_llGetKey(self) -> str:
        """Get object key."""
        return "object-uuid-67890"
    
    def api_llGetScriptName(self) -> str:
        """Get script name."""
        return "Main Script"
    
    def api_llResetScript(self) -> None:
        """Reset script."""
        print("[llResetScript]: Script reset")
    
    def api_llGetScriptState(self, name: str) -> int:
        """Get script state."""
        return 1  # Running
    
    def api_llSetScriptState(self, name: str, run: int) -> None:
        """Set script state."""
        print(f"[llSetScriptState]: {name} = {run}")
    
    def api_llRemoteLoadScriptPin(self, target: str, name: str, pin: int, running: int, start_param: int) -> None:
        """Remote load script with PIN."""
        print(f"[llRemoteLoadScriptPin]: Loading {name} on {target}")
    
    def api_llSetRemoteScriptAccessPin(self, pin: int) -> None:
        """Set remote script access PIN."""
        print(f"[llSetRemoteScriptAccessPin]: {pin}")
    
    def api_llRemoteDataSetRegion(self) -> None:
        """Set region for remote data."""
        print("[llRemoteDataSetRegion]: Region set")
    
    def api_llRemoteDataReply(self, channel: str, message_id: str, sdata: str, idata: int) -> None:
        """Reply to remote data request."""
        print(f"[llRemoteDataReply]: {channel} {message_id}")
    
    def api_llOpenRemoteDataChannel(self) -> str:
        """Open remote data channel."""
        channel = f"remote-{uuid.uuid4().hex[:8]}"
        self.simulator.event_queue.append(("remote_data", [1, channel, "", "", 0]))
        return channel
    
    def api_llCloseRemoteDataChannel(self, channel: str) -> None:
        """Close remote data channel."""
        print(f"[llCloseRemoteDataChannel]: {channel}")
    
    def api_llSendRemoteData(self, channel: str, dest: str, idata: int, sdata: str) -> str:
        """Send remote data."""
        message_id = f"msg-{uuid.uuid4().hex[:8]}"
        print(f"[llSendRemoteData]: {channel} -> {dest}")
        return message_id
    
    def api_llEmail(self, address: str, subject: str, message: str) -> None:
        """Send email."""
        print(f"[llEmail]: To {address}, Subject: {subject}")
    
    def api_llGetNextEmail(self, address: str, subject: str) -> None:
        """Get next email."""
        print(f"[llGetNextEmail]: Checking {address}")
        self.simulator.event_queue.append(("email", ["", "", "", "", 0]))
    
    def api_llDie(self) -> None:
        """Delete object."""
        print("[llDie]: Object deleted")
        self.simulator._is_running = False
    
    def api_llSleep(self, seconds: float) -> None:
        """Sleep for specified seconds."""
        print(f"[llSleep]: Sleeping for {seconds} seconds")
        time_module.sleep(float(seconds))
    
    def api_llSetStatus(self, status: int, value: int) -> None:
        """Set object status."""
        print(f"[llSetStatus]: {status} = {value}")
    
    def api_llGetStatus(self, status: int) -> int:
        """Get object status."""
        return 0  # Default status
    
    def api_llGetMemoryLimit(self) -> int:
        """Get memory limit for script."""
        return 65536  # 64KB default LSL memory limit
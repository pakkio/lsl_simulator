#!/usr/bin/env python3
"""
Mock Flask server for testing OpenSim Corona Agent integration
Based on nexus project OpenSim integration endpoints
"""

from flask import Flask, request, jsonify
import json
import time
import logging
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class MockNexusServer:
    """
    A mock server that simulates the behavior of the Nexus AI backend for OpenSim.
    It manages NPC registration, conversation state, and generates contextual responses.
    """
    def __init__(self):
        """
        Initializes the mock server with empty NPC tracking and predefined conversation templates.
        """
        self.active_npcs = {}  # Stores data for all registered NPCs
        self.conversation_templates = {
            'greeting': [
                "Welcome to our region! I'm here to help you explore.",
                "Is this your first time visiting? I'd be happy to show you around.",
                "Looking for something specific? I know this area quite well.",
                "Need any assistance with navigation or finding activities?"
            ],
            'helpful': [
                "I'd be happy to help with that!",
                "Let me think about your question...",
                "That's an interesting point you raise.",
                "I can definitely assist you with that."
            ],
            'farewell': [
                "It was wonderful talking with you!",
                "Feel free to come back anytime you need help.",
                "Safe travels in your virtual adventures!",
                "I'll be here if you need anything else."
            ]
        }
    
    def parse_npc_profile(self, profile_text):
        """
        Parses a notecard-style NPC profile into a structured dictionary.
        The profile is expected to be a series of key-value pairs separated by colons.
        
        Args:
            profile_text (str): The raw text from the NPC's profile notecard.
            
        Returns:
            dict: A dictionary containing the parsed NPC attributes.
        """
        npc_data = {}
        current_key = None
        current_value = []
        
        lines = profile_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line and not line.startswith(' ') and not line.startswith('-'):
                # Save previous key-value
                if current_key:
                    npc_data[current_key] = '\n'.join(current_value).strip()
                
                # Start new key-value
                parts = line.split(':', 1)
                current_key = parts[0].strip()
                current_value = [parts[1].strip()] if len(parts) > 1 else []
            else:
                # Continue previous value
                if current_key:
                    current_value.append(line)
        
        # Save last key-value
        if current_key:
            npc_data[current_key] = '\n'.join(current_value).strip()
        
        return npc_data
    
    def find_npc_by_context(self, region, profile_text):
        """
        Finds a registered NPC based on its region. This is a simplified lookup.
        
        Args:
            region (str): The region where the NPC is located.
            profile_text (str): The NPC's profile text (currently unused in this mock function).
            
        Returns:
            str or None: The ID of the found NPC, or None if not found.
        """
        for npc_id, npc_info in self.active_npcs.items():
            if npc_info['region'] == region:
                return npc_id
        return None
    
    def generate_smart_response(self, npc_data, message_context, conversation_type='helpful'):
        """
        Generates a contextually appropriate response for the NPC to say.
        
        Args:
            npc_data (dict): The NPC's profile data.
            message_context (str): The message from the user.
            conversation_type (str): The type of conversation (e.g., 'greeting', 'farewell').
            
        Returns:
            str: A generated response string, truncated to LSL's 200-character limit.
        """
        name = npc_data.get('Name', 'Corona AI Agent')
        role = npc_data.get('Role', 'Virtual World Guide')
        
        # Select appropriate response template
        templates = self.conversation_templates.get(conversation_type, self.conversation_templates['helpful'])
        base_response = random.choice(templates)
        
        # Add context-specific information
        if 'help' in message_context.lower() or 'assist' in message_context.lower():
            base_response += f" As your {role.lower()}, I have access to information about this region and can guide you to various activities."
        elif 'question' in message_context.lower() or '?' in message_context:
            base_response += " I'll do my best to provide you with accurate information."
        elif any(word in message_context.lower() for word in ['goodbye', 'bye', 'farewell', 'leave']):
            base_response = random.choice(self.conversation_templates['farewell'])
        
        return base_response[:200]  # LSL character limit
    
    def create_npc_actions(self, response_text, npc_data, conversation_type='helpful'):
        """
        Creates a dictionary of actions for the NPC to perform in OpenSim.
        
        Args:
            response_text (str): The text the NPC should say.
            npc_data (dict): The NPC's profile data.
            conversation_type (str): The type of conversation.
            
        Returns:
            dict: A dictionary of actions (e.g., 'say', 'animate').
        """
        actions = {
            'say': response_text,
            'look_at': 'player',
            'text_display': '',
            'animation': '',
            'emote': ''
        }
        
        # Add appropriate animations/emotes based on context
        if conversation_type == 'greeting':
            actions['animation'] = 'wave'
            actions['text_display'] = '👋 Welcome! 👋'
        elif conversation_type == 'helpful':
            actions['text_display'] = '💡 Ready to Help 💡'
        elif conversation_type == 'farewell':
            actions['animation'] = 'bow'
            actions['text_display'] = '👋 Farewell! 👋'
        
        return actions

# Initialize mock server
mock_server = MockNexusServer()

@app.route('/npc/register', methods=['POST'])
def register_npc():
    """
    API Endpoint: Registers an NPC with the mock AI system.
    The NPC sends its profile data, and the server adds it to the active pool.
    """
    try:
        data = request.get_json()
        
        # Extract NPC profile data
        profile_text = data.get('profile', '')
        region = data.get('region', 'Unknown')
        position = data.get('position', [0, 0, 0])
        owner = data.get('owner', '')
        object_key = data.get('object_key', '')
        
        logging.info(f"NPC Registration request from region: {region}")
        logging.info(f"Profile data length: {len(profile_text)} chars")
        
        # Parse profile into structured data
        npc_data = mock_server.parse_npc_profile(profile_text)
        
        # Register with mock system
        npc_id = f"{region}_{object_key}"
        mock_server.active_npcs[npc_id] = {
            'npc_data': npc_data,
            'region': region,
            'position': position,
            'owner': owner,
            'object_key': object_key,
            'registered_at': time.time(),
            'last_interaction': None,
            'active_conversations': {}
        }
        
        # Extract info from parsed data
        npc_name = npc_data.get('Name', 'Corona AI Agent')
        npc_role = npc_data.get('Role', 'Virtual World Guide')
        
        logging.info(f"Successfully registered NPC: {npc_name} in {region}")
        
        return jsonify({
            'status': 'registered',
            'npc_id': npc_id,
            'npc_name': npc_name,
            'role': npc_role,
            'region': region,
            'capabilities': {
                'emotes': ['wave', 'bow', 'nod', 'point'],
                'animations': ['wave', 'bow', 'gesture', 'think'],
                'text_displays': ['Welcome!', 'Ready to Help', 'Thinking...']
            }
        }), 200
        
    except Exception as e:
        logging.error(f"NPC registration error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/npc/hook', methods=['POST'])
def npc_hook():
    """
    API Endpoint: Handles the initial interaction when an avatar approaches an NPC.
    It generates a greeting and initiates a conversation.
    """
    try:
        data = request.get_json()
        
        avatar_key = data.get('avatar')
        avatar_name = data.get('avatar_name', 'Unknown')
        region = data.get('region', 'Unknown')
        npc_profile = data.get('npc_profile', '')
        
        logging.info(f"Hook request: {avatar_name} approaching NPC in {region}")
        
        # Find NPC by profile or region
        npc_id = mock_server.find_npc_by_context(region, npc_profile)
        if not npc_id:
            # Create temporary NPC data from profile
            npc_data = mock_server.parse_npc_profile(npc_profile)
            npc_id = f"{region}_temp"
            mock_server.active_npcs[npc_id] = {
                'npc_data': npc_data,
                'region': region,
                'active_conversations': {}
            }
        
        npc_info = mock_server.active_npcs[npc_id]
        npc_data = npc_info['npc_data']
        
        # Generate greeting response
        greeting = mock_server.generate_smart_response(npc_data, f"greeting {avatar_name}", 'greeting')
        
        # Create structured response
        actions = mock_server.create_npc_actions(greeting, npc_data, 'greeting')
        
        # Track conversation
        npc_info['active_conversations'][avatar_key] = {
            'started_at': time.time(),
            'avatar_name': avatar_name,
            'conversation_state': 'greeting',
            'history': [{'type': 'system', 'content': 'Conversation initiated'}]
        }
        
        logging.info(f"Generated greeting for {avatar_name}: {greeting}")
        
        return jsonify(actions), 200
        
    except Exception as e:
        logging.error(f"Hook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/npc/talk', methods=['POST'])
def npc_talk():
    """
    API Endpoint: Manages an ongoing conversation between an avatar and an NPC.
    It takes the user's message and returns a contextual response.
    """
    try:
        data = request.get_json()
        
        avatar_key = data.get('avatar')
        avatar_name = data.get('avatar_name', 'Unknown')
        message = data.get('message', '')
        conversation_state = data.get('conversation_state', '')
        npc_profile = data.get('npc_profile', '')
        
        logging.info(f"Talk request: {avatar_name} said '{message}'")
        
        # Find active NPC conversation
        npc_id = None
        conversation = None
        
        for npc_key, npc_info in mock_server.active_npcs.items():
            if avatar_key in npc_info.get('active_conversations', {}):
                npc_id = npc_key
                conversation = npc_info['active_conversations'][avatar_key]
                break
        
        if not npc_id:
            # Create temporary conversation context
            npc_data = mock_server.parse_npc_profile(npc_profile)
            npc_id = f"temp_{avatar_key}"
            mock_server.active_npcs[npc_id] = {
                'npc_data': npc_data,
                'active_conversations': {
                    avatar_key: {
                        'started_at': time.time(),
                        'avatar_name': avatar_name,
                        'conversation_state': conversation_state,
                        'history': []
                    }
                }
            }
            conversation = mock_server.active_npcs[npc_id]['active_conversations'][avatar_key]
        
        npc_info = mock_server.active_npcs[npc_id]
        npc_data = npc_info['npc_data']
        
        # Add player message to history
        conversation['history'].append({
            'type': 'player',
            'content': message,
            'timestamp': time.time()
        })
        
        # Determine conversation type based on message
        conv_type = 'helpful'
        if any(word in message.lower() for word in ['goodbye', 'bye', 'farewell', 'leave']):
            conv_type = 'farewell'
        elif any(word in message.lower() for word in ['hello', 'hi', 'greet']):
            conv_type = 'greeting'
        
        # Generate contextual response
        response_text = mock_server.generate_smart_response(npc_data, message, conv_type)
        
        # Create structured actions
        actions = mock_server.create_npc_actions(response_text, npc_data, conv_type)
        
        # Update conversation state
        actions['conversation_state'] = conv_type
        
        # Add NPC response to history
        conversation['history'].append({
            'type': 'npc',
            'content': response_text,
            'timestamp': time.time()
        })
        
        logging.info(f"Generated response for {avatar_name}: {response_text}")
        
        return jsonify(actions), 200
        
    except Exception as e:
        logging.error(f"Talk error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/npc/status', methods=['GET'])
def npc_status():
    """
    API Endpoint: Provides the current status of all registered NPCs.
    """
    status = {
        'active_npcs': len(mock_server.active_conversations),
        'total_conversations': sum(len(npc['active_conversations']) for npc in mock_server.active_npcs.values()),
        'npcs': []
    }
    
    for npc_id, npc_info in mock_server.active_npcs.items():
        npc_data = npc_info['npc_data']
        status['npcs'].append({
            'npc_id': npc_id,
            'name': npc_data.get('Name', 'Unknown'),
            'region': npc_info.get('region', 'Unknown'),
            'active_conversations': len(npc_info.get('active_conversations', {})),
            'registered_at': npc_info.get('registered_at', 0)
        })
    
    return jsonify(status), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    API Endpoint: A simple health check to confirm the server is running.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'message': 'Mock Nexus Server is running'
    }), 200

if __name__ == '__main__':
    print("Starting Mock Nexus Server for OpenSim Corona Agent Integration")
    print("Endpoints available:")
    print("  POST /npc/register - Register NPC")
    print("  POST /npc/hook - Initial avatar interaction")
    print("  POST /npc/talk - Ongoing conversation")
    print("  GET /npc/status - NPC status")
    print("  GET /health - Health check")
    print("\nServer starting on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

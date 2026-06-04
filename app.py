import os
import uuid
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
from config import Config, config
from modules.ai_engine import ai_engine
from modules.voice_handler import voice_handler
from modules.database import db
from modules.college_data import college_data

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Enable CORS
CORS(app)

# Store conversation history in session
@app.before_request
def create_session():
    """Create session if not exists"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    if 'conversation' not in session:
        session['conversation'] = []

# Routes

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', 
                         college_name=college_data.get_college_name(),
                         model=ai_engine.get_current_model())

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        if len(user_message) > Config.MAX_MESSAGE_LENGTH:
            return jsonify({'error': 'Message too long'}), 400
        
        # Get conversation history
        conversation = session.get('conversation', [])
        
        # Generate response
        bot_response = ai_engine.generate_response(user_message, conversation)
        
        # Save to database
        chat_id = db.save_chat(user_message, bot_response, session['session_id'], ai_engine.get_current_model())
        db.save_query(user_message, category=None, user_ip=request.remote_addr)
        
        # Add to session history
        conversation.append({
            'role': 'user',
            'content': user_message
        })
        conversation.append({
            'role': 'assistant',
            'content': bot_response
        })
        
        # Keep only last 50 messages
        if len(conversation) > Config.MAX_CHAT_HISTORY:
            conversation = conversation[-Config.MAX_CHAT_HISTORY:]
        
        session['conversation'] = conversation
        session.modified = True
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().isoformat(),
            'chat_id': chat_id,
            'model': ai_engine.get_current_model()
        })
    
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice', methods=['POST'])
def voice():
    """Handle voice input"""
    try:
        if not Config.ENABLE_VOICE:
            return jsonify({'error': 'Voice feature disabled'}), 400
        
        # Get speech from microphone
        user_message = voice_handler.speech_to_text()
        
        if "Error" in user_message or "error" in user_message:
            return jsonify({'error': user_message}), 400
        
        # Process like normal chat
        conversation = session.get('conversation', [])
        bot_response = ai_engine.generate_response(user_message, conversation)
        
        # Convert response to speech
        voice_handler.text_to_speech(bot_response, use_thread=True)
        
        # Save to database
        chat_id = db.save_chat(user_message, bot_response, session['session_id'], ai_engine.get_current_model())
        
        # Add to history
        conversation.append({'role': 'user', 'content': user_message})
        conversation.append({'role': 'assistant', 'content': bot_response})
        session['conversation'] = conversation
        session.modified = True
        
        return jsonify({
            'user_message': user_message,
            'response': bot_response,
            'timestamp': datetime.now().isoformat(),
            'chat_id': chat_id
        })
    
    except Exception as e:
        print(f"Error in voice: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    """Get chat history"""
    try:
        history = db.get_chat_history(session.get('session_id'), limit=50)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    try:
        session['conversation'] = []
        session['session_id'] = str(uuid.uuid4())
        session.modified = True
        return jsonify({'success': True, 'message': 'Chat cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def send_feedback():
    """Save user feedback"""
    try:
        data = request.json
        chat_id = data.get('chat_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not chat_id or not rating:
            return jsonify({'error': 'Missing required fields'}), 400
        
        db.save_feedback(chat_id, rating, comment)
        return jsonify({'success': True, 'message': 'Feedback saved'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/college-info', methods=['GET'])
def get_college_info():
    """Get college information"""
    try:
        info_type = request.args.get('type', 'all')
        
        if info_type == 'contact':
            return jsonify(college_data.get_contact_info())
        elif info_type == 'departments':
            return jsonify(college_data.get_departments())
        elif info_type == 'facilities':
            return jsonify(college_data.get_facilities())
        elif info_type == 'scholarships':
            return jsonify(college_data.get_scholarships())
        elif info_type == 'admission':
            return jsonify(college_data.get_admission_requirements())
        elif info_type == 'faqs':
            return jsonify(college_data.get_faqs())
        else:
            return jsonify(college_data.get_full_info())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/switch-model', methods=['POST'])
def switch_model():
    """Switch AI model"""
    try:
        data = request.json
        model = data.get('model', 'openai')
        
        result = ai_engine.switch_model(model)
        return jsonify({'success': True, 'message': result, 'current_model': ai_engine.get_current_model()})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get chatbot statistics"""
    try:
        stats = db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': ai_engine.get_current_model(),
        'voice_enabled': Config.ENABLE_VOICE,
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Run app
    host = Config.FLASK_HOST
    port = Config.FLASK_PORT
    debug = Config.DEBUG
    
    print(f"🚀 Starting AI Chatbot on {host}:{port}")
    print(f"📊 Model: {ai_engine.get_current_model()}")
    print(f"🎙️ Voice: {'Enabled' if Config.ENABLE_VOICE else 'Disabled'}")
    
    app.run(host=host, port=port, debug=debug)

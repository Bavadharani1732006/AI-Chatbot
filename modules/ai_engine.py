import openai
import google.generativeai as genai
from config import Config
from modules.college_data import college_data

class AIEngine:
    """AI Engine for handling OpenAI and Gemini API integration"""
    
    def __init__(self, model_choice='openai'):
        self.model_choice = model_choice
        self.setup_api()
    
    def setup_api(self):
        """Setup API configuration based on model choice"""
        if self.model_choice == 'openai':
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            openai.api_key = Config.OPENAI_API_KEY
        elif self.model_choice == 'gemini':
            if not Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            genai.configure(api_key=Config.GEMINI_API_KEY)
        else:
            raise ValueError(f"Unknown model: {self.model_choice}")
    
    def get_system_prompt(self):
        """Get system prompt with college context"""
        college_info = college_data.format_info_for_chat()
        return f"""You are a helpful college information assistant chatbot.
        
{college_info}

Your responsibilities:
1. Answer questions about college admissions, programs, and facilities
2. Provide accurate information about fees, scholarships, and scholarships
3. Help students with their queries about campus life
4. Guide them through the application process
5. Be friendly, professional, and helpful

When you don't know an answer, suggest contacting the college directly.
Keep responses concise and informative."""
    
    def generate_response_openai(self, user_message, conversation_history=None):
        """Generate response using OpenAI API"""
        try:
            messages = []
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    if isinstance(msg, dict):
                        messages.append({
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", "")
                        })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()}
                ] + messages,
                temperature=Config.OPENAI_TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                top_p=0.9,
                frequency_penalty=0.5
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_response_gemini(self, user_message, conversation_history=None):
        """Generate response using Google Gemini API"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # Build context
            context = self.get_system_prompt()
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    if isinstance(msg, dict):
                        context += f"\nUser: {msg.get('content', '')}\n"
            
            # Create full prompt
            full_prompt = f"{context}\n\nUser: {user_message}"
            
            response = model.generate_content(full_prompt)
            return response.text
        
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_response(self, user_message, conversation_history=None):
        """Generate response based on selected model"""
        # Check for college-specific queries
        if self._is_college_query(user_message):
            college_response = self._get_college_specific_response(user_message)
            if college_response:
                return college_response
        
        # Fall back to AI model
        if self.model_choice == 'openai':
            return self.generate_response_openai(user_message, conversation_history)
        elif self.model_choice == 'gemini':
            return self.generate_response_gemini(user_message, conversation_history)
        else:
            return "Model not configured properly"
    
    def _is_college_query(self, message):
        """Check if query is college-related"""
        college_keywords = [
            'admission', 'admission', 'course', 'department', 'scholarship',
            'fee', 'facility', 'hostel', 'campus', 'program', 'placement',
            'application', 'requirement', 'semester', 'exam', 'college'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in college_keywords)
    
    def _get_college_specific_response(self, message):
        """Get response for college-specific queries"""
        message_lower = message.lower()
        
        # Admissions
        if 'admission' in message_lower or 'apply' in message_lower:
            reqs = college_data.get_admission_requirements()
            return f"Admission Requirements: {reqs.get('bachelor', [])}"
        
        # Departments
        elif 'department' in message_lower or 'course' in message_lower or 'program' in message_lower:
            depts = college_data.get_departments()
            dept_names = [d['name'] for d in depts]
            return f"We offer the following programs: {', '.join(dept_names)}"
        
        # Scholarships
        elif 'scholarship' in message_lower:
            scholarships = college_data.get_scholarships()
            return f"Available Scholarships:\n" + '\n'.join(scholarships)
        
        # Facilities
        elif 'facility' in message_lower or 'campus' in message_lower:
            facilities = college_data.get_facilities()
            return f"Campus Facilities: {', '.join(facilities)}"
        
        # Contact info
        elif 'contact' in message_lower or 'phone' in message_lower or 'email' in message_lower:
            contact = college_data.get_contact_info()
            return f"""Contact Information:
            Phone: {contact.get('phone')}
            Email: {contact.get('email')}
            Website: {contact.get('website')}
            Location: {contact.get('location')}"""
        
        # FAQs
        elif 'faq' in message_lower or 'question' in message_lower:
            results = college_data.search_faq(message)
            if results:
                return f"FAQ: {results[0]['question']}\nAnswer: {results[0]['answer']}"
        
        return None
    
    def switch_model(self, model_choice):
        """Switch between AI models"""
        if model_choice in ['openai', 'gemini']:
            self.model_choice = model_choice
            self.setup_api()
            return f"Switched to {model_choice}"
        return f"Unknown model: {model_choice}"
    
    def get_current_model(self):
        """Get current model in use"""
        return self.model_choice

# Initialize AI Engine
ai_engine = AIEngine(Config.AI_MODEL)

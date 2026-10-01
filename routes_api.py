import os
import re
import json
from groq import Groq
from flask import Blueprint, request, jsonify, session, current_app
from extensions import db
from models import Setting, Knowledge, Subject, Chat
from sqlalchemy import or_

api = Blueprint('api', __name__)

# Initialize the official Groq SDK client (lazy so .env is loaded first)
_groq_client = None
def get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get('GROQ_API_KEY', '')
        if not api_key or 'your_groq_api_key' in api_key:
            raise Exception('Groq API key is not configured. Set GROQ_API_KEY in your .env file.')
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def get_setting(key):
    setting = db.session.get(Setting, key)
    return setting.setting_value if setting else 'Sorry, I cannot find that information.'

def groq_request(messages, is_json=False):
    client = get_groq_client()
    
    # Resolve models dynamically so we don't cache stale environment variables
    text_model = os.environ.get('GROQ_MODEL', 'qwen/qwen3.8-27b')
    json_model = os.environ.get('GROQ_JSON_MODEL', 'qwen/qwen3.8-27b')
    model = json_model if is_json else text_model

    kwargs = {
        'model': model,
        'messages': messages,
        'temperature': 0.1 if is_json else 0.3,
    }
    if is_json:
        kwargs['response_format'] = {'type': 'json_object'}
    else:
        kwargs['max_tokens'] = 600

    completion = client.chat.completions.create(**kwargs)
    content = completion.choices[0].message.content
    if not content:
        raise Exception('Groq returned an empty response.')
    return content

def groq_json(prompt_str):
    messages = [{'role': 'user', 'content': prompt_str}]
    raw = groq_request(messages, is_json=True).strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)

def groq_text(messages):
    return groq_request(messages, is_json=False)

def session_id_value():
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    return session['session_id']

@api.route('/init', methods=['GET', 'POST'])
def init_chat():
    try:
        name_setting = db.session.get(Setting, "institute_name")
        welcome_setting = db.session.get(Setting, "welcome_message")
        
        name = name_setting.setting_value if name_setting else "Your Coaching Institute"
        welcome = welcome_setting.setting_value if welcome_setting else "Hi! I can answer questions about our institute."
        
        chat_history = []
        if 'session_id' in session:
            history_chats = Chat.query.filter_by(session_id=session['session_id']).order_by(Chat.id.desc()).limit(50).all()
            for c in reversed(history_chats):
                chat_history.append({'user': c.student_message, 'ai': c.answer})
                
        return jsonify({
            'success': True,
            'institute_name': name,
            'welcome_message': welcome,
            'history': chat_history
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'message': 'Message is required.'}), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({'success': False, 'message': 'Message cannot be empty.'}), 400
        if len(message) > 2000:
            return jsonify({'success': False, 'message': 'Message is too long.'}), 400

        result = route_question(message)
        
        # Save to database
        new_chat = Chat(
            session_id=session_id_value(),
            student_message=message,
            route=result['route'],
            intent=result.get('intent'),
            answer=result['answer']
        )
        db.session.add(new_chat)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'route': result['route'],
            'intent': result.get('intent')
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e) if current_app.debug else 'Something went wrong. Please try again.'}), 500

def route_question(message):
    history_chats = Chat.query.filter_by(session_id=session_id_value()).order_by(Chat.id.desc()).limit(4).all()
    history = [{'student_message': c.student_message, 'answer': c.answer} for c in reversed(history_chats)]

    # Pre-filter for simple greetings/thanks
    normalized = re.sub(r'[^\w\s]', '', message.lower()).strip()
    words = [w for w in normalized.split() if w]
    
    if 0 < len(words) <= 3:
        is_greeting = True
        is_thanks = True
        greeting_whitelist = {'hi','hello','hey','namaste','pranam','good','morning','afternoon','evening','sir','maam','madam','teacher','there'}
        thanks_whitelist = {'thanks','thank','you','ok','okay','great','awesome','nice','dhanyawad','shukriya','sir','maam','madam','teacher','very','much'}
        
        for w in words:
            if w not in greeting_whitelist: is_greeting = False
            if w not in thanks_whitelist: is_thanks = False
            
        if is_greeting and any(w in {'hi','hello','hey','namaste','pranam','morning','afternoon','evening'} for w in words):
            return {'route': 'greeting', 'intent': 'greeting', 'answer': "Hello! Welcome to our institute. How can I help you today?"}
        if is_thanks and any(w in {'thanks','thank','ok','okay','dhanyawad','shukriya'} for w in words):
            return {'route': 'greeting', 'intent': 'thanks', 'answer': "You're very welcome! Let me know if you need help with anything else."}

    subjects_db = Subject.query.filter_by(is_active=True).order_by(Subject.name).all()
    subject_text = "\n".join([f"- {s.name} (classes {s.class_level or 'all'})" for s in subjects_db])
    
    prompt = router_prompt(message, subject_text, history)
    router = groq_json(prompt)
    
    q_type = router.get('type', 'other')
    intent = router.get('intent', '')

    if q_type == 'institute':
        answer = institute_answer(message, router, history)
        return {'route': 'institute', 'intent': intent or 'institute_query', 'answer': answer}

    if q_type == 'subject':
        subject_name = router.get('subject', '').strip()
        allowed = next((s for s in subjects_db if s.name.lower() == subject_name.lower()), None)
        
        if not allowed:
            return {'route': 'blocked', 'intent': 'out_of_scope', 'answer': get_setting('out_of_scope_message')}
        
        return {'route': 'subject', 'intent': 'subject_question', 'answer': subject_answer(message, allowed, router, subject_text, history)}

    return {'route': 'blocked', 'intent': 'out_of_scope', 'answer': get_setting('out_of_scope_message')}

def router_prompt(message, subjects, history):
    history_context = ''
    if history:
        history_context = "Recent conversation context (use this to resolve pronouns/references like 'it', 'that', 'how much'):\n"
        for h in history:
            history_context += f"Student: {h['student_message']}\nAI: {h['answer']}\n"
        history_context += "\n"

    return f"""You are a strict question router for a coaching institute chatbot.
Return ONLY valid JSON. Do not use markdown.

Your job is to classify the student's message into exactly one type:
- institute: questions about this institute, including fees, admission, teachers, batches, timetable, address, contact, rules, facilities, holidays, courses, policies, or anything that asks for institute-specific information.
- subject: an academic question about one of the explicitly allowed subjects below.
- other: anything else.

Allowed subjects:
{subjects}

Understand spelling mistakes, Hinglish, Hindi written in Latin script, abbreviations, and informal language.
Examples:
"10th ka fee kitna hai" => institute, intent fee, class_level 10
"sir 10 ka kitna lagega" => institute, intent fee, class_level 10
"admisn kaise lena h" => institute, intent admission
"what is photosynthesis" => subject if Biology is allowed
"who is the president" => other unless that is explicitly institute information

Never answer the question yourself. Only classify it.

Return this shape:
{{"type":"institute|subject|other","intent":"short_intent","subject":"allowed subject or empty","class_level":"or empty"}}

{history_context}
Current Student message:
{message}
"""

def institute_answer(message, router, history):
    intent = router.get('intent', '')
    
    # Simple SQLite search instead of MySQL FULLTEXT MATCH AGAINST
    # Instead of brittle SQL LIKE keyword matching, we fetch all active knowledge records 
    # (up to a safe limit of 50 items to stay within context windows). 
    # The LLM's massive attention mechanism acts as the ultimate semantic search engine, 
    # natively understanding synonyms (cost = fee) without needing exact word matches.
    rows = Knowledge.query.filter_by(is_active=True).order_by(Knowledge.updated_at.desc()).limit(50).all()
    
    context = ''
    if rows:
        for r in rows:
            context += f"\n[{r.title} | {r.category}]\n{r.content}\n"
    else:
        context = "No institute records currently exist in the database."

    institute_name = get_setting('institute_name')
    
    
    sys_prompt = f"""You are the friendly, helpful counselor for {institute_name} (located in Chapra, Bihar).
Be warm, encouraging, and highly professional. Answer the student's question using ONLY the supplied institute records below.
Do not add, guess, or infer any institute fact that is not explicitly present.
If the records do not contain the answer, politely say you do not have that information and advise contacting the institute office.
Be concise and natural. Match the student's language when practical.

INSTITUTE RECORDS:
{context}"""

    messages = [{'role': 'system', 'content': sys_prompt}]
    for h in history:
        messages.append({'role': 'user', 'content': h['student_message']})
        messages.append({'role': 'assistant', 'content': h['answer']})
    messages.append({'role': 'user', 'content': message})

    return groq_text(messages)

def subject_answer(message, subject, router, subject_text, history):
    sys_prompt = f"""You are a friendly, encouraging academic tutor for Deep Vihar coaching institute in Chapra, Bihar.
The student's question has been classified as a question about the allowed subject: {subject.name}.
Only answer academic content that belongs to this subject and, when possible, to the student's class level: {router.get('class_level', '')}.
Do not answer unrelated general-knowledge, political, medical, legal, or other out-of-scope questions.
If the question is clearly outside the subject, politely say you can only help with the allowed coaching subjects.
Explain clearly and accurately. KEEP YOUR EXPLANATION CONCISE, strictly answering the student's question without adding unrequested extra sections (e.g. no extra "sanity checks" or long derivations unless asked).
Do NOT use ASCII art for drawings; rely on simple Markdown text explanations.
Do not claim that a fact comes from the institute unless institute records were supplied (none are supplied here).

Allowed subjects:
{subject_text}"""

    messages = [{'role': 'system', 'content': sys_prompt}]
    for h in history:
        messages.append({'role': 'user', 'content': h['student_message']})
        messages.append({'role': 'assistant', 'content': h['answer']})
    messages.append({'role': 'user', 'content': message})

    return groq_text(messages)

"""
chatbot/views.py
Model: gemini-2.5-flash (Google's current best free model, April 2026)
URL: v1beta endpoint (required for AI Studio keys)
No SDK needed — pure requests only.
"""
import json, base64, uuid, requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ChatSession, ChatMessage

# v1beta is the correct endpoint for AI Studio (aistudio.google.com) API keys
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# Current models as of April 2026 — confirmed from ai.google.dev/gemini-api/docs/models
MODELS = [
    "gemini-2.5-flash",       # Best free model — fast, smart, multimodal
    "gemini-2.5-flash-lite",  # Lighter fallback — still free
    "gemini-2.0-flash",       # Older stable fallback
]

SYSTEM_PROMPT = """You are Dr. Aida, a compassionate AI medical assistant specialising in geriatric care for elderly patients in Malaysia.

Analyse the patient's symptoms carefully and respond ONLY as valid JSON:
{
  "risk_level": "LOW|MODERATE|HIGH|CRITICAL",
  "risk_color": "green|yellow|orange|red",
  "possible_conditions": ["condition1", "condition2"],
  "analysis": "Detailed analysis of the symptoms",
  "advice": ["advice1", "advice2", "advice3"],
  "suggestions": ["suggestion1", "suggestion2"],
  "follow_up_questions": ["question1", "question2", "question3"],
  "see_doctor": true,
  "emergency": false,
  "message": "Warm conversational reply to the patient"
}
If emergency=true, include 'Please call 999 immediately' in message.
Be empathetic, use simple language for elderly patients.
Always respond in the same language the patient uses (English or Malay)."""


def get_or_create_session(request):
    sid = request.session.get('chat_session_id')
    if not sid:
        sid = str(uuid.uuid4())
        request.session['chat_session_id'] = sid
    session, _ = ChatSession.objects.get_or_create(session_id=sid)
    return session


def chatbot_page(request):
    session = get_or_create_session(request)
    messages = session.messages.all()
    return render(request, 'chatbot/chatbot.html', {'messages': messages})


def _call_gemini(api_key, contents):
    """
    Call Gemini REST API. Tries each model in MODELS until one succeeds.
    System prompt injected as first turn — works reliably on all models.
    """
    full_contents = [
        {"role": "user",  "parts": [{"text": f"SYSTEM: {SYSTEM_PROMPT}\n\nAcknowledge your role."}]},
        {"role": "model", "parts": [{"text": "Understood. I am Dr. Aida. Please describe your symptoms and I will respond in JSON."}]},
    ] + contents

    payload = {
        "contents": full_contents,
        "generationConfig": {"maxOutputTokens": 1500, "temperature": 0.4},
    }

    last_error = "No model succeeded"
    for model in MODELS:
        try:
            r = requests.post(
                GEMINI_URL.format(model=model),
                params={"key": api_key},
                json=payload,
                timeout=30,
            )
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]

            err = r.json().get("error", {})
            code = err.get("code", r.status_code)
            msg  = err.get("message", r.text[:200])

            # Bad key — stop immediately
            if code in (400, 401, 403) and any(w in msg for w in ["API_KEY_INVALID", "API key", "invalid"]):
                raise Exception(f"INVALID_KEY: {msg}")

            last_error = f"HTTP {code}: {msg}"
            continue   # quota / not-found / other → try next model

        except requests.exceptions.Timeout:
            last_error = "Request timed out (30s). Check internet connection."; continue
        except requests.exceptions.ConnectionError:
            last_error = "Cannot reach Gemini API. Check internet connection."; continue
        except Exception as e:
            if "INVALID_KEY" in str(e): raise
            last_error = str(e); continue

    raise Exception(last_error)


@csrf_exempt
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user_text      = request.POST.get('message', '').strip()
    uploaded_image = request.FILES.get('image')
    uploaded_file  = request.FILES.get('file')

    if not user_text and not uploaded_image and not uploaded_file:
        return JsonResponse({'error': 'No input provided'}, status=400)

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return JsonResponse({'error': 'GEMINI_API_KEY is empty in .env. Add your key and restart the server.'}, status=500)

    session = get_or_create_session(request)
    ChatMessage.objects.create(
        session=session, role='user',
        content=user_text or '[Attachment uploaded]',
        image=uploaded_image, file_attachment=uploaded_file,
    )

    # Build conversation history
    msgs = list(session.messages.all())
    contents = []
    for msg in msgs[:-1]:
        role = 'user' if msg.role == 'user' else 'model'
        contents.append({"role": role, "parts": [{"text": msg.content}]})

    # Build current message
    parts = []
    if user_text:
        parts.append({"text": user_text})
    if uploaded_image:
        uploaded_image.seek(0)
        parts.append({"inline_data": {"mime_type": uploaded_image.content_type,
                                       "data": base64.b64encode(uploaded_image.read()).decode()}})
        if not user_text:
            parts.insert(0, {"text": "Analyse this medical image."})
    if uploaded_file and not uploaded_image:
        uploaded_file.seek(0)
        try:    parts.append({"text": f"Medical document:\n{uploaded_file.read().decode('utf-8')}"})
        except: parts.append({"text": "A medical document was uploaded."})
    if not parts:
        parts = [{"text": "Hello, I need medical assistance."}]

    contents.append({"role": "user", "parts": parts})

    try:
        raw = _call_gemini(api_key, contents)
    except Exception as e:
        err = str(e)
        if "INVALID_KEY" in err:
            return JsonResponse({'error': 'Invalid API key. Get a new one at https://aistudio.google.com/'}, status=401)
        return JsonResponse({'error': f'Gemini error: {err}'}, status=500)

    raw = raw.strip()
    if '```json' in raw: raw = raw.split('```json')[1].split('```')[0].strip()
    elif '```' in raw:   raw = raw.split('```')[1].split('```')[0].strip()

    try:
        ai_data = json.loads(raw)
    except json.JSONDecodeError:
        ai_data = {
            "risk_level": "MODERATE", "risk_color": "yellow",
            "possible_conditions": ["Assessment needed"],
            "analysis": raw, "advice": ["Please consult a doctor."],
            "suggestions": ["Visit your nearest clinic"],
            "follow_up_questions": ["How long have you had these symptoms?",
                                    "Do you have existing medical conditions?",
                                    "Are you on any medication?"],
            "see_doctor": True, "emergency": False, "message": raw,
        }

    ChatMessage.objects.create(session=session, role='assistant', content=json.dumps(ai_data))
    return JsonResponse({'success': True, 'response': ai_data})


@csrf_exempt
def clear_chat(request):
    if request.method == 'POST':
        sid = request.session.get('chat_session_id')
        if sid:
            ChatSession.objects.filter(session_id=sid).delete()
        if 'chat_session_id' in request.session:
            del request.session['chat_session_id']
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

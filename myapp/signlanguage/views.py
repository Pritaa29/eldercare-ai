"""
signlanguage/views.py
Model: gemini-2.5-flash (current stable free model, April 2026)
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json, base64, requests
import numpy as np, cv2

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]

SIGN_PROMPT = """You are a medical sign language interpreter helping elderly patients in Malaysia communicate with healthcare providers.

Look at this image showing a hand gesture or sign language sign.
1. Identify the gesture shown
2. Interpret its medical/healthcare meaning
3. Provide appropriate medical advice

Respond ONLY as valid JSON:
{
  "gesture_detected": "description of what you see in the image",
  "medical_interpretation": "what this gesture means in a medical context",
  "response": "appropriate advice or response for the patient",
  "confidence": "high|medium|low",
  "common_medical_signs": ["example 1", "example 2", "example 3"]
}"""


def signlanguage_page(request):
    return render(request, 'signlanguage/signlanguage.html')


def _gemini_vision(api_key, image_bytes, mime_type):
    img_b64 = base64.b64encode(image_bytes).decode()
    payload = {
        "contents": [{"role": "user", "parts": [
            {"text": SIGN_PROMPT},
            {"inline_data": {"mime_type": mime_type, "data": img_b64}}
        ]}],
        "generationConfig": {"maxOutputTokens": 800, "temperature": 0.3}
    }
    last_err = "No model succeeded"
    for model in MODELS:
        try:
            r = requests.post(GEMINI_URL.format(model=model), params={"key": api_key},
                              json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            err = r.json().get("error", {})
            if err.get("code") in (400, 401, 403) and any(
                    w in err.get("message","") for w in ["API_KEY_INVALID","API key","invalid"]):
                raise Exception(f"INVALID_KEY: {err.get('message','')}")
            last_err = f"HTTP {err.get('code','?')}: {err.get('message', r.text[:100])}"
            continue
        except Exception as e:
            if "INVALID_KEY" in str(e): raise
            last_err = str(e); continue
    raise Exception(last_err)


def _parse(raw):
    raw = raw.strip()
    if '```json' in raw: raw = raw.split('```json')[1].split('```')[0].strip()
    elif '```' in raw:   raw = raw.split('```')[1].split('```')[0].strip()
    return json.loads(raw)


@csrf_exempt
def analyze_sign(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return JsonResponse({'error': 'GEMINI_API_KEY not set in .env'}, status=500)
    try:
        data = json.loads(request.body)
        frame_data = data.get('frame', '')
        if not frame_data:
            return JsonResponse({'error': 'No frame data'}, status=400)
        if ',' in frame_data:
            frame_data = frame_data.split(',')[1]

        img_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return JsonResponse({'error': 'Could not decode frame'}, status=400)

        import mediapipe as mp
        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        hand_detected = False
        annotated_b64 = None

        with mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                            min_detection_confidence=0.6, min_tracking_confidence=0.5) as hands:
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_hand_landmarks:
                hand_detected = True
                for hl in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(37,99,235),thickness=2,circle_radius=4),
                        mp_drawing.DrawingSpec(color=(96,165,250),thickness=2))
                _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                annotated_b64 = base64.b64encode(buf).decode()

        try:
            raw = _gemini_vision(api_key, base64.b64decode(frame_data), 'image/jpeg')
            try:    gesture_data = _parse(raw)
            except: gesture_data = {
                "gesture_detected": "Hand gesture detected" if hand_detected else "No clear gesture",
                "medical_interpretation": raw, "response": "Please consult your healthcare provider.",
                "confidence": "medium", "common_medical_signs": ["Pain","Help needed","Yes/No"]
            }
        except Exception as e:
            if "INVALID_KEY" in str(e):
                return JsonResponse({'error': 'Invalid API key. Check your .env file.'}, status=401)
            gesture_data = {
                "gesture_detected": "Analysis unavailable", "medical_interpretation": f"Error: {e}",
                "response": "Please consult your healthcare provider.", "confidence": "low",
                "common_medical_signs": ["Pain","Help needed","Yes/No"]
            }

        return JsonResponse({'success': True, 'hand_detected': hand_detected,
                             'gesture_data': gesture_data,
                             'annotated_frame': f'data:image/jpeg;base64,{annotated_b64}' if annotated_b64 else None})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def analyze_uploaded_sign(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return JsonResponse({'error': 'GEMINI_API_KEY not set in .env'}, status=500)
    f = request.FILES.get('image')
    if not f:
        return JsonResponse({'error': 'No image uploaded'}, status=400)
    try:
        raw = _gemini_vision(api_key, f.read(), f.content_type)
        try:    result = _parse(raw)
        except: result = {"gesture_detected":"Detected","medical_interpretation":raw,"response":raw,"confidence":"medium"}
        return JsonResponse({'success': True, 'gesture_data': result})
    except Exception as e:
        if "INVALID_KEY" in str(e):
            return JsonResponse({'error': 'Invalid API key. Check your .env file.'}, status=401)
        return JsonResponse({'error': str(e)}, status=500)

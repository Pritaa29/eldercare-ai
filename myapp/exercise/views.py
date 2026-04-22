"""
exercise/views.py
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


def get_pose():
    import mediapipe as mp
    return mp.solutions.pose, mp.solutions.drawing_utils


def exercise_page(request):
    return render(request, 'exercise/exercise.html')


def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    rad = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(rad * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle


def _gemini_text(api_key, prompt):
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
               "generationConfig": {"maxOutputTokens": 600, "temperature": 0.3}}
    last_err = "No model succeeded"
    for model in MODELS:
        try:
            r = requests.post(GEMINI_URL.format(model=model), params={"key": api_key},
                              json=payload, timeout=20)
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


@csrf_exempt
def analyze_frame(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        frame_data = data.get('frame', '')
        exercise_type = data.get('exercise_type', 'general')
        if not frame_data:
            return JsonResponse({'error': 'No frame data'}, status=400)
        if ',' in frame_data:
            frame_data = frame_data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(frame_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return JsonResponse({'error': 'Could not decode frame'}, status=400)

        mp_pose, mp_drawing = get_pose()
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            feedback, angles, score, warnings = [], {}, 100, []
            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                def gl(i): l=lm[i]; return [l.x, l.y]
                LS=gl(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
                RS=gl(mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
                LE=gl(mp_pose.PoseLandmark.LEFT_ELBOW.value)
                RE=gl(mp_pose.PoseLandmark.RIGHT_ELBOW.value)
                LW=gl(mp_pose.PoseLandmark.LEFT_WRIST.value)
                RW=gl(mp_pose.PoseLandmark.RIGHT_WRIST.value)
                LH=gl(mp_pose.PoseLandmark.LEFT_HIP.value)
                RH=gl(mp_pose.PoseLandmark.RIGHT_HIP.value)
                LK=gl(mp_pose.PoseLandmark.LEFT_KNEE.value)
                RK=gl(mp_pose.PoseLandmark.RIGHT_KNEE.value)
                LA=gl(mp_pose.PoseLandmark.LEFT_ANKLE.value)
                RA=gl(mp_pose.PoseLandmark.RIGHT_ANKLE.value)
                NOSE=gl(mp_pose.PoseLandmark.NOSE.value)
                angles = {
                    'left_elbow':  round(calculate_angle(LS,LE,LW),1),
                    'right_elbow': round(calculate_angle(RS,RE,RW),1),
                    'left_knee':   round(calculate_angle(LH,LK,LA),1),
                    'right_knee':  round(calculate_angle(RH,RK,RA),1),
                    'left_hip':    round(calculate_angle(LS,LH,LK),1),
                    'right_hip':   round(calculate_angle(RS,RH,RK),1),
                }
                sdiff = abs(LS[1]-RS[1]); hdiff = abs(LH[1]-RH[1])
                if exercise_type == 'squat':
                    avg_k = (angles['left_knee']+angles['right_knee'])/2
                    if avg_k > 160:   feedback.append({'type':'info','text':'Standing. Bend knees to begin squat.'})
                    elif 80<=avg_k<=120: feedback.append({'type':'success','text':'✅ Excellent squat depth!'})
                    elif avg_k < 80:
                        feedback.append({'type':'warning','text':'⚠️ Too deep — risk of knee strain.'})
                        score-=20; warnings.append('Knee too acute')
                    if sdiff > 0.05: feedback.append({'type':'warning','text':'⚠️ Shoulders uneven.'}); score-=10
                elif exercise_type == 'arm_raise':
                    avg_e = (angles['left_elbow']+angles['right_elbow'])/2
                    if avg_e > 150: feedback.append({'type':'success','text':'✅ Arms fully extended!'})
                    elif avg_e < 90: feedback.append({'type':'info','text':'Raise arms higher if comfortable.'})
                elif exercise_type == 'standing':
                    if abs(NOSE[0]-(LH[0]+RH[0])/2) > 0.1:
                        feedback.append({'type':'warning','text':'⚠️ Leaning detected. Stand straight.'}); score-=15
                    else: feedback.append({'type':'success','text':'✅ Good upright posture!'})
                    if sdiff > 0.04: feedback.append({'type':'warning','text':'⚠️ One shoulder higher.'}); score-=10
                else:
                    if sdiff > 0.05: feedback.append({'type':'warning','text':'⚠️ Shoulders appear uneven.'}); score-=10
                    if hdiff > 0.05: feedback.append({'type':'warning','text':'⚠️ Hips appear tilted.'}); score-=10
                    if not feedback: feedback.append({'type':'success','text':'✅ Posture looks balanced!'})
                score = max(0, min(100, score))
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(37,99,235),thickness=2,circle_radius=3),
                    mp_drawing.DrawingSpec(color=(96,165,250),thickness=2))
                _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                return JsonResponse({'success':True,'pose_detected':True,'angles':angles,
                    'feedback':feedback,'posture_score':score,'warnings':warnings,
                    'annotated_frame':f'data:image/jpeg;base64,{base64.b64encode(buf).decode()}'})
            else:
                return JsonResponse({'success':True,'pose_detected':False,
                    'feedback':[{'type':'info','text':'No person detected. Step into frame and ensure good lighting.'}],
                    'posture_score':0,'angles':{},'warnings':[],'annotated_frame':None})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_ai_advice(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return JsonResponse({'error': 'GEMINI_API_KEY not set in .env'}, status=500)
    try:
        d = json.loads(request.body)
        prompt = (
            f"You are a physiotherapist helping an elderly patient in Malaysia.\n"
            f"Exercise: {d.get('exercise_type','general')} | Score: {d.get('posture_score',100)}/100\n"
            f"Issues: {', '.join(d.get('warnings',[])) or 'none'} | Angles: {json.dumps(d.get('angles',{}))}\n\n"
            f"Write 3-4 sentences of warm encouraging advice covering: what they did well, "
            f"one thing to improve, and one safety tip. Plain text only."
        )
        text = _gemini_text(api_key, prompt)
        return JsonResponse({'success': True, 'advice': text})
    except Exception as e:
        if "INVALID_KEY" in str(e):
            return JsonResponse({'error': 'Invalid API key. Check your .env file.'}, status=401)
        return JsonResponse({'error': str(e)}, status=500)

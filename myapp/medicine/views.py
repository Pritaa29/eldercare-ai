import uuid, json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MedicineProfile, Medicine, ReminderTime

def get_or_create_profile(request):
    sid = request.session.get('medicine_session_id')
    if not sid:
        sid = str(uuid.uuid4())
        request.session['medicine_session_id'] = sid
    profile, _ = MedicineProfile.objects.get_or_create(session_id=sid)
    return profile

def medicine_page(request):
    profile = get_or_create_profile(request)
    medicines = profile.medicines.filter(is_active=True).prefetch_related('reminder_times')
    return render(request, 'medicine/medicine.html', {'medicines': medicines, 'profile': profile})

@csrf_exempt
def add_medicine(request):
    if request.method != 'POST': return JsonResponse({'error':'Method not allowed'},status=405)
    try:
        data = json.loads(request.body)
        profile = get_or_create_profile(request)
        med = Medicine.objects.create(
            profile=profile, name=data['name'], dosage=data['dosage'],
            frequency=data.get('frequency','once'), meal_timing=data.get('meal_timing','after'),
            notes=data.get('notes',''),
        )
        for t in data.get('times',[]):
            ReminderTime.objects.create(medicine=med, time=t)
        return JsonResponse({'success':True,'medicine':{
            'id':med.id,'name':med.name,'dosage':med.dosage,
            'frequency':med.get_frequency_display(),'meal_timing':med.get_meal_timing_display(),
            'times':[str(rt.time)[:5] for rt in med.reminder_times.all()],'notes':med.notes,
        }})
    except Exception as e: return JsonResponse({'error':str(e)},status=400)

@csrf_exempt
def delete_medicine(request, medicine_id):
    if request.method != 'DELETE': return JsonResponse({'error':'Method not allowed'},status=405)
    profile = get_or_create_profile(request)
    med = get_object_or_404(Medicine, id=medicine_id, profile=profile)
    med.is_active = False; med.save()
    return JsonResponse({'success':True})

@csrf_exempt
def acknowledge_reminder(request):
    return JsonResponse({'success':True})

def get_medicines_api(request):
    profile = get_or_create_profile(request)
    meds = profile.medicines.filter(is_active=True).prefetch_related('reminder_times')
    return JsonResponse({'medicines':[{
        'id':m.id,'name':m.name,'dosage':m.dosage,
        'frequency':m.get_frequency_display(),'meal_timing':m.get_meal_timing_display(),
        'times':[str(rt.time)[:5] for rt in m.reminder_times.all()],'notes':m.notes,
    } for m in meds]})

def get_due_reminders(request):
    """API for Service Worker / polling: returns medicines due at current minute."""
    from django.utils import timezone
    now = timezone.localtime(timezone.now())
    current_h = now.hour
    current_m = now.minute

    profile = get_or_create_profile(request)
    meds = profile.medicines.filter(is_active=True).prefetch_related('reminder_times')

    due = []
    all_meds = []
    for m in meds:
        times = [str(rt.time)[:5] for rt in m.reminder_times.all()]
        all_meds.append({
            'id': m.id,
            'name': m.name,
            'dosage': m.dosage,
            'meal_timing': m.get_meal_timing_display(),
            'times': times,
        })
        for t in times:
            try:
                h, mn = map(int, t.split(':'))
                if h == current_h and mn == current_m:
                    due.append({'name': m.name, 'dosage': m.dosage, 'meal_timing': m.get_meal_timing_display()})
            except Exception:
                pass

    return JsonResponse({'due': due, 'all_medicines': all_meds, 'current_time': f'{current_h:02d}:{current_m:02d}'})

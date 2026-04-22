
import uuid
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from .models import EmergencyContact, EmergencyAlert
import requests


def get_session_id(request):
    sid = request.session.get('emergency_session_id')
    if not sid:
        sid = str(uuid.uuid4())
        request.session['emergency_session_id'] = sid
    return sid


def emergency_page(request):
    session_id = get_session_id(request)
    contacts = EmergencyContact.objects.filter(session_id=session_id)
    recent_alerts = EmergencyAlert.objects.filter(session_id=session_id)[:5]
    return render(request, 'emergency/emergency.html', {
        'contacts': contacts,
        'recent_alerts': recent_alerts,
    })


@csrf_exempt
def add_contact(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        session_id = get_session_id(request)

        contact = EmergencyContact.objects.create(
            session_id=session_id,
            name=data['name'],
            relationship=data.get('relationship', 'Family Member'),
            email=data.get('email', ''),
            telegram_chat_id=data.get('telegram_chat_id', ''),
            phone=data.get('phone', ''),
            is_primary=data.get('is_primary', False),
        )
        return JsonResponse({
            'success': True,
            'contact': {
                'id': contact.id,
                'name': contact.name,
                'relationship': contact.relationship,
                'email': contact.email,
                'phone': contact.phone,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def delete_contact(request, contact_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    session_id = get_session_id(request)
    try:
        contact = EmergencyContact.objects.get(id=contact_id, session_id=session_id)
        contact.delete()
        return JsonResponse({'success': True})
    except EmergencyContact.DoesNotExist:
        return JsonResponse({'error': 'Contact not found'}, status=404)


@csrf_exempt
def trigger_sos(request):
    """
    Main SOS trigger — sends alerts to ALL emergency contacts.
    Supports: Email via SendGrid + Telegram Bot messages.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        session_id = get_session_id(request)
        lat = data.get('latitude')
        lng = data.get('longitude')
        address = data.get('address', 'Location unavailable')
        patient_name = data.get('patient_name', 'Your elderly family member')
        custom_message = data.get('message', '')

        contacts = EmergencyContact.objects.filter(session_id=session_id)

        if not contacts.exists():
            return JsonResponse({
                'error': 'No emergency contacts found. Please add contacts first.'
            }, status=400)

        # Create alert record
        alert = EmergencyAlert.objects.create(
            session_id=session_id,
            patient_name=patient_name,
            latitude=lat,
            longitude=lng,
            address=address,
            message=custom_message,
            status='pending',
        )

        maps_link = ''
        if lat and lng:
            maps_link = f'https://www.google.com/maps?q={lat},{lng}'

        timestamp = timezone.localtime(timezone.now()).strftime('%d %B %Y, %I:%M %p')

        notified = 0
        failed = 0

        for contact in contacts:
            email_ok = False
            telegram_ok = False

            # ── Email Alert ──
            if contact.email:
                try:
                    _send_emergency_email(
                        to_email=contact.email,
                        contact_name=contact.name,
                        patient_name=patient_name,
                        address=address,
                        maps_link=maps_link,
                        timestamp=timestamp,
                        custom_message=custom_message,
                    )
                    email_ok = True
                except Exception as e:
                    print(f"Email failed for {contact.email}: {e}")

            # ── Telegram Alert ──
            if contact.telegram_chat_id:
                try:
                    _send_telegram_alert(
                        chat_id=contact.telegram_chat_id,
                        contact_name=contact.name,
                        patient_name=patient_name,
                        address=address,
                        maps_link=maps_link,
                        timestamp=timestamp,
                        custom_message=custom_message,
                    )
                    telegram_ok = True
                except Exception as e:
                    print(f"Telegram failed for {contact.telegram_chat_id}: {e}")

            if email_ok or telegram_ok:
                notified += 1
            else:
                failed += 1

        alert.contacts_notified = notified
        alert.status = 'sent' if notified > 0 else 'failed'
        alert.save()

        return JsonResponse({
            'success': True,
            'notified': notified,
            'failed': failed,
            'alert_id': alert.id,
            'timestamp': timestamp,
            'message': f'🚨 SOS sent to {notified} contact(s) successfully!' if notified > 0
                       else 'Alert failed. Check contact details.'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _send_emergency_email(to_email, contact_name, patient_name, address, maps_link, timestamp, custom_message):
    """Send emergency email via SendGrid."""
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail

        location_html = f'<a href="{maps_link}" style="color:#dc2626;">📍 View on Google Maps</a>' if maps_link else '📍 Location unavailable'

        html_content = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
            <div style="background:#dc2626;padding:30px;text-align:center;">
                <h1 style="color:white;margin:0;font-size:32px;">🚨 EMERGENCY SOS</h1>
                <p style="color:#fecaca;margin:5px 0 0;">ElderCare AI Emergency Alert System</p>
            </div>
            <div style="padding:30px;">
                <p style="font-size:18px;">Dear <strong>{contact_name}</strong>,</p>
                <p style="font-size:16px;background:#fef2f2;padding:15px;border-radius:8px;border-left:4px solid #dc2626;">
                    <strong>{patient_name}</strong> has triggered an emergency SOS alert and needs your immediate help.
                </p>
                {"<p><strong>Message:</strong> " + custom_message + "</p>" if custom_message else ""}
                <div style="background:#f9fafb;padding:15px;border-radius:8px;margin:20px 0;">
                    <p style="margin:5px 0;"><strong>📍 Location:</strong> {address}</p>
                    <p style="margin:10px 0;">{location_html}</p>
                    <p style="margin:5px 0;"><strong>🕐 Time:</strong> {timestamp}</p>
                </div>
                <div style="background:#fef2f2;padding:15px;border-radius:8px;margin-top:20px;">
                    <h3 style="color:#dc2626;margin-top:0;">Immediate Actions:</h3>
                    <ol style="color:#374151;">
                        <li>Call <strong>{patient_name}</strong> immediately</li>
                        <li>Go to their location or send help</li>
                        <li>If unresponsive, call <strong>999</strong></li>
                    </ol>
                </div>
                <p style="color:#9ca3af;font-size:12px;margin-top:30px;">
                    This is an automated alert from ElderCare AI. Do not reply to this email.
                </p>
            </div>
        </div>
        """

        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=f'🚨 EMERGENCY: {patient_name} needs help NOW!',
            html_content=html_content,
        )
        sg.send(message)
    except ImportError:
        # Fallback: Django email
        from django.core.mail import send_mail
        send_mail(
            subject=f'🚨 EMERGENCY: {patient_name} needs help NOW!',
            message=f'{patient_name} has triggered SOS. Location: {address}. Maps: {maps_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
        )


def _send_telegram_alert(chat_id, contact_name, patient_name, address, maps_link, timestamp, custom_message):
    """Send emergency Telegram message via Bot API."""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        raise ValueError("Telegram bot token not configured")

    location_text = f'[📍 View on Google Maps]({maps_link})' if maps_link else '📍 Location unavailable'

    message = f"""🚨 *EMERGENCY SOS ALERT* 🚨

Dear *{contact_name}*,

*{patient_name}* has triggered an emergency SOS and needs your immediate assistance!

{"📝 *Message:* " + custom_message if custom_message else ""}

📍 *Location:* {address}
{location_text}
🕐 *Time:* {timestamp}

*Immediate Actions:*
1️⃣ Call {patient_name} immediately
2️⃣ Go to their location
3️⃣ Call *999* if unresponsive

_This alert was sent by ElderCare AI_"""

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    response = requests.post(url, json={
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
    }, timeout=10)

    if not response.ok:
        raise Exception(f"Telegram API error: {response.text}")
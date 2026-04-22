# """
# Care Centre views — Nearby clinics, hospitals & pharmacies
# Uses Google Maps Places API
# """

# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings
# import requests
# import json


# def carecentre_page(request):
#     return render(request, 'carecentre/carecentre.html', {
#         'google_maps_key': settings.GOOGLE_MAPS_API_KEY
#     })


# @csrf_exempt
# def search_nearby(request):
#     """Search for nearby medical facilities using Google Places API."""
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Method not allowed'}, status=405)

#     try:
#         data = json.loads(request.body)
#         lat = data.get('lat')
#         lng = data.get('lng')
#         place_type = data.get('type', 'hospital')  # hospital, pharmacy, doctor
#         radius = data.get('radius', 5000)  # 5km default

#         if not lat or not lng:
#             return JsonResponse({'error': 'Location required'}, status=400)

#         # Map our types to Google Places types
#         type_mapping = {
#             'hospital': 'hospital',
#             'clinic': 'doctor',
#             'pharmacy': 'pharmacy',
#             'all': 'hospital',
#         }
#         google_type = type_mapping.get(place_type, 'hospital')

#         url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
#         params = {
#             'location': f'{lat},{lng}',
#             'radius': radius,
#             'type': google_type,
#             'key': settings.GOOGLE_MAPS_API_KEY,
#             'language': 'en',
#         }

#         response = requests.get(url, params=params, timeout=10)
#         places_data = response.json()

#         results = []
#         for place in places_data.get('results', [])[:15]:
#             location = place.get('geometry', {}).get('location', {})
#             results.append({
#                 'place_id': place.get('place_id'),
#                 'name': place.get('name'),
#                 'address': place.get('vicinity'),
#                 'rating': place.get('rating'),
#                 'total_ratings': place.get('user_ratings_total', 0),
#                 'open_now': place.get('opening_hours', {}).get('open_now'),
#                 'lat': location.get('lat'),
#                 'lng': location.get('lng'),
#                 'types': place.get('types', []),
#                 'photo_ref': place.get('photos', [{}])[0].get('photo_reference') if place.get('photos') else None,
#             })

#         return JsonResponse({'success': True, 'results': results, 'count': len(results)})

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


# def get_place_details(request, place_id):
#     """Get detailed info about a specific place."""
#     url = 'https://maps.googleapis.com/maps/api/place/details/json'
#     params = {
#         'place_id': place_id,
#         'fields': 'name,formatted_address,formatted_phone_number,opening_hours,rating,website,geometry',
#         'key': settings.GOOGLE_MAPS_API_KEY,
#     }
#     try:
#         response = requests.get(url, params=params, timeout=10)
#         data = response.json()
#         return JsonResponse({'success': True, 'details': data.get('result', {})})
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


"""
Care Centre views — Nearby clinics, hospitals & pharmacies
Uses Google Maps Places API
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json


def carecentre_page(request):
    return render(request, 'carecentre/carecentre.html', {
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY
    })


@csrf_exempt
def search_nearby(request):
    """Search for nearby medical facilities using Google Places API."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        lat = data.get('lat')
        lng = data.get('lng')
        place_type = data.get('type', 'hospital')  # hospital, pharmacy, doctor
        radius = data.get('radius', 5000)  # 5km default

        if not lat or not lng:
            return JsonResponse({'error': 'Location required'}, status=400)

        # Map our types to Google Places types
        type_mapping = {
            'hospital': 'hospital',
            'clinic': 'doctor',
            'pharmacy': 'pharmacy',
            'all': 'hospital',
        }
        google_type = type_mapping.get(place_type, 'hospital')

        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        params = {
            'location': f'{lat},{lng}',
            'radius': radius,
            'type': google_type,
            'key': settings.GOOGLE_MAPS_API_KEY,
            'language': 'en',
        }

        response = requests.get(url, params=params, timeout=10)
        places_data = response.json()

        results = []
        for place in places_data.get('results', [])[:15]:
            location = place.get('geometry', {}).get('location', {})
            results.append({
                'place_id': place.get('place_id'),
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'rating': place.get('rating'),
                'total_ratings': place.get('user_ratings_total', 0),
                'open_now': place.get('opening_hours', {}).get('open_now'),
                'lat': location.get('lat'),
                'lng': location.get('lng'),
                'types': place.get('types', []),
                'photo_ref': place.get('photos', [{}])[0].get('photo_reference') if place.get('photos') else None,
            })

        return JsonResponse({'success': True, 'results': results, 'count': len(results)})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_place_details(request, place_id):
    """Get detailed info about a specific place."""
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,formatted_phone_number,opening_hours,rating,website,geometry',
        'key': settings.GOOGLE_MAPS_API_KEY,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return JsonResponse({'success': True, 'details': data.get('result', {})})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
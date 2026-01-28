#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

def test_recommendation_creation():
    """Debug recommendation creation"""
    base_url = "https://transcript-rec-app.preview.emergentagent.com"
    
    # Login as admin first
    admin_login = requests.post(f"{base_url}/api/auth/login", json={
        "email": "admin@wolmers.org",
        "password": "Admin123!"
    })
    
    if admin_login.status_code != 200:
        print(f"❌ Admin login failed: {admin_login.status_code}")
        return
    
    admin_token = admin_login.json()['access_token']
    
    # Register a student
    student_email = f"debug_student_{datetime.now().strftime('%H%M%S')}@example.com"
    student_register = requests.post(f"{base_url}/api/auth/register", json={
        "full_name": "Debug Student",
        "email": student_email,
        "password": "TestPass123!",
        "role": "student"
    })
    
    if student_register.status_code != 200:
        print(f"❌ Student registration failed: {student_register.status_code}")
        return
    
    student_token = student_register.json()['access_token']
    print("✅ Student registered and logged in")
    
    # Create recommendation request
    needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    request_data = {
        "first_name": "Debug",
        "middle_name": "Test",
        "last_name": "Student",
        "email": "debug.test@email.com",
        "phone_number": "+1 876 555 1111",
        "address": "Debug Test Address, Kingston, Jamaica",
        "years_attended": [{"from_year": "2018", "to_year": "2023"}],
        "enrollment_status": "Graduate",
        "last_form_class": "Upper 6th",
        "co_curricular_activities": "Debug Club President",
        "reason": "University application",
        "institution_name": "Debug University",
        "institution_address": "Debug University Address",
        "directed_to": "Admissions Office",
        "program_name": "Computer Science",
        "needed_by_date": needed_date,
        "collection_method": "pickup"
    }
    
    headers = {'Authorization': f'Bearer {student_token}'}
    response = requests.post(f"{base_url}/api/recommendations", json=request_data, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Recommendation creation failed: {response.status_code}")
        try:
            print(f"Error details: {response.json()}")
        except:
            print(f"Response text: {response.text}")
        return
    
    data = response.json()
    print("✅ Recommendation created successfully")
    
    # Print the full response for debugging
    print("\n📊 FULL RECOMMENDATION RESPONSE:")
    print(json.dumps(data, indent=2))
    
    # Check enrollment status specifically
    print(f"\n🔍 ENROLLMENT STATUS ANALYSIS:")
    print(f"enrollment_status field: '{data.get('enrollment_status', 'MISSING')}'")
    print(f"Type: {type(data.get('enrollment_status', 'MISSING'))}")
    
    # Get the recommendation via API to see if it's stored correctly
    rec_id = data.get('id')
    if rec_id:
        get_response = requests.get(f"{base_url}/api/recommendations/{rec_id}", headers=headers)
        if get_response.status_code == 200:
            get_data = get_response.json()
            print(f"Retrieved enrollment_status: '{get_data.get('enrollment_status', 'MISSING')}'")
        else:
            print(f"❌ Could not retrieve recommendation: {get_response.status_code}")

if __name__ == "__main__":
    test_recommendation_creation()
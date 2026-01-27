#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

def test_edit_recommendation_issue():
    """Test the specific edit recommendation issue"""
    base_url = "https://transcript-rec-app.preview.emergentagent.com"
    
    # Login as student
    response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "student@test.com",
        "password": "password123"
    })
    
    if response.status_code != 200:
        print(f"❌ Student login failed: {response.status_code}")
        return
    
    student_token = response.json()['access_token']
    print("✅ Student login successful")
    
    # Login as admin
    response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "admin@wolmers.org",
        "password": "Admin123!"
    })
    
    if response.status_code != 200:
        print(f"❌ Admin login failed: {response.status_code}")
        return
    
    admin_token = response.json()['access_token']
    print("✅ Admin login successful")
    
    # Create a recommendation request
    needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    request_data = {
        "first_name": "Debug",
        "middle_name": "Edit",
        "last_name": "Test",
        "email": "debug.edit@email.com",
        "phone_number": "+1 876 555 1234",
        "address": "123 Debug Street, Kingston, Jamaica",
        "years_attended": [{"from_year": "2018", "to_year": "2023"}],
        "last_form_class": "Upper 6th",
        "co_curricular_activities": "Student Council",
        "institution_name": "Debug University",
        "institution_address": "Debug University Address",
        "directed_to": "Admissions Office",
        "program_name": "Computer Science",
        "needed_by_date": needed_date,
        "collection_method": "pickup"
    }
    
    response = requests.post(f"{base_url}/api/recommendations", 
                           json=request_data,
                           headers={'Authorization': f'Bearer {student_token}'})
    
    if response.status_code != 200:
        print(f"❌ Create recommendation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    request_id = response.json()['id']
    print(f"✅ Created recommendation: {request_id}")
    
    # Change status to "In Progress"
    response = requests.patch(f"{base_url}/api/recommendations/{request_id}",
                            json={"status": "In Progress"},
                            headers={'Authorization': f'Bearer {admin_token}'})
    
    if response.status_code != 200:
        print(f"❌ Status update failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    print("✅ Status updated to In Progress")
    
    # Try to edit - should fail with 400
    response = requests.put(f"{base_url}/api/recommendations/{request_id}/edit",
                          json={"phone_number": "+1 876 555 9999"},
                          headers={'Authorization': f'Bearer {student_token}'})
    
    print(f"Edit attempt status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        print("✅ Edit correctly blocked for non-pending recommendation")
    else:
        print(f"❌ Expected 400, got {response.status_code}")

if __name__ == "__main__":
    test_edit_recommendation_issue()
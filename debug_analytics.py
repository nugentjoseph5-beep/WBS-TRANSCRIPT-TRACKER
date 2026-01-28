#!/usr/bin/env python3

import requests
import json

def test_analytics_api():
    """Debug the analytics API response"""
    base_url = "https://transcript-rec-app.preview.emergentagent.com"
    
    # Login as admin
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "admin@wolmers.org",
        "password": "Admin123!"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed: {login_response.status_code}")
        return
    
    token = login_response.json()['access_token']
    print("✅ Admin login successful")
    
    # Get analytics
    headers = {'Authorization': f'Bearer {token}'}
    analytics_response = requests.get(f"{base_url}/api/analytics", headers=headers)
    
    if analytics_response.status_code != 200:
        print(f"❌ Analytics API failed: {analytics_response.status_code}")
        return
    
    data = analytics_response.json()
    print("✅ Analytics API successful")
    
    # Print the full response for debugging
    print("\n📊 FULL ANALYTICS RESPONSE:")
    print(json.dumps(data, indent=2))
    
    # Check specific fields
    print(f"\n🔍 FIELD ANALYSIS:")
    print(f"requests_by_month: {type(data.get('requests_by_month', 'MISSING'))}")
    if 'requests_by_month' in data and data['requests_by_month']:
        print(f"  Sample month data: {data['requests_by_month'][0]}")
    
    print(f"recommendations_by_enrollment: {type(data.get('recommendations_by_enrollment', 'MISSING'))}")
    if 'recommendations_by_enrollment' in data and data['recommendations_by_enrollment']:
        print(f"  Sample enrollment data: {data['recommendations_by_enrollment'][0]}")
    
    print(f"staff_workload: {type(data.get('staff_workload', 'MISSING'))}")
    if 'staff_workload' in data and data['staff_workload']:
        print(f"  Sample workload data: {data['staff_workload'][0]}")

if __name__ == "__main__":
    test_analytics_api()
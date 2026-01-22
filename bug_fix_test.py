#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

class BugFixTester:
    def __init__(self, base_url="https://transcript-rec.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.student_token = None
        self.staff_token = None
        
    def make_request(self, method, endpoint, data=None, token=None):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            else:
                return None, f"Unsupported method: {method}"
            
            return response, None
        except Exception as e:
            return None, str(e)

    def login_users(self):
        """Login with specific credentials from review request"""
        print("🔐 Logging in with review request credentials...")
        
        # Admin login
        response, error = self.make_request('POST', 'auth/login', {
            "email": "admin@wolmers.org",
            "password": "Admin123!"
        })
        
        if response and response.status_code == 200:
            self.admin_token = response.json()['access_token']
            print("✅ Admin login successful")
        else:
            print(f"❌ Admin login failed: {response.status_code if response else error}")
            return False
        
        # Staff login
        response, error = self.make_request('POST', 'auth/login', {
            "email": "staff@wolmers.org",
            "password": "password123"
        })
        
        if response and response.status_code == 200:
            self.staff_token = response.json()['access_token']
            print("✅ Staff login successful")
        else:
            print(f"❌ Staff login failed: {response.status_code if response else error}")
        
        # Student login
        response, error = self.make_request('POST', 'auth/login', {
            "email": "student@test.com",
            "password": "password123"
        })
        
        if response and response.status_code == 200:
            self.student_token = response.json()['access_token']
            print("✅ Student login successful")
        else:
            print(f"❌ Student login failed: {response.status_code if response else error}")
        
        return True

    def test_years_attended_display_bug_fix(self):
        """Test the Years Attended display bug fix"""
        print("\n🔍 Testing Years Attended Display Bug Fix...")
        
        if not self.student_token:
            print("❌ No student token available")
            return
        
        # Create a recommendation request with years_attended array
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Years",
            "middle_name": "Attended",
            "last_name": "Test",
            "email": "years.test@email.com",
            "phone_number": "+1 876 555 1111",
            "address": "Years Test Address, Kingston, Jamaica",
            "years_attended": [{"from_year": "2015", "to_year": "2020"}, {"from_year": "2021", "to_year": "2022"}],
            "last_form_class": "Upper 6th",
            "co_curricular_activities": "Head Boy, Football Captain",
            "institution_name": "Test University",
            "institution_address": "Test Address",
            "directed_to": "Admissions Office",
            "program_name": "Computer Science",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'recommendations', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            print(f"❌ Failed to create recommendation request: {response.status_code if response else error}")
            return
        
        request_id = response.json()['id']
        print(f"✅ Created recommendation request: {request_id}")
        
        # Test 1: Student viewing recommendation detail
        print("\n📋 Testing Student View...")
        response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            years_attended = data.get('years_attended')
            years_attended_str = data.get('years_attended_str')
            
            print(f"   years_attended (array): {years_attended}")
            print(f"   years_attended_str (string): {years_attended_str}")
            
            # Verify the fix: years_attended_str should be a proper string
            if years_attended_str == "2015-2020, 2021-2022":
                print("✅ Student view: Years Attended displays correctly as string")
            else:
                print(f"❌ Student view: Expected '2015-2020, 2021-2022', got '{years_attended_str}'")
            
            # Verify years_attended is still an array (for backend processing)
            if isinstance(years_attended, list) and len(years_attended) == 2:
                print("✅ Student view: years_attended array structure preserved")
            else:
                print(f"❌ Student view: years_attended should be array with 2 items, got {years_attended}")
        else:
            print(f"❌ Student view failed: {response.status_code if response else error}")
        
        # Test 2: Staff viewing recommendation detail
        if self.staff_token:
            print("\n👨‍💼 Testing Staff View...")
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.staff_token)
            
            if response and response.status_code == 200:
                data = response.json()
                years_attended_str = data.get('years_attended_str')
                
                print(f"   years_attended_str (string): {years_attended_str}")
                
                if years_attended_str == "2015-2020, 2021-2022":
                    print("✅ Staff view: Years Attended displays correctly as string")
                else:
                    print(f"❌ Staff view: Expected '2015-2020, 2021-2022', got '{years_attended_str}'")
            else:
                print(f"❌ Staff view failed: {response.status_code if response else error}")
        
        # Test 3: Admin viewing recommendation detail
        if self.admin_token:
            print("\n👑 Testing Admin View...")
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.admin_token)
            
            if response and response.status_code == 200:
                data = response.json()
                years_attended_str = data.get('years_attended_str')
                
                print(f"   years_attended_str (string): {years_attended_str}")
                
                if years_attended_str == "2015-2020, 2021-2022":
                    print("✅ Admin view: Years Attended displays correctly as string")
                else:
                    print(f"❌ Admin view: Expected '2015-2020, 2021-2022', got '{years_attended_str}'")
            else:
                print(f"❌ Admin view failed: {response.status_code if response else error}")

    def test_student_dashboard_clickable_tiles(self):
        """Test Student Dashboard data for clickable recommendation tiles"""
        print("\n🔍 Testing Student Dashboard Clickable Tiles Data...")
        
        if not self.student_token:
            print("❌ No student token available")
            return
        
        # Get student's recommendations for dashboard
        response, error = self.make_request('GET', 'recommendations', token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            
            print(f"📊 Found {len(data)} recommendation requests")
            
            if len(data) > 0:
                # Check that each recommendation has required fields for filtering
                sample_rec = data[0]
                required_fields = ['id', 'status', 'student_name', 'institution_name', 'program_name', 'created_at']
                
                print("🔍 Checking required fields for dashboard filtering:")
                for field in required_fields:
                    if field in sample_rec:
                        print(f"   ✅ {field}: {sample_rec[field]}")
                    else:
                        print(f"   ❌ Missing field: {field}")
                
                # Check status values for filtering
                statuses = set(rec.get('status', 'Unknown') for rec in data)
                print(f"📈 Available statuses for filtering: {list(statuses)}")
                
                # Verify data structure supports clickable tiles
                if all(field in sample_rec for field in required_fields):
                    print("✅ Student Dashboard: All required fields present for clickable tiles")
                else:
                    print("❌ Student Dashboard: Missing required fields for clickable tiles")
            else:
                print("ℹ️  No recommendation requests found (empty state)")
        else:
            print(f"❌ Failed to get student recommendations: {response.status_code if response else error}")

    def run_bug_fix_tests(self):
        """Run all bug fix tests"""
        print("🚀 Starting Bug Fix Verification Tests")
        print("=" * 60)
        
        if not self.login_users():
            print("❌ Failed to login users")
            return
        
        # Test 1: Years Attended Display Fix
        self.test_years_attended_display_bug_fix()
        
        # Test 2: Student Dashboard Clickable Tiles
        self.test_student_dashboard_clickable_tiles()
        
        print("\n" + "=" * 60)
        print("🎯 Bug Fix Testing Complete")

def main():
    tester = BugFixTester()
    tester.run_bug_fix_tests()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class ReviewRequestTester:
    def __init__(self, base_url="https://transcript-rec.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.student_token = None
        self.staff_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test credentials from review request
        self.admin_email = "admin@wolmers.org"
        self.admin_password = "Admin123!"
        self.staff_email = "staff@wolmers.org"
        self.staff_password = "password123"
        self.student_email = "student@test.com"
        self.student_password = "password123"

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name} - {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })

    def make_request(self, method, endpoint, data=None, token=None, files=None):
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        if files:
            # Remove content-type for file uploads
            headers.pop('Content-Type', None)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, headers=headers, files=files, data=data)
                else:
                    response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return None, f"Unsupported method: {method}"
            
            return response, None
        except Exception as e:
            return None, str(e)

    def authenticate_users(self):
        """Authenticate all test users"""
        print("\n🔐 Authenticating Test Users...")
        
        # Admin login
        response, error = self.make_request('POST', 'auth/login', {
            "email": self.admin_email,
            "password": self.admin_password
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'admin':
                self.admin_token = data['access_token']
                self.log_result("Admin authentication", True)
            else:
                self.log_result("Admin authentication", False, "Invalid response format")
                return False
        else:
            self.log_result("Admin authentication", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        # Staff login
        response, error = self.make_request('POST', 'auth/login', {
            "email": self.staff_email,
            "password": self.staff_password
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'staff':
                self.staff_token = data['access_token']
                self.log_result("Staff authentication", True)
            else:
                self.log_result("Staff authentication", False, "Invalid response format")
                return False
        else:
            self.log_result("Staff authentication", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        # Student login
        response, error = self.make_request('POST', 'auth/login', {
            "email": self.student_email,
            "password": self.student_password
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'student':
                self.student_token = data['access_token']
                self.log_result("Student authentication", True)
            else:
                self.log_result("Student authentication", False, "Invalid response format")
                return False
        else:
            self.log_result("Student authentication", False, f"Status: {response.status_code if response else 'No response'}")
            return False
        
        return True

    def test_recommendation_notifications_routing(self):
        """Test P0: Fix Recommendation Notifications - Test notification routing"""
        print("\n🔍 Testing P0: Recommendation Notifications Routing...")
        
        if not all([self.student_token, self.admin_token]):
            self.log_result("Recommendation Notifications Setup", False, "Missing required tokens")
            return None
        
        # Step 1: Create a recommendation request as student
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Notification",
            "middle_name": "Test",
            "last_name": "Student",
            "email": "notification.test@email.com",
            "phone_number": "+1 876 555 1111",
            "address": "123 Notification Street, Kingston, Jamaica",
            "years_attended": [{"from_year": "2018", "to_year": "2023"}],
            "last_form_class": "Upper 6th",
            "co_curricular_activities": "Student Council",
            "institution_name": "Test University",
            "institution_address": "Test University Address",
            "directed_to": "Admissions Office",
            "program_name": "Computer Science",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'recommendations', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            self.log_result("Create recommendation for notification test", False, f"Status: {response.status_code if response else 'No response'}")
            return None
        
        request_id = response.json()['id']
        self.log_result("Create recommendation for notification test", True)
        
        # Step 2: Admin updates the status (this should trigger a notification)
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "status": "In Progress"
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            self.log_result("Admin update recommendation status", True)
        else:
            self.log_result("Admin update recommendation status", False, f"Status: {response.status_code if response else 'No response'}")
            return None
        
        # Step 3: Check student notifications
        response, error = self.make_request('GET', 'notifications', token=self.student_token)
        
        if response and response.status_code == 200:
            notifications = response.json()
            
            # Look for recommendation notification
            recommendation_notification = None
            for notif in notifications:
                if notif.get('type') == 'recommendation_status_update' and notif.get('request_id') == request_id:
                    recommendation_notification = notif
                    break
            
            if recommendation_notification:
                self.log_result("Recommendation notification created", True)
                
                # Verify notification has correct request_id for routing
                if recommendation_notification.get('request_id') == request_id:
                    self.log_result("Recommendation notification has correct request_id", True)
                else:
                    self.log_result("Recommendation notification has correct request_id", False, f"Expected {request_id}, got {recommendation_notification.get('request_id')}")
                
                return request_id
            else:
                self.log_result("Recommendation notification created", False, "No recommendation notification found")
        else:
            self.log_result("Get student notifications", False, f"Status: {response.status_code if response else 'No response'}")
        
        return request_id

    def test_transcript_notifications_still_work(self):
        """Test that transcript notifications still work correctly"""
        print("\n🔍 Testing Transcript Notifications Still Work...")
        
        if not all([self.student_token, self.admin_token]):
            self.log_result("Transcript Notifications Setup", False, "Missing required tokens")
            return None
        
        # Step 1: Create a transcript request as student
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Transcript",
            "middle_name": "Notification",
            "last_name": "Test",
            "school_id": "WBS2024999",
            "enrollment_status": "graduate",
            "academic_years": [{"from_year": "2018", "to_year": "2023"}],
            "wolmers_email": "transcript.test@wolmers.org",
            "personal_email": "transcript.test@email.com",
            "phone_number": "+1 876 555 2222",
            "reason": "University application",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'requests', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            self.log_result("Create transcript for notification test", False, f"Status: {response.status_code if response else 'No response'}")
            return None
        
        request_id = response.json()['id']
        self.log_result("Create transcript for notification test", True)
        
        # Step 2: Admin updates the status (this should trigger a notification)
        response, error = self.make_request('PATCH', f'requests/{request_id}', {
            "status": "In Progress"
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            self.log_result("Admin update transcript status", True)
        else:
            self.log_result("Admin update transcript status", False, f"Status: {response.status_code if response else 'No response'}")
            return None
        
        # Step 3: Check student notifications
        response, error = self.make_request('GET', 'notifications', token=self.student_token)
        
        if response and response.status_code == 200:
            notifications = response.json()
            
            # Look for transcript notification
            transcript_notification = None
            for notif in notifications:
                if notif.get('type') == 'status_update' and notif.get('request_id') == request_id:
                    transcript_notification = notif
                    break
            
            if transcript_notification:
                self.log_result("Transcript notification created", True)
                
                # Verify notification has correct request_id for routing
                if transcript_notification.get('request_id') == request_id:
                    self.log_result("Transcript notification has correct request_id", True)
                else:
                    self.log_result("Transcript notification has correct request_id", False, f"Expected {request_id}, got {transcript_notification.get('request_id')}")
                
                return request_id
            else:
                self.log_result("Transcript notification created", False, "No transcript notification found")
        else:
            self.log_result("Get student notifications", False, f"Status: {response.status_code if response else 'No response'}")
        
        return request_id

    def test_status_change_notes_for_transcripts(self):
        """Test P1: Status Change Notes for Transcripts - Admin and Staff"""
        print("\n🔍 Testing P1: Status Change Notes for Transcripts...")
        
        if not all([self.student_token, self.admin_token, self.staff_token]):
            self.log_result("Status Change Notes Setup", False, "Missing required tokens")
            return
        
        # Create a transcript request first
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Status",
            "middle_name": "Notes",
            "last_name": "Test",
            "school_id": "WBS2024888",
            "enrollment_status": "graduate",
            "academic_years": [{"from_year": "2018", "to_year": "2023"}],
            "wolmers_email": "status.notes@wolmers.org",
            "personal_email": "status.notes@email.com",
            "phone_number": "+1 876 555 3333",
            "reason": "Testing status notes",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'requests', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            self.log_result("Create transcript for status notes test", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        request_id = response.json()['id']
        self.log_result("Create transcript for status notes test", True)
        
        # Test Admin Status Update with Notes
        # Note: The backend currently doesn't have a separate notes field in the PATCH request
        # But we can test that timeline entries are created with notes
        response, error = self.make_request('PATCH', f'requests/{request_id}', {
            "status": "In Progress"
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            
            # Check that timeline has been updated
            timeline = data.get('timeline', [])
            if timeline:
                # Find the "In Progress" entry
                in_progress_entry = None
                for entry in timeline:
                    if entry.get('status') == 'In Progress':
                        in_progress_entry = entry
                        break
                
                if in_progress_entry:
                    # Check that the entry has a note
                    if 'note' in in_progress_entry and in_progress_entry['note']:
                        self.log_result("Admin status update creates timeline entry with note", True)
                    else:
                        self.log_result("Admin status update creates timeline entry with note", False, "Timeline entry missing note")
                else:
                    self.log_result("Admin status update creates timeline entry with note", False, "No 'In Progress' timeline entry found")
            else:
                self.log_result("Admin status update creates timeline entry with note", False, "No timeline entries found")
        else:
            self.log_result("Admin status update with notes", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Assign staff to the request first
        staff_response, _ = self.make_request('GET', 'admin/staff', token=self.admin_token)
        if staff_response and staff_response.status_code == 200:
            staff_members = staff_response.json()
            if staff_members:
                staff_id = staff_members[0]['id']
                
                response, error = self.make_request('PATCH', f'requests/{request_id}', {
                    "assigned_staff_id": staff_id
                }, token=self.admin_token)
                
                if response and response.status_code == 200:
                    self.log_result("Assign staff to transcript request", True)
                    
                    # Test Staff Status Update with Notes
                    response, error = self.make_request('PATCH', f'requests/{request_id}', {
                        "status": "Ready"
                    }, token=self.staff_token)
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        
                        # Check that timeline has been updated
                        timeline = data.get('timeline', [])
                        ready_entry = None
                        for entry in timeline:
                            if entry.get('status') == 'Ready':
                                ready_entry = entry
                                break
                        
                        if ready_entry:
                            # Check that the entry has a note
                            if 'note' in ready_entry and ready_entry['note']:
                                self.log_result("Staff status update creates timeline entry with note", True)
                            else:
                                self.log_result("Staff status update creates timeline entry with note", False, "Timeline entry missing note")
                        else:
                            self.log_result("Staff status update creates timeline entry with note", False, "No 'Ready' timeline entry found")
                    else:
                        self.log_result("Staff status update with notes", False, f"Status: {response.status_code if response else 'No response'}")
                else:
                    self.log_result("Assign staff to transcript request", False, f"Status: {response.status_code if response else 'No response'}")

    def test_display_status_notes_in_timeline(self):
        """Test P1: Display Status Notes in Timeline - All Detail Pages"""
        print("\n🔍 Testing P1: Display Status Notes in Timeline...")
        
        if not all([self.student_token, self.admin_token, self.staff_token]):
            self.log_result("Timeline Notes Display Setup", False, "Missing required tokens")
            return
        
        # Create both transcript and recommendation requests with timeline entries
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Create transcript request
        transcript_data = {
            "first_name": "Timeline",
            "middle_name": "Display",
            "last_name": "Test",
            "school_id": "WBS2024777",
            "enrollment_status": "graduate",
            "academic_years": [{"from_year": "2018", "to_year": "2023"}],
            "wolmers_email": "timeline.display@wolmers.org",
            "personal_email": "timeline.display@email.com",
            "phone_number": "+1 876 555 4444",
            "reason": "Testing timeline display",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'requests', transcript_data, token=self.student_token)
        
        if response and response.status_code == 200:
            transcript_id = response.json()['id']
            self.log_result("Create transcript for timeline test", True)
            
            # Update status to create timeline entries
            response, error = self.make_request('PATCH', f'requests/{transcript_id}', {
                "status": "In Progress"
            }, token=self.admin_token)
            
            if response and response.status_code == 200:
                # Test Admin Transcript Detail View
                response, error = self.make_request('GET', f'requests/{transcript_id}', token=self.admin_token)
                
                if response and response.status_code == 200:
                    data = response.json()
                    timeline = data.get('timeline', [])
                    
                    # Check that timeline entries have notes
                    has_notes = False
                    for entry in timeline:
                        if 'note' in entry and entry['note'] and entry['note'].strip():
                            has_notes = True
                            break
                    
                    if has_notes:
                        self.log_result("Admin Transcript Detail - Timeline shows notes", True)
                    else:
                        self.log_result("Admin Transcript Detail - Timeline shows notes", False, "No timeline entries with notes found")
                else:
                    self.log_result("Admin Transcript Detail - Timeline shows notes", False, f"Status: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Create transcript for timeline test", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Create recommendation request
        recommendation_data = {
            "first_name": "Timeline",
            "middle_name": "Recommendation",
            "last_name": "Test",
            "email": "timeline.rec@email.com",
            "phone_number": "+1 876 555 5555",
            "address": "123 Timeline Street, Kingston, Jamaica",
            "years_attended": [{"from_year": "2018", "to_year": "2023"}],
            "last_form_class": "Upper 6th",
            "co_curricular_activities": "Student Council",
            "institution_name": "Timeline University",
            "institution_address": "Timeline University Address",
            "directed_to": "Admissions Office",
            "program_name": "Computer Science",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'recommendations', recommendation_data, token=self.student_token)
        
        if response and response.status_code == 200:
            recommendation_id = response.json()['id']
            self.log_result("Create recommendation for timeline test", True)
            
            # Update status to create timeline entries
            response, error = self.make_request('PATCH', f'recommendations/{recommendation_id}', {
                "status": "In Progress"
            }, token=self.admin_token)
            
            if response and response.status_code == 200:
                # Test Admin Recommendation Detail View
                response, error = self.make_request('GET', f'recommendations/{recommendation_id}', token=self.admin_token)
                
                if response and response.status_code == 200:
                    data = response.json()
                    timeline = data.get('timeline', [])
                    
                    # Check that timeline entries have notes
                    has_notes = False
                    for entry in timeline:
                        if 'note' in entry and entry['note'] and entry['note'].strip():
                            has_notes = True
                            break
                    
                    if has_notes:
                        self.log_result("Admin Recommendation Detail - Timeline shows notes", True)
                    else:
                        self.log_result("Admin Recommendation Detail - Timeline shows notes", False, "No timeline entries with notes found")
                        
                    # Test Staff Recommendation Detail View (if staff has access)
                    response, error = self.make_request('GET', f'recommendations/{recommendation_id}', token=self.staff_token)
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        timeline = data.get('timeline', [])
                        
                        # Check that timeline entries have notes
                        has_notes = False
                        for entry in timeline:
                            if 'note' in entry and entry['note'] and entry['note'].strip():
                                has_notes = True
                                break
                        
                        if has_notes:
                            self.log_result("Staff Recommendation Detail - Timeline shows notes", True)
                        else:
                            self.log_result("Staff Recommendation Detail - Timeline shows notes", False, "No timeline entries with notes found")
                    else:
                        self.log_result("Staff Recommendation Detail - Timeline shows notes", False, f"Status: {response.status_code if response else 'No response'}")
                else:
                    self.log_result("Admin Recommendation Detail - Timeline shows notes", False, f"Status: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Create recommendation for timeline test", False, f"Status: {response.status_code if response else 'No response'}")

    def test_edit_recommendation_page(self):
        """Test Bonus: EditRecommendation Page - Student can edit pending recommendations"""
        print("\n🔍 Testing Bonus: EditRecommendation Page...")
        
        if not all([self.student_token, self.admin_token]):
            self.log_result("EditRecommendation Setup", False, "Missing required tokens")
            return
        
        # Create a recommendation request
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Edit",
            "middle_name": "Test",
            "last_name": "Student",
            "email": "edit.test@email.com",
            "phone_number": "+1 876 555 6666",
            "address": "123 Edit Street, Kingston, Jamaica",
            "years_attended": [{"from_year": "2018", "to_year": "2023"}],
            "last_form_class": "Upper 6th",
            "co_curricular_activities": "Student Council",
            "institution_name": "Edit University",
            "institution_address": "Edit University Address",
            "directed_to": "Admissions Office",
            "program_name": "Computer Science",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'recommendations', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            self.log_result("Create recommendation for edit test", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        request_id = response.json()['id']
        self.log_result("Create recommendation for edit test", True)
        
        # Test editing pending recommendation
        update_data = {
            "phone_number": "+1 876 555 7777",
            "program_name": "Software Engineering",
            "directed_to": "Graduate Admissions Office"
        }
        
        response, error = self.make_request('PUT', f'recommendations/{request_id}/edit', update_data, token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            
            # Verify changes were saved
            if (data.get('phone_number') == update_data['phone_number'] and 
                data.get('program_name') == update_data['program_name'] and
                data.get('directed_to') == update_data['directed_to']):
                self.log_result("Student can edit pending recommendation", True)
            else:
                self.log_result("Student can edit pending recommendation", False, "Changes not saved properly")
        else:
            self.log_result("Student can edit pending recommendation", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test that non-pending recommendations cannot be edited
        # First change status to "In Progress"
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "status": "In Progress"
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            # Now try to edit - should fail
            response, error = self.make_request('PUT', f'recommendations/{request_id}/edit', {
                "phone_number": "+1 876 555 8888"
            }, token=self.student_token)
            
            if response and response.status_code == 400:
                self.log_result("Non-pending recommendation cannot be edited", True)
            else:
                self.log_result("Non-pending recommendation cannot be edited", False, f"Expected 400, got {response.status_code if response else 'No response'}")
        else:
            self.log_result("Change recommendation status to In Progress", False, f"Status: {response.status_code if response else 'No response'}")

    def test_last_form_class_field(self):
        """Test Bonus: Last Form Class Field - Text input for both transcript and recommendation forms"""
        print("\n🔍 Testing Bonus: Last Form Class Field...")
        
        if not self.student_token:
            self.log_result("Last Form Class Field Setup", False, "Missing student token")
            return
        
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Test transcript form with Last Form Class as text input
        transcript_data = {
            "first_name": "Form",
            "middle_name": "Class",
            "last_name": "Test",
            "school_id": "WBS2024666",
            "enrollment_status": "graduate",
            "academic_years": [{"from_year": "2018", "to_year": "2023"}],
            "wolmers_email": "form.class@wolmers.org",
            "personal_email": "form.class@email.com",
            "phone_number": "+1 876 555 9999",
            "reason": "Testing form class field",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'requests', transcript_data, token=self.student_token)
        
        if response and response.status_code == 200:
            self.log_result("Transcript request creation (form class field test)", True)
        else:
            self.log_result("Transcript request creation (form class field test)", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test recommendation form with Last Form Class as text input
        recommendation_data = {
            "first_name": "Form",
            "middle_name": "Class",
            "last_name": "Recommendation",
            "email": "form.class.rec@email.com",
            "phone_number": "+1 876 555 0000",
            "address": "123 Form Class Street, Kingston, Jamaica",
            "years_attended": [{"from_year": "2018", "to_year": "2023"}],
            "last_form_class": "Upper 6th",  # Text input field
            "co_curricular_activities": "Student Council",
            "institution_name": "Form Class University",
            "institution_address": "Form Class University Address",
            "directed_to": "Admissions Office",
            "program_name": "Computer Science",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'recommendations', recommendation_data, token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            
            # Verify that last_form_class was saved as text
            if data.get('last_form_class') == "Upper 6th":
                self.log_result("Recommendation last_form_class field accepts text input", True)
            else:
                self.log_result("Recommendation last_form_class field accepts text input", False, f"Expected 'Upper 6th', got '{data.get('last_form_class')}'")
        else:
            self.log_result("Recommendation request creation (form class field test)", False, f"Status: {response.status_code if response else 'No response'}")

    def run_review_request_tests(self):
        """Run all review request tests"""
        print("🚀 Starting Review Request Feature Tests")
        print(f"🎯 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Authenticate all users
        if not self.authenticate_users():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return 1
        
        # P0 - Critical: Fix Recommendation Notifications
        print("\n" + "🔥" * 20)
        print("🔥 P0 - CRITICAL: RECOMMENDATION NOTIFICATIONS")
        print("🔥" * 20)
        self.test_recommendation_notifications_routing()
        self.test_transcript_notifications_still_work()
        
        # P1: Status Change Notes for Transcripts
        print("\n" + "⭐" * 20)
        print("⭐ P1: STATUS CHANGE NOTES FOR TRANSCRIPTS")
        print("⭐" * 20)
        self.test_status_change_notes_for_transcripts()
        
        # P1: Display Status Notes in Timeline
        print("\n" + "⭐" * 20)
        print("⭐ P1: DISPLAY STATUS NOTES IN TIMELINE")
        print("⭐" * 20)
        self.test_display_status_notes_in_timeline()
        
        # Bonus: EditRecommendation Page
        print("\n" + "🎁" * 20)
        print("🎁 BONUS: EDIT RECOMMENDATION PAGE")
        print("🎁" * 20)
        self.test_edit_recommendation_page()
        
        # Bonus: Last Form Class Field
        print("\n" + "🎁" * 20)
        print("🎁 BONUS: LAST FORM CLASS FIELD")
        print("🎁" * 20)
        self.test_last_form_class_field()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Review Request Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All review request tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            
            # Print failed tests
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
            
            return 1

def main():
    tester = ReviewRequestTester()
    return tester.run_review_request_tests()

if __name__ == "__main__":
    sys.exit(main())
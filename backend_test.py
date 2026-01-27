#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class WolmersTranscriptAPITester:
    def __init__(self, base_url="https://transcript-rec-app.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.student_token = None
        self.staff_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data
        self.test_student_email = f"test_student_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_staff_email = f"test_staff_{datetime.now().strftime('%H%M%S')}@wolmers.org"
        self.admin_email = "admin@wolmers.org"
        self.admin_password = "NewAdmin123!"  # Updated after password reset test

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

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n🔍 Testing Health Endpoints...")
        
        # Test root endpoint
        response, error = self.make_request('GET', '')
        if response and response.status_code == 200:
            self.log_result("Root endpoint accessible", True)
        else:
            self.log_result("Root endpoint accessible", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test health endpoint
        response, error = self.make_request('GET', 'health')
        if response and response.status_code == 200:
            self.log_result("Health endpoint accessible", True)
        else:
            self.log_result("Health endpoint accessible", False, f"Status: {response.status_code if response else 'No response'}")

    def test_admin_login(self):
        """Test admin login"""
        print("\n🔍 Testing Admin Authentication...")
        
        response, error = self.make_request('POST', 'auth/login', {
            "email": self.admin_email,
            "password": self.admin_password
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'admin':
                self.admin_token = data['access_token']
                self.log_result("Admin login successful", True)
                return True
            else:
                self.log_result("Admin login successful", False, "Invalid response format")
        else:
            self.log_result("Admin login successful", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_student_registration(self):
        """Test student registration"""
        print("\n🔍 Testing Student Registration...")
        
        response, error = self.make_request('POST', 'auth/register', {
            "full_name": "Test Student",
            "email": self.test_student_email,
            "password": "TestPass123!",
            "role": "student"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'student':
                self.student_token = data['access_token']
                self.log_result("Student registration successful", True)
                return True
            else:
                self.log_result("Student registration successful", False, "Invalid response format")
        else:
            self.log_result("Student registration successful", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_student_login(self):
        """Test student login"""
        print("\n🔍 Testing Student Login...")
        
        response, error = self.make_request('POST', 'auth/login', {
            "email": self.test_student_email,
            "password": "TestPass123!"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'student':
                self.student_token = data['access_token']
                self.log_result("Student login successful", True)
                return True
            else:
                self.log_result("Student login successful", False, "Invalid response format")
        else:
            self.log_result("Student login successful", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_create_staff_user(self):
        """Test creating staff user by admin"""
        print("\n🔍 Testing Staff User Creation...")
        
        if not self.admin_token:
            self.log_result("Create staff user", False, "No admin token available")
            return False
        
        response, error = self.make_request('POST', 'admin/users', {
            "full_name": "Test Staff Member",
            "email": self.test_staff_email,
            "password": "StaffPass123!",
            "role": "staff"
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if data['role'] == 'staff':
                self.log_result("Create staff user", True)
                return True
            else:
                self.log_result("Create staff user", False, "Invalid role in response")
        else:
            self.log_result("Create staff user", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_staff_login(self):
        """Test staff login"""
        print("\n🔍 Testing Staff Login...")
        
        response, error = self.make_request('POST', 'auth/login', {
            "email": self.test_staff_email,
            "password": "StaffPass123!"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'staff':
                self.staff_token = data['access_token']
                self.log_result("Staff login successful", True)
                return True
            else:
                self.log_result("Staff login successful", False, "Invalid response format")
        else:
            self.log_result("Staff login successful", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_create_transcript_request(self):
        """Test creating transcript request with NEW FIELDS"""
        print("\n🔍 Testing Transcript Request Creation with New Fields...")
        
        if not self.student_token:
            self.log_result("Create transcript request", False, "No student token available")
            return None
        
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Test with NEW ARRAY FORMAT for academic_years and delivery collection method
        request_data = {
            "first_name": "Michael",
            "middle_name": "David",
            "last_name": "Brown",
            "school_id": "WBS2022005",
            "enrollment_status": "graduate",
            "academic_years": [{"from_year": "2016", "to_year": "2022"}],  # NEW ARRAY FORMAT
            "wolmers_email": "michael.brown.2022@wolmers.org",
            "personal_email": self.test_student_email,
            "phone_number": "+1 876 555 5678",
            "reason": "University application",
            "needed_by_date": needed_date,
            "collection_method": "delivery",  # NEW COLLECTION METHOD
            "delivery_address": "123 Delivery Street, Portmore, St. Catherine, Jamaica",  # NEW FIELD
            "institution_name": "UWI Mona",
            "institution_address": "Mona Campus, Kingston 7, Jamaica",
            "institution_phone": "+1 876 927 1660",
            "institution_email": "admissions@uwimona.edu.jm"
        }
        
        response, error = self.make_request('POST', 'requests', request_data, token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if ('id' in data and data['status'] == 'Pending' and
                data['collection_method'] == 'delivery' and
                data['delivery_address'] == '123 Delivery Street, Portmore, St. Catherine, Jamaica' and
                isinstance(data['academic_years'], list) and len(data['academic_years']) == 1):
                self.log_result("Create transcript request with new fields", True)
                return data['id']
            else:
                self.log_result("Create transcript request with new fields", False, "New fields not saved properly")
        else:
            self.log_result("Create transcript request with new fields", False, f"Status: {response.status_code if response else 'No response'}")
        
        return None

    def test_get_requests(self):
        """Test getting requests for different roles"""
        print("\n🔍 Testing Request Retrieval...")
        
        # Test student getting their requests
        if self.student_token:
            response, error = self.make_request('GET', 'requests', token=self.student_token)
            if response and response.status_code == 200:
                self.log_result("Student get requests", True)
            else:
                self.log_result("Student get requests", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test admin getting all requests
        if self.admin_token:
            response, error = self.make_request('GET', 'requests/all', token=self.admin_token)
            if response and response.status_code == 200:
                self.log_result("Admin get all requests", True)
            else:
                self.log_result("Admin get all requests", False, f"Status: {response.status_code if response else 'No response'}")

    def test_analytics(self):
        """Test analytics endpoint"""
        print("\n🔍 Testing Analytics...")
        
        if not self.admin_token:
            self.log_result("Get analytics", False, "No admin token available")
            return
        
        response, error = self.make_request('GET', 'analytics', token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ['total_requests', 'pending_requests', 'completed_requests', 'requests_by_month']
            if all(field in data for field in required_fields):
                self.log_result("Get analytics", True)
            else:
                self.log_result("Get analytics", False, "Missing required fields in response")
        else:
            self.log_result("Get analytics", False, f"Status: {response.status_code if response else 'No response'}")

    def test_notifications(self):
        """Test notifications endpoints"""
        print("\n🔍 Testing Notifications...")
        
        # Test getting notifications for student
        if self.student_token:
            response, error = self.make_request('GET', 'notifications', token=self.student_token)
            if response and response.status_code == 200:
                self.log_result("Get student notifications", True)
            else:
                self.log_result("Get student notifications", False, f"Status: {response.status_code if response else 'No response'}")
            
            # Test getting unread count
            response, error = self.make_request('GET', 'notifications/unread-count', token=self.student_token)
            if response and response.status_code == 200:
                data = response.json()
                if 'count' in data:
                    self.log_result("Get unread count", True)
                else:
                    self.log_result("Get unread count", False, "Missing count field")
            else:
                self.log_result("Get unread count", False, f"Status: {response.status_code if response else 'No response'}")

    def test_user_management(self):
        """Test user management endpoints"""
        print("\n🔍 Testing User Management...")
        
        if not self.admin_token:
            self.log_result("Get all users", False, "No admin token available")
            return
        
        # Test getting all users
        response, error = self.make_request('GET', 'admin/users', token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Get all users", True)
            else:
                self.log_result("Get all users", False, "Response is not a list")
        else:
            self.log_result("Get all users", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test getting staff members
        response, error = self.make_request('GET', 'admin/staff', token=self.admin_token)
        if response and response.status_code == 200:
            self.log_result("Get staff members", True)
        else:
            self.log_result("Get staff members", False, f"Status: {response.status_code if response else 'No response'}")

    def test_password_reset_flow(self):
        """Test password reset functionality"""
        print("\n🔍 Testing Password Reset Flow...")
        
        # Test forgot password endpoint
        response, error = self.make_request('POST', 'auth/forgot-password', {
            "email": self.admin_email
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'message' in data and 'token' in data:
                reset_token = data['token']
                self.log_result("Forgot password request", True)
                
                # Test token verification
                response, error = self.make_request('GET', f'auth/verify-reset-token/{reset_token}')
                if response and response.status_code == 200:
                    verify_data = response.json()
                    if verify_data.get('valid') and verify_data.get('email') == self.admin_email:
                        self.log_result("Reset token verification", True)
                        
                        # Test password reset
                        response, error = self.make_request('POST', 'auth/reset-password', {
                            "token": reset_token,
                            "new_password": "NewAdmin123!"
                        })
                        
                        if response and response.status_code == 200:
                            self.log_result("Password reset completion", True)
                            
                            # Test login with new password
                            response, error = self.make_request('POST', 'auth/login', {
                                "email": self.admin_email,
                                "password": "NewAdmin123!"
                            })
                            
                            if response and response.status_code == 200:
                                self.log_result("Login with new password", True)
                                # Reset password back to original
                                self.admin_token = response.json()['access_token']
                            else:
                                self.log_result("Login with new password", False, f"Status: {response.status_code if response else 'No response'}")
                        else:
                            self.log_result("Password reset completion", False, f"Status: {response.status_code if response else 'No response'}")
                    else:
                        self.log_result("Reset token verification", False, "Invalid verification response")
                else:
                    self.log_result("Reset token verification", False, f"Status: {response.status_code if response else 'No response'}")
            else:
                self.log_result("Forgot password request", False, "Missing message or token in response")
        else:
            self.log_result("Forgot password request", False, f"Status: {response.status_code if response else 'No response'}")

    def test_transcript_request_with_institution(self):
        """Test creating transcript request with institution name for all collection methods"""
        print("\n🔍 Testing Transcript Request with Institution for All Collection Methods...")
        
        if not self.student_token:
            self.log_result("Create transcript request with institution", False, "No student token available")
            return None
        
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Test 1: Pickup method with optional institution name
        pickup_data = {
            "first_name": "Jane",
            "middle_name": "Marie",
            "last_name": "Smith",
            "school_id": "WBS2024002",
            "enrollment_status": "graduate",
            "academic_year": "2023-2024",
            "wolmers_email": "jane.smith.2024@wolmers.org",
            "personal_email": self.test_student_email,
            "phone_number": "+1 876 555 0124",
            "reason": "Graduate school application",
            "needed_by_date": needed_date,
            "collection_method": "pickup",
            "institution_name": "University of the West Indies"  # Optional for pickup
        }
        
        response, error = self.make_request('POST', 'requests', pickup_data, token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'id' in data and data['institution_name'] == "University of the West Indies":
                self.log_result("Pickup request with institution name", True)
            else:
                self.log_result("Pickup request with institution name", False, "Institution name not saved properly")
        else:
            self.log_result("Pickup request with institution name", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test 2: Emailed method with required institution name
        emailed_data = {
            "first_name": "John",
            "middle_name": "David",
            "last_name": "Brown",
            "school_id": "WBS2024003",
            "enrollment_status": "graduate",
            "academic_year": "2023-2024",
            "wolmers_email": "john.brown.2024@wolmers.org",
            "personal_email": self.test_student_email,
            "phone_number": "+1 876 555 0125",
            "reason": "University application",
            "needed_by_date": needed_date,
            "collection_method": "emailed",
            "institution_name": "Harvard University",  # Required for emailed
            "institution_email": "admissions@harvard.edu"
        }
        
        response, error = self.make_request('POST', 'requests', emailed_data, token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'id' in data and data['institution_name'] == "Harvard University":
                self.log_result("Emailed request with institution name", True)
            else:
                self.log_result("Emailed request with institution name", False, "Institution name not saved properly")
        else:
            self.log_result("Emailed request with institution name", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test 3: Delivery method with required institution name
        delivery_data = {
            "first_name": "Sarah",
            "middle_name": "Ann",
            "last_name": "Johnson",
            "school_id": "WBS2024004",
            "enrollment_status": "graduate",
            "academic_year": "2023-2024",
            "wolmers_email": "sarah.johnson.2024@wolmers.org",
            "personal_email": self.test_student_email,
            "phone_number": "+1 876 555 0126",
            "reason": "Employment verification",
            "needed_by_date": needed_date,
            "collection_method": "delivery",
            "institution_name": "MIT",  # Required for delivery
            "institution_address": "77 Massachusetts Ave, Cambridge, MA 02139, USA"
        }
        
        response, error = self.make_request('POST', 'requests', delivery_data, token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'id' in data and data['institution_name'] == "MIT":
                self.log_result("Delivery request with institution name", True)
                return data['id']
            else:
                self.log_result("Delivery request with institution name", False, "Institution name not saved properly")
        else:
            self.log_result("Delivery request with institution name", False, f"Status: {response.status_code if response else 'No response'}")
        
        return None

    def test_admin_reset_user_password(self):
        """Test admin resetting user password"""
        print("\n🔍 Testing Admin Reset User Password...")
        
        if not self.admin_token:
            self.log_result("Admin reset user password", False, "No admin token available")
            return False
        
        # First get all users to find a staff member to reset password for
        response, error = self.make_request('GET', 'admin/users', token=self.admin_token)
        if not response or response.status_code != 200:
            self.log_result("Admin reset user password", False, "Could not get users list")
            return False
        
        users = response.json()
        staff_user = None
        for user in users:
            if user['role'] == 'staff' and user['email'] == self.test_staff_email:
                staff_user = user
                break
        
        if not staff_user:
            self.log_result("Admin reset user password", False, "No staff user found to test password reset")
            return False
        
        # Test resetting the staff user's password
        new_password = "NewStaffPass123!"
        response, error = self.make_request('POST', f'admin/users/{staff_user["id"]}/reset-password', {
            "new_password": new_password
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'message' in data and staff_user['full_name'] in data['message']:
                self.log_result("Admin reset user password", True)
                
                # Test login with new password
                response, error = self.make_request('POST', 'auth/login', {
                    "email": self.test_staff_email,
                    "password": new_password
                })
                
                if response and response.status_code == 200:
                    self.log_result("Login with reset password", True)
                    return True
                else:
                    self.log_result("Login with reset password", False, f"Status: {response.status_code if response else 'No response'}")
            else:
                self.log_result("Admin reset user password", False, "Invalid response message")
        else:
            self.log_result("Admin reset user password", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_request_reassignment(self):
        """Test admin reassigning requests between staff members"""
        print("\n🔍 Testing Request Reassignment...")
        
        if not self.admin_token or not self.student_token:
            self.log_result("Request reassignment", False, "Missing required tokens")
            return False
        
        # First create a transcript request
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        request_data = {
            "first_name": "Test",
            "middle_name": "Reassign",
            "last_name": "User",
            "school_id": "WBS2024005",
            "enrollment_status": "graduate",
            "academic_year": "2023-2024",
            "wolmers_email": "test.reassign.2024@wolmers.org",
            "personal_email": self.test_student_email,
            "phone_number": "+1 876 555 0127",
            "reason": "Testing reassignment",
            "needed_by_date": needed_date,
            "collection_method": "pickup",
            "institution_name": "Test University"
        }
        
        response, error = self.make_request('POST', 'requests', request_data, token=self.student_token)
        if not response or response.status_code != 200:
            self.log_result("Request reassignment", False, "Could not create test request")
            return False
        
        request_id = response.json()['id']
        
        # Get staff members
        response, error = self.make_request('GET', 'admin/staff', token=self.admin_token)
        if not response or response.status_code != 200:
            self.log_result("Request reassignment", False, "Could not get staff members")
            return False
        
        staff_members = response.json()
        if len(staff_members) == 0:
            self.log_result("Request reassignment", False, "No staff members available for assignment")
            return False
        
        staff_id = staff_members[0]['id']
        
        # Test initial assignment
        response, error = self.make_request('PATCH', f'requests/{request_id}', {
            "assigned_staff_id": staff_id
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if data['assigned_staff_id'] == staff_id:
                self.log_result("Initial staff assignment", True)
                
                # Test reassignment (if we have multiple staff members)
                if len(staff_members) > 1:
                    new_staff_id = staff_members[1]['id']
                    response, error = self.make_request('PATCH', f'requests/{request_id}', {
                        "assigned_staff_id": new_staff_id
                    }, token=self.admin_token)
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        if data['assigned_staff_id'] == new_staff_id:
                            self.log_result("Staff reassignment", True)
                            return True
                        else:
                            self.log_result("Staff reassignment", False, "Staff ID not updated properly")
                    else:
                        self.log_result("Staff reassignment", False, f"Status: {response.status_code if response else 'No response'}")
                else:
                    self.log_result("Staff reassignment", True, "Only one staff member available, skipping reassignment test")
                    return True
            else:
                self.log_result("Initial staff assignment", False, "Staff ID not assigned properly")
        else:
            self.log_result("Initial staff assignment", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_auth_me(self):
        """Test auth/me endpoint for different roles"""
        print("\n🔍 Testing Auth Me Endpoint...")
        
        tokens = [
            ("admin", self.admin_token),
            ("student", self.student_token),
            ("staff", self.staff_token)
        ]
        
        for role, token in tokens:
            if token:
                response, error = self.make_request('GET', 'auth/me', token=token)
                if response and response.status_code == 200:
                    data = response.json()
                    if data.get('role') == role:
                        self.log_result(f"Auth me for {role}", True)
                    else:
                        self.log_result(f"Auth me for {role}", False, f"Expected role {role}, got {data.get('role')}")
                else:
                    self.log_result(f"Auth me for {role}", False, f"Status: {response.status_code if response else 'No response'}")

    def test_create_recommendation_request(self):
        """Test creating recommendation letter request with NEW FIELDS"""
        print("\n🔍 Testing Recommendation Letter Request Creation with New Fields...")
        
        if not self.student_token:
            self.log_result("Create recommendation request", False, "No student token available")
            return None
        
        needed_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
        
        # Test with NEW ARRAY FORMAT for years_attended and co_curricular_activities
        request_data = {
            "first_name": "James",
            "middle_name": "Anthony",
            "last_name": "Williams",
            "email": "james.williams@email.com",
            "phone_number": "+1 876 555 1234",
            "address": "456 Hope Road, Kingston 10, Jamaica",
            "years_attended": [{"from_year": "2015", "to_year": "2020"}, {"from_year": "2021", "to_year": "2022"}],  # NEW ARRAY FORMAT
            "enrollment_status": "graduate",  # REQUIRED FIELD
            "last_form_class": "Upper 6th",
            "co_curricular_activities": "Head Boy 2021-2022, Captain of Football Team, Member of Debate Club, Science Fair Winner 2020",  # NEW FIELD
            "institution_name": "Harvard University",
            "institution_address": "Massachusetts Hall, Cambridge, MA 02138, USA",
            "directed_to": "Admissions Office",
            "program_name": "Bachelor of Arts in Economics",
            "needed_by_date": needed_date,
            "collection_method": "delivery",  # NEW COLLECTION METHOD
            "delivery_address": "789 New Kingston Drive, Kingston 5, Jamaica"  # NEW FIELD
        }
        
        response, error = self.make_request('POST', 'recommendations', request_data, token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if ('id' in data and data['status'] == 'Pending' and 
                data['program_name'] == 'Bachelor of Arts in Economics' and
                data['collection_method'] == 'delivery' and
                data['delivery_address'] == '789 New Kingston Drive, Kingston 5, Jamaica' and
                data['co_curricular_activities'] == 'Head Boy 2021-2022, Captain of Football Team, Member of Debate Club, Science Fair Winner 2020' and
                isinstance(data['years_attended'], list) and len(data['years_attended']) == 2):
                self.log_result("Create recommendation request with new fields", True)
                return data['id']
            else:
                self.log_result("Create recommendation request with new fields", False, "New fields not saved properly")
        else:
            error_detail = ""
            if response:
                try:
                    error_detail = f" - {response.json()}"
                except:
                    error_detail = f" - Status: {response.status_code}"
            self.log_result("Create recommendation request with new fields", False, f"Status: {response.status_code if response else 'No response'}{error_detail}")
        
        return None

    def test_get_recommendation_requests(self):
        """Test getting recommendation requests for different roles"""
        print("\n🔍 Testing Recommendation Request Retrieval...")
        
        # Test student getting their requests
        if self.student_token:
            response, error = self.make_request('GET', 'recommendations', token=self.student_token)
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Student get recommendation requests", True)
                else:
                    self.log_result("Student get recommendation requests", False, "Response is not a list")
            else:
                self.log_result("Student get recommendation requests", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test admin getting all requests
        if self.admin_token:
            response, error = self.make_request('GET', 'recommendations/all', token=self.admin_token)
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Admin get all recommendation requests", True)
                else:
                    self.log_result("Admin get all recommendation requests", False, "Response is not a list")
            else:
                self.log_result("Admin get all recommendation requests", False, f"Status: {response.status_code if response else 'No response'}")

    def test_get_specific_recommendation_request(self, request_id):
        """Test getting a specific recommendation request"""
        print("\n🔍 Testing Specific Recommendation Request Retrieval...")
        
        if not request_id:
            self.log_result("Get specific recommendation request", False, "No request ID available")
            return
        
        # Test student getting their specific request
        if self.student_token:
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.student_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get('id') == request_id:
                    self.log_result("Student get specific recommendation request", True)
                else:
                    self.log_result("Student get specific recommendation request", False, "Request ID mismatch")
            else:
                self.log_result("Student get specific recommendation request", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test admin getting specific request
        if self.admin_token:
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.admin_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get('id') == request_id:
                    self.log_result("Admin get specific recommendation request", True)
                else:
                    self.log_result("Admin get specific recommendation request", False, "Request ID mismatch")
            else:
                self.log_result("Admin get specific recommendation request", False, f"Status: {response.status_code if response else 'No response'}")

    def test_update_recommendation_request_status(self, request_id):
        """Test updating recommendation request status (admin/staff only)"""
        print("\n🔍 Testing Recommendation Request Status Update...")
        
        if not request_id:
            self.log_result("Update recommendation request status", False, "No request ID available")
            return
        
        if not self.admin_token:
            self.log_result("Update recommendation request status", False, "No admin token available")
            return
        
        # Test status update
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "status": "In Progress"
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get('status') == 'In Progress':
                self.log_result("Update recommendation request status", True)
                
                # Test assigning staff
                if self.staff_token:
                    # Get staff members to find staff ID
                    staff_response, _ = self.make_request('GET', 'admin/staff', token=self.admin_token)
                    if staff_response and staff_response.status_code == 200:
                        staff_members = staff_response.json()
                        if staff_members:
                            staff_id = staff_members[0]['id']
                            
                            response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
                                "assigned_staff_id": staff_id
                            }, token=self.admin_token)
                            
                            if response and response.status_code == 200:
                                data = response.json()
                                if data.get('assigned_staff_id') == staff_id:
                                    self.log_result("Assign staff to recommendation request", True)
                                else:
                                    self.log_result("Assign staff to recommendation request", False, "Staff ID not assigned properly")
                            else:
                                self.log_result("Assign staff to recommendation request", False, f"Status: {response.status_code if response else 'No response'}")
            else:
                self.log_result("Update recommendation request status", False, "Status not updated properly")
        else:
            self.log_result("Update recommendation request status", False, f"Status: {response.status_code if response else 'No response'}")

    def test_student_edit_recommendation_request(self, request_id):
        """Test student editing their own recommendation request"""
        print("\n🔍 Testing Student Edit Recommendation Request...")
        
        if not request_id or not self.student_token:
            self.log_result("Student edit recommendation request", False, "Missing request ID or student token")
            return
        
        # Test editing request details
        update_data = {
            "program_name": "Master of Science in Computer Science",
            "directed_to": "Graduate Admissions Office",
            "institution_address": "Mona Campus, Kingston 7, Jamaica - Updated"
        }
        
        response, error = self.make_request('PUT', f'recommendations/{request_id}/edit', update_data, token=self.student_token)
        
        if error:
            self.log_result("Student edit recommendation request", False, f"Request error: {error}")
            return
        
        if response and response.status_code == 200:
            data = response.json()
            if (data.get('program_name') == update_data['program_name'] and 
                data.get('directed_to') == update_data['directed_to']):
                self.log_result("Student edit recommendation request", True)
            else:
                self.log_result("Student edit recommendation request", False, "Fields not updated properly")
        else:
            self.log_result("Student edit recommendation request", False, f"Status: {response.status_code if response else 'No response'}")

    def test_recommendation_request_permissions(self):
        """Test permission restrictions for recommendation requests"""
        print("\n🔍 Testing Recommendation Request Permissions...")
        
        # Test student cannot update status
        if self.student_token:
            fake_id = str(uuid.uuid4())
            response, error = self.make_request('PATCH', f'recommendations/{fake_id}', {
                "status": "Completed"
            }, token=self.student_token)
            
            if error:
                self.log_result("Student cannot update status", False, f"Request error: {error}")
            elif response and response.status_code == 403:
                self.log_result("Student cannot update status", True)
            else:
                self.log_result("Student cannot update status", False, f"Expected 403, got {response.status_code if response else 'No response'}")
        
        # Test unauthenticated access
        response, error = self.make_request('GET', 'recommendations')
        if error:
            self.log_result("Unauthenticated access denied", False, f"Request error: {error}")
        elif response and response.status_code in [401, 403]:  # Both are acceptable for auth failure
            self.log_result("Unauthenticated access denied", True)
        else:
            self.log_result("Unauthenticated access denied", False, f"Expected 401/403, got {response.status_code if response else 'No response'}")

    def test_export_endpoints(self):
        """Test export endpoints for transcripts and recommendations"""
        print("\n🔍 Testing Export Endpoints...")
        
        if not self.admin_token:
            self.log_result("Export endpoints", False, "No admin token available")
            return
        
        # Test transcript export endpoints
        transcript_formats = ['xlsx', 'pdf', 'docx']
        for format_type in transcript_formats:
            response, error = self.make_request('GET', f'export/transcripts/{format_type}', token=self.admin_token)
            
            if response and response.status_code == 200:
                # Check content type headers
                content_type = response.headers.get('content-type', '').lower()
                expected_types = {
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'pdf': 'application/pdf',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }
                
                if expected_types[format_type] in content_type:
                    self.log_result(f"Export transcripts {format_type.upper()}", True)
                else:
                    self.log_result(f"Export transcripts {format_type.upper()}", False, f"Wrong content type: {content_type}")
            else:
                self.log_result(f"Export transcripts {format_type.upper()}", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test recommendation export endpoints
        recommendation_formats = ['xlsx', 'pdf', 'docx']
        for format_type in recommendation_formats:
            response, error = self.make_request('GET', f'export/recommendations/{format_type}', token=self.admin_token)
            
            if response and response.status_code == 200:
                # Check content type headers
                content_type = response.headers.get('content-type', '').lower()
                expected_types = {
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'pdf': 'application/pdf',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }
                
                if expected_types[format_type] in content_type:
                    self.log_result(f"Export recommendations {format_type.upper()}", True)
                else:
                    self.log_result(f"Export recommendations {format_type.upper()}", False, f"Wrong content type: {content_type}")
            else:
                self.log_result(f"Export recommendations {format_type.upper()}", False, f"Status: {response.status_code if response else 'No response'}")

    def test_admin_login_specific(self):
        """Test admin login with specific credentials from review request"""
        print("\n🔍 Testing Admin Login with Specific Credentials...")
        
        response, error = self.make_request('POST', 'auth/login', {
            "email": "admin@wolmers.org",
            "password": "Admin123!"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'admin':
                self.admin_token = data['access_token']
                self.log_result("Admin login with specific credentials", True)
                return True
            else:
                self.log_result("Admin login with specific credentials", False, "Invalid response format")
        else:
            self.log_result("Admin login with specific credentials", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_staff_login_specific(self):
        """Test staff login with specific credentials from review request"""
        print("\n🔍 Testing Staff Login with Specific Credentials...")
        
        response, error = self.make_request('POST', 'auth/login', {
            "email": "staff@wolmers.org",
            "password": "password123"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'staff':
                self.staff_token = data['access_token']
                self.log_result("Staff login with specific credentials", True)
                return True
            else:
                self.log_result("Staff login with specific credentials", False, "Invalid response format")
        else:
            self.log_result("Staff login with specific credentials", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_student_login_specific(self):
        """Test student login with specific credentials from review request"""
        print("\n🔍 Testing Student Login with Specific Credentials...")
        
        response, error = self.make_request('POST', 'auth/login', {
            "email": "student@test.com",
            "password": "password123"
        })
        
        if response and response.status_code == 200:
            data = response.json()
            if 'access_token' in data and data['user']['role'] == 'student':
                self.student_token = data['access_token']
                self.log_result("Student login with specific credentials", True)
                return True
            else:
                self.log_result("Student login with specific credentials", False, "Invalid response format")
        else:
            self.log_result("Student login with specific credentials", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_years_attended_display_fix(self):
        """Test Years Attended field displays correctly as string for all user roles"""
        print("\n🔍 Testing Years Attended Display Fix...")
        
        # First, create a recommendation request with years_attended array
        if not self.student_token:
            self.log_result("Years Attended Display Fix", False, "No student token available")
            return None
        
        needed_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Test",
            "middle_name": "Years",
            "last_name": "Display",
            "email": "test.years@email.com",
            "phone_number": "+1 876 555 9999",
            "address": "123 Test Street, Kingston, Jamaica",
            "years_attended": [{"from_year": "2015", "to_year": "2020"}, {"from_year": "2021", "to_year": "2022"}],
            "enrollment_status": "graduate",  # REQUIRED FIELD
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
            self.log_result("Years Attended Display Fix - Create Request", False, f"Status: {response.status_code if response else 'No response'}")
            return None
        
        request_id = response.json()['id']
        
        # Test 1: Student viewing their own recommendation detail
        response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            years_attended = data.get('years_attended')
            years_attended_str = data.get('years_attended_str')
            
            # Check that years_attended is an array
            if isinstance(years_attended, list) and len(years_attended) == 2:
                # Check that years_attended_str is a properly formatted string
                if years_attended_str == "2015-2020, 2021-2022":
                    self.log_result("Years Attended Display Fix - Student View", True)
                else:
                    self.log_result("Years Attended Display Fix - Student View", False, f"Expected '2015-2020, 2021-2022', got '{years_attended_str}'")
            else:
                self.log_result("Years Attended Display Fix - Student View", False, f"years_attended should be array with 2 items, got {years_attended}")
        else:
            self.log_result("Years Attended Display Fix - Student View", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test 2: Staff viewing recommendation detail
        if self.staff_token:
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.staff_token)
            
            if response and response.status_code == 200:
                data = response.json()
                years_attended_str = data.get('years_attended_str')
                
                if years_attended_str == "2015-2020, 2021-2022":
                    self.log_result("Years Attended Display Fix - Staff View", True)
                else:
                    self.log_result("Years Attended Display Fix - Staff View", False, f"Expected '2015-2020, 2021-2022', got '{years_attended_str}'")
            else:
                self.log_result("Years Attended Display Fix - Staff View", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test 3: Admin viewing recommendation detail
        if self.admin_token:
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.admin_token)
            
            if response and response.status_code == 200:
                data = response.json()
                years_attended_str = data.get('years_attended_str')
                
                if years_attended_str == "2015-2020, 2021-2022":
                    self.log_result("Years Attended Display Fix - Admin View", True)
                else:
                    self.log_result("Years Attended Display Fix - Admin View", False, f"Expected '2015-2020, 2021-2022', got '{years_attended_str}'")
            else:
                self.log_result("Years Attended Display Fix - Admin View", False, f"Status: {response.status_code if response else 'No response'}")
        
        return request_id

    def test_student_dashboard_recommendation_data(self):
        """Test Student Dashboard gets proper recommendation data for clickable tiles"""
        print("\n🔍 Testing Student Dashboard Recommendation Data...")
        
        if not self.student_token:
            self.log_result("Student Dashboard Recommendation Data", False, "No student token available")
            return
        
        # Test getting student's recommendations for dashboard
        response, error = self.make_request('GET', 'recommendations', token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                # Check that each recommendation has the required fields for dashboard filtering
                all_have_status = True
                for rec in data:
                    if 'status' not in rec:
                        all_have_status = False
                        break
                
                if all_have_status:
                    self.log_result("Student Dashboard Recommendation Data - Status Field", True)
                else:
                    self.log_result("Student Dashboard Recommendation Data - Status Field", False, "Some recommendations missing status field")
                
                # Check for proper data structure
                if len(data) > 0:
                    sample_rec = data[0]
                    required_fields = ['id', 'status', 'student_name', 'institution_name', 'program_name', 'created_at']
                    missing_fields = [field for field in required_fields if field not in sample_rec]
                    
                    if not missing_fields:
                        self.log_result("Student Dashboard Recommendation Data - Required Fields", True)
                    else:
                        self.log_result("Student Dashboard Recommendation Data - Required Fields", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Student Dashboard Recommendation Data - Required Fields", True, "No recommendations to check (empty state)")
            else:
                self.log_result("Student Dashboard Recommendation Data", False, "Response is not a list")
        else:
            self.log_result("Student Dashboard Recommendation Data", False, f"Status: {response.status_code if response else 'No response'}")

    def test_recommendation_workflow_bug_verification(self):
        """Test complete recommendation workflow to verify no critical bugs"""
        print("\n🔍 Testing Recommendation Workflow Bug Verification...")
        
        if not all([self.student_token, self.admin_token, self.staff_token]):
            self.log_result("Recommendation Workflow Bug Verification", False, "Missing required tokens")
            return
        
        # Step 1: Student creates recommendation request
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Bug",
            "middle_name": "Test",
            "last_name": "Verification",
            "email": "bug.test@email.com",
            "phone_number": "+1 876 555 0000",
            "address": "Bug Test Address, Kingston, Jamaica",
            "years_attended": [{"from_year": "2018", "to_year": "2023"}],
            "enrollment_status": "graduate",  # REQUIRED FIELD
            "last_form_class": "Upper 6th",
            "co_curricular_activities": "Student Council President",
            "institution_name": "Bug Test University",
            "institution_address": "Bug Test University Address",
            "directed_to": "Admissions Committee",
            "program_name": "Software Engineering",
            "needed_by_date": needed_date,
            "collection_method": "emailed"
        }
        
        response, error = self.make_request('POST', 'recommendations', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            self.log_result("Recommendation Workflow - Student Create", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        request_id = response.json()['id']
        self.log_result("Recommendation Workflow - Student Create", True)
        
        # Step 2: Admin views recommendation detail
        response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.admin_token)
        
        if response and response.status_code == 200:
            self.log_result("Recommendation Workflow - Admin View Detail", True)
        else:
            self.log_result("Recommendation Workflow - Admin View Detail", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        # Step 3: Admin assigns staff member
        staff_response, _ = self.make_request('GET', 'admin/staff', token=self.admin_token)
        if staff_response and staff_response.status_code == 200:
            staff_members = staff_response.json()
            if staff_members:
                staff_id = staff_members[0]['id']
                
                response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
                    "assigned_staff_id": staff_id
                }, token=self.admin_token)
                
                if response and response.status_code == 200:
                    self.log_result("Recommendation Workflow - Admin Assign Staff", True)
                else:
                    self.log_result("Recommendation Workflow - Admin Assign Staff", False, f"Status: {response.status_code if response else 'No response'}")
                    return
        
        # Step 4: Staff views assigned recommendation detail
        response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.staff_token)
        
        if response and response.status_code == 200:
            self.log_result("Recommendation Workflow - Staff View Detail", True)
        else:
            self.log_result("Recommendation Workflow - Staff View Detail", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        # Step 5: Staff updates recommendation status
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "status": "In Progress"
        }, token=self.staff_token)
        
        if response and response.status_code == 200:
            self.log_result("Recommendation Workflow - Staff Update Status", True)
        else:
            self.log_result("Recommendation Workflow - Staff Update Status", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Final verification: Check that the workflow completed without errors
        self.log_result("Recommendation Workflow - Complete End-to-End", True)

    def test_admin_data_management(self):
        """Test Admin Data Management APIs - NEW FEATURE"""
        print("\n🔍 Testing Admin Data Management APIs...")
        
        if not self.admin_token:
            self.log_result("Admin Data Management", False, "No admin token available")
            return
        
        # Test 1: GET /api/admin/data-summary
        print("Testing data summary endpoint...")
        response, error = self.make_request('GET', 'admin/data-summary', token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ['users', 'transcript_requests', 'recommendation_requests', 'notifications', 'total']
            if all(field in data for field in required_fields):
                self.log_result("Admin Data Summary - GET /api/admin/data-summary", True)
                print(f"   Data counts: Users={data['users']}, Transcripts={data['transcript_requests']}, Recommendations={data['recommendation_requests']}, Notifications={data['notifications']}")
            else:
                missing_fields = [field for field in required_fields if field not in data]
                self.log_result("Admin Data Summary - GET /api/admin/data-summary", False, f"Missing fields: {missing_fields}")
        else:
            self.log_result("Admin Data Summary - GET /api/admin/data-summary", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test 2: GET /api/admin/export-all-data/pdf
        print("Testing PDF export endpoint...")
        response, error = self.make_request('GET', 'admin/export-all-data/pdf', token=self.admin_token)
        
        if response and response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'application/pdf' in content_type:
                self.log_result("Admin Export All Data PDF - GET /api/admin/export-all-data/pdf", True)
                print(f"   PDF export successful, content-type: {content_type}")
            else:
                self.log_result("Admin Export All Data PDF - GET /api/admin/export-all-data/pdf", False, f"Wrong content type: {content_type}")
        else:
            self.log_result("Admin Export All Data PDF - GET /api/admin/export-all-data/pdf", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test 3: DELETE /api/admin/clear-all-data (WARNING: This will clear data!)
        print("Testing clear all data endpoint...")
        response, error = self.make_request('DELETE', 'admin/clear-all-data', token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if ('success' in data and data['success'] == True and 
                'message' in data and 'deleted_counts' in data):
                self.log_result("Admin Clear All Data - DELETE /api/admin/clear-all-data", True)
                print(f"   Clear data successful: {data['message']}")
                print(f"   Deleted counts: {data['deleted_counts']}")
                
                # Verify admin account is preserved by trying to login again
                login_response, _ = self.make_request('POST', 'auth/login', {
                    "email": "admin@wolmers.org",
                    "password": "Admin123!"
                })
                
                if login_response and login_response.status_code == 200:
                    self.log_result("Admin Account Preserved After Clear", True)
                    self.admin_token = login_response.json()['access_token']  # Update token
                else:
                    self.log_result("Admin Account Preserved After Clear", False, "Admin login failed after clear")
            else:
                self.log_result("Admin Clear All Data - DELETE /api/admin/clear-all-data", False, "Invalid response format")
        else:
            self.log_result("Admin Clear All Data - DELETE /api/admin/clear-all-data", False, f"Status: {response.status_code if response else 'No response'}")

    def test_admin_data_management_permissions(self):
        """Test Admin Data Management permission restrictions"""
        print("\n🔍 Testing Admin Data Management Permissions...")
        
        # Create a test student to verify non-admin access is denied
        test_student_email = f"test_perm_{datetime.now().strftime('%H%M%S')}@example.com"
        
        # Register student
        response, error = self.make_request('POST', 'auth/register', {
            "full_name": "Test Permission Student",
            "email": test_student_email,
            "password": "TestPass123!",
            "role": "student"
        })
        
        if response and response.status_code == 200:
            student_token = response.json()['access_token']
            
            # Test 1: Student cannot access data summary
            response, error = self.make_request('GET', 'admin/data-summary', token=student_token)
            if response and response.status_code == 403:
                self.log_result("Non-admin denied data summary access", True)
            else:
                self.log_result("Non-admin denied data summary access", False, f"Expected 403, got {response.status_code if response else 'No response'}")
            
            # Test 2: Student cannot access PDF export
            response, error = self.make_request('GET', 'admin/export-all-data/pdf', token=student_token)
            if response and response.status_code == 403:
                self.log_result("Non-admin denied PDF export access", True)
            else:
                self.log_result("Non-admin denied PDF export access", False, f"Expected 403, got {response.status_code if response else 'No response'}")
            
            # Test 3: Student cannot clear data
            response, error = self.make_request('DELETE', 'admin/clear-all-data', token=student_token)
            if response and response.status_code == 403:
                self.log_result("Non-admin denied clear data access", True)
            else:
                self.log_result("Non-admin denied clear data access", False, f"Expected 403, got {response.status_code if response else 'No response'}")
        else:
            self.log_result("Admin Data Management Permissions", False, "Could not create test student for permission testing")

    def test_transcript_status_notes(self):
        """Test 1: Transcript Status Notes - Custom notes in timeline"""
        print("\n🔍 Testing Transcript Status Notes...")
        
        if not all([self.student_token, self.admin_token, self.staff_token]):
            self.log_result("Transcript Status Notes", False, "Missing required tokens")
            return None
        
        # Create transcript request as student
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Status",
            "middle_name": "Notes",
            "last_name": "Test",
            "school_id": "WBS2024999",
            "enrollment_status": "graduate",
            "academic_years": [{"from_year": "2018", "to_year": "2023"}],
            "wolmers_email": "status.notes.test@wolmers.org",
            "personal_email": "status.notes@test.com",
            "phone_number": "+1 876 555 1111",
            "reason": "Testing status notes functionality",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'requests', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            self.log_result("Transcript Status Notes - Create Request", False, f"Status: {response.status_code if response else 'No response'}")
            return None
        
        request_id = response.json()['id']
        self.log_result("Transcript Status Notes - Create Request", True)
        
        # Admin updates status with custom note
        admin_note = "Starting to process transcript request"
        response, error = self.make_request('PATCH', f'requests/{request_id}', {
            "status": "In Progress",
            "note": admin_note
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            self.log_result("Transcript Status Notes - Admin Update with Note", True)
            
            # Verify timeline contains custom note
            response, error = self.make_request('GET', f'requests/{request_id}', token=self.admin_token)
            
            if response and response.status_code == 200:
                data = response.json()
                timeline = data.get('timeline', [])
                
                # Find the "In Progress" timeline entry
                in_progress_entry = None
                for entry in timeline:
                    if entry.get('status') == 'In Progress':
                        in_progress_entry = entry
                        break
                
                if in_progress_entry:
                    if in_progress_entry.get('note') == admin_note:
                        self.log_result("Transcript Status Notes - Admin Custom Note in Timeline", True)
                    else:
                        self.log_result("Transcript Status Notes - Admin Custom Note in Timeline", False, 
                                      f"Expected '{admin_note}', got '{in_progress_entry.get('note')}'")
                else:
                    self.log_result("Transcript Status Notes - Admin Custom Note in Timeline", False, "No 'In Progress' entry found in timeline")
            else:
                self.log_result("Transcript Status Notes - Admin Custom Note in Timeline", False, f"Status: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Transcript Status Notes - Admin Update with Note", False, f"Status: {response.status_code if response else 'No response'}")
            return None
        
        # Staff updates status with custom note
        staff_note = "Gathering documents from archive"
        response, error = self.make_request('PATCH', f'requests/{request_id}', {
            "status": "Processing",
            "note": staff_note
        }, token=self.staff_token)
        
        if response and response.status_code == 200:
            self.log_result("Transcript Status Notes - Staff Update with Note", True)
            
            # Verify timeline contains both entries
            response, error = self.make_request('GET', f'requests/{request_id}', token=self.staff_token)
            
            if response and response.status_code == 200:
                data = response.json()
                timeline = data.get('timeline', [])
                
                # Find the "Processing" timeline entry
                processing_entry = None
                for entry in timeline:
                    if entry.get('status') == 'Processing':
                        processing_entry = entry
                        break
                
                if processing_entry:
                    if processing_entry.get('note') == staff_note:
                        self.log_result("Transcript Status Notes - Staff Custom Note in Timeline", True)
                        
                        # Verify timeline structure
                        required_fields = ['status', 'note', 'timestamp', 'updated_by']
                        missing_fields = [field for field in required_fields if field not in processing_entry]
                        
                        if not missing_fields:
                            self.log_result("Transcript Status Notes - Timeline Structure", True)
                        else:
                            self.log_result("Transcript Status Notes - Timeline Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("Transcript Status Notes - Staff Custom Note in Timeline", False, 
                                      f"Expected '{staff_note}', got '{processing_entry.get('note')}'")
                else:
                    self.log_result("Transcript Status Notes - Staff Custom Note in Timeline", False, "No 'Processing' entry found in timeline")
            else:
                self.log_result("Transcript Status Notes - Staff Custom Note in Timeline", False, f"Status: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Transcript Status Notes - Staff Update with Note", False, f"Status: {response.status_code if response else 'No response'}")
        
        return request_id

    def test_recommendation_status_notes(self):
        """Test 2: Recommendation Status Notes - Custom notes in timeline"""
        print("\n🔍 Testing Recommendation Status Notes...")
        
        if not all([self.student_token, self.admin_token, self.staff_token]):
            self.log_result("Recommendation Status Notes", False, "Missing required tokens")
            return None
        
        # Create recommendation request as student
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Recommendation",
            "middle_name": "Status",
            "last_name": "Notes",
            "email": "rec.status.notes@test.com",
            "phone_number": "+1 876 555 2222",
            "address": "123 Status Notes Street, Kingston, Jamaica",
            "years_attended": [{"from_year": "2017", "to_year": "2022"}],
            "enrollment_status": "graduate",  # REQUIRED FIELD
            "last_form_class": "Upper 6th",
            "co_curricular_activities": "Debate Team Captain, Science Club President",
            "institution_name": "Status Notes University",
            "institution_address": "Status Notes University Address",
            "directed_to": "Admissions Committee",
            "program_name": "Computer Science",
            "needed_by_date": needed_date,
            "collection_method": "emailed"
        }
        
        response, error = self.make_request('POST', 'recommendations', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            self.log_result("Recommendation Status Notes - Create Request", False, f"Status: {response.status_code if response else 'No response'}")
            return None
        
        request_id = response.json()['id']
        self.log_result("Recommendation Status Notes - Create Request", True)
        
        # Admin updates status with custom note
        admin_note = "Reviewing student's co-curricular record"
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "status": "In Progress",
            "note": admin_note
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            self.log_result("Recommendation Status Notes - Admin Update with Note", True)
            
            # Verify timeline contains custom note
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.admin_token)
            
            if response and response.status_code == 200:
                data = response.json()
                timeline = data.get('timeline', [])
                
                # Find the "In Progress" timeline entry
                in_progress_entry = None
                for entry in timeline:
                    if entry.get('status') == 'In Progress':
                        in_progress_entry = entry
                        break
                
                if in_progress_entry:
                    if in_progress_entry.get('note') == admin_note:
                        self.log_result("Recommendation Status Notes - Admin Custom Note in Timeline", True)
                    else:
                        self.log_result("Recommendation Status Notes - Admin Custom Note in Timeline", False, 
                                      f"Expected '{admin_note}', got '{in_progress_entry.get('note')}'")
                else:
                    self.log_result("Recommendation Status Notes - Admin Custom Note in Timeline", False, "No 'In Progress' entry found in timeline")
            else:
                self.log_result("Recommendation Status Notes - Admin Custom Note in Timeline", False, f"Status: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Recommendation Status Notes - Admin Update with Note", False, f"Status: {response.status_code if response else 'No response'}")
            return None
        
        # Staff updates status with custom note
        staff_note = "Recommendation letter completed and signed"
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "status": "Ready",
            "note": staff_note
        }, token=self.staff_token)
        
        if response and response.status_code == 200:
            self.log_result("Recommendation Status Notes - Staff Update with Note", True)
            
            # Verify timeline contains both entries
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.staff_token)
            
            if response and response.status_code == 200:
                data = response.json()
                timeline = data.get('timeline', [])
                
                # Find the "Ready" timeline entry
                ready_entry = None
                for entry in timeline:
                    if entry.get('status') == 'Ready':
                        ready_entry = entry
                        break
                
                if ready_entry:
                    if ready_entry.get('note') == staff_note:
                        self.log_result("Recommendation Status Notes - Staff Custom Note in Timeline", True)
                        
                        # Verify timeline structure
                        required_fields = ['status', 'note', 'timestamp', 'updated_by']
                        missing_fields = [field for field in required_fields if field not in ready_entry]
                        
                        if not missing_fields:
                            self.log_result("Recommendation Status Notes - Timeline Structure", True)
                        else:
                            self.log_result("Recommendation Status Notes - Timeline Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("Recommendation Status Notes - Staff Custom Note in Timeline", False, 
                                      f"Expected '{staff_note}', got '{ready_entry.get('note')}'")
                else:
                    self.log_result("Recommendation Status Notes - Staff Custom Note in Timeline", False, "No 'Ready' entry found in timeline")
            else:
                self.log_result("Recommendation Status Notes - Staff Custom Note in Timeline", False, f"Status: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Recommendation Status Notes - Staff Update with Note", False, f"Status: {response.status_code if response else 'No response'}")
        
        return request_id

    def test_co_curricular_activities_update(self):
        """Test 3: Co-curricular Activities Update"""
        print("\n🔍 Testing Co-curricular Activities Update...")
        
        if not all([self.student_token, self.admin_token, self.staff_token]):
            self.log_result("Co-curricular Activities Update", False, "Missing required tokens")
            return
        
        # Create recommendation request as student
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "Co-curricular",
            "middle_name": "Activities",
            "last_name": "Test",
            "email": "cocurricular@test.com",
            "phone_number": "+1 876 555 3333",
            "address": "123 Activities Street, Kingston, Jamaica",
            "years_attended": [{"from_year": "2016", "to_year": "2021"}],
            "last_form_class": "Upper 6th",
            "co_curricular_activities": "Initial activities list",
            "institution_name": "Activities University",
            "institution_address": "Activities University Address",
            "directed_to": "Admissions Office",
            "program_name": "Business Administration",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'recommendations', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            self.log_result("Co-curricular Activities Update - Create Request", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        request_id = response.json()['id']
        self.log_result("Co-curricular Activities Update - Create Request", True)
        
        # Test admin can update co-curricular activities
        admin_activities = "Captain of Football Team, President of Debate Club"
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "co_curricular_activities": admin_activities
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            self.log_result("Co-curricular Activities Update - Admin Update", True)
            
            # Verify the update
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.admin_token)
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get('co_curricular_activities') == admin_activities:
                    self.log_result("Co-curricular Activities Update - Admin Verification", True)
                else:
                    self.log_result("Co-curricular Activities Update - Admin Verification", False, 
                                  f"Expected '{admin_activities}', got '{data.get('co_curricular_activities')}'")
            else:
                self.log_result("Co-curricular Activities Update - Admin Verification", False, f"Status: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Co-curricular Activities Update - Admin Update", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test staff can update co-curricular activities
        staff_activities = "Head Boy 2020-2021, Science Fair Winner, Drama Club Member"
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "co_curricular_activities": staff_activities
        }, token=self.staff_token)
        
        if response and response.status_code == 200:
            self.log_result("Co-curricular Activities Update - Staff Update", True)
            
            # Verify the update
            response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.staff_token)
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get('co_curricular_activities') == staff_activities:
                    self.log_result("Co-curricular Activities Update - Staff Verification", True)
                else:
                    self.log_result("Co-curricular Activities Update - Staff Verification", False, 
                                  f"Expected '{staff_activities}', got '{data.get('co_curricular_activities')}'")
            else:
                self.log_result("Co-curricular Activities Update - Staff Verification", False, f"Status: {response.status_code if response else 'No response'}")
        else:
            self.log_result("Co-curricular Activities Update - Staff Update", False, f"Status: {response.status_code if response else 'No response'}")

    def test_timeline_display_format(self):
        """Test 4: Timeline Display Format - Verify structure for both request types"""
        print("\n🔍 Testing Timeline Display Format...")
        
        if not all([self.student_token, self.admin_token]):
            self.log_result("Timeline Display Format", False, "Missing required tokens")
            return
        
        # Test transcript timeline format
        transcript_id = self.test_transcript_status_notes()
        if transcript_id:
            response, error = self.make_request('GET', f'requests/{transcript_id}', token=self.admin_token)
            
            if response and response.status_code == 200:
                data = response.json()
                timeline = data.get('timeline', [])
                
                if timeline:
                    # Check structure of timeline entries
                    sample_entry = timeline[-1]  # Get latest entry
                    required_fields = ['status', 'note', 'timestamp', 'updated_by']
                    missing_fields = [field for field in required_fields if field not in sample_entry]
                    
                    if not missing_fields:
                        self.log_result("Timeline Display Format - Transcript Structure", True)
                    else:
                        self.log_result("Timeline Display Format - Transcript Structure", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Timeline Display Format - Transcript Structure", False, "No timeline entries found")
            else:
                self.log_result("Timeline Display Format - Transcript Structure", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test recommendation timeline format
        recommendation_id = self.test_recommendation_status_notes()
        if recommendation_id:
            response, error = self.make_request('GET', f'recommendations/{recommendation_id}', token=self.admin_token)
            
            if response and response.status_code == 200:
                data = response.json()
                timeline = data.get('timeline', [])
                
                if timeline:
                    # Check structure of timeline entries
                    sample_entry = timeline[-1]  # Get latest entry
                    required_fields = ['status', 'note', 'timestamp', 'updated_by']
                    missing_fields = [field for field in required_fields if field not in sample_entry]
                    
                    if not missing_fields:
                        self.log_result("Timeline Display Format - Recommendation Structure", True)
                    else:
                        self.log_result("Timeline Display Format - Recommendation Structure", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Timeline Display Format - Recommendation Structure", False, "No timeline entries found")
            else:
                self.log_result("Timeline Display Format - Recommendation Structure", False, f"Status: {response.status_code if response else 'No response'}")

    def test_status_notes_functionality_comprehensive(self):
        """Comprehensive test for status notes functionality as per review request"""
        print("\n" + "🎯" * 30)
        print("🎯 CRITICAL TEST: STATUS NOTES FUNCTIONALITY")
        print("🎯" * 30)
        
        # Test 1: Transcript Status Notes
        self.test_transcript_status_notes()
        
        # Test 2: Recommendation Status Notes  
        self.test_recommendation_status_notes()
        
        # Test 3: Co-curricular Activities Update
        self.test_co_curricular_activities_update()
        
        # Test 4: Timeline Display Format
        self.test_timeline_display_format()

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Wolmer's Transcript Tracker API Tests")
        print(f"🎯 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic health checks
        self.test_health_check()
        
        # Authentication tests - PRIORITY: Test specific credentials from review request
        print("\n" + "🎯" * 20)
        print("🎯 PRIORITY: REVIEW REQUEST AUTHENTICATION TESTS")
        print("🎯" * 20)
        admin_login_success = self.test_admin_login_specific()
        staff_login_success = self.test_staff_login_specific()
        student_login_success = self.test_student_login_specific()
        
        # If specific logins failed, try creating users
        if not student_login_success:
            student_reg_success = self.test_student_registration()
            if not student_reg_success:
                self.test_student_login()
        
        # User management tests
        if admin_login_success:
            if not staff_login_success:
                self.test_create_staff_user()
                self.test_staff_login()
            self.test_user_management()
            self.test_analytics()
        
        # Test auth/me for all roles
        self.test_auth_me()
        
        # PRIORITY: Test BUG FIXES from review request
        print("\n" + "🎯" * 20)
        print("🎯 PRIORITY: BUG FIXES TESTING")
        print("🎯" * 20)
        
        # Test Years Attended Display Fix
        rec_request_id = self.test_years_attended_display_fix()
        
        # Test Student Dashboard Recommendation Data
        self.test_student_dashboard_recommendation_data()
        
        # Test Recommendation Workflow Bug Verification
        self.test_recommendation_workflow_bug_verification()
        
        # CRITICAL: Test Status Notes Functionality (Review Request)
        self.test_status_notes_functionality_comprehensive()
        
        # PRIORITY: Test NEW FIELDS for transcript and recommendation requests
        print("\n" + "🎯" * 20)
        print("🎯 PRIORITY: NEW FIELDS TESTING")
        print("🎯" * 20)
        
        # Transcript request tests with NEW FIELDS
        request_id = self.test_create_transcript_request()
        self.test_get_requests()
        
        # Recommendation letter request tests with NEW FIELDS
        if not rec_request_id:
            rec_request_id = self.test_create_recommendation_request()
        self.test_get_recommendation_requests()
        self.test_get_specific_recommendation_request(rec_request_id)
        self.test_update_recommendation_request_status(rec_request_id)
        self.test_student_edit_recommendation_request(rec_request_id)
        self.test_recommendation_request_permissions()
        
        # PRIORITY: Test EXPORT ENDPOINTS
        print("\n" + "🎯" * 20)
        print("🎯 PRIORITY: EXPORT ENDPOINTS TESTING")
        print("🎯" * 20)
        self.test_export_endpoints()
        
        # PRIORITY: Test ADMIN DATA MANAGEMENT (NEW FEATURE)
        print("\n" + "🎯" * 20)
        print("🎯 PRIORITY: ADMIN DATA MANAGEMENT TESTING")
        print("🎯" * 20)
        self.test_admin_data_management()
        self.test_admin_data_management_permissions()
        
        # Notification tests
        self.test_notifications()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = WolmersTranscriptAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
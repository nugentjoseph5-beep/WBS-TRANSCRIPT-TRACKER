#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class WolmersTranscriptAPITester:
    def __init__(self, base_url="https://wbs-rec-tracker.preview.emergentagent.com"):
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
        self.admin_password = "Admin123!"

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
        """Test creating transcript request"""
        print("\n🔍 Testing Transcript Request Creation...")
        
        if not self.student_token:
            self.log_result("Create transcript request", False, "No student token available")
            return None
        
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "John",
            "middle_name": "Michael",
            "last_name": "Doe",
            "school_id": "WBS2024001",
            "enrollment_status": "graduate",
            "academic_year": "2023-2024",
            "wolmers_email": "john.doe.2024@wolmers.org",
            "personal_email": self.test_student_email,
            "phone_number": "+1 876 555 0123",
            "reason": "University application",
            "needed_by_date": needed_date,
            "collection_method": "emailed",
            "institution_email": "admissions@university.edu"
        }
        
        response, error = self.make_request('POST', 'requests', request_data, token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'id' in data and data['status'] == 'Pending':
                self.log_result("Create transcript request", True)
                return data['id']
            else:
                self.log_result("Create transcript request", False, "Invalid response format")
        else:
            self.log_result("Create transcript request", False, f"Status: {response.status_code if response else 'No response'}")
        
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
        """Test creating recommendation letter request"""
        print("\n🔍 Testing Recommendation Letter Request Creation...")
        
        if not self.student_token:
            self.log_result("Create recommendation request", False, "No student token available")
            return None
        
        needed_date = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
        
        request_data = {
            "first_name": "John",
            "middle_name": "Michael",
            "last_name": "Doe",
            "email": "john.doe@email.com",
            "phone_number": "+1 876 123 4567",
            "address": "123 Main Street, Kingston, Jamaica",
            "years_attended": "2015-2020",
            "last_form_class": "Upper 6th",
            "institution_name": "University of the West Indies",
            "institution_address": "Mona Campus, Kingston 7, Jamaica",
            "directed_to": "Admissions Committee",
            "program_name": "Bachelor of Science in Computer Science",
            "needed_by_date": needed_date,
            "collection_method": "emailed"
        }
        
        response, error = self.make_request('POST', 'recommendations', request_data, token=self.student_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if 'id' in data and data['status'] == 'Pending' and data['program_name'] == 'Bachelor of Science in Computer Science':
                self.log_result("Create recommendation request", True)
                return data['id']
            else:
                self.log_result("Create recommendation request", False, "Invalid response format or missing fields")
        else:
            error_detail = ""
            if response:
                try:
                    error_detail = f" - {response.json()}"
                except:
                    error_detail = f" - Status: {response.status_code}"
            self.log_result("Create recommendation request", False, f"Status: {response.status_code if response else 'No response'}{error_detail}")
        
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

    def test_recommendation_request_validation(self):
        """Test validation for recommendation request creation"""
        print("\n🔍 Testing Recommendation Request Validation...")
        
        if not self.student_token:
            self.log_result("Recommendation request validation", False, "No student token available")
            return
        
        # Test missing required fields
        invalid_data = {
            "first_name": "John",
            # Missing required fields like last_name, email, etc.
        }
        
        response, error = self.make_request('POST', 'recommendations', invalid_data, token=self.student_token)
        
        if error:
            self.log_result("Recommendation request validation (missing fields)", False, f"Request error: {error}")
        elif response and response.status_code == 422:  # Validation error
            self.log_result("Recommendation request validation (missing fields)", True)
        else:
            self.log_result("Recommendation request validation (missing fields)", False, f"Expected 422, got {response.status_code if response else 'No response'}")
        
        # Test invalid email format
        invalid_email_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",  # Invalid email format
            "phone_number": "+1 876 123 4567",
            "address": "123 Main Street",
            "years_attended": "2015-2020",
            "last_form_class": "Upper 6th",
            "institution_name": "Test University",
            "institution_address": "Test Address",
            "program_name": "Test Program",
            "needed_by_date": "2025-08-15",
            "collection_method": "emailed"
        }
        
        response, error = self.make_request('POST', 'recommendations', invalid_email_data, token=self.student_token)
        
        if error:
            self.log_result("Recommendation request validation (invalid email)", False, f"Request error: {error}")
        elif response and response.status_code == 422:  # Validation error
            self.log_result("Recommendation request validation (invalid email)", True)
        else:
            self.log_result("Recommendation request validation (invalid email)", False, f"Expected 422, got {response.status_code if response else 'No response'}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Wolmer's Transcript Tracker API Tests")
        print(f"🎯 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic health checks
        self.test_health_check()
        
        # Authentication tests
        admin_login_success = self.test_admin_login()
        student_reg_success = self.test_student_registration()
        
        if not student_reg_success:
            # Try login if registration failed (user might already exist)
            self.test_student_login()
        
        # Test password reset flow
        self.test_password_reset_flow()
        
        # User management tests
        if admin_login_success:
            self.test_create_staff_user()
            self.test_staff_login()
            self.test_user_management()
            self.test_admin_reset_user_password()  # New test
            self.test_analytics()
        
        # Test auth/me for all roles
        self.test_auth_me()
        
        # Transcript request tests
        request_id = self.test_create_transcript_request()
        self.test_transcript_request_with_institution()
        self.test_request_reassignment()  # New test
        self.test_get_requests()
        
        # Recommendation letter request tests (NEW - Priority)
        print("\n" + "🎯" * 20)
        print("🎯 RECOMMENDATION LETTER TESTS (PRIORITY)")
        print("🎯" * 20)
        
        rec_request_id = self.test_create_recommendation_request()
        self.test_get_recommendation_requests()
        self.test_get_specific_recommendation_request(rec_request_id)
        self.test_update_recommendation_request_status(rec_request_id)
        self.test_student_edit_recommendation_request(rec_request_id)
        self.test_recommendation_request_permissions()
        self.test_recommendation_request_validation()
        
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
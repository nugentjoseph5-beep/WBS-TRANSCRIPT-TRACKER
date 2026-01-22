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

    def test_admin_login(self):
        """Test admin login with specific credentials"""
        print("\n🔍 Testing Admin Login...")
        
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

    def test_staff_login(self):
        """Test staff login with specific credentials"""
        print("\n🔍 Testing Staff Login...")
        
        response, error = self.make_request('POST', 'auth/login', {
            "email": self.staff_email,
            "password": self.staff_password
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

    def test_student_login(self):
        """Test student login with specific credentials"""
        print("\n🔍 Testing Student Login...")
        
        response, error = self.make_request('POST', 'auth/login', {
            "email": self.student_email,
            "password": self.student_password
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

    def test_staff_dashboard_apis(self):
        """Test APIs that support staff dashboard functionality"""
        print("\n🔍 Testing Staff Dashboard APIs...")
        
        if not self.staff_token:
            self.log_result("Staff dashboard APIs", False, "No staff token available")
            return
        
        # Test getting transcript requests for staff
        response, error = self.make_request('GET', 'requests/all', token=self.staff_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Staff get transcript requests", True)
            else:
                self.log_result("Staff get transcript requests", False, "Response is not a list")
        else:
            self.log_result("Staff get transcript requests", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test getting recommendation requests for staff
        response, error = self.make_request('GET', 'recommendations/all', token=self.staff_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Staff get recommendation requests", True)
            else:
                self.log_result("Staff get recommendation requests", False, "Response is not a list")
        else:
            self.log_result("Staff get recommendation requests", False, f"Status: {response.status_code if response else 'No response'}")

    def test_export_functionality(self):
        """Test export functionality for staff dashboard"""
        print("\n🔍 Testing Export Functionality...")
        
        if not self.staff_token:
            self.log_result("Export functionality", False, "No staff token available")
            return
        
        # Test transcript export endpoints
        formats = ['xlsx', 'pdf', 'docx']
        for format_type in formats:
            response, error = self.make_request('GET', f'export/transcripts/{format_type}', token=self.staff_token)
            
            if response and response.status_code == 200:
                # Check content type headers
                content_type = response.headers.get('content-type', '').lower()
                expected_types = {
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'pdf': 'application/pdf',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }
                
                if expected_types[format_type] in content_type:
                    self.log_result(f"Staff export transcripts {format_type.upper()}", True)
                else:
                    self.log_result(f"Staff export transcripts {format_type.upper()}", False, f"Wrong content type: {content_type}")
            else:
                self.log_result(f"Staff export transcripts {format_type.upper()}", False, f"Status: {response.status_code if response else 'No response'}")
        
        # Test recommendation export endpoints
        for format_type in formats:
            response, error = self.make_request('GET', f'export/recommendations/{format_type}', token=self.staff_token)
            
            if response and response.status_code == 200:
                # Check content type headers
                content_type = response.headers.get('content-type', '').lower()
                expected_types = {
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'pdf': 'application/pdf',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }
                
                if expected_types[format_type] in content_type:
                    self.log_result(f"Staff export recommendations {format_type.upper()}", True)
                else:
                    self.log_result(f"Staff export recommendations {format_type.upper()}", False, f"Wrong content type: {content_type}")
            else:
                self.log_result(f"Staff export recommendations {format_type.upper()}", False, f"Status: {response.status_code if response else 'No response'}")

    def test_admin_dashboard_analytics(self):
        """Test admin dashboard analytics endpoints"""
        print("\n🔍 Testing Admin Dashboard Analytics...")
        
        if not self.admin_token:
            self.log_result("Admin dashboard analytics", False, "No admin token available")
            return
        
        response, error = self.make_request('GET', 'analytics', token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            
            # Check for required fields for charts
            required_fields = [
                'total_requests', 'pending_requests', 'completed_requests', 'rejected_requests',
                'total_recommendation_requests', 'pending_recommendation_requests', 
                'completed_recommendation_requests', 'overdue_requests', 'overdue_recommendation_requests',
                'requests_by_enrollment', 'staff_workload', 'requests_by_month'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if not missing_fields:
                self.log_result("Admin analytics - all required fields present", True)
                
                # Test specific chart data
                if isinstance(data.get('requests_by_enrollment'), list):
                    self.log_result("Admin analytics - enrollment status chart data", True)
                else:
                    self.log_result("Admin analytics - enrollment status chart data", False, "requests_by_enrollment is not a list")
                
                if isinstance(data.get('staff_workload'), list):
                    self.log_result("Admin analytics - staff workload chart data", True)
                else:
                    self.log_result("Admin analytics - staff workload chart data", False, "staff_workload is not a list")
                
                if isinstance(data.get('requests_by_month'), list):
                    self.log_result("Admin analytics - monthly requests chart data", True)
                else:
                    self.log_result("Admin analytics - monthly requests chart data", False, "requests_by_month is not a list")
                
            else:
                self.log_result("Admin analytics - all required fields present", False, f"Missing fields: {missing_fields}")
        else:
            self.log_result("Admin analytics - all required fields present", False, f"Status: {response.status_code if response else 'No response'}")

    def test_recommendation_workflow_end_to_end(self):
        """Test recommendation workflow end-to-end"""
        print("\n🔍 Testing Recommendation Workflow End-to-End...")
        
        if not self.admin_token or not self.staff_token or not self.student_token:
            self.log_result("Recommendation workflow end-to-end", False, "Missing required tokens")
            return
        
        # Step 1: Create a recommendation request as student
        needed_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        request_data = {
            "first_name": "Test",
            "middle_name": "Workflow",
            "last_name": "Student",
            "email": "test.workflow@email.com",
            "phone_number": "+1 876 555 9999",
            "address": "123 Test Street, Kingston, Jamaica",
            "years_attended": [{"from_year": "2018", "to_year": "2023"}],
            "last_form_class": "Upper 6th",
            "co_curricular_activities": "Test activities",
            "institution_name": "Test University",
            "institution_address": "Test Address",
            "directed_to": "Admissions Office",
            "program_name": "Test Program",
            "needed_by_date": needed_date,
            "collection_method": "pickup"
        }
        
        response, error = self.make_request('POST', 'recommendations', request_data, token=self.student_token)
        
        if not response or response.status_code != 200:
            self.log_result("Recommendation workflow - create request", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        request_id = response.json()['id']
        self.log_result("Recommendation workflow - create request", True)
        
        # Step 2: Admin views the recommendation request detail
        response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.admin_token)
        
        if response and response.status_code == 200:
            self.log_result("Recommendation workflow - admin view detail", True)
        else:
            self.log_result("Recommendation workflow - admin view detail", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        # Step 3: Admin assigns staff member to the request
        # First get staff members
        staff_response, _ = self.make_request('GET', 'admin/staff', token=self.admin_token)
        if not staff_response or staff_response.status_code != 200:
            self.log_result("Recommendation workflow - get staff members", False, "Could not get staff members")
            return
        
        staff_members = staff_response.json()
        if not staff_members:
            self.log_result("Recommendation workflow - assign staff", False, "No staff members available")
            return
        
        staff_id = staff_members[0]['id']
        
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "assigned_staff_id": staff_id
        }, token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get('assigned_staff_id') == staff_id:
                self.log_result("Recommendation workflow - assign staff", True)
            else:
                self.log_result("Recommendation workflow - assign staff", False, "Staff not assigned properly")
        else:
            self.log_result("Recommendation workflow - assign staff", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        # Step 4: Staff views the assigned recommendation detail
        response, error = self.make_request('GET', f'recommendations/{request_id}', token=self.staff_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get('assigned_staff_id') == staff_id:
                self.log_result("Recommendation workflow - staff view assigned detail", True)
            else:
                self.log_result("Recommendation workflow - staff view assigned detail", False, "Staff assignment not reflected")
        else:
            self.log_result("Recommendation workflow - staff view assigned detail", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        # Step 5: Staff updates the status of the recommendation
        response, error = self.make_request('PATCH', f'recommendations/{request_id}', {
            "status": "In Progress"
        }, token=self.staff_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get('status') == 'In Progress':
                self.log_result("Recommendation workflow - staff update status", True)
            else:
                self.log_result("Recommendation workflow - staff update status", False, "Status not updated properly")
        else:
            self.log_result("Recommendation workflow - staff update status", False, f"Status: {response.status_code if response else 'No response'}")

    def test_clickable_stats_functionality(self):
        """Test that the backend supports filtering for clickable stats tiles"""
        print("\n🔍 Testing Backend Support for Clickable Stats Filtering...")
        
        if not self.staff_token:
            self.log_result("Clickable stats backend support", False, "No staff token available")
            return
        
        # Test that we can get all requests (for "Total" tile)
        response, error = self.make_request('GET', 'requests/all', token=self.staff_token)
        if response and response.status_code == 200:
            all_requests = response.json()
            self.log_result("Backend supports 'all' filter for transcripts", True)
        else:
            self.log_result("Backend supports 'all' filter for transcripts", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        # Test that we can get all recommendation requests (for "Total" tile)
        response, error = self.make_request('GET', 'recommendations/all', token=self.staff_token)
        if response and response.status_code == 200:
            all_recommendations = response.json()
            self.log_result("Backend supports 'all' filter for recommendations", True)
        else:
            self.log_result("Backend supports 'all' filter for recommendations", False, f"Status: {response.status_code if response else 'No response'}")
            return
        
        # Verify that the data includes status information for filtering
        if all_requests and len(all_requests) > 0:
            if 'status' in all_requests[0]:
                self.log_result("Transcript requests include status for filtering", True)
            else:
                self.log_result("Transcript requests include status for filtering", False, "Status field missing")
        else:
            self.log_result("Transcript requests include status for filtering", True, "No requests to check (acceptable)")
        
        if all_recommendations and len(all_recommendations) > 0:
            if 'status' in all_recommendations[0]:
                self.log_result("Recommendation requests include status for filtering", True)
            else:
                self.log_result("Recommendation requests include status for filtering", False, "Status field missing")
        else:
            self.log_result("Recommendation requests include status for filtering", True, "No recommendations to check (acceptable)")

    def run_review_tests(self):
        """Run all tests for the review request features"""
        print("🚀 Starting Review Request Feature Tests")
        print(f"🎯 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Authentication tests
        print("\n" + "🔐" * 20)
        print("🔐 AUTHENTICATION TESTS")
        print("🔐" * 20)
        admin_success = self.test_admin_login()
        staff_success = self.test_staff_login()
        student_success = self.test_student_login()
        
        if not admin_success or not staff_success or not student_success:
            print("\n⚠️ Some authentication tests failed. Continuing with available tokens...")
        
        # Staff Dashboard Tests
        print("\n" + "👨‍💼" * 20)
        print("👨‍💼 STAFF DASHBOARD TESTS")
        print("👨‍💼" * 20)
        self.test_staff_dashboard_apis()
        self.test_clickable_stats_functionality()
        
        # Export Functionality Tests
        print("\n" + "📊" * 20)
        print("📊 EXPORT FUNCTIONALITY TESTS")
        print("📊" * 20)
        self.test_export_functionality()
        
        # Admin Dashboard Tests
        print("\n" + "👑" * 20)
        print("👑 ADMIN DASHBOARD TESTS")
        print("👑" * 20)
        self.test_admin_dashboard_analytics()
        
        # Critical Bug Verification
        print("\n" + "🐛" * 20)
        print("🐛 CRITICAL BUG VERIFICATION")
        print("🐛" * 20)
        self.test_recommendation_workflow_end_to_end()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Review Request Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All review request tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = ReviewRequestTester()
    return tester.run_review_tests()

if __name__ == "__main__":
    sys.exit(main())
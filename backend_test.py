import requests
import sys
import json
from datetime import datetime
import uuid

class WBSTranscriptTrackerTester:
    def __init__(self, base_url="https://transcript-saver-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.admin_token = None
        self.student_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_result(self, test_name, success, response=None, error=None):
        """Log test results with detailed information"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}")
            if error:
                print(f"   Error: {error}")
            if response and hasattr(response, 'status_code'):
                print(f"   Status: {response.status_code}")
                try:
                    if response.text:
                        print(f"   Response: {response.text[:200]}")
                except:
                    pass
            self.failed_tests.append(test_name)
        print()

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            result_data = {}
            try:
                result_data = response.json() if response.text else {}
            except:
                pass

            self.log_result(name, success, response)
            return success, result_data

        except Exception as e:
            self.log_result(name, False, error=str(e))
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        print("🔍 Testing API Health Check...")
        success, _ = self.run_test(
            "API Health Check",
            "GET",
            f"{self.base_url}/",  # Test root endpoint
            200
        )
        
        # Also test if API endpoint responds
        success2, _ = self.run_test(
            "API Endpoint Check",
            "GET",
            "auth/microsoft/config",  # Simple GET endpoint
            200
        )
        
        return success or success2

    def test_admin_login(self):
        """Test admin login with default credentials"""
        print("🔍 Testing Admin Login...")
        admin_data = {
            "email": "admin@wolmers.org",
            "password": "Admin123!"
        }
        
        success, response_data = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            admin_data
        )
        
        if success and 'access_token' in response_data:
            self.admin_token = response_data['access_token']
            self.token = self.admin_token  # Use admin token for subsequent tests
            print(f"   Admin user: {response_data.get('user', {}).get('full_name', 'Unknown')}")
        
        return success

    def test_student_registration(self):
        """Test student registration"""
        print("🔍 Testing Student Registration...")
        
        # Create unique test student
        timestamp = datetime.now().strftime("%H%M%S")
        student_data = {
            "email": f"test.student.{timestamp}@example.com",
            "full_name": f"Test Student {timestamp}",
            "password": "TestPass123!",
            "role": "student"
        }
        
        success, response_data = self.run_test(
            "Student Registration",
            "POST",
            "auth/register",
            200,
            student_data
        )
        
        if success and 'access_token' in response_data:
            self.student_user = response_data['user']
            print(f"   Created student: {response_data.get('user', {}).get('full_name', 'Unknown')}")
        
        return success

    def test_microsoft_config(self):
        """Test Microsoft OAuth configuration"""
        print("🔍 Testing Microsoft OAuth Config...")
        success, response_data = self.run_test(
            "Microsoft OAuth Config",
            "GET",
            "auth/microsoft/config",
            200
        )
        
        if success:
            print(f"   Client ID configured: {'Yes' if response_data.get('client_id') else 'No'}")
            print(f"   Google Form URL: {response_data.get('google_form_url', 'Not set')}")
        
        return success

    def test_auth_me(self):
        """Test auth/me endpoint"""
        print("🔍 Testing Auth Me Endpoint...")
        success, response_data = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        
        if success:
            print(f"   Current user: {response_data.get('full_name', 'Unknown')}")
            print(f"   Role: {response_data.get('role', 'Unknown')}")
        
        return success

    def test_transcript_request_endpoints(self):
        """Test transcript request endpoints"""
        print("🔍 Testing Transcript Request Endpoints...")
        
        # Test get all requests (should be empty or populated)
        success1, requests_data = self.run_test(
            "Get All Transcript Requests",
            "GET",
            "requests/all",
            200
        )
        
        if success1:
            print(f"   Found {len(requests_data)} transcript requests")

        # Test creating a transcript request (as admin)
        transcript_data = {
            "first_name": "John",
            "middle_name": "Test",
            "last_name": "Doe",
            "date_of_birth": "01/01/2000",
            "school_id": "12345",
            "enrollment_status": "graduate",
            "academic_years": [{"from_year": "2018", "to_year": "2023"}],
            "wolmers_email": "john.doe@wolmers.org",
            "personal_email": "john.doe@example.com",
            "phone_number": "876-123-4567",
            "last_form_class": "6AG1",
            "reason": "University Application",
            "other_reason": "",
            "needed_by_date": "2024-12-31",
            "collection_method": "pickup",
            "delivery_address": "",
            "institution_name": "Test University",
            "institution_address": "123 Test St",
            "institution_phone": "876-123-4567",
            "institution_email": "admissions@testuni.edu",
            "number_of_copies": 2,
            "received_transcript_before": "NO",
            "external_exams": [{"exam": "CSEC", "year": "2020"}]
        }
        
        # This might fail if admin can't create requests, that's expected
        success2, created_request = self.run_test(
            "Create Transcript Request (as Admin)",
            "POST",
            "requests",
            200,  # Might be 403 if only students can create
            transcript_data
        )
        
        return success1

    def test_recommendation_request_endpoints(self):
        """Test recommendation request endpoints"""
        print("🔍 Testing Recommendation Request Endpoints...")
        
        # Test get all recommendation requests
        success1, requests_data = self.run_test(
            "Get All Recommendation Requests",
            "GET",
            "recommendations/all",
            200
        )
        
        if success1:
            print(f"   Found {len(requests_data)} recommendation requests")

        return success1

    def test_user_management_endpoints(self):
        """Test user management endpoints (admin only)"""
        print("🔍 Testing User Management Endpoints...")
        
        # Test get all users
        success1, users_data = self.run_test(
            "Get All Users",
            "GET",
            "admin/users",
            200
        )
        
        if success1:
            print(f"   Found {len(users_data)} users")
            print(f"   User roles: {set(user.get('role') for user in users_data)}")

        # Test get staff members
        success2, staff_data = self.run_test(
            "Get Staff Members",
            "GET",
            "admin/staff",
            200
        )
        
        if success2:
            print(f"   Found {len(staff_data)} staff members")

        return success1 and success2

    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        print("🔍 Testing Analytics Endpoints...")
        
        success, analytics_data = self.run_test(
            "Get Analytics",
            "GET",
            "analytics",
            200
        )
        
        if success:
            print(f"   Total requests: {analytics_data.get('total_requests', 'N/A')}")
            print(f"   Pending requests: {analytics_data.get('pending_requests', 'N/A')}")

        return success

    def test_notification_endpoints(self):
        """Test notification endpoints"""
        print("🔍 Testing Notification Endpoints...")
        
        # Test get notifications
        success1, notifications = self.run_test(
            "Get Notifications",
            "GET",
            "notifications",
            200
        )
        
        if success1:
            print(f"   Found {len(notifications)} notifications")

        # Test get unread count
        success2, unread_data = self.run_test(
            "Get Unread Notifications Count",
            "GET",
            "notifications/unread-count",
            200
        )
        
        if success2:
            print(f"   Unread count: {unread_data.get('unread_count', 'N/A')}")

        return success1 and success2

    def run_all_tests(self):
        """Run all backend API tests"""
        print("=" * 60)
        print("🚀 STARTING WBS TRANSCRIPT TRACKER API TESTS")
        print("=" * 60)
        
        # Test basic connectivity
        if not self.test_health_check():
            print("❌ Basic connectivity failed. Stopping tests.")
            self.print_summary()
            return False
        
        # Test admin login (required for most other tests)
        if not self.test_admin_login():
            print("❌ Admin login failed. Some tests may not work properly.")
        
        # Test other endpoints
        self.test_microsoft_config()
        self.test_auth_me()
        self.test_student_registration()
        self.test_transcript_request_endpoints()
        self.test_recommendation_request_endpoints()
        self.test_user_management_endpoints()
        self.test_analytics_endpoints()
        self.test_notification_endpoints()
        
        self.print_summary()
        return self.tests_passed == self.tests_run

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test}")
        
        print("=" * 60)

def main():
    """Main test execution"""
    tester = WBSTranscriptTrackerTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
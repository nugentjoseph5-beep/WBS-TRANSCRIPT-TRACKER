#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class AdminDataManagementTester:
    def __init__(self, base_url="https://transcript-rec-app.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name} - {details}")

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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return None, f"Unsupported method: {method}"
            
            return response, None
        except Exception as e:
            return None, str(e)

    def test_admin_login(self):
        """Test admin login with specific credentials"""
        print("🔍 Testing Admin Login...")
        
        response, error = self.make_request('POST', 'auth/login', {
            "email": "admin@wolmers.org",
            "password": "Admin123!"
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

    def test_data_summary(self):
        """Test GET /api/admin/data-summary"""
        print("🔍 Testing Data Summary Endpoint...")
        
        if not self.admin_token:
            self.log_result("Data Summary", False, "No admin token available")
            return
        
        response, error = self.make_request('GET', 'admin/data-summary', token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ['users', 'transcript_requests', 'recommendation_requests', 'notifications', 'total']
            if all(field in data for field in required_fields):
                self.log_result("GET /api/admin/data-summary", True)
                print(f"   📊 Data counts: Users={data['users']}, Transcripts={data['transcript_requests']}, Recommendations={data['recommendation_requests']}, Notifications={data['notifications']}, Total={data['total']}")
                return data
            else:
                missing_fields = [field for field in required_fields if field not in data]
                self.log_result("GET /api/admin/data-summary", False, f"Missing fields: {missing_fields}")
        else:
            self.log_result("GET /api/admin/data-summary", False, f"Status: {response.status_code if response else 'No response'}")
        
        return None

    def test_export_pdf(self):
        """Test GET /api/admin/export-all-data/pdf"""
        print("🔍 Testing PDF Export Endpoint...")
        
        if not self.admin_token:
            self.log_result("PDF Export", False, "No admin token available")
            return
        
        response, error = self.make_request('GET', 'admin/export-all-data/pdf', token=self.admin_token)
        
        if response and response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            content_disposition = response.headers.get('content-disposition', '')
            
            if 'application/pdf' in content_type:
                self.log_result("GET /api/admin/export-all-data/pdf", True)
                print(f"   📄 PDF export successful")
                print(f"   📄 Content-Type: {content_type}")
                print(f"   📄 Content-Disposition: {content_disposition}")
                print(f"   📄 Content Length: {len(response.content)} bytes")
                return True
            else:
                self.log_result("GET /api/admin/export-all-data/pdf", False, f"Wrong content type: {content_type}")
        else:
            self.log_result("GET /api/admin/export-all-data/pdf", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_clear_data(self):
        """Test DELETE /api/admin/clear-all-data"""
        print("🔍 Testing Clear All Data Endpoint...")
        
        if not self.admin_token:
            self.log_result("Clear All Data", False, "No admin token available")
            return
        
        response, error = self.make_request('DELETE', 'admin/clear-all-data', token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            if ('success' in data and data['success'] == True and 
                'message' in data and 'deleted_counts' in data):
                self.log_result("DELETE /api/admin/clear-all-data", True)
                print(f"   🗑️ Clear data successful: {data['message']}")
                print(f"   🗑️ Deleted counts: {data['deleted_counts']}")
                
                # Verify admin account is preserved by trying to login again
                login_response, _ = self.make_request('POST', 'auth/login', {
                    "email": "admin@wolmers.org",
                    "password": "Admin123!"
                })
                
                if login_response and login_response.status_code == 200:
                    self.log_result("Admin Account Preserved After Clear", True)
                    self.admin_token = login_response.json()['access_token']  # Update token
                    return True
                else:
                    self.log_result("Admin Account Preserved After Clear", False, "Admin login failed after clear")
            else:
                self.log_result("DELETE /api/admin/clear-all-data", False, "Invalid response format")
        else:
            self.log_result("DELETE /api/admin/clear-all-data", False, f"Status: {response.status_code if response else 'No response'}")
        
        return False

    def test_non_admin_permissions(self):
        """Test that non-admin users cannot access admin endpoints"""
        print("🔍 Testing Non-Admin Permission Restrictions...")
        
        # Create a test student
        student_email = f"test_perm_{datetime.now().strftime('%H%M%S')}@example.com"
        
        response, error = self.make_request('POST', 'auth/register', {
            "full_name": "Test Permission Student",
            "email": student_email,
            "password": "TestPass123!",
            "role": "student"
        })
        
        if response and response.status_code == 200:
            student_token = response.json()['access_token']
            
            # Test 1: Student cannot access data summary
            response, error = self.make_request('GET', 'admin/data-summary', token=student_token)
            if response and response.status_code == 403:
                self.log_result("Non-admin denied data summary access (403)", True)
            else:
                self.log_result("Non-admin denied data summary access (403)", False, f"Expected 403, got {response.status_code if response else 'No response'}")
            
            # Test 2: Student cannot access PDF export
            response, error = self.make_request('GET', 'admin/export-all-data/pdf', token=student_token)
            if response and response.status_code == 403:
                self.log_result("Non-admin denied PDF export access (403)", True)
            else:
                self.log_result("Non-admin denied PDF export access (403)", False, f"Expected 403, got {response.status_code if response else 'No response'}")
            
            # Test 3: Student cannot clear data
            response, error = self.make_request('DELETE', 'admin/clear-all-data', token=student_token)
            if response and response.status_code == 403:
                self.log_result("Non-admin denied clear data access (403)", True)
            else:
                self.log_result("Non-admin denied clear data access (403)", False, f"Expected 403, got {response.status_code if response else 'No response'}")
        else:
            self.log_result("Non-Admin Permission Testing", False, "Could not create test student for permission testing")

    def run_tests(self):
        """Run all admin data management tests"""
        print("🚀 Testing Admin Data Management APIs")
        print(f"🎯 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Step 1: Login as admin
        if not self.test_admin_login():
            print("❌ Cannot proceed without admin login")
            return 1
        
        # Step 2: Test data summary
        initial_data = self.test_data_summary()
        
        # Step 3: Test PDF export
        self.test_export_pdf()
        
        # Step 4: Test clear data (WARNING: This will clear data!)
        self.test_clear_data()
        
        # Step 5: Verify data is cleared
        final_data = self.test_data_summary()
        if final_data and initial_data:
            if (final_data['users'] < initial_data['users'] or 
                final_data['transcript_requests'] < initial_data['transcript_requests'] or
                final_data['recommendation_requests'] < initial_data['recommendation_requests']):
                self.log_result("Data Successfully Cleared", True)
            else:
                self.log_result("Data Successfully Cleared", False, "Data counts did not decrease")
        
        # Step 6: Test permission restrictions
        self.test_non_admin_permissions()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All Admin Data Management tests passed!")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = AdminDataManagementTester()
    return tester.run_tests()

if __name__ == "__main__":
    sys.exit(main())
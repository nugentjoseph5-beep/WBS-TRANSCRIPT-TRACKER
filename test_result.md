#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Rebuild the WBS Transcript Tracker app from GitHub repo and rename it to 
  "WBS Transcript and Recommendation Tracker". Add recommendation letter tracking feature 
  where students can select between Transcript or Recommendation Letter request after login.
  
  Recommendation letter request form includes:
  1. Full name (first, middle, last)
  2. Email address
  3. Phone number
  4. Address
  5. Years attended Wolmer's Boys' School
  6. Last Form Class
  7. Institution name for recommendation
  8. Institution address
  9. Whom should the letter be directed to (optional)
  10. Program name
  11. Date needed by
  12. Collection method (pickup at school, emailed to institution)

backend:
  - task: "User authentication (register, login)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "JWT-based authentication implemented"

  - task: "Transcript request CRUD"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Transcript request endpoints working"

  - task: "Recommendation letter request CRUD"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: NA
        agent: "main"
        comment: "Newly implemented - needs testing"
      - working: true
        agent: "testing"
        comment: "✅ COMPREHENSIVE TESTING COMPLETED - All recommendation letter APIs working correctly:
        
        TESTED ENDPOINTS:
        • POST /api/recommendations - ✅ Creates recommendation requests with proper validation
        • GET /api/recommendations - ✅ Returns user-specific requests (students see own, admin sees all)
        • GET /api/recommendations/all - ✅ Admin endpoint returns all requests
        • GET /api/recommendations/{id} - ✅ Returns specific request with proper permissions
        • PATCH /api/recommendations/{id} - ✅ Updates status (admin/staff only, proper 403 for students)
        • PUT /api/recommendations/{id}/edit - ✅ Students can edit their own pending requests
        
        VALIDATION TESTED:
        • ✅ Required fields validation (422 for missing fields)
        • ✅ Email format validation (422 for invalid email)
        • ✅ Authentication required (403 for unauthenticated access)
        • ✅ Permission restrictions (403 when students try to update status)
        
        FUNCTIONALITY VERIFIED:
        • ✅ Request creation with all required fields (name, email, phone, address, years_attended, etc.)
        • ✅ Status updates by admin/staff (Pending → In Progress → Completed)
        • ✅ Staff assignment functionality
        • ✅ Student editing of own requests (only when status is Pending)
        • ✅ Timeline tracking for all changes
        • ✅ Notification system integration
        
        All core recommendation letter tracking features are fully functional and properly secured."

  - task: "Notifications system"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false

frontend:
  - task: "Landing page with updated branding"
    implemented: true
    working: NA
    file: "frontend/src/pages/LandingPage.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Service selection page (Transcript vs Recommendation)"
    implemented: true
    working: NA
    file: "frontend/src/pages/student/ServiceSelection.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Recommendation letter request form"
    implemented: true
    working: NA
    file: "frontend/src/pages/student/NewRecommendation.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Student dashboard with tabs (Transcripts/Recommendations)"
    implemented: true
    working: NA
    file: "frontend/src/pages/student/StudentDashboard.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

  - task: "Recommendation detail page"
    implemented: true
    working: NA
    file: "frontend/src/pages/student/RecommendationDetail.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Recommendation letter request CRUD"
    - "Service selection page"
    - "Recommendation letter request form"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      Implemented recommendation letter tracking feature:
      1. Backend APIs: POST/GET/PATCH /api/recommendations endpoints
      2. Frontend: Service selection page, recommendation request form, 
         recommendation detail page, updated dashboard with tabs
      3. Updated app branding to "WBS Transcript and Recommendation Tracker"
      
      Please test the new recommendation letter APIs.
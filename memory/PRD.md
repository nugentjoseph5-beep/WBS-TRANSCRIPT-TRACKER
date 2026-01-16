# Wolmer's Boys' School Transcript Tracker - PRD

## Project Overview
A comprehensive transcript request tracking system for Wolmer's Boys' School with three portals: Student, Admin, and Staff.

## User Personas
1. **Students** - Current students, graduates, and withdrawn students who need academic transcripts
2. **Staff** - School employees who process transcript requests
3. **Administrators** - System administrators who manage users and oversee operations

## Core Requirements (Static)
- JWT-based authentication with role-based access control
- Three distinct portals (Student, Admin, Staff)
- In-app notification system with email notifications
- File upload/attachment support for documents
- Analytics dashboard with charts (pie, bar, trend lines)
- Privacy enforcement (students only see their own requests)
- Status workflow: Pending → In Progress → Processing → Ready → Completed
- Reject functionality with reason tracking
- Password reset functionality

## Tech Stack
- **Backend**: FastAPI (Python) with JWT authentication
- **Frontend**: React with Tailwind CSS, Shadcn/UI components
- **Database**: MongoDB
- **Charts**: Recharts
- **Email**: Resend (MOCKED - requires API key configuration)

## What's Been Implemented (January 2025)

### Backend
- ✅ JWT authentication with bcrypt password hashing
- ✅ User registration (students only self-register)
- ✅ Admin can create staff/admin accounts
- ✅ Role-based access control (student, staff, admin)
- ✅ Transcript request CRUD operations
- ✅ Status update workflow
- ✅ File upload/download for documents
- ✅ In-app notification system
- ✅ Analytics API with aggregated data
- ✅ Default admin account seeding (admin@wolmers.org / Admin123!)
- ✅ Password reset functionality (forgot password, token verification, reset)

### Frontend - Student Portal
- ✅ Registration page with full name, email, password
- ✅ Login page with split-screen layout and "Forgot password?" link
- ✅ Dashboard with request stats and list
- ✅ **Search & Filter**: Search by name, school ID, academic year; filter by status
- ✅ New transcript request form (all required fields)
- ✅ **Institution fields mandatory**: Name, Address, Email, Phone - all required on every request
- ✅ Request detail view with timeline and institution details
- ✅ Notifications page
- ✅ **Edit Pending Requests**: Students can edit their transcript requests while status is "Pending"

### Frontend - Admin Portal
- ✅ Dashboard with analytics charts (pie, bar)
- ✅ Request management with staff assignment
- ✅ User management (create staff/admin, delete users)
- ✅ Sidebar navigation
- ✅ **Request Detail View**: Full details of any transcript request with ability to update status, reassign staff, reject requests, and upload documents
- ✅ **Notifications page**: View and manage notifications via bell icon in header

### Frontend - Staff Portal
- ✅ Dashboard with assigned requests
- ✅ Request detail with status update workflow
- ✅ Document upload functionality
- ✅ Reject request with reason
- ✅ **Notifications page**: View and manage notifications via bell icon in header
- ✅ **Institution details always visible**: Name, Address, Email, Phone shown in request detail

### Password Reset Flow
- ✅ Forgot Password page at /forgot-password
- ✅ Reset Password page at /reset-password?token=xxx
- ✅ Token verification and expiration (1 hour)
- ✅ Email notification with reset link

### Design
- ✅ Maroon (#800000) and Gold (#FFD700) color palette
- ✅ White background with colored accents
- ✅ Playfair Display (headings) + Inter (body) fonts
- ✅ School building header image
- ✅ Responsive design for mobile
- ✅ **Official Wolmer's Schools Logo**: Sun breaking through clouds crest with "Age Quod Agis" motto displayed across all pages
- ✅ **Updated School Motto**: "Age Quod Agis: Whatever you do, do it to the best of your ability"

## Prioritized Backlog

### P0 - Critical (Done)
- [x] All 3 portals functional
- [x] Authentication system
- [x] Transcript request workflow
- [x] Status tracking with timeline
- [x] Password reset functionality
- [x] Student search/filter
- [x] Institution name on request form

### P1 - High Priority
- [ ] Configure Resend API for actual email delivery
- [ ] Export analytics to PDF/CSV
- [ ] Add pagination for large request lists

### P2 - Medium Priority
- [ ] Bulk status update for admin
- [ ] Request priority/urgency levels
- [ ] Estimated completion dates
- [ ] Staff workload balancing

### P3 - Low Priority
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] SMS notifications via Twilio
- [ ] Integration with student information system

## Default Credentials
- **Admin**: admin@wolmers.org / Admin123!

## API Endpoints
### Authentication
- POST /api/auth/register - Student registration
- POST /api/auth/login - User login
- GET /api/auth/me - Get current user
- POST /api/auth/forgot-password - Request password reset
- GET /api/auth/verify-reset-token/{token} - Verify reset token
- POST /api/auth/reset-password - Reset password with token

### User Management (Admin)
- POST /api/admin/users - Create staff/admin
- GET /api/admin/users - List all users
- GET /api/admin/staff - List staff members
- DELETE /api/admin/users/{id} - Delete user

### Transcript Requests
- POST /api/requests - Create transcript request (student)
- GET /api/requests - Get user's requests (role-filtered)
- GET /api/requests/all - Get all requests (admin/staff)
- GET /api/requests/{id} - Get request details
- PATCH /api/requests/{id} - Update request status
- POST /api/requests/{id}/documents - Upload document
- GET /api/documents/{id} - Download document

### Notifications
- GET /api/notifications - Get user notifications
- GET /api/notifications/unread-count - Get unread count
- PATCH /api/notifications/{id}/read - Mark as read
- PATCH /api/notifications/read-all - Mark all as read

### Analytics
- GET /api/analytics - Get dashboard analytics (admin only)

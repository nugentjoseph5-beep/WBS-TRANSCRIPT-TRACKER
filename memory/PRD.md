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

### Frontend - Student Portal
- ✅ Registration page with full name, email, password
- ✅ Login page with split-screen layout
- ✅ Dashboard with request stats and list
- ✅ New transcript request form (all required fields)
- ✅ Request detail view with timeline
- ✅ Notifications page

### Frontend - Admin Portal
- ✅ Dashboard with analytics charts (pie, bar)
- ✅ Request management with staff assignment
- ✅ User management (create staff/admin, delete users)
- ✅ Sidebar navigation

### Frontend - Staff Portal
- ✅ Dashboard with assigned requests
- ✅ Request detail with status update workflow
- ✅ Document upload functionality
- ✅ Reject request with reason

### Design
- ✅ Maroon (#800000) and Gold (#FFD700) color palette
- ✅ White background with colored accents
- ✅ Playfair Display (headings) + Inter (body) fonts
- ✅ School building header image
- ✅ Responsive design for mobile

## Prioritized Backlog

### P0 - Critical (Done)
- [x] All 3 portals functional
- [x] Authentication system
- [x] Transcript request workflow
- [x] Status tracking with timeline

### P1 - High Priority
- [ ] Configure Resend API for actual email delivery
- [ ] Add password reset functionality
- [ ] Add request search/filter for students
- [ ] Export analytics to PDF/CSV

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
- POST /api/auth/register - Student registration
- POST /api/auth/login - User login
- GET /api/auth/me - Get current user
- POST /api/admin/users - Create staff/admin (admin only)
- GET /api/admin/users - List all users (admin only)
- DELETE /api/admin/users/{id} - Delete user (admin only)
- POST /api/requests - Create transcript request (student)
- GET /api/requests - Get user's requests (role-filtered)
- GET /api/requests/{id} - Get request details
- PATCH /api/requests/{id} - Update request status
- POST /api/requests/{id}/documents - Upload document
- GET /api/notifications - Get user notifications
- PATCH /api/notifications/{id}/read - Mark as read
- GET /api/analytics - Get dashboard analytics (admin only)

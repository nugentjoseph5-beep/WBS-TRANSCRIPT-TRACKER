# WBS Transcript & Recommendation Tracker - PRD

## Original Problem Statement
Clone the GitHub repo (https://github.com/joefrass-gif/WBS-TRANSCRIPT-and-Recommendation-Tracker) and build the app exactly as stipulated by the code.

## Project Overview
A comprehensive web application for Wolmer's Boys' School that allows students to request academic transcripts and recommendation letters, with staff/admin processing capabilities.

## Tech Stack
- **Frontend**: React 19, TailwindCSS, Radix UI components, Recharts
- **Backend**: FastAPI (Python), MongoDB
- **Authentication**: JWT tokens + Microsoft 365 OAuth for students
- **Email**: Resend API for notifications

## User Personas
1. **Students**: Request transcripts and recommendation letters, track status
2. **Staff**: Process assigned requests, upload documents
3. **Admin**: Full access - user management, analytics, request oversight

## Core Features
- Multi-role authentication (Student/Staff/Admin)
- Microsoft 365 OAuth for @wolmers.org students
- Transcript request workflow
- Recommendation letter request workflow
- Status tracking with timeline
- Document upload/download
- Email notifications
- Analytics dashboard (Admin)
- User management (Admin)

## What's Been Implemented (March 2026)
- ✅ Complete GitHub repo cloned and deployed
- ✅ Backend API with 30+ endpoints
- ✅ Frontend with all pages (Landing, Login, Register, Dashboards)
- ✅ Role-based routing and protection
- ✅ Default admin account (admin@wolmers.org / Admin123!)
- ✅ PDF export functionality
- ✅ Analytics dashboard

## Default Credentials
- **Admin**: admin@wolmers.org / Admin123!

## API Endpoints
- Auth: /api/auth/login, /api/auth/register, /api/auth/me
- Requests: /api/requests, /api/requests/{id}
- Recommendations: /api/recommendations, /api/recommendations/{id}
- Admin: /api/admin/users, /api/admin/staff
- Analytics: /api/analytics

## Next Steps
- Configure Microsoft OAuth credentials for full @wolmers.org login
- Set up Resend API key for email notifications
- Add production SSL certificates

## Backlog
- P1: Microsoft OAuth full configuration
- P2: Email notification templates
- P3: Bulk operations for admin

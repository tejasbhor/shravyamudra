from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render

INDEX_CONTENT = {
    "title": "ShravyaMudra Backend",
    "heading": "ShravyaMudra Backend is Running 🚀",
    "links": [
        {"name": "Django Admin", "url": "/admin/"},
        {"name": "Auth Login API", "url": "/api/auth/login/"},
        {"name": "Register API", "url": "/api/auth/register/"},
        {"name": "Profile API", "url": "/api/auth/me/"},
        {"name": "User Management API (DRF Browsable)", "url": "/api/auth/manage/"},
    ],
    "api_endpoints": [
        {"method": "POST", "endpoint": "/api/auth/register/", "description": "Register user"},
        {"method": "POST", "endpoint": "/api/auth/login/", "description": "Login (JWT)"},
        {"method": "GET", "endpoint": "/api/auth/me/", "description": "User profile"},
        {"method": "GET", "endpoint": "/api/auth/manage/", "description": "<b>List users (admin only)</b>"},
        {"method": "POST", "endpoint": "/api/auth/manage/", "description": "<b>Create user (admin only)</b>"},
        {"method": "GET", "endpoint": "/api/auth/manage/<id>/", "description": "<b>Retrieve user (admin only)</b>"},
        {"method": "PUT/PATCH", "endpoint": "/api/auth/manage/<id>/", "description": "<b>Update user (admin only)</b>"},
        {"method": "DELETE", "endpoint": "/api/auth/manage/<id>/", "description": "<b>Delete user (admin only)</b>"},
        {"method": "POST", "endpoint": "/api/auth/manage/<id>/promote/", "description": "<b>Promote user to admin</b>"},
        {"method": "POST", "endpoint": "/api/auth/manage/<id>/demote/", "description": "<b>Demote admin to user</b>"},
        {"method": "POST", "endpoint": "/api/auth/manage/repair_profiles/", "description": "<b>Repair missing user profiles</b>"},
    ],
    "footer": "ShravyaMudra Backend 2025",
}

def index(request):
    return render(request, 'landing.html')
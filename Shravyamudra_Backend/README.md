# ShravyaMudra Backend

This is the backend for the ShravyaMudra project, built with Django and PostgreSQL. It is designed to support all frontend features, including:
- Role-based access (User/Admin)
- User management
- Profile and extended user info
- Translation history and services
- Learning modules and progress tracking
- Notifications and admin dashboards

## Setup Instructions

1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file for environment variables (see `.env.example`).
4. Run migrations and create a superuser:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Apps Structure
- `users/` — Custom user model, roles, authentication
- `profiles/` — Extended profile info
- `translation/` — Translation requests, history
- `learning/` — Learning modules, progress
- `notifications/` — System/user notifications
- `adminpanel/` — Admin dashboards, stats, user management
- `common/` — Shared utilities, permissions

## Development Notes
- Role-based access is enforced using Django groups and custom permissions.
- The backend is designed to be iteratively developed and easily integrated with the frontend.
- Refer to the mock data in the frontend for API structure and sample responses.

---

For detailed API docs, see `docs/` (to be generated as the backend evolves).

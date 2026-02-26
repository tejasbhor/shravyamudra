## 2025-05-22 - Excessive Logging in Auth Flow
**Vulnerability:** The authentication logic in `users/views.py` was logging sensitive details about login attempts (usernames, existence of users, password validation results) to standard output.
**Learning:** Developers likely added these logs for debugging but forgot to remove them in production, leading to potential user enumeration and information leakage.
**Prevention:** Avoid using `print()` for debugging in production code. Use a logging framework with appropriate log levels (DEBUG/INFO) and ensure sensitive data is not logged at INFO level. Configure production logging to suppress DEBUG logs.

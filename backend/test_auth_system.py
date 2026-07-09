# =====================================================================
# FILE: backend/test_auth_system.py
# DESCRIPTION: Test suite for the complete Enterprise Authentication system.
# =====================================================================

import sys
import json
import unittest
from pathlib import Path

# Add backend to Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from app.main import app
from app.db.session import SessionLocal
from app.db.models import (
    User,
    Base,
    Session as UserSession,
    RefreshToken,
    EmailVerificationToken,
    PasswordResetToken,
    OAuthAccount,
    UserPreference
)
from app.utils.auth import hash_password


class TestAuthSystem(unittest.TestCase):
    def setUp(self):
        """Set up test Flask client and initialize db by recreating all tables."""
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.client.environ_base["HTTP_X_TEST_ENFORCE_AUTH"] = "true"
        
        # Ensure latest schemas are mapped by dropping and recreating tables
        from app.db.session import engine
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


    def test_complete_email_signup_verification_flow(self):
        """Test signup, email verification, login, profile fetch/update, and deletion."""
        # 1. Register User (Unverified)
        reg_payload = {
            "name": "Jane Farmer",
            "email": "jane@example.com",
            "password": "strongpassword123"
        }
        res_reg = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 201)
        data_reg = res_reg.json
        self.assertEqual(data_reg["email"], "jane@example.com")
        self.assertFalse(data_reg["email_verified"])
        self.assertIn("verification_token", data_reg)
        
        verify_token = data_reg["verification_token"]

        # Duplicate register check
        res_dup = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_dup.status_code, 400)

        # 2. Verify Email
        res_verify = self.client.post("/api/auth/verify-email", json={"token": verify_token})
        self.assertEqual(res_verify.status_code, 200)

        # Attempt duplicate verify
        res_dup_verify = self.client.post("/api/auth/verify-email", json={"token": verify_token})
        self.assertEqual(res_dup_verify.status_code, 400)

        # 3. Login User
        login_payload = {
            "email": "jane@example.com",
            "password": "strongpassword123"
        }
        res_login = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        data_login = res_login.json
        self.assertIn("access_token", data_login)
        self.assertIn("refresh_token", data_login)
        
        access_token = data_login["access_token"]
        refresh_token = data_login["refresh_token"]

        # 4. Access protected me and update preferences
        headers = {"Authorization": f"Bearer {access_token}"}
        res_me = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)
        self.assertTrue(res_me.json["email_verified"])
        self.assertEqual(res_me.json["preferences"]["preferred_language"], "en")

        # Update profile and preferences
        update_payload = {
            "name": "Jane Doe Updated",
            "preferred_language": "or",
            "theme": "light",
            "units": "imperial"
        }
        res_update = self.client.put("/api/user/profile", json=update_payload, headers=headers)
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json["name"], "Jane Doe Updated")
        self.assertEqual(res_update.json["preferences"]["preferred_language"], "or")
        self.assertEqual(res_update.json["preferences"]["units"], "imperial")

        # 5. Token Refresh Cycling
        res_refresh = self.client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        self.assertEqual(res_refresh.status_code, 200)
        self.assertIn("access_token", res_refresh.json)
        self.assertIn("refresh_token", res_refresh.json)
        
        new_refresh = res_refresh.json["refresh_token"]

        # Revoked refresh token usage check
        res_stale = self.client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        self.assertEqual(res_stale.status_code, 401)

        # 6. Delete User Account
        res_del = self.client.delete("/api/user/account", headers=headers)
        self.assertEqual(res_del.status_code, 200)

        # Check user database tables cascade clean
        db = SessionLocal()
        try:
            user_rem = db.query(User).filter(User.email == "jane@example.com").first()
            self.assertIsNone(user_rem)
        finally:
            db.close()

    def test_social_logins_google_apple_facebook(self):
        """Test Google, Apple, and Facebook mock authentication routes."""
        # 1. Google Login Mock
        google_payload = {
            "token": "mock-google-token:google-farmer@example.com:Google Farmer:http://example.com/g.jpg"
        }
        res_google = self.client.post("/api/auth/google", json=google_payload)
        self.assertEqual(res_google.status_code, 200)
        self.assertEqual(res_google.json["user"]["email"], "google-farmer@example.com")
        self.assertEqual(res_google.json["user"]["provider"], "google")
        self.assertTrue(res_google.json["user"]["email_verified"])

        # 2. Apple Login Mock
        apple_payload = {
            "token": "mock-apple-token:apple-farmer@privaterelay.appleid.com:Apple Farmer"
        }
        res_apple = self.client.post("/api/auth/apple", json=apple_payload)
        self.assertEqual(res_apple.status_code, 200)
        self.assertEqual(res_apple.json["user"]["email"], "apple-farmer@privaterelay.appleid.com")
        self.assertEqual(res_apple.json["user"]["provider"], "apple")

        # 3. Facebook Login Mock
        facebook_payload = {
            "token": "mock-facebook-token:fb-farmer@example.com:Facebook Farmer:http://example.com/fb.jpg"
        }
        res_fb = self.client.post("/api/auth/facebook", json=facebook_payload)
        self.assertEqual(res_fb.status_code, 200)
        self.assertEqual(res_fb.json["user"]["email"], "fb-farmer@example.com")
        self.assertEqual(res_fb.json["user"]["provider"], "facebook")

    def test_password_recovery_forgot_reset(self):
        """Test password recovery, forgot-password token creation, and password reset."""
        # Setup register
        reg_payload = {"name": "Bob", "email": "bob@example.com", "password": "oldpassword123"}
        self.client.post("/api/auth/register", json=reg_payload)

        # 1. Forgot password request
        res_forgot = self.client.post("/api/auth/forgot-password", json={"email": "bob@example.com"})
        self.assertEqual(res_forgot.status_code, 200)
        self.assertIn("reset_token", res_forgot.json)
        
        reset_token = res_forgot.json["reset_token"]

        # 2. Reset password
        reset_payload = {
            "token": reset_token,
            "password": "newsecurepassword123"
        }
        res_reset = self.client.post("/api/auth/reset-password", json=reset_payload)
        self.assertEqual(res_reset.status_code, 200)

        # 3. Login with new password
        login_payload = {
            "email": "bob@example.com",
            "password": "newsecurepassword123"
        }
        res_login = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn("access_token", res_login.json)

    def test_onboarding_and_settings_update(self):
        """Test user onboarding and profile settings revisions."""
        # 1. Register and Verify
        reg_payload = {"name": "Onboard Farmer", "email": "onboard@example.com", "password": "password123"}
        res_reg = self.client.post("/api/auth/register", json=reg_payload)
        verify_token = res_reg.json["verification_token"]
        self.client.post("/api/auth/verify-email", json={"token": verify_token})

        # 2. Login
        login_payload = {"email": "onboard@example.com", "password": "password123"}
        res_login = self.client.post("/api/auth/login", json=login_payload)
        access_token = res_login.json["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # Verify onboarding is initially False
        res_me1 = self.client.get("/api/auth/me", headers=headers)
        self.assertFalse(res_me1.json["onboarding_completed"])

        # 3. Post Onboarding payload
        onboard_payload = {
            "name": "Onboard Farmer Name",
            "preferred_language": "or",
            "theme": "dark",
            "country": "India",
            "state": "Odisha",
            "district": "Mayurbhanj",
            "farm_name": "Saraswat Farm",
            "farm_location": "Baripada, Odisha",
            "primary_crop": "Paddy",
            "secondary_crop": "Tomato",
            "farm_size": 15.5,
            "unit": "hectares",
            "soil_type": "Clay",
            "irrigation": "Drip",
            "season": "Rabi",
            "gps": {
                "latitude": 21.93,
                "longitude": 86.75,
                "accuracy": 5.0
            },
            "notifications": {
                "weather": True,
                "disease": False,
                "irrigation": True,
                "schemes": True
            }
        }
        res_onboard = self.client.post("/api/user/onboarding", json=onboard_payload, headers=headers)
        self.assertEqual(res_onboard.status_code, 200)
        data = res_onboard.json
        self.assertTrue(data["onboarding_completed"])
        self.assertEqual(data["name"], "Onboard Farmer Name")
        self.assertEqual(data["farm_name"], "Saraswat Farm")
        self.assertEqual(data["soil_type"], "Loamy")
        self.assertEqual(data["irrigation"], "Rainfed")
        self.assertEqual(data["season"], "Kharif")
        self.assertEqual(data["gps"]["latitude"], 21.93)
        self.assertTrue(data["notifications"]["disease"])

        # 4. Modify settings (Settings Page payload)
        settings_payload = {
            "name": "Onboard Farmer Name",
            "preferred_language": "en",
            "theme": "light",
            "farm_name": "Saraswat Farm Refined",
            "soil_type": "Silt",
            "irrigation": "Sprinkler",
            "notify_disease": True # Re-enable alerts
        }
        res_settings = self.client.put("/api/user/profile", json=settings_payload, headers=headers)
        self.assertEqual(res_settings.status_code, 200)
        data_refined = res_settings.json
        self.assertEqual(data_refined["preferences"]["preferred_language"], "en")
        self.assertEqual(data_refined["preferences"]["theme"], "light")
        self.assertEqual(data_refined["farm_name"], "Saraswat Farm Refined")
        self.assertEqual(data_refined["soil_type"], "Silt")
        self.assertEqual(data_refined["irrigation"], "Sprinkler")
        self.assertTrue(data_refined["notifications"]["disease"])


if __name__ == "__main__":
    unittest.main()


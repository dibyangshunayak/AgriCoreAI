# =====================================================================
# FILE: backend/app/routes/auth.py
# DESCRIPTION: Enterprise Authentication REST API endpoints.
# =====================================================================

import logging
from typing import Any
import uuid
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, g, make_response
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import (
    User,
    Session as UserSession,
    RefreshToken,
    EmailVerificationToken,
    PasswordResetToken,
    OAuthAccount,
    UserPreference,
    UserSetting,
    FarmProfile
)
from app.utils.auth import (
    hash_password,
    verify_password,
    generate_access_token,
    generate_refresh_token,
    decode_token,
    login_required
)
from app.services.auth_providers import AuthProviderRegistry
from app.config import settings

logger = logging.getLogger(__name__)

auth_blueprint = Blueprint("auth", __name__)
user_blueprint = Blueprint("user", __name__)

def get_db_session():
    return SessionLocal()


@auth_blueprint.route("/auth/config", methods=["GET"])
def get_auth_config():
    """Serves public client configuration for social sign-in providers."""
    return jsonify({
        "google_client_id": settings.GOOGLE_CLIENT_ID
    }), 200


@auth_blueprint.route("/auth/register", methods=["POST"])
def register():
    """Register a new user, initialize preferences, and issue verification token."""
    data = request.json or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    db: Session = get_db_session()
    try:
        # Check duplicate
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 400

        # Create user
        hashed = hash_password(password)
        new_user = User(
            name=name,
            email=email,
            password_hash=hashed,
            provider="email",
            email_verified=False
        )
        db.add(new_user)
        db.flush() # Populate user.id

        # Automatically create default UserPreference record
        user_pref = UserPreference(
            user_id=new_user.id,
            preferred_language="en",
            theme="dark",
            country="India",
            farm_location="",
            units="metric",
            ai_preferences="{}"
        )
        db.add(user_pref)

        # Create single-use EmailVerificationToken
        verification_token = f"verify-token:{uuid.uuid4().hex}"
        token_record = EmailVerificationToken(
            user_id=new_user.id,
            token=verification_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        db.add(token_record)
        db.commit()

        logger.info(f"Registered user: {email}")
        
        # Return verification_token in payload to allow easy simulation testing
        response_data = new_user.to_dict()
        response_data["verification_token"] = verification_token
        return jsonify(response_data), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Error during registration: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


@auth_blueprint.route("/auth/verify-email", methods=["POST"])
def verify_email():
    """Verify user email via single-use verification token."""
    data = request.json or {}
    token = data.get("token", "").strip()

    if not token:
        return jsonify({"error": "Verification token is required"}), 400

    db: Session = get_db_session()
    try:
        record = db.query(EmailVerificationToken).filter(EmailVerificationToken.token == token).first()
        if not record:
            return jsonify({"error": "Invalid or expired verification token"}), 400

        if record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            db.delete(record)
            db.commit()
            return jsonify({"error": "Verification token has expired"}), 400

        # Mark user as verified
        user = db.query(User).filter(User.id == record.user_id).first()
        if user:
            user.email_verified = True
            
        db.delete(record)
        db.commit()

        logger.info(f"Verified email for user: {user.email if user else 'Unknown'}")
        return jsonify({"message": "Email address verified successfully!"})

    except Exception as e:
        db.rollback()
        logger.error(f"Error verifying email: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


@auth_blueprint.route("/auth/login", methods=["POST"])
def login():
    """Log in with email/password."""
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    db: Session = get_db_session()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or user.provider != "email":
            return jsonify({"error": "Invalid email or password"}), 401

        if not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid email or password"}), 401

        user.last_login = datetime.now(timezone.utc)
        
        # Tokens
        access_token = generate_access_token(user.id)
        refresh_token = generate_refresh_token(user.id)

        # Store RefreshToken in database
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        db_refresh = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at
        )
        db.add(db_refresh)

        # Store active session details
        db_session = UserSession(
            user_id=user.id,
            device=request.headers.get("User-Agent", "Unknown"),
            ip_address=request.remote_addr
        )
        db.add(db_session)
        db.commit()

        # Build response
        response = make_response(jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }))
        
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60,
            secure=False
        )
        
        logger.info(f"User logged in: {email}")
        return response
    except Exception as e:
        db.rollback()
        logger.error(f"Error during login: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


def handle_social_login(provider_name: str, token: str) -> Any:
    """Helper implementing Strategy Pattern OAuth validation."""
    provider = AuthProviderRegistry.get_provider(provider_name)
    if not provider:
        return jsonify({"error": f"Auth provider '{provider_name}' not supported"}), 400

    try:
        identity = provider.verify_token(token)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    email = identity["email"]
    name = identity["name"]
    prov_id = identity["provider_user_id"]
    pic = identity["profile_picture"]

    db: Session = get_db_session()
    try:
        # Check OAuth mapping
        oauth_acct = db.query(OAuthAccount).filter(
            OAuthAccount.provider == provider_name,
            OAuthAccount.provider_user_id == prov_id
        ).first()

        user = None
        if oauth_acct:
            user = db.query(User).filter(User.id == oauth_acct.user_id).first()
        else:
            # Check by email
            user = db.query(User).filter(User.email == email).first()

        if not user:
            # Auto-create user
            user = User(
                name=name,
                email=email,
                profile_picture=pic,
                provider=provider_name,
                email_verified=True # Social logins are pre-verified
            )
            db.add(user)
            db.flush()

            # Initialize preferences
            user_pref = UserPreference(
                user_id=user.id,
                preferred_language="en",
                theme="dark",
                country="India",
                farm_location="",
                units="metric",
                ai_preferences="{}"
            )
            db.add(user_pref)

        # Ensure OAuth mapping exists
        if not oauth_acct:
            new_mapping = OAuthAccount(
                user_id=user.id,
                provider=provider_name,
                provider_user_id=prov_id
            )
            db.add(new_mapping)

        user.last_login = datetime.now(timezone.utc)
        if pic and not user.profile_picture:
            user.profile_picture = pic

        # Generate tokens
        access_token = generate_access_token(user.id)
        refresh_token = generate_refresh_token(user.id)

        # Store RefreshToken
        db_refresh = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.add(db_refresh)

        # Store Session
        db_session = UserSession(
            user_id=user.id,
            device=request.headers.get("User-Agent", "Unknown"),
            ip_address=request.remote_addr
        )
        db.add(db_session)
        db.commit()

        response = make_response(jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }))
        
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60,
            secure=False
        )
        
        logger.info(f"Social login successful for {provider_name}: {email}")
        return response

    except Exception as e:
        db.rollback()
        logger.error(f"Error handling social login for {provider_name}: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


@auth_blueprint.route("/auth/google", methods=["POST"])
def google():
    data = request.json or {}
    token = data.get("id_token") or data.get("token")
    if not token:
        return jsonify({"error": "Google ID token is required"}), 400
    return handle_social_login("google", token)


@auth_blueprint.route("/auth/apple", methods=["POST"])
def apple():
    data = request.json or {}
    token = data.get("id_token") or data.get("token")
    if not token:
        return jsonify({"error": "Apple ID token is required"}), 400
    return handle_social_login("apple", token)


@auth_blueprint.route("/auth/facebook", methods=["POST"])
def facebook():
    data = request.json or {}
    token = data.get("access_token") or data.get("token")
    if not token:
        return jsonify({"error": "Facebook access token is required"}), 400
    return handle_social_login("facebook", token)


@auth_blueprint.route("/auth/logout", methods=["POST"])
def logout():
    refresh_token = (request.json or {}).get("refresh_token") or request.cookies.get("refresh_token")
    
    if refresh_token:
        db: Session = get_db_session()
        try:
            db_ref = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
            if db_ref:
                db_ref.revoked = True
                db.commit()
        except Exception as e:
            logger.error(f"Error during logout token revocation: {e}")
        finally:
            db.close()

    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.delete_cookie("refresh_token")
    return response


@auth_blueprint.route("/auth/refresh", methods=["POST"])
def refresh():
    refresh_token = (request.json or {}).get("refresh_token") or request.cookies.get("refresh_token")
    
    if not refresh_token:
        return jsonify({"error": "Refresh token is missing"}), 400


    payload = decode_token(refresh_token, is_refresh=True)
    if not payload:
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    user_id = int(payload["sub"])
    db: Session = get_db_session()
    try:
        db_ref = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked == False
        ).first()

        if not db_ref:
            return jsonify({"error": "Session token has been revoked"}), 401

        if db_ref.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            db.delete(db_ref)
            db.commit()
            return jsonify({"error": "Session has expired"}), 401

        # Cycle token
        new_access_token = generate_access_token(user_id)
        new_refresh_token = generate_refresh_token(user_id)

        # Mark old revoked, save new
        db_ref.revoked = True
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        new_ref_record = RefreshToken(
            user_id=user_id,
            token=new_refresh_token,
            expires_at=expires_at
        )
        db.add(new_ref_record)
        db.commit()

        response = make_response(jsonify({
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }))
        
        response.set_cookie(
            "refresh_token",
            new_refresh_token,
            httponly=True,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60,
            secure=False
        )
        return response

    except Exception as e:
        db.rollback()
        logger.error(f"Error handling token refresh: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


@auth_blueprint.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    
    if not email:
        return jsonify({"error": "Email is required"}), 400

    db: Session = get_db_session()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Silent fallback to protect user privacy
            return jsonify({"message": "If this email is registered, a password reset link has been sent."})

        # Remove existing tokens
        db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()

        # Create PasswordResetToken
        reset_token = f"reset-token:{uuid.uuid4().hex}"
        token_record = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=2)
        )
        db.add(token_record)
        db.commit()

        logger.info(f"Password reset link generated for {email}")
        return jsonify({
            "message": "If this email is registered, a password reset link has been sent.",
            "reset_token": reset_token # Returned for ease of local validation
        })

    except Exception as e:
        db.rollback()
        logger.error(f"Error during forgot password: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


@auth_blueprint.route("/auth/reset-password", methods=["POST"])
def reset_password():
    data = request.json or {}
    token = data.get("token", "").strip()
    new_password = data.get("password", "")

    if not token or not new_password:
        return jsonify({"error": "Token and password are required"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db: Session = get_db_session()
    try:
        record = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
        if not record:
            return jsonify({"error": "Invalid or expired reset token"}), 400

        if record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            db.delete(record)
            db.commit()
            return jsonify({"error": "Reset token has expired"}), 400

        user = db.query(User).filter(User.id == record.user_id).first()
        if user:
            user.password_hash = hash_password(new_password)
            
        db.delete(record)
        db.commit()

        logger.info(f"Successfully reset password for user ID {user.id if user else 'Unknown'}")
        return jsonify({"message": "Password has been successfully updated"})

    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting password: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


@auth_blueprint.route("/auth/me", methods=["GET"])
@login_required
def me():
    db: Session = get_db_session()
    try:
        user = db.query(User).filter(User.id == g.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict())
    finally:
        db.close()


@user_blueprint.route("/user/profile", methods=["PUT"])
@login_required
def update_profile():
    """Allows updating user profile parameters, passwords, preferences, and farm details."""
    data = request.json or {}
    name = data.get("name", "").strip()
    profile_picture = data.get("profile_picture")
    password = data.get("password")
    
    # Preferences & Agricultural options
    preferred_language = data.get("preferred_language")
    theme = data.get("theme")
    country = data.get("country")
    state = data.get("state")
    district = data.get("district")
    farm_location = data.get("farm_location")
    units = data.get("units")
    soil_type = data.get("soil_type")
    irrigation = data.get("irrigation")
    season = data.get("season")
    
    # GPS elements
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    accuracy = data.get("accuracy")

    # Notifications alerts
    notify_weather = data.get("notify_weather")
    notify_disease = data.get("notify_disease")
    notify_irrigation = data.get("notify_irrigation")
    notify_schemes = data.get("notify_schemes")

    # Farm parameters
    farm_name = data.get("farm_name")
    primary_crop = data.get("primary_crop")
    secondary_crop = data.get("secondary_crop")
    farm_size = data.get("farm_size")
    unit = data.get("unit")

    db: Session = get_db_session()
    try:
        user = db.query(User).filter(User.id == g.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if name:
            user.name = name
        if profile_picture is not None:
            user.profile_picture = profile_picture

        # Password reset validation for email providers
        if password:
            if user.provider != "email":
                return jsonify({"error": "Password updates are only allowed for email accounts"}), 400
            if len(password) < 6:
                return jsonify({"error": "Password must be at least 6 characters"}), 400
            user.password_hash = hash_password(password)

        # Update UserPreference
        pref = user.preferences
        if not pref:
            pref = UserPreference(user_id=user.id)
            db.add(pref)

        if preferred_language:
            pref.preferred_language = preferred_language
        if theme:
            pref.theme = theme
        if country:
            pref.country = country
        if state is not None:
            pref.state = state
        if district is not None:
            pref.district = district
        if farm_location is not None:
            pref.farm_location = farm_location
        if units:
            pref.units = units
        if soil_type:
            pref.soil_type = soil_type
        if irrigation:
            pref.irrigation = irrigation
        if season:
            pref.season = season

        if latitude is not None:
            pref.latitude = float(latitude)
        if longitude is not None:
            pref.longitude = float(longitude)
        if accuracy is not None:
            pref.location_accuracy = float(accuracy)

        if notify_weather is not None:
            pref.notify_weather = bool(notify_weather)
        if notify_disease is not None:
            pref.notify_disease = bool(notify_disease)
        if notify_irrigation is not None:
            pref.notify_irrigation = bool(notify_irrigation)
        if notify_schemes is not None:
            pref.notify_schemes = bool(notify_schemes)

        # Update FarmProfile
        farm = db.query(FarmProfile).filter(FarmProfile.user_id == user.id).first()
        if not farm:
            farm = FarmProfile(user_id=user.id, farm_name="My Farm")
            db.add(farm)

        if farm_name:
            farm.farm_name = farm_name
        if primary_crop is not None:
            farm.primary_crop = primary_crop
        if secondary_crop is not None:
            farm.secondary_crop = secondary_crop
        if farm_size is not None:
            try:
                farm.farm_size = float(farm_size)
            except ValueError:
                pass
        if unit:
            farm.unit = unit

        db.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user profile details: {e}", exc_info=True)
        return jsonify({"error": "Failed to update profile details"}), 500
    finally:
        db.close()


@user_blueprint.route("/user/onboarding", methods=["POST"])
@login_required
def save_onboarding():
    """Ingests the complete onboarding JSON payload and activates user status."""
    data = request.json or {}
    
    db: Session = get_db_session()
    try:
        user = db.query(User).filter(User.id == g.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if "name" in data:
            user.name = data["name"].strip()
            
        user.onboarding_completed = True

        # Get or create UserPreference
        pref = user.preferences
        if not pref:
            pref = UserPreference(user_id=user.id)
            db.add(pref)

        pref.country = data.get("country", pref.country)
        pref.state = data.get("state", pref.state)
        pref.district = data.get("district", pref.district)
        pref.preferred_language = data.get("preferred_language", pref.preferred_language)
        pref.theme = data.get("theme", pref.theme)

        # Farm Location
        if "farm_location" in data:
            pref.farm_location = data["farm_location"]

        # GPS fields
        gps_data = data.get("gps") or {}
        if gps_data:
            if gps_data.get("latitude") is not None:
                pref.latitude = float(gps_data["latitude"])
            if gps_data.get("longitude") is not None:
                pref.longitude = float(gps_data["longitude"])
            if gps_data.get("accuracy") is not None:
                pref.location_accuracy = float(gps_data["accuracy"])
        else:
            if data.get("latitude") is not None:
                pref.latitude = float(data["latitude"])
            if data.get("longitude") is not None:
                pref.longitude = float(data["longitude"])
            if data.get("accuracy") is not None:
                pref.location_accuracy = float(data["accuracy"])

        # FarmProfile fields
        farm = db.query(FarmProfile).filter(FarmProfile.user_id == user.id).first()
        if not farm:
            farm = FarmProfile(user_id=user.id, farm_name="My Farm")
            db.add(farm)

        farm.farm_name = data.get("farm_name", farm.farm_name)
        farm.location = data.get("farm_location", farm.location)
        farm.primary_crop = data.get("primary_crop", farm.primary_crop)

        db.commit()
        logger.info(f"Successfully processed onboarding for: {user.email}")
        return jsonify(user.to_dict())
    except Exception as e:
        db.rollback()
        logger.error(f"Error handling onboarding save: {e}", exc_info=True)
        return jsonify({"error": "Failed to save onboarding configuration"}), 500
    finally:
        db.close()



@user_blueprint.route("/user/account", methods=["DELETE"])
@login_required
def delete_account():
    db: Session = get_db_session()
    try:
        user = db.query(User).filter(User.id == g.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        db.delete(user)
        db.commit()

        # Delete database isolated chat history, weather, etc.
        try:
            from app.services.memory_service import cleanup_user_data
            cleanup_user_data(user_id=g.user_id)
        except Exception as e:
            logger.error(f"Failed to cleanup isolated user memory: {e}")

        logger.info(f"Account permanently deleted for user: {user.email}")
        return jsonify({"message": "Account and all associated records permanently cleared."})
    except Exception as e:
        db.rollback()
        logger.error(f"Error during account deletion: {e}")
        return jsonify({"error": "Failed to delete account"}), 500
    finally:
        db.close()


@user_blueprint.route("/user/preferences", methods=["GET"])
@login_required
def get_preferences():
    """Retrieve the user's preferences database record."""
    db: Session = get_db_session()
    try:
        user = db.query(User).filter(User.id == g.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        pref = user.preferences
        if not pref:
            pref = UserPreference(user_id=user.id)
            db.add(pref)
            db.commit()
            
        return jsonify(pref.to_dict()), 200
    except Exception as e:
        logger.exception(f"Error fetching user preferences: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()


@user_blueprint.route("/user/preferences", methods=["PUT"])
@login_required
def update_preferences():
    """Dynamically update preferences attributes including theme, language, and regions."""
    data = request.json or {}
    db: Session = get_db_session()
    try:
        user = db.query(User).filter(User.id == g.user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        pref = user.preferences
        if not pref:
            pref = UserPreference(user_id=user.id)
            db.add(pref)

        # Update core preferences fields if they are explicitly sent
        if "preferred_language" in data:
            pref.preferred_language = data["preferred_language"]
        if "theme" in data:
            pref.theme = data["theme"]
        if "country" in data:
            pref.country = data["country"]
        if "state" in data:
            pref.state = data["state"]
        if "district" in data:
            pref.district = data["district"]
        if "farm_location" in data:
            pref.farm_location = data["farm_location"]
        if "units" in data:
            pref.units = data["units"]
        if "soil_type" in data:
            pref.soil_type = data["soil_type"]
        if "irrigation" in data:
            pref.irrigation = data["irrigation"]
        if "season" in data:
            pref.season = data["season"]

        if "latitude" in data:
            pref.latitude = float(data["latitude"]) if data["latitude"] is not None else None
        if "longitude" in data:
            pref.longitude = float(data["longitude"]) if data["longitude"] is not None else None
        if "accuracy" in data:
            pref.location_accuracy = float(data["accuracy"]) if data["accuracy"] is not None else None

        if "notify_weather" in data:
            pref.notify_weather = bool(data["notify_weather"])
        if "notify_disease" in data:
            pref.notify_disease = bool(data["notify_disease"])
        if "notify_irrigation" in data:
            pref.notify_irrigation = bool(data["notify_irrigation"])
        if "notify_schemes" in data:
            pref.notify_schemes = bool(data["notify_schemes"])

        db.commit()
        return jsonify(pref.to_dict()), 200
    except Exception as e:
        db.rollback()
        logger.exception(f"Error updating user preferences: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        db.close()

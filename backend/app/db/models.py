# =====================================================================
# FILE: backend/app/db/models.py
# DESCRIPTION: Expanded SQLAlchemy Database Models for Enterprise Onboarding.
# =====================================================================

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    """
    SQLAlchemy database model representing an AgriCore AI user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=True) # Nullable for OAuth users
    profile_picture = Column(String(300), nullable=True)
    provider = Column(String(20), default="email") # 'email', 'google', 'apple', 'facebook'
    email_verified = Column(Boolean, default=False)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    verification_tokens = relationship("EmailVerificationToken", back_populates="user", cascade="all, delete-orphan")
    reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    farm_profiles = relationship("FarmProfile", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSetting", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        pref = self.preferences
        farm = self.farm_profiles[0] if self.farm_profiles else None

        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "provider": self.provider,
            "email_verified": self.email_verified,
            "onboarding_completed": self.onboarding_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            
            # Expanded onboarding fields mapped for easy frontend parsing
            "country": pref.country if pref else "India",
            "state": pref.state if pref else "",
            "district": pref.district if pref else "",
            "farm_name": farm.farm_name if farm else "",
            "primary_crop": farm.primary_crop if farm else "",
            "secondary_crop": farm.secondary_crop if farm else "",
            "farm_size": farm.farm_size if farm else 0.0,
            "unit": farm.unit if farm else "hectares",
            "soil_type": pref.soil_type if pref else "Loamy",
            "irrigation": pref.irrigation if pref else "Rainfed",
            "season": pref.season if pref else "Kharif",
            "gps": {
                "latitude": pref.latitude if pref else None,
                "longitude": pref.longitude if pref else None,
                "accuracy": pref.location_accuracy if pref else None
            } if pref else {"latitude": None, "longitude": None, "accuracy": None},
            "notifications": {
                "weather": pref.notify_weather if pref else True,
                "disease": pref.notify_disease if pref else True,
                "irrigation": pref.notify_irrigation if pref else True,
                "schemes": pref.notify_schemes if pref else True
            } if pref else {"weather": True, "disease": True, "irrigation": True, "schemes": True},
            "preferences": pref.to_dict() if pref else None
        }


class Session(Base):
    """
    SQLAlchemy model tracking active user login device metadata.
    """
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device = Column(String(150), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="sessions")


class RefreshToken(Base):
    """
    SQLAlchemy model tracking refresh tokens and revocation status.
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(250), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class EmailVerificationToken(Base):
    """
    SQLAlchemy model storing single-use email verification tokens.
    """
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(150), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="verification_tokens")


class PasswordResetToken(Base):
    """
    SQLAlchemy model tracking active password reset keys.
    """
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(150), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="reset_tokens")


class OAuthAccount(Base):
    """
    SQLAlchemy model linking third-party OAuth provider details (Google, Apple, Facebook).
    """
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(20), nullable=False) # 'google', 'apple', 'facebook'
    provider_user_id = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="oauth_accounts")


class UserPreference(Base):
    """
    SQLAlchemy model representing customizable user and AI parameters.
    """
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    preferred_language = Column(String(10), default="en") # 'en', 'or', 'hi'
    theme = Column(String(15), default="dark") # 'dark', 'light'
    country = Column(String(100), default="India")
    state = Column(String(100), default="")
    district = Column(String(100), default="")
    farm_location = Column(String(250), default="")
    units = Column(String(15), default="metric") # 'metric', 'imperial'
    soil_type = Column(String(50), default="Loamy") # Dropdown
    irrigation = Column(String(50), default="Rainfed") # Dropdown
    season = Column(String(50), default="Kharif") # Dropdown
    
    # GPS Coordinate properties
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_accuracy = Column(Float, nullable=True)

    # Agronomic notification categories
    notify_weather = Column(Boolean, default=True)
    notify_disease = Column(Boolean, default=True)
    notify_irrigation = Column(Boolean, default=True)
    notify_schemes = Column(Boolean, default=True)

    ai_preferences = Column(Text, default="{}") # JSON-serialized parameters

    # Relationships
    user = relationship("User", back_populates="preferences")

    def to_dict(self) -> dict:
        return {
            "preferred_language": self.preferred_language,
            "theme": self.theme,
            "country": self.country,
            "state": self.state,
            "district": self.district,
            "farm_location": self.farm_location,
            "units": self.units,
            "soil_type": self.soil_type,
            "irrigation": self.irrigation,
            "season": self.season,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_accuracy": self.location_accuracy,
            "notify_weather": self.notify_weather,
            "notify_disease": self.notify_disease,
            "notify_irrigation": self.notify_irrigation,
            "notify_schemes": self.notify_schemes,
            "ai_preferences": self.ai_preferences
        }


class FarmProfile(Base):
    """
    SQLAlchemy model storing user-owned farms.
    """
    __tablename__ = "farm_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    farm_name = Column(String(150), nullable=False)
    location = Column(String(250), nullable=True)
    farm_size = Column(Float, default=0.0)
    unit = Column(String(15), default="hectares") # 'acres', 'hectares'
    primary_crop = Column(String(100), default="")
    secondary_crop = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="farm_profiles")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "farm_name": self.farm_name,
            "location": self.location,
            "farm_size": self.farm_size,
            "unit": self.unit,
            "primary_crop": self.primary_crop,
            "secondary_crop": self.secondary_crop
        }


class UserSetting(Base):
    """
    SQLAlchemy model storing custom key-value settings.
    """
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="settings")

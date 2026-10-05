import os
import hashlib
import bcrypt
import logging
from datetime import datetime, timezone
from typing import Optional, Generator

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext

logger = logging.getLogger("uvicorn.error")

# Database URL configuration - defaults to SQLite heatshield.db in the backend folder
DB_FILE = os.path.join(os.path.dirname(__file__), "heatshield.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")

# Handle Render / Heroku postgres:// -> postgresql:// conversion
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLAlchemy engine & session setup
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Passlib CryptContext for password hashing (pbkdf2_sha256 + bcrypt fallback)
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # either "citizen" or "authority"
    ward_or_department = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "ward_or_department": self.ward_or_department,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at),
            "is_active": self.is_active
        }


class CitizenProfile(Base):
    __tablename__ = "citizen_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    age_group = Column(String, nullable=False, default="adult")
    gender = Column(String, nullable=True, default="prefer_not_to_say")
    occupation_type = Column(String, nullable=False, default="outdoor_manual")
    health_flags = Column(Text, nullable=True, default="none")
    activity_level = Column(String, nullable=True, default="heavy_exertion")
    ward_id = Column(String, nullable=False, default="CHA_001")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age_group": self.age_group,
            "gender": self.gender,
            "occupation_type": self.occupation_type,
            "health_flags": self.health_flags.split(",") if self.health_flags else ["none"],
            "activity_level": self.activity_level,
            "ward_id": self.ward_id,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else str(self.updated_at)
        }


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """Hash password using passlib CryptContext."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hash using passlib, with legacy bcrypt fallback."""
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception:
        pass
    try:
        digest = hashlib.sha256(plain_password.encode("utf-8")).digest()
        return bcrypt.checkpw(digest, hashed_password.encode("utf-8"))
    except Exception:
        return False


def _format_user_dict(user: Optional[User]) -> Optional[dict]:
    if not user:
        return None
    return user.to_dict()


def get_citizen_profile(user_id: int) -> Optional[dict]:
    db = SessionLocal()
    try:
        prof = db.query(CitizenProfile).filter(CitizenProfile.user_id == user_id).first()
        return prof.to_dict() if prof else None
    finally:
        db.close()


def save_citizen_profile(user_id: int, age_group: str, gender: Optional[str], occupation_type: str, health_flags: list, activity_level: Optional[str], ward_id: str) -> dict:
    db = SessionLocal()
    try:
        prof = db.query(CitizenProfile).filter(CitizenProfile.user_id == user_id).first()
        h_flags_str = ",".join(health_flags) if isinstance(health_flags, list) else str(health_flags or "none")
        if not prof:
            prof = CitizenProfile(
                user_id=user_id,
                age_group=age_group,
                gender=gender or "prefer_not_to_say",
                occupation_type=occupation_type,
                health_flags=h_flags_str,
                activity_level=activity_level or "heavy_exertion",
                ward_id=ward_id,
                updated_at=datetime.now(timezone.utc)
            )
            db.add(prof)
        else:
            prof.age_group = age_group
            prof.gender = gender or "prefer_not_to_say"
            prof.occupation_type = occupation_type
            prof.health_flags = h_flags_str
            prof.activity_level = activity_level or "heavy_exertion"
            prof.ward_id = ward_id
            prof.updated_at = datetime.now(timezone.utc)
        
        # Also update ward_or_department on User record if present
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.ward_or_department = ward_id
        
        db.commit()
        db.refresh(prof)
        return prof.to_dict()
    finally:
        db.close()


def init_db():
    """Initialize database tables using SQLAlchemy and seed default authority user if missing."""
    Base.metadata.create_all(bind=engine)

    # Ensure ward_or_department column exists if SQLite table was created prior
    if DATABASE_URL.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                inspector = inspect(engine)
                columns = [col["name"] for col in inspector.get_columns("users")]
                if "ward_or_department" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN ward_or_department TEXT"))
                    conn.commit()
                if "phone" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN phone TEXT"))
                    conn.commit()
        except Exception as e:
            logger.warning(f"Column check notice: {e}")

    # Seed default authority user
    db = SessionLocal()
    try:
        default_phone = "+919876543210"
        default_email = "authority@heatshield.gov.in"
        authority_count = db.query(User).filter((User.phone == default_phone) | (User.email == default_email)).count()

        if authority_count == 0:
            default_name = "District Authority Officer"
            default_pass = "HeatShield2026!"
            hashed = hash_password(default_pass)
            
            default_user = User(
                name=default_name,
                phone=default_phone,
                email=default_email,
                password_hash=hashed,
                role="AUTHORITY",
                ward_or_department="Disaster Management Cell",
                created_at=datetime.now(timezone.utc),
                is_active=1
            )
            db.add(default_user)
            db.commit()
            logger.info(f"Initialized default authority user: {default_phone} / {default_pass}")
    except Exception as e:
        logger.error(f"Error seeding default authority user: {e}")
        db.rollback()
    finally:
        db.close()



def get_user_by_email(email: str) -> Optional[dict]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email.ilike(email.strip())).first()
        return _format_user_dict(user)
    finally:
        db.close()


def get_user_by_phone(phone: str) -> Optional[dict]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone == phone.strip()).first()
        return _format_user_dict(user)
    finally:
        db.close()


def get_user_by_id(user_id: int) -> Optional[dict]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return _format_user_dict(user)
    finally:
        db.close()


def create_user(name: str, email: str, password_hash: str, role: str, ward_or_department: Optional[str] = None) -> dict:
    db = SessionLocal()
    try:
        clean_role = role.strip().upper()
        user = User(
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=password_hash,
            role=clean_role,
            ward_or_department=ward_or_department,
            created_at=datetime.now(timezone.utc),
            is_active=1
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.to_dict()
    finally:
        db.close()


def create_user_with_phone(name: str, phone: str, password_hash: str, role: str, ward_or_department: Optional[str] = None, email: Optional[str] = None) -> dict:
    db = SessionLocal()
    try:
        clean_role = role.strip().upper()
        clean_phone = phone.strip()
        clean_email = email.strip().lower() if email else f"{clean_phone}@heatshield.local"

        user = User(
            name=name.strip(),
            phone=clean_phone,
            email=clean_email,
            password_hash=password_hash,
            role=clean_role,
            ward_or_department=ward_or_department,
            created_at=datetime.now(timezone.utc),
            is_active=1
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.to_dict()
    finally:
        db.close()


def get_all_users(role_filter: Optional[str] = None) -> list:

    db = SessionLocal()
    try:
        query = db.query(User)
        if role_filter and role_filter.strip():
            query = query.filter(User.role.ilike(role_filter.strip()))
        users = query.order_by(User.id.asc()).all()
        result = []
        for u in users:
            u_dict = u.to_dict()
            u_dict.pop("password_hash", None)
            u_dict["role"] = u_dict["role"].lower() if u_dict.get("role") else "citizen"
            result.append(u_dict)
        return result
    finally:
        db.close()


def delete_user_by_id(user_id: int) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



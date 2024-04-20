from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    company: Mapped[str] = mapped_column(String, nullable=True)

    # Relationship to link users to their search settings
    search_settings: Mapped[list["SearchSetting"]] = relationship("SearchSetting", back_populates="owner")

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


class SearchSetting(Base):
    __tablename__ = "search_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    domain_base: Mapped[str] = mapped_column(String, nullable=False, comment='Example: "reiffeisen"')
    tld: Mapped[str] = mapped_column(String, nullable=False, comment='Example: "cz"')
    additional_settings: Mapped[Optional[JSON]] = mapped_column(
        JSON, comment="To have possibility to add more than base settings if needs to be", nullable=True
    )
    logo_id: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable=True)

    owner: Mapped[User] = relationship("User", back_populates="search_settings")
    # Relationship to FlaggedData
    flagged_data = relationship("FlaggedData", back_populates="search_setting", lazy="noload")
    # Relationship to Image for the logo
    logo = relationship("Image", back_populates="logo_setting", lazy="joined")


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    origin: Mapped[str] = mapped_column(String, nullable=False, comment="scraped or logo")
    flag_id: Mapped[int] = mapped_column(ForeignKey("flagged_data.id"), nullable=True)
    hash: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String)
    local_path: Mapped[str] = mapped_column(String, nullable=True)
    format: Mapped[str] = mapped_column(String, nullable=True)
    created: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    note: Mapped[Optional[str]] = mapped_column(String)

    flagged_data = relationship("FlaggedData", foreign_keys=[flag_id], back_populates="images")
    logo_setting = relationship("SearchSetting", foreign_keys=[SearchSetting.logo_id], back_populates="logo")


class FlaggedData(Base):
    __tablename__ = "flagged_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain: Mapped[str] = mapped_column(String, nullable=False)
    search_setting_id: Mapped[int] = mapped_column(ForeignKey("search_settings.id"), nullable=False)
    algorithm: Mapped[str] = mapped_column(String, nullable=False)
    flagged_time: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    images_scraped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    suspected_logo_found: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable=True)

    last_scraped: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship to SearchSetting
    search_setting = relationship("SearchSetting", back_populates="flagged_data", lazy="noload")

    # images = relationship("Image", back_populates="flagged_data")
    images = relationship("Image", foreign_keys=[Image.flag_id], back_populates="flagged_data")
    suspected_logo = relationship("Image", foreign_keys=[suspected_logo_found], post_update=True)

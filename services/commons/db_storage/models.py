from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class FlaggedDomain(Base):
    __tablename__ = "flagged_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String, nullable=False)
    flagged_domain_base: Mapped[str] = mapped_column(String, nullable=False)
    algorithm_name: Mapped[str] = mapped_column(String, nullable=False)
    scraped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    scraped_images: Mapped[Optional[JSON]] = mapped_column(JSON)
    last_scraped: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return (
            f"FlaggedDomain(id={self.id!r}, domain={self.domain!r}, flagged_domain_base={self.flagged_domain_base!r},"
            f"algorithm_name={self.algorithm_name!r}, scraped={self.scraped!r}, "
            f"scraped_images={self.scraped_images!r}, last_scraped={self.last_scraped!r})"
        )

from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

CATEGORY_NAME_MAX_LENGTH = 30


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(CATEGORY_NAME_MAX_LENGTH))
    color: Mapped[str] = mapped_column(String(7))  # "#RRGGBB"


Index("uq_categories_name_lower", func.lower(Category.name), unique=True)

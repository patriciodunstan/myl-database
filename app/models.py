"""SQLAlchemy 2.0 ORM models for MyL database."""
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Boolean, ForeignKey, Index, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Edition(Base):
    """Edition model."""
    __tablename__ = "editions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    image: Mapped[str | None] = mapped_column(String, nullable=True)
    date_release: Mapped[str | None] = mapped_column(String, nullable=True)
    flags: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    cards: Mapped[list["Card"]] = relationship("Card", back_populates="edition")


class Race(Base):
    """Race model."""
    __tablename__ = "races"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship
    cards: Mapped[list["Card"]] = relationship("Card", back_populates="race")


class Type(Base):
    """Type model."""
    __tablename__ = "types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship
    cards: Mapped[list["Card"]] = relationship("Card", back_populates="type")


class Rarity(Base):
    """Rarity model."""
    __tablename__ = "rarities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship
    cards: Mapped[list["Card"]] = relationship("Card", back_populates="rarity")


class Card(Base):
    """Card model."""
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    edid: Mapped[str | None] = mapped_column(String, nullable=True)
    slug: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    edition_id: Mapped[int] = mapped_column(ForeignKey("editions.id"), nullable=False, index=True)
    race_id: Mapped[int | None] = mapped_column(ForeignKey("races.id"), nullable=True, index=True)
    type_id: Mapped[int | None] = mapped_column(ForeignKey("types.id"), nullable=True, index=True)
    rarity_id: Mapped[int | None] = mapped_column(ForeignKey("rarities.id"), nullable=True, index=True)
    cost: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    damage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ability: Mapped[str | None] = mapped_column(Text, nullable=True)
    flavour: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    edition: Mapped["Edition"] = relationship("Edition", back_populates="cards")
    race: Mapped["Race"] = relationship("Race", back_populates="cards")
    type: Mapped["Type"] = relationship("Type", back_populates="cards")
    rarity: Mapped["Rarity"] = relationship("Rarity", back_populates="cards")

    # Indexes
    __table_args__ = (
        Index("idx_cards_name", "name"),
        Index("idx_cards_race", "race_id"),
        Index("idx_cards_type", "type_id"),
        Index("idx_cards_edition", "edition_id"),
        Index("idx_cards_cost", "cost"),
    )


class Banlist(Base):
    """Banlist model."""
    __tablename__ = "banlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_name: Mapped[str] = mapped_column(String, nullable=False)
    edition: Mapped[str | None] = mapped_column(String, nullable=True)
    format: Mapped[str] = mapped_column(String, nullable=False, index=True)
    restriction: Mapped[str] = mapped_column(String, nullable=False)
    updated: Mapped[str] = mapped_column(String, default="2026-04-07")

    # Indexes + unique constraint for upsert
    __table_args__ = (
        Index("idx_banlist_format", "format"),
        Index("idx_banlist_card_format", "card_name", "format", unique=True),
    )


class Deck(Base):
    """Deck model."""
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement="ignore_fk")
    name: Mapped[str] = mapped_column(String, nullable=False)
    race: Mapped[str | None] = mapped_column(String, nullable=True)
    format: Mapped[str] = mapped_column(String, default="racial_edicion")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now())

    # Relationship
    deck_cards: Mapped[list["DeckCard"]] = relationship("DeckCard", back_populates="deck", cascade="all, delete-orphan")


class DeckCard(Base):
    """Deck-Card relationship model."""
    __tablename__ = "deck_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement="ignore_fk")
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), nullable=False, index=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    deck: Mapped["Deck"] = relationship("Deck", back_populates="deck_cards")
    card: Mapped["Card"] = relationship("Card")

    # Index
    __table_args__ = (
        Index("idx_deck_cards_deck", "deck_id"),
    )

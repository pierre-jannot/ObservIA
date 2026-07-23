"""
Modèles SQLAlchemy représentant les tables de la base de données.
"""
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Float,
    Date,
    UniqueConstraint,
    ForeignKey,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import relationship
from db.session import Base

class Skill(Base):
    """Table des compétences France Travail"""
    __tablename__ = "skills"

    id              = Column(Integer, primary_key=True)
    source          = Column(String, primary_key=True)
    name            = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("source", "name", name="uq_skill_source_name"),
    )

    offer_skills = relationship("OfferSkill", back_populates="skill")

class Region(Base):
    """Table des régions"""
    __tablename__ = "regions"

    id_region       = Column(String, primary_key=True)
    name_region     = Column(String, nullable=False)

    departments = relationship("Department", back_populates="region")
    sirets = relationship("Siret", back_populates="region")
    offers = relationship("Offer", back_populates="region")

class Department(Base):
    """Table des départements"""
    __tablename__ = "departments"

    id_department   = Column(String, primary_key=True)
    name_department = Column(String, nullable=False)
    id_region       = Column(String, ForeignKey("regions.id_region"), nullable=False)

    region = relationship("Region", back_populates="departments")

class Rome(Base):
    """Table des codes ROME"""
    __tablename__ = "romes"

    code_rome       = Column(String, primary_key=True)
    rome_name       = Column(String, nullable=False)

    rome_rncp_corres = relationship("RomeRncp", back_populates="rome")
    offers = relationship("Offer", back_populates="rome")

class Siret(Base):
    """Table des codes SIRET"""
    __tablename__ = "sirets"

    id_siret        = Column(BigInteger, primary_key=True)
    name            = Column(String)
    id_region       = Column(String, ForeignKey("regions.id_region"))

    region = relationship("Region", back_populates="sirets")
    formations = relationship("Formation", back_populates="siret")

class Offer(Base):
    """Table des offres d'emploi"""
    __tablename__ = "offers"

    id_offer        = Column(String, primary_key=True)
    source          = Column(String, primary_key=True)
    title           = Column(String, nullable=False)
    description     = Column(String, nullable=False)
    experience      = Column(String)
    min_daily_sal   = Column(Float)
    max_daily_sal   = Column(Float)
    min_annual_sal  = Column(Float)
    max_annual_sal  = Column(Float)
    month_dur       = Column(Integer)
    id_region       = Column(String, ForeignKey("regions.id_region"))
    pub_date        = Column(Date, nullable=False)
    rome_code       = Column(String, ForeignKey("romes.code_rome"))

    region = relationship("Region", back_populates="offers")
    rome = relationship("Rome", back_populates="offers")
    offer_skills = relationship("OfferSkill", back_populates="offer")


class OfferSkill(Base):
    """Table de jonction entre offres et compétences."""
    __tablename__ = "offer_skills"

    id_offer        = Column(String, primary_key=True)
    source          = Column(String, primary_key=True)
    id_skill        = Column(Integer, primary_key=True)
    skill_source    = Column(String, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id_offer", "source"],
            ["offers.id_offer", "offers.source"],
        ),
        ForeignKeyConstraint(
            ["id_skill", "skill_source"],
            ["skills.id", "skills.source"],
        ),
        UniqueConstraint(
            "id_offer",
            "source",
            "id_skill",
            "skill_source",
            name="uq_offer_skill",
        ),
    )

    offer = relationship("Offer", back_populates="offer_skills")
    skill = relationship("Skill", back_populates="offer_skills")

class RomeRncp(Base):
    """Table de correspondance ROME/RNCP"""
    __tablename__ = "rome_rncp_corres"

    code_rome       = Column(String, ForeignKey("romes.code_rome"), primary_key=True)
    code_rncp       = Column(String, primary_key=True)

    rome = relationship("Rome", back_populates="rome_rncp_corres")

class Formation(Base):
    """Table des formations MonCompteFormation."""
    __tablename__ = "formations"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    id_siret        = Column(BigInteger, ForeignKey("sirets.id_siret"), index=True, nullable=False)
    code_rncp       = Column(String, index=True, nullable=False)
    title           = Column(String, nullable=False)
    entries         = Column(Integer, nullable=False)
    exits_full      = Column(Integer, nullable=False)
    year_month      = Column(String, nullable=False)

    siret = relationship("Siret", back_populates="formations")

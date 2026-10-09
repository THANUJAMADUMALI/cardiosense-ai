from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    DateTime
)

from sqlalchemy.sql import func

from app.database import Base

class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )

    prediction = Column(Integer)

    risk_level = Column(String)

    confidence_score = Column(Float)

    no_risk_probability = Column(Float)

    moderate_risk_probability = Column(Float)

    high_risk_probability = Column(Float)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
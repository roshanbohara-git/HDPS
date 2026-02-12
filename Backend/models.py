from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from database import Base

class HeartDiseasePredictionDB(Base):
    __tablename__ = "heart_predictions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Input Features
    age = Column(Integer)
    sex = Column(String(10))
    chest_pain_type = Column(String(10))
    resting_bp = Column(Integer)
    cholesterol = Column(Integer)
    fasting_bs = Column(Integer)
    resting_ecg = Column(String(10))
    max_hr = Column(Integer)
    exercise_angina = Column(String(10))
    oldpeak = Column(Float)
    st_slope = Column(String(10))

    # Prediction Result
    prediction = Column(String(50))  # "Normal" or "Heart Disease"
    probability = Column(Float)      # e.g., 0.85
    created_at = Column(DateTime(timezone=True), server_default=func.now())
from pydantic import BaseModel
from typing import Optional

class HeartDiseaseInput(BaseModel):
    Age: int
    Sex: str
    ChestPainType: str
    RestingBP: int
    Cholesterol: int
    FastingBS: int
    RestingECG: str
    MaxHR: int
    ExerciseAngina: str
    Oldpeak: float
    ST_Slope: str
    
    # Optional: If you want to send the actual result from frontend (usually not needed for prediction)
    # But useful if you are storing patient history manually
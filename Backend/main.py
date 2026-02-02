from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import joblib
import pandas as pd
import numpy as np
import os
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from database import engine, Base, get_db
from model import HeartDiseasePredictionDB
from schemas import HeartDiseaseInput

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Assumes files are in the same folder as main.py
MODEL_PATH = os.path.join(BASE_DIR, "heart_disease_model.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "heart_disease_datasets.csv")

# --- GLOBAL VARIABLES ---
model = None
preprocessor = None

# --- STARTUP EVENT: LOAD MODEL & PREPARE PREPROCESSOR ---
@app.on_event("startup")
def load_artifacts():
    global model, preprocessor
    
    try:
        # 1. Load the Model
        model = joblib.load(MODEL_PATH)
        print("✅ Model loaded successfully.")

        # 2. Re-create Preprocessor (Crucial if pickle doesn't have it)
        # We assume the model was trained on the dataset provided.
        # We need to fit encoders on the original data structure.
        print("⚙️  Fitting preprocessor on dataset...")
        df = pd.read_csv(DATASET_PATH)
        
        # Define categorical and numerical columns based on your dataset
        categorical_cols = ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']
        numerical_cols = ['Age', 'RestingBP', 'Cholesterol', 'FastingBS', 'MaxHR', 'Oldpeak']
        
        # Create a transformer that matches your likely training steps
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_cols),
                ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
            ]
        )
        
        # Fit on the dataset (excluding target)
        X = df.drop(columns=['HeartDisease'])
        preprocessor.fit(X)
        print("✅ Preprocessor ready.")
        
    except Exception as e:
        print(f"❌ Critical Error loading artifacts: {e}")
        raise e

@app.post("/predict/heart")
def predict_heart(data: HeartDiseaseInput, db: Session = Depends(get_db)):
    if not model or not preprocessor:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # 1. Convert Input to DataFrame
    input_data = pd.DataFrame([data.dict()])
    
    # 2. Preprocess (Encode & Scale)
    # This converts "M", "ATA" etc. into the numbers the model expects
    try:
        processed_data = preprocessor.transform(input_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Preprocessing error: {e}")

    # 3. Predict
    prediction_idx = model.predict(processed_data)[0]
    probs = model.predict_proba(processed_data)[0]
    
    # Map result (Assuming 0=Normal, 1=Heart Disease based on your CSV)
    result_label = "Heart Disease" if prediction_idx == 1 else "Normal"
    probability_score = round(probs[prediction_idx], 2)

    # 4. Save to Database
    db_record = HeartDiseasePredictionDB(
        age=data.Age,
        sex=data.Sex,
        chest_pain_type=data.ChestPainType,
        resting_bp=data.RestingBP,
        cholesterol=data.Cholesterol,
        fasting_bs=data.FastingBS,
        resting_ecg=data.RestingECG,
        max_hr=data.MaxHR,
        exercise_angina=data.ExerciseAngina,
        oldpeak=data.Oldpeak,
        st_slope=data.ST_Slope,
        prediction=result_label,
        probability=probability_score
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "prediction": result_label,
        "probability": f"{probability_score:.1%}",
        "risk_level": "High" if result_label == "Heart Disease" else "Low"
    }
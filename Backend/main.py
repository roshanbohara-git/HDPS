from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import joblib
import pandas as pd
import os
from contextlib import asynccontextmanager
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Import your local modules
from database import engine, Base, get_db
from models import HeartDiseasePredictionDB
from schemas import HeartDiseaseInput

# 1. Create Database Tables
Base.metadata.create_all(bind=engine)

# --- GLOBAL VARIABLES ---
artifacts = {
    "model": None,
    "preprocessor": None
}

# --- PATH CONFIGURATION ---
# ⚠️ Make sure the 'saved_model' folder exists, or change this back to just the filename
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "saved_model", "heart_disease_model.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "saved_model", "heart_disease_datasets.csv")

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Starting up: Loading model and preparing preprocessor...")
    
    try:
        # A. Load the Trained Model
        if os.path.exists(MODEL_PATH):
            loaded_object = joblib.load(MODEL_PATH)
            
            if isinstance(loaded_object, dict):
                artifacts["model"] = loaded_object.get("model")
                if "preprocessor" in loaded_object:
                    artifacts["preprocessor"] = loaded_object["preprocessor"]
                    print("✅ Loaded both model and preprocessor from pickle.")
                else:
                    print("✅ Loaded model from pickle (dictionary format).")
            else:
                artifacts["model"] = loaded_object
                print(f"✅ Model loaded from: {MODEL_PATH}")
        else:
            print(f"❌ Error: Model file not found at {MODEL_PATH}")

        # B. Prepare the Preprocessor
        if artifacts["preprocessor"] is None:
            if os.path.exists(DATASET_PATH):
                print("⚙️  Fitting preprocessor on dataset...")
                df = pd.read_csv(DATASET_PATH)
                
                categorical_cols = ['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope']
                numerical_cols = ['Age', 'RestingBP', 'Cholesterol', 'FastingBS', 'MaxHR', 'Oldpeak']
                
                preprocessor = ColumnTransformer(
                    transformers=[
                        ('num', StandardScaler(), numerical_cols),
                        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
                    ]
                )
                
                X = df.drop(columns=['HeartDisease'])
                preprocessor.fit(X)
                artifacts["preprocessor"] = preprocessor
                print("✅ Preprocessor ready.")
            else:
                print(f"❌ Error: Dataset not found at {DATASET_PATH}")
        else:
            print("✅ Using preprocessor from pickle.")

    except Exception as e:
        print(f"❌ Critical Error during startup: {e}")

    yield 
    
    print("🛑 Shutting down...")
    artifacts.clear()

# 2. Initialize App
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Prediction Endpoint
@app.post("/predict/heart")
def predict_heart(data: HeartDiseaseInput, db: Session = Depends(get_db)):
    model = artifacts["model"]
    preprocessor = artifacts["preprocessor"]

    if not model or not preprocessor:
        raise HTTPException(status_code=500, detail="Server Error: Model or Preprocessor not loaded.")

    input_df = pd.DataFrame([data.dict()])
    
    try:
        processed_data = preprocessor.transform(input_df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data Processing Error: {str(e)}")

    pred_idx = model.predict(processed_data)[0]
    probs = model.predict_proba(processed_data)[0]
    
    result_label = "Heart Disease" if pred_idx == 1 else "Normal"
    probability_score = round(probs[pred_idx], 2)

    new_prediction = HeartDiseasePredictionDB(
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
    
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return {
        "prediction": result_label,
        "probability": f"{probability_score:.1%}",
        "risk_level": "High" if result_label == "Heart Disease" else "Low"
    }
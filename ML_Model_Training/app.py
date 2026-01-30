import streamlit as st
import pandas as pd
import numpy as np
import pickle

# 1. Load the Saved Model and Preprocessor
# We use @st.cache_resource to load this only once, making the app faster
@st.cache_resource
def load_model():
    with open('heart_disease_model.pkl', 'rb') as file:
        data = pickle.load(file)
    return data

data = load_model()
model = data['model']
preprocessor = data['preprocessor']

# 2. App Title and Description
st.set_page_config(page_title="Heart Disease Predictor", page_icon="❤️")
st.title("❤️ Heart Disease Prediction System")
st.markdown("Enter the patient's clinical details below to predict the risk of heart disease.")

# 3. Create the Input Form
# We organize inputs into 3 columns for a cleaner look
col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=1, max_value=120, value=50)
    sex = st.selectbox("Sex", ["M", "F"])
    chest_pain = st.selectbox("Chest Pain Type", ["ATA", "NAP", "ASY", "TA"], 
                              help="ATA: Atypical Angina, NAP: Non-Anginal Pain, ASY: Asymptomatic, TA: Typical Angina")
    resting_bp = st.number_input("Resting BP (mm Hg)", min_value=50, max_value=250, value=120)

with col2:
    cholesterol = st.number_input("Cholesterol (mm/dl)", min_value=0, max_value=600, value=200)
    if cholesterol == 0:
        st.warning("⚠️ 0 Cholesterol is medically impossible. The model will auto-correct this.")
    
    fasting_bs = st.selectbox("Fasting Blood Sugar > 120 mg/dl?", [0, 1], format_func=lambda x: "Yes (1)" if x == 1 else "No (0)")
    resting_ecg = st.selectbox("Resting ECG", ["Normal", "ST", "LVH"])
    max_hr = st.number_input("Max Heart Rate", min_value=60, max_value=220, value=150)

with col3:
    exercise_angina = st.selectbox("Exercise Induced Angina?", ["Y", "N"])
    oldpeak = st.number_input("Oldpeak (ST Depression)", min_value=-5.0, max_value=10.0, value=0.0)
    st_slope = st.selectbox("ST Slope", ["Up", "Flat", "Down"])

# 4. Prediction Logic
if st.button("Predict Risk", type="primary"):
    # Create a DataFrame from inputs (Must match the training column names exactly)
    input_data = pd.DataFrame({
        'Age': [age],
        'Sex': [sex],
        'ChestPainType': [chest_pain],
        'RestingBP': [resting_bp],
        'Cholesterol': [cholesterol],
        'FastingBS': [fasting_bs],
        'RestingECG': [resting_ecg],
        'MaxHR': [max_hr],
        'ExerciseAngina': [exercise_angina],
        'Oldpeak': [oldpeak],
        'ST_Slope': [st_slope]
    })

    # Preprocess the input (using the saved scaler/encoder)
    # Note: If cholesterol is 0, our logic in Python notebook handled it during training. 
    # Ideally, we should apply the same median replacement here if we want consistency.
    if input_data['Cholesterol'][0] == 0:
         # Using a hardcoded median approx from standard datasets if you don't have the training median saved
         # Or simply let the model handle it if 0 was used in training (which we fixed in Step 4)
         input_data['Cholesterol'] = 223 # Example Median
    
    try:
        input_processed = preprocessor.transform(input_data)
        
        # Make Prediction
        prediction = model.predict(input_processed)[0]
        probability = model.predict_proba(input_processed)[0][1]

        # 5. Display Result
        st.divider()
        if prediction == 1:
            st.error(f"🚨 **High Risk Detected**")
            st.write(f"The model predicts a **{probability:.1%}** probability of Heart Disease.")
            st.info("Recommendation: Please consult a cardiologist for further testing.")
        else:
            st.success(f"✅ **Normal**")
            st.write(f"The model predicts a low probability (**{probability:.1%}**) of Heart Disease.")
            
    except Exception as e:
        st.error(f"An error occurred during prediction: {e}")
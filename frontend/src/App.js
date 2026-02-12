import React, { useState } from "react";
import "./App.css";

function App() {
  // State matches your FastAPI Schema exactly
  const [formData, setFormData] = useState({
    Age: "",
    Sex: "M",
    ChestPainType: "ATA",
    RestingBP: "",
    Cholesterol: "",
    FastingBS: 0,
    RestingECG: "Normal",
    MaxHR: "",
    ExerciseAngina: "N",
    Oldpeak: "",
    ST_Slope: "Up",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    // Convert types to match Pydantic models (int/float)
    const payload = {
      ...formData,
      Age: parseInt(formData.Age),
      RestingBP: parseInt(formData.RestingBP),
      Cholesterol: parseInt(formData.Cholesterol),
      FastingBS: parseInt(formData.FastingBS),
      MaxHR: parseInt(formData.MaxHR),
      Oldpeak: parseFloat(formData.Oldpeak),
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/predict/heart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch prediction");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError("Error connecting to server. Is backend running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>❤️ Heart Disease Predictor</h1>
        <p>Enter patient details below for assessment</p>
      </header>

      <div className="content-wrapper">
        <form onSubmit={handleSubmit} className="form-grid">
          {/* Age */}
          <div className="input-group">
            <label>Age</label>
            <input
              type="number"
              name="Age"
              placeholder="e.g. 45"
              required
              value={formData.Age}
              onChange={handleChange}
            />
          </div>

          {/* Sex */}
          <div className="input-group">
            <label>Sex</label>
            <select name="Sex" value={formData.Sex} onChange={handleChange}>
              <option value="M">Male</option>
              <option value="F">Female</option>
            </select>
          </div>

          {/* Chest Pain Type */}
          <div className="input-group">
            <label>Chest Pain Type</label>
            <select name="ChestPainType" value={formData.ChestPainType} onChange={handleChange}>
              <option value="ATA">Atypical Angina (ATA)</option>
              <option value="NAP">Non-Anginal Pain (NAP)</option>
              <option value="ASY">Asymptomatic (ASY)</option>
              <option value="TA">Typical Angina (TA)</option>
            </select>
          </div>

          {/* Resting BP */}
          <div className="input-group">
            <label>Resting BP (mm Hg)</label>
            <input
              type="number"
              name="RestingBP"
              placeholder="e.g. 120"
              required
              value={formData.RestingBP}
              onChange={handleChange}
            />
          </div>

          {/* Cholesterol */}
          <div className="input-group">
            <label>Cholesterol (mm/dl)</label>
            <input
              type="number"
              name="Cholesterol"
              placeholder="e.g. 200"
              required
              value={formData.Cholesterol}
              onChange={handleChange}
            />
          </div>

          {/* Fasting BS */}
          <div className="input-group">
            <label>Fasting Blood Sugar > 120 mg/dl?</label>
            <select name="FastingBS" value={formData.FastingBS} onChange={handleChange}>
              <option value="0">No (0)</option>
              <option value="1">Yes (1)</option>
            </select>
          </div>

          {/* Resting ECG */}
          <div className="input-group">
            <label>Resting ECG</label>
            <select name="RestingECG" value={formData.RestingECG} onChange={handleChange}>
              <option value="Normal">Normal</option>
              <option value="ST">ST-T Wave Abnormality</option>
              <option value="LVH">Left Ventricular Hypertrophy</option>
            </select>
          </div>

          {/* Max HR */}
          <div className="input-group">
            <label>Max Heart Rate</label>
            <input
              type="number"
              name="MaxHR"
              placeholder="e.g. 150"
              required
              value={formData.MaxHR}
              onChange={handleChange}
            />
          </div>

          {/* Exercise Angina */}
          <div className="input-group">
            <label>Exercise Induced Angina?</label>
            <select name="ExerciseAngina" value={formData.ExerciseAngina} onChange={handleChange}>
              <option value="N">No</option>
              <option value="Y">Yes</option>
            </select>
          </div>

          {/* Oldpeak */}
          <div className="input-group">
            <label>Oldpeak (Depression)</label>
            <input
              type="number"
              step="0.1"
              name="Oldpeak"
              placeholder="e.g. 1.5"
              required
              value={formData.Oldpeak}
              onChange={handleChange}
            />
          </div>

          {/* ST Slope */}
          <div className="input-group">
            <label>ST Slope</label>
            <select name="ST_Slope" value={formData.ST_Slope} onChange={handleChange}>
              <option value="Up">Up</option>
              <option value="Flat">Flat</option>
              <option value="Down">Down</option>
            </select>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? "Analyzing..." : "Predict Risk"}
          </button>
        </form>

        {/* --- RESULTS SECTION --- */}
        {error && <div className="error-box">{error}</div>}

        {result && (
          <div className={`result-box ${result.prediction === "Heart Disease" ? "danger" : "safe"}`}>
            <h2>Result: {result.prediction}</h2>
            <p>Result Probability: <strong>{result.probability}</strong></p>
            <div className="badge">{result.risk_level} Risk</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
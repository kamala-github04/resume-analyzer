import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const getColor = (score) => {
    if (score > 80) return "#00f260";
    if (score > 60) return "#f9d423";
    return "#ff4b2b";
  };

  const handleSubmit = async () => {
    if (!file || !jd) {
      alert("Upload resume + enter job description");
      return;
    }

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("jd", jd);

    try {
      setLoading(true);
      const res = await axios.post("http://127.0.0.1:5000/analyze", formData);
      setResult(res.data);
    } catch (err) {
      alert("Error connecting backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>🚀 Resume Analyzer</h1>

      <div className="card">
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />

        <textarea
          placeholder="Enter Job Description..."
          value={jd}
          onChange={(e) => setJd(e.target.value)}
        />

        <button onClick={handleSubmit}>
          {loading ? "Analyzing..." : "Analyze Resume"}
        </button>
      </div>

      {result && (
        <div className="results">
          <div className="card">
            <h2>📊 ATS Score</h2>
            <div className="progress">
              <div
                className="progress-bar"
                style={{ 
                  width: `${result.score}%`,
                  background: getColor(result.score) 
                }}
              >
                {result.score}%
              </div>
            </div>
          </div>

          <div className="grid">
            <div className="card">
              <h3>🎯 Domain</h3>
              <p className="badge">{result.domain}</p>
            </div>

            <div className="card">
              <h3>📊 Skill Match</h3>
              <p>{result.skill_score}%</p>
            </div>

            <div className="card">
              <h3>📈 Similarity</h3>
              <p>{result.tfidf_score}%</p>
            </div>
          </div>

          <div className="card">
            <h3 className="missing">❌ Missing Skills</h3>
            <ul>
              {result.missing_skills.map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          </div>

          <div className="card">
            <h3>💡 Suggestions</h3>
            <ul className="suggestions">
              {result.suggestions.map((s, i) => (
                <li key={i}>✔ {s}</li>
              ))}
            </ul>
          </div>

          <h3>🧠 Detected Skills</h3>
          <div className="skills">
            {result.skills.map((s, i) => (
              <span key={i} className="skill-tag">{s}</span>
            ))}
          </div>

          <div className="card">
            <h3>🚀 Recommended Jobs</h3>
            <ul>
              {result.jobs.map((j, i) => (
                <div className="job" key={i}>
                  👉 {j[0]} ({j[1]}%)
                </div>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
// frontend/src/App.jsx
import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setReport(data);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-8">
      <h1 className="text-2xl font-bold mb-6">AI Compliance Officer</h1>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />
      <button
        onClick={handleUpload}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow-md"
      >
        Analyze Document
      </button>

      {report && (
        <div className="mt-6 p-4 bg-white rounded-lg shadow-md w-2/3">
          <h2 className="text-xl font-semibold">Compliance Report</h2>
          <p className="mt-2 text-red-600">
            Risks: {report.risks.length ? report.risks.join(", ") : "None"}
          </p>
          <p className="mt-2 text-gray-700">
            Analysis: {report.compliance_analysis}
          </p>
        </div>
      )}
    </div>
  );
}

export default App;

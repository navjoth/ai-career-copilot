import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);

  const [jobForm, setJobForm] = useState({
    title: '',
    company: '',
    location: '',
    description: '',
  });
  const [jobPostedMessage, setJobPostedMessage] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    console.log("Selected file:", file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select a resume file first.');
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/match', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMatches(response.data.matches);
    } catch (error) {
      alert('Error uploading resume or connecting to backend.');
      console.error(error);
    }
    setLoading(false);
  };

  const handleJobInputChange = (e) => {
    const { name, value } = e.target;
    setJobForm({ ...jobForm, [name]: value });
  };

  const handlePostJob = async () => {
    const { title, company, location, description } = jobForm;
    if (!title || !company || !location || !description) {
      alert("Please fill in all job fields.");
      return;
    }

    try {
      const response = await axios.post('http://127.0.0.1:8000/add_job', jobForm);
      setJobPostedMessage(response.data.message || 'Job posted successfully!');
      setJobForm({ title: '', company: '', location: '', description: '' });
    } catch (error) {
      console.error("Job post error:", error);
      alert("Failed to post job.");
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial', maxWidth: '800px', margin: 'auto' }}>
      <h1>AI Career Copilot</h1>

      {/* === Resume Upload Section === */}
      <section style={{ marginBottom: '3rem' }}>
        <h2>📄 Match Resume to Jobs</h2>
        <p>Upload your resume to get top job matches:</p>
        <input type="file" accept=".pdf" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading} style={{ marginLeft: '10px' }}>
          {loading ? 'Matching...' : 'Match Resume'}
        </button>

        <div style={{ marginTop: '2rem' }}>
          {matches.map((match, index) => (
            <div key={index} style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}>
              <h3>{match.title} at {match.company}</h3>
              <p><strong>Location:</strong> {match.location}</p>
              <p><strong>Score:</strong> {match.score.toFixed(2)}</p>
              <p><strong>Missing Skills:</strong> 
                {match.missing_skills.length > 0 
                  ? match.missing_skills.join(', ')
                  : '✅ All skills matched!'}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* === Job Posting Section === */}
      <section>
        <h2>📢 Post a New Job</h2>
        <p>Add a job to the system (for testing resume matching):</p>

        <input
          type="text"
          name="title"
          value={jobForm.title}
          onChange={handleJobInputChange}
          placeholder="Job Title"
          style={{ display: 'block', marginBottom: '10px', width: '100%' }}
        />
        <input
          type="text"
          name="company"
          value={jobForm.company}
          onChange={handleJobInputChange}
          placeholder="Company"
          style={{ display: 'block', marginBottom: '10px', width: '100%' }}
        />
        <input
          type="text"
          name="location"
          value={jobForm.location}
          onChange={handleJobInputChange}
          placeholder="Location"
          style={{ display: 'block', marginBottom: '10px', width: '100%' }}
        />
        <textarea
          name="description"
          value={jobForm.description}
          onChange={handleJobInputChange}
          placeholder="Job Description"
          rows={4}
          style={{ display: 'block', marginBottom: '10px', width: '100%' }}
        />
        <button onClick={handlePostJob}>Post Job</button>

        {jobPostedMessage && (
          <p style={{ marginTop: '10px', color: 'green' }}>{jobPostedMessage}</p>
        )}
      </section>
    </div>
  );
}

export default App;

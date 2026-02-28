// App.js
import React, { useState } from 'react';
import './App.css';

function App() {
  const [issue, setIssue] = useState('');
  const [chatLog, setChatLog] = useState([]);
  const [file, setFile] = useState(null);

  // Simulate sending input to backend agent
  const sendIssue = async () => {
    if (!issue) return;
    
    // Add user input to chat log
    setChatLog([...chatLog, { sender: 'tech', message: issue }]);

    // TODO: call your backend LLM agent
    const response = `AI recommends: Check sensor readings and capture logs.`;

    setChatLog([...chatLog, { sender: 'tech', message: issue }, { sender: 'ai', message: response }]);
    setIssue('');
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  return (
    <div className="app-container">
      <h1>TRACE – Field Technician Interface</h1>

      {/* Issue Input */}
      <div className="issue-section">
        <input
          type="text"
          placeholder="Enter fault code or issue description"
          value={issue}
          onChange={(e) => setIssue(e.target.value)}
        />
        <button onClick={sendIssue}>Send</button>
      </div>

      {/* Chatbot / Agent Responses */}
      <div className="chat-log">
        {chatLog.map((msg, idx) => (
          <div key={idx} className={msg.sender === 'tech' ? 'chat-tech' : 'chat-ai'}>
            <strong>{msg.sender === 'tech' ? 'You' : 'TRACE AI'}:</strong> {msg.message}
          </div>
        ))}
      </div>

      {/* Evidence Upload */}
      <div className="evidence-section">
        <input type="file" onChange={handleFileChange} />
        {file && <p>Selected file: {file.name}</p>}
      </div>
    </div>
  );
}

export default App;

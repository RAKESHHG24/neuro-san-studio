import { useState } from 'react';

function App() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const askAssistant = async () => {
    setLoading(true);
    const response = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();
    setAnswer(data.answer || 'No response');
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 700, margin: '40px auto', fontFamily: 'Arial, sans-serif' }}>
      <h2>Assistant UI</h2>
      <p>Type a question and send it to the FastAPI backend.</p>

      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask something"
        style={{ width: '100%', padding: 10, marginBottom: 10 }}
      />

      <button onClick={askAssistant} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </button>

      <div style={{ marginTop: 20, padding: 12, background: '#f5f5f5', borderRadius: 8 }}>
        <strong>Answer:</strong> {answer}
      </div>
    </div>
  );
}

export default App;

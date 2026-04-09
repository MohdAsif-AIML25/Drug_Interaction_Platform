import React, { useState, useEffect, useRef } from 'react';
import './index.css';

const COMMON_DRUGS = [
  "Aspirin", "Warfarin", "Amoxicillin", "Metformin", "Paracetamol", "Omeprazole", 
  "Atorvastatin", "Ibuprofen", "Lisinopril", "Metoprolol", "Amlodipine", "Alprazolam",
  "Clopidogrel", "Losartan", "Gabapentin", "Sertraline", "Furosemide", "Levothyroxine"
];

const App = () => {
  const [drugA, setDrugA] = useState('');
  const [drugB, setDrugB] = useState('');
  const [suggestionsA, setSuggestionsA] = useState([]);
  const [suggestionsB, setSuggestionsB] = useState([]);
  const [loading, setLoading] = useState(false);

  const [events, setEvents] = useState([]);
  const [analysisText, setAnalysisText] = useState('');
  const [mlResult, setMlResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [streaming, setStreaming] = useState(false);
  
  const analysisEndRef = useRef(null);

  // Load history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('drug_history');
    if (savedHistory) setHistory(JSON.parse(savedHistory));
  }, []);

  const saveToHistory = (item) => {
    const newHistory = [item, ...history.slice(0, 9)];
    setHistory(newHistory);
    localStorage.setItem('drug_history', JSON.stringify(newHistory));
  };

  const startAnalysis = async (e) => {
    if (e) e.preventDefault();
    if (!drugA || !drugB) return;

    setLoading(true);
    setStreaming(true);
    setEvents([]);
    setAnalysisText('');
    setMlResult(null);

    try {
      const response = await fetch('http://localhost:8000/analyse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ drug_a: drugA, drug_b: drugB }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop();

        for (const part of parts) {
          if (!part.trim()) continue;
          try {
            const jsonPart = JSON.parse(part);
            if (jsonPart.type === 'ml_result') {
              setMlResult(jsonPart.data);
              // Save to history when ML result arrives
              saveToHistory({
                drugA,
                drug_b: drugB,
                severity: jsonPart.data.severity,
                timestamp: new Date().toLocaleTimeString()
              });
            } else if (jsonPart.type === 'events') {
              setEvents(jsonPart.data);
            } else if (jsonPart.type === 'token') {
              setAnalysisText((prev) => prev + jsonPart.data);
            } else if (jsonPart.type === 'error') {
              setAnalysisText((prev) => prev + '\n\n**Error:** ' + jsonPart.data);
            }
          } catch (e) {
            console.error('SSE Error:', e, part);
          }
        }
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setAnalysisText('Failed to connect to the server. Check if the backend is running.');
    } finally {
      setLoading(false);
      setStreaming(false);
    }
  };

  useEffect(() => {
    analysisEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [analysisText]);

  const getSeverityClass = (sev) => {
    if (!sev) return 'badge-none';
    return `badge-${sev.toLowerCase().replace(' ', '-')}`;
  };

  const exportAsPDF = () => {
    window.print();
  };

  const handleInputChange = (val, type) => {
    if (type === 'A') {
      setDrugA(val);
      setSuggestionsA(val ? COMMON_DRUGS.filter(d => d.toLowerCase().includes(val.toLowerCase()) && d !== val) : []);
    } else {
      setDrugB(val);
      setSuggestionsB(val ? COMMON_DRUGS.filter(d => d.toLowerCase().includes(val.toLowerCase()) && d !== val) : []);
    }
  };

  return (
    <div className="layout">
      {/* Sidebar - Interaction History */}
      <aside className="sidebar">
        <h2>History</h2>
        {history.length === 0 && <p className="text-muted">No recent queries</p>}
        {history.map((item, idx) => (
          <div key={idx} className="history-item fade-in" onClick={() => {
            setDrugA(item.drugA);
            setDrugB(item.drug_b);
          }}>
            <span className="drugs">{item.drugA} + {item.drug_b}</span>
            <div className="meta">
              <span className={`severity-badge ${getSeverityClass(item.severity)}`} style={{padding: '2px 8px', fontSize: '10px', margin: 0}}>
                {item.severity}
              </span>
              <span className="text-muted">{item.timestamp}</span>
            </div>
          </div>
        ))}
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          <header>
            <h1>DrugSafe AI</h1>
            <p className="text-muted">Real-time Clinical Clinical Pharmacology Assistant</p>
          </header>

          <form onSubmit={startAnalysis} className="search-grid">
            <div className="input-wrapper">
              <input 
                type="text" placeholder="Drug A (e.g. Aspirin)" 
                value={drugA} 
                onChange={(e) => handleInputChange(e.target.value, 'A')} 
                disabled={loading}
              />
              {suggestionsA.length > 0 && (
                <div className="suggestions">
                  {suggestionsA.map(s => <div key={s} className="suggestion-item" onClick={() => { setDrugA(s); setSuggestionsA([]); }}>{s}</div>)}
                </div>
              )}
            </div>
            <div className="input-wrapper">
              <input 
                type="text" placeholder="Drug B (e.g. Warfarin)" 
                value={drugB} 
                onChange={(e) => handleInputChange(e.target.value, 'B')} 
                disabled={loading}
              />
               {suggestionsB.length > 0 && (
                <div className="suggestions">
                  {suggestionsB.map(s => <div key={s} className="suggestion-item" onClick={() => { setDrugB(s); setSuggestionsB([]); }}>{s}</div>)}
                </div>
              )}
            </div>
            <button type="submit" disabled={loading || !drugA || !drugB} className="btn-primary">
              {loading ? 'Analyzing...' : 'Analyse'}
            </button>
          </form>


          {(mlResult || analysisText) && (
            <div className="results-container fade-in">
              <div className="results-header">
                {/* Severity Card */}
                {mlResult && (
                  <div className="severity-card">
                    <span className={`severity-badge ${getSeverityClass(mlResult.severity)}`}>
                      {mlResult.severity}
                    </span>
                    <p style={{fontSize: '0.9rem', marginBottom: '0.5rem'}}>Classification Confidence</p>
                    <div className="confidence-meter">
                      <div className="confidence-fill" style={{ width: `${mlResult.confidence}%` }}></div>
                    </div>
                    <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.3rem'}}>{mlResult.confidence}%</p>
                  </div>
                )}

                {/* Info Card */}
                {mlResult && (
                  <div className="severity-card" style={{flex: 1}}>
                    <h3>Interaction Result</h3>
                    <p className="text-muted" style={{marginTop: '0.5rem'}}>
                      Analyzed pair: <strong>{drugA}</strong> and <strong>{drugB}</strong>
                    </p>
                    <button className="export-btn" onClick={exportAsPDF}>Export Report (PDF)</button>
                  </div>
                )}
              </div>

              {/* Streaming Panel */}
              <div className="streaming-panel">
                <h3>Clinical Insight</h3>
                <div className="markdown-content" style={{marginTop: '1rem'}}>
                  {analysisText}
                  {streaming && <span className="cursor"></span>}
                  {!analysisText && !streaming && "Consulting AI Pharmacist..."}
                </div>
              </div>

              {/* FDA Reports */}
              {events.length > 0 && (
                <div className="fda-list">
                  <h3>FDA Reported Incidents</h3>
                  <div style={{marginTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                    {events.map((event, idx) => (
                      <div key={idx} className="event-card">
                        <span className="severity-badge badge-none" style={{fontSize: '0.7rem'}}>{event.seriousness}</span>
                        <p style={{fontSize: '0.85rem', marginTop: '0.5rem'}}><strong>ID:</strong> {event.id}</p>
                        <p style={{fontSize: '0.85rem'}}><strong>Reactions:</strong> {event.reactions.join(', ')}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;

import React, { useState } from 'react';
import axios from 'axios';

function SimpleApp() {
  const [query, setQuery] = useState('');
  const [objectType, setObjectType] = useState('contacts');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Determine if this is a search or a query based on the input
      const isSearch = query.toLowerCase().includes('search') || 
                      query.toLowerCase().includes('find') || 
                      query.toLowerCase().includes('look for');
      
      const endpoint = isSearch ? 'search' : 'query';
      
      const response = await axios.post(`http://localhost:8000/${endpoint}`, {
        query: query,
        object_type: objectType,
        limit: 10
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setResults(response.data.data);
    } catch (err) {
      console.error('Error querying the API:', err);
      setError('Failed to get a response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setResults(null);
    setError(null);
    setQuery('');
  };

  return (
    <div className="App" style={{ 
      fontFamily: 'Arial, sans-serif',
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '20px'
    }}>
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        padding: '10px',
        backgroundColor: '#f0f0f0',
        borderRadius: '8px'
      }}>
        <h1 style={{ margin: 0 }}>HubSpot Agentic Workflow</h1>
        <button 
          onClick={clearChat}
          style={{
            backgroundColor: '#ff4d4f',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Clear Chat
        </button>
      </header>

      <div style={{ 
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gap: '20px'
      }}>
        {/* Chat Panel */}
        <div style={{
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '10px',
            borderBottom: '1px solid #e0e0e0',
            backgroundColor: '#f9f9f9',
            display: 'flex',
            justifyContent: 'space-between'
          }}>
            <h2 style={{ margin: 0 }}>HubSpot Query Assistant</h2>
            <div>
              <select 
                value={objectType} 
                onChange={(e) => setObjectType(e.target.value)}
                style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  marginRight: '10px'
                }}
              >
                <option value="contacts">Contacts</option>
                <option value="companies">Companies</option>
                <option value="deals">Deals</option>
              </select>
            </div>
          </div>
          
          <div style={{
            height: '400px',
            overflowY: 'auto',
            padding: '20px',
            backgroundColor: '#fff'
          }}>
            {messages.length === 0 ? (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: '#888',
                textAlign: 'center'
              }}>
                <h3>No messages yet</h3>
                <p>
                  Start by asking a question about your HubSpot data. For example:
                  "Show me the top 5 deals" or "Find all contacts in the technology industry"
                </p>
              </div>
            ) : (
              <div>
                {messages.map((message, index) => (
                  <div 
                    key={index}
                    style={{
                      marginBottom: '16px',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: message.role === 'user' ? 'flex-end' : 'flex-start'
                    }}
                  >
                    <div style={{
                      maxWidth: '80%',
                      padding: '12px',
                      borderRadius: '8px',
                      backgroundColor: message.role === 'user' ? '#1677ff' : '#f0f0f0',
                      color: message.role === 'user' ? 'white' : 'black'
                    }}>
                      <div style={{ 
                        fontSize: '12px', 
                        marginBottom: '4px',
                        opacity: 0.7
                      }}>
                        {message.role === 'user' ? 'You' : 'Assistant'}
                      </div>
                      <div>{message.content}</div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div style={{ textAlign: 'center', padding: '20px' }}>
                    Loading...
                  </div>
                )}
                {error && (
                  <div style={{ 
                    padding: '12px', 
                    backgroundColor: '#fff1f0', 
                    color: '#ff4d4f',
                    borderRadius: '4px'
                  }}>
                    {error}
                  </div>
                )}
              </div>
            )}
          </div>
          
          <div style={{ padding: '10px', borderTop: '1px solid #e0e0e0' }}>
            <form onSubmit={handleSubmit} style={{ display: 'flex' }}>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about your HubSpot data..."
                style={{
                  flex: 1,
                  padding: '10px',
                  borderRadius: '4px',
                  border: '1px solid #d9d9d9',
                  marginRight: '10px'
                }}
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                style={{
                  backgroundColor: '#1677ff',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '4px',
                  cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
                  opacity: loading || !query.trim() ? 0.7 : 1
                }}
              >
                Send
              </button>
            </form>
          </div>
        </div>

        {/* Results Panel */}
        <div style={{
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '10px',
            borderBottom: '1px solid #e0e0e0',
            backgroundColor: '#f9f9f9'
          }}>
            <h2 style={{ margin: 0 }}>Data Results</h2>
          </div>
          
          <div style={{
            height: '460px',
            overflowY: 'auto',
            padding: '20px',
            backgroundColor: '#fff'
          }}>
            {!results ? (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: '#888',
                textAlign: 'center'
              }}>
                <h3>No data to display</h3>
                <p>
                  Query HubSpot data to see results here.
                </p>
              </div>
            ) : (
              <div>
                <h3>Results ({results.results ? results.results.length : 0})</h3>
                {results.results && results.results.length > 0 ? (
                  <div>
                    {results.results.map((item, index) => (
                      <div 
                        key={index}
                        style={{
                          border: '1px solid #e0e0e0',
                          borderRadius: '4px',
                          padding: '10px',
                          marginBottom: '10px'
                        }}
                      >
                        <h4 style={{ margin: '0 0 10px 0' }}>
                          {item.properties?.firstname 
                            ? `${item.properties.firstname} ${item.properties.lastname || ''}`
                            : item.properties?.name 
                              ? item.properties.name
                              : item.properties?.dealname 
                                ? item.properties.dealname
                                : `Item #${index + 1}`}
                        </h4>
                        <pre style={{ 
                          backgroundColor: '#f5f5f5',
                          padding: '10px',
                          borderRadius: '4px',
                          overflow: 'auto',
                          fontSize: '12px'
                        }}>
                          {JSON.stringify(item.properties, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No results found</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SimpleApp;

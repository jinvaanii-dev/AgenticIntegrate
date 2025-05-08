import React, { useState, useEffect } from 'react';
import { 
  Navbar, 
  NavbarBrand, 
  NavbarContent, 
  NavbarItem, 
  Link, 
  Button,
  Input,
  Card,
  CardBody,
  CardHeader,
  CardFooter,
  Divider,
  Textarea,
  Chip,
  Spinner,
  Tooltip,
  Switch
} from "@nextui-org/react";
import { FiSend, FiDatabase, FiRefreshCw, FiInfo, FiMoon, FiSun } from 'react-icons/fi';
import ChatMessage from './components/ChatMessage';
import ResultPanel from './components/ResultPanel';
import axios from 'axios';

function App() {
  const [darkMode, setDarkMode] = useState(window.matchMedia('(prefers-color-scheme: dark)').matches);
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

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
      // Convert chat history to the format expected by the API
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await axios.post('http://localhost:8000/query', {
        query: query,
        history: history
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // If there are sources or structured data in the response
      if (response.data.sources) {
        setResults(response.data.sources);
      }
    } catch (err) {
      console.error('Error querying the API:', err);
      setError('Failed to get a response. Please try again.');
    } finally {
      setLoading(false);
      setQuery('');
    }
  };

  const clearChat = () => {
    setMessages([]);
    setResults(null);
    setError(null);
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-dark' : 'bg-light'}`}>
      <div className="futuristic-gradient absolute inset-0 opacity-20"></div>
      
      <Navbar 
        isBordered 
        className="glass-effect"
        maxWidth="xl"
      >
        <NavbarBrand>
          <div className="flex items-center gap-2">
            <FiDatabase className="text-secondary-500" size={24} />
            <p className="font-bold text-inherit">HubSpot Agentic Workflow</p>
          </div>
        </NavbarBrand>
        <NavbarContent justify="end">
          <NavbarItem>
            <Tooltip content={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}>
              <Switch
                size="sm"
                color="secondary"
                isSelected={darkMode}
                onChange={() => setDarkMode(!darkMode)}
                thumbIcon={({ isSelected, className }) =>
                  isSelected ? (
                    <FiMoon className={className} />
                  ) : (
                    <FiSun className={className} />
                  )
                }
              />
            </Tooltip>
          </NavbarItem>
          <NavbarItem>
            <Button 
              color="danger" 
              variant="flat" 
              startContent={<FiRefreshCw />}
              onClick={clearChat}
            >
              Clear Chat
            </Button>
          </NavbarItem>
        </NavbarContent>
      </Navbar>

      <main className="container mx-auto px-4 py-8 max-w-6xl relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Panel */}
          <Card className="lg:col-span-2 glass-effect">
            <CardHeader className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">HubSpot Query Assistant</h2>
              <Chip color="primary" variant="flat">GPT-4o</Chip>
            </CardHeader>
            <Divider />
            <CardBody className="overflow-y-auto max-h-[60vh] min-h-[60vh] p-4">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
                  <FiInfo size={48} className="mb-4" />
                  <h3 className="text-lg font-medium mb-2">No messages yet</h3>
                  <p className="max-w-md">
                    Start by asking a question about your HubSpot data. For example:
                    "Show me the top 5 deals from last month" or "Find all contacts in the technology industry"
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <ChatMessage key={index} message={message} />
                  ))}
                  {loading && (
                    <div className="flex justify-center py-4">
                      <Spinner color="secondary" size="lg" />
                    </div>
                  )}
                  {error && (
                    <div className="p-3 bg-danger-100 text-danger-500 rounded-lg">
                      {error}
                    </div>
                  )}
                </div>
              )}
            </CardBody>
            <Divider />
            <CardFooter>
              <form onSubmit={handleSubmit} className="w-full">
                <div className="flex gap-2 w-full">
                  <Textarea
                    placeholder="Ask about your HubSpot data..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full"
                    minRows={1}
                    maxRows={3}
                    disabled={loading}
                  />
                  <Button
                    isIconOnly
                    color="primary"
                    type="submit"
                    disabled={loading || !query.trim()}
                    aria-label="Send message"
                  >
                    <FiSend />
                  </Button>
                </div>
              </form>
            </CardFooter>
          </Card>

          {/* Results Panel */}
          <Card className="glass-effect">
            <CardHeader>
              <h2 className="text-xl font-semibold">Data Visualization</h2>
            </CardHeader>
            <Divider />
            <CardBody className="overflow-y-auto max-h-[60vh] min-h-[60vh]">
              <ResultPanel results={results} />
            </CardBody>
          </Card>
        </div>
      </main>
    </div>
  );
}

export default App;

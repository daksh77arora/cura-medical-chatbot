import { useState, useRef, useEffect } from 'react';
import { useChat } from './hooks/useChat';
import { SourceCard } from './components/SourceCard';
import { Disclaimer } from './components/Disclaimer';

function App() {
  const { messages, send, loading } = useChat();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    send(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100 font-sans">
      <header className="bg-gray-900 border-b border-gray-800 p-4 sticky top-0 z-10">
        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          MediBot Pro v2.0
        </h1>
        <p className="text-xs text-gray-400">Industry-Level Medical RAG Assistant</p>
      </header>
      
      <main className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center text-3xl">⚕️</div>
            <h2 className="text-2xl font-semibold">How can I help you today?</h2>
            <p className="text-gray-500 max-w-md">Ask me about medical conditions, medications, or health guidelines based on verified medical literature.</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-br-none shadow-blue-900/20' 
                  : 'bg-gray-900 border border-gray-800 rounded-bl-none shadow-lg'
              }`}>
                {msg.role === 'bot' && <div className="flex items-center gap-2 mb-2 text-blue-400 text-xs font-semibold uppercase tracking-wider"><div className="w-5 h-5 bg-blue-500/20 rounded flex items-center justify-center">⚕️</div> MediBot</div>}
                
                <div className="whitespace-pre-wrap leading-relaxed">{msg.content || (loading && i === messages.length - 1 ? <span className="animate-pulse">Thinking...</span> : '')}</div>
                
                {msg.role === 'bot' && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 border-t border-gray-800 pt-3">
                    <p className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-2">Sources</p>
                    {msg.sources.map((src, idx) => <SourceCard key={idx} source={src} />)}
                  </div>
                )}
                {msg.role === 'bot' && i === messages.length - 1 && !loading && <Disclaimer />}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </main>
      
      <footer className="bg-gray-900 border-t border-gray-800 p-4">
        <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto flex gap-2">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Type your medical query..."
            className="flex-1 bg-gray-950 border border-gray-800 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all disabled:opacity-50 text-gray-100 placeholder-gray-600"
          />
          <button 
            type="submit" 
            disabled={!input.trim() || loading}
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <span>Send</span>
          </button>
        </form>
      </footer>
    </div>
  );
}

export default App;

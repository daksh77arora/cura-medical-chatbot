import { useState } from 'react';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const send = async (msg) => {
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: msg }]);
    setLoading(true);

    // Initial bot message for streaming tokens
    setMessages(prev => [...prev, { role: 'bot', content: '', sources: null }]);

    const baseUrl = import.meta.env.VITE_API_URL || '';
    try {
      // Setup the event source for SSE token streaming
      const response = await fetch(`${baseUrl}/api/v1/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      
      if (!response.body) throw new Error("Streaming not supported");
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr === '[DONE]') break;
            if (dataStr.trim()) {
              try {
                const data = JSON.parse(dataStr);
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  // Properly clone the object to avoid mutating the previous state directly
                  newMessages[lastIndex] = {
                    ...newMessages[lastIndex],
                    content: newMessages[lastIndex].content + data.token
                  };
                  return newMessages;
                });
              } catch (e) {
                console.error("Token parsing error", e);
              }
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        newMessages[lastIndex].content = "Sorry, I encountered an error connecting to out servers.";
        return newMessages;
      });
    } finally {
      setLoading(false);
    }
  };

  return { messages, send, loading };
};

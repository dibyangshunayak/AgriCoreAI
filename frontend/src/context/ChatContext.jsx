// =====================================================================
// FILE: frontend/src/context/ChatContext.jsx
// DESCRIPTION: Context for managing chat sessions, themes, GPS, and
//              streaming state. All data persisted to localStorage.
//              No authentication or demo mode required.
// =====================================================================

import React, { createContext, useState, useEffect, useContext } from 'react';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  // --- Persistent Theme State ---
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('agri_theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  // --- Persistent Chat Sessions State ---
  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem('agri_sessions');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error("Failed to parse saved sessions:", e);
      }
    }
    // Default initial session
    const initialSessionId = 'session_' + Date.now();
    return [{
      id: initialSessionId,
      name: 'New Chat 🌱',
      messages: []
    }];
  });

  const [activeSessionId, setActiveSessionId] = useState(() => {
    const saved = localStorage.getItem('agri_active_session_id');
    if (saved) return saved;
    return sessions[0]?.id || '';
  });

  // --- Current Interaction States ---
  const [attachment, setAttachment] = useState(null); // { file_path, file_name, type, context }
  const [gpsCoordinates, setGpsCoordinates] = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [thinkingStage, setThinkingStage] = useState(null);
  const [liveMcpCalls, setLiveMcpCalls] = useState([]);

  // --- Theme Syncing ---
  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
    try {
      localStorage.setItem('agri_theme', theme);
    } catch (e) {
      console.warn("Failed to save theme to localStorage:", e);
    }
  }, [theme]);

  // --- Save Chat Sessions to LocalStorage ---
  useEffect(() => {
    try {
      const sanitizedSessions = sessions.map(s => ({
        ...s,
        messages: s.messages.map(m => {
          // Strip base64 images to prevent localStorage quota issues
          if (m.image && m.image.startsWith('data:image/')) {
            return { ...m, image: null };
          }
          return m;
        })
      }));
      localStorage.setItem('agri_sessions', JSON.stringify(sanitizedSessions));
    } catch (e) {
      console.warn("Failed to save sessions to localStorage (quota exceeded or disabled):", e);
    }
  }, [sessions]);

  useEffect(() => {
    try {
      localStorage.setItem('agri_active_session_id', activeSessionId);
    } catch (e) {
      console.warn("Failed to save active session ID to localStorage:", e);
    }
  }, [activeSessionId]);


  // --- Get current messages helper ---
  const currentSession = sessions.find(s => s.id === activeSessionId) || sessions[0];
  const messages = currentSession ? currentSession.messages : [];

  // --- Actions ---
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const createNewChat = () => {
    const newId = 'session_' + Date.now();
    const newSession = {
      id: newId,
      name: 'New Chat 🌱',
      messages: []
    };
    setSessions(prev => [newSession, ...prev]);
    setActiveSessionId(newId);
    setAttachment(null); // Reset attachments on new chat
  };

  const switchChat = (id) => {
    setActiveSessionId(id);
    setAttachment(null);
  };

  const deleteChat = (id) => {
    const filtered = sessions.filter(s => s.id !== id);
    if (filtered.length === 0) {
      // Re-initialize if all sessions deleted
      const newId = 'session_' + Date.now();
      setSessions([{
        id: newId,
        name: 'New Chat 🌱',
        messages: []
      }]);
      setActiveSessionId(newId);
    } else {
      setSessions(filtered);
      if (activeSessionId === id) {
        setActiveSessionId(filtered[0].id);
      }
    }
  };

  const renameChat = (id, name) => {
    setSessions(prev => prev.map(s => s.id === id ? { ...s, name } : s));
  };

  const pinChat = (id) => {
    setSessions(prev => prev.map(s => s.id === id ? { ...s, pinned: !s.pinned } : s));
  };

  const setAttachmentDetails = (file_path, file_name, type, context, previewUrl = null) => {
    setAttachment({ file_path, file_name, type, context, previewUrl });
  };

  const removeAttachment = () => {
    setAttachment(null);
  };

  const addMessageToSession = (role, content, image = null) => {
    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        // Use provided image or fall back to current attachment previewUrl if it's a user image
        const userImage = image || (role === 'user' && attachment?.type === 'image' ? attachment.previewUrl : null);
        const updatedMsgs = [...s.messages, { 
          id: 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5), 
          role, 
          content,
          image: userImage
        }];
        
        // Auto-generate session name if it's the first user message
        let newName = s.name;
        if (s.name === 'New Chat 🌱' && role === 'user') {
          newName = content.length > 25 ? content.substring(0, 25) + '...' : content;
        }
        
        return {
          ...s,
          name: newName,
          messages: updatedMsgs
        };
      }
      return s;
    }));
  };

  const updateLastAssistantMessage = (content) => {
    setSessions(prev => prev.map(s => {
      if (s.id === activeSessionId) {
        const msgs = [...s.messages];
        // Find last message
        const lastIdx = msgs.length - 1;
        if (lastIdx >= 0 && msgs[lastIdx].role === 'assistant') {
          msgs[lastIdx] = { ...msgs[lastIdx], content };
        } else {
          // If no assistant message, add one
          msgs.push({ id: 'msg_stream_' + Date.now(), role: 'assistant', content });
        }
        return { ...s, messages: msgs };
      }
      return s;
    }));
  };

  const requestGpsLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }
    setGpsLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setGpsCoordinates({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        });
        setGpsLoading(false);
      },
      (error) => {
        console.error("GPS access error:", error);
        alert("Could not retrieve GPS coordinates. Defaulting coordinates will be used.");
        setGpsLoading(false);
      },
      { enableHighAccuracy: true, timeout: 5000 }
    );
  };

  return (
    <ChatContext.Provider value={{
      theme,
      toggleTheme,
      sessions,
      activeSessionId,
      messages,
      attachment,
      gpsCoordinates,
      gpsLoading,
      isThinking,
      isStreaming,
      thinkingStage,
      setThinkingStage,
      liveMcpCalls,
      setLiveMcpCalls,
      setTheme,
      createNewChat,
      switchChat,
      deleteChat,
      renameChat,
      pinChat,
      setAttachmentDetails,
      removeAttachment,
      addMessageToSession,
      updateLastAssistantMessage,
      requestGpsLocation,
      setGpsCoordinates,
      setIsThinking,
      setIsStreaming
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => useContext(ChatContext);

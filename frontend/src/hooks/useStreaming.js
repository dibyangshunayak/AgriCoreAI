import { useChatContext } from '../context/ChatContext';
import { BACKEND_URL } from '../services/api';
import { useLocation } from './useLocation';

export const useStreaming = () => {
  const {
    messages,
    attachment,
    activeSessionId,
    addMessageToSession,
    updateLastAssistantMessage,
    removeAttachment,
    setIsThinking,
    setIsStreaming,
    setThinkingStage,
    setLiveMcpCalls
  } = useChatContext();

  const { location: activeLocation } = useLocation();

  const sendMessage = async (userQuery, options = {}) => {
    const activeAttachment = options.attachment || attachment;
    if (!userQuery.trim() && !activeAttachment) return;
    const activeCoords = activeLocation;

    // Add the user's message
    addMessageToSession(
      'user',
      userQuery,
      activeAttachment?.type === 'image' ? activeAttachment.previewUrl : null
    );
    setIsThinking(true);
    setIsStreaming(false);
    removeAttachment();

    // Map history
    const historyPayload = messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    // Load user's preferred language from localStorage profile
    let preferredLanguage = 'en';
    try {
      const storedProfile = localStorage.getItem('agri_user_profile');
      if (storedProfile) {
        const parsed = JSON.parse(storedProfile);
        preferredLanguage = parsed.preferred_language || 'en';
      }
    } catch (e) { /* ignore */ }

    const payload = {
      message: userQuery,
      latitude: activeCoords?.latitude || null,
      longitude: activeCoords?.longitude || null,
      file_path: activeAttachment?.file_path || null,
      file_context: activeAttachment?.context || null,
      history: historyPayload,
      session_id: activeSessionId,
      preferred_language: preferredLanguage
    };

    // Setup animated thinking stages for live mode
    let stageIndex = 0;
    const stages = [
      { stage: 'Thinking...', calls: [] },
      { stage: 'Planning...', calls: ['Calling Search MCP...'] },
      { stage: 'Calling Weather...', calls: ['Calling Search MCP...', 'Calling Weather MCP...'] },
      { stage: 'Calling Memory...', calls: ['Calling Search MCP...', 'Calling Weather MCP...', 'Calling Crop MCP...'] },
      { stage: 'Preparing Recommendation...', calls: ['Calling Search MCP...', 'Calling Weather MCP...', 'Calling Crop MCP...', 'Calling Government Scheme MCP...'] }
    ];

    setThinkingStage(stages[0].stage);
    setLiveMcpCalls(stages[0].calls);


    const stageInterval = setInterval(() => {
      stageIndex++;
      if (stageIndex < stages.length) {
        setThinkingStage(stages[stageIndex].stage);
        setLiveMcpCalls(stages[stageIndex].calls);
      } else {
        clearInterval(stageInterval);
      }
    }, 800);

    const targetUrl = `${BACKEND_URL}/api/chat`;
    console.log(`[useStreaming] Initiating request to: ${targetUrl}`);

    try {
      const response = await fetch(targetUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        clearInterval(stageInterval);
        setThinkingStage(null);
        console.error(`[useStreaming] HTTP Error Response (Non-200):`, {
          status: response.status,
          statusText: response.statusText,
          url: response.url
        });
        throw new Error(`Server returned status code ${response.status}`);
      }

      if (!response.body) {
        clearInterval(stageInterval);
        setThinkingStage(null);
        throw new Error("No response body available for streaming");
      }

      clearInterval(stageInterval);
      setThinkingStage(null);

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      setIsThinking(false);
      setIsStreaming(true);

      // Create initial assistant message in session
      addMessageToSession('assistant', '');

      let buffer = '';
      let accumulatedResponseText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        buffer = lines.pop();

        for (const line of lines) {
          const cleanLine = line.trim();
          if (cleanLine.startsWith('data: ')) {
            try {
              const jsonStr = cleanLine.substring(6);
              const data = JSON.parse(jsonStr);
              const token = data.token;
              const error = data.error;
              
              if (token) {
                accumulatedResponseText += token;
                updateLastAssistantMessage(accumulatedResponseText);
              } else if (error) {
                accumulatedResponseText = `⚠ Error: ${error}`;
                updateLastAssistantMessage(accumulatedResponseText);
              }
            } catch (err) {
              console.error("Error parsing stream token JSON:", err);
            }
          }
        }
      }

      if (buffer.trim().startsWith('data: ')) {
        try {
          const jsonStr = buffer.trim().substring(6);
          const data = JSON.parse(jsonStr);
          const token = data.token;
          const error = data.error;
          if (token) {
            accumulatedResponseText += token;
            updateLastAssistantMessage(accumulatedResponseText);
          } else if (error) {
            accumulatedResponseText = `⚠ Error: ${error}`;
            updateLastAssistantMessage(accumulatedResponseText);
          }
        } catch (err) {
          console.error("Error parsing leftover stream buffer JSON:", err);
        }
      }

    } catch (error) {
      clearInterval(stageInterval);
      setThinkingStage(null);
      
      if (error instanceof TypeError && (error.message.includes('fetch') || error.message.includes('NetworkError') || error.message.includes('Failed to'))) {
        console.error(`[useStreaming] Network or CORS Error: Connection failed when requesting ${targetUrl}.`, {
          message: error.message,
          name: error.name,
          stack: error.stack,
          isOnline: navigator.onLine,
          probableCauses: [
            "CORS policy restriction (e.g., origin not allowed by backend CORS configuration)",
            "Backend server is offline or unreachable (e.g., cold start, crashed, or invalid URL)",
            "Client has no internet connection or DNS lookup failed"
          ]
        });
      } else {
        console.error("[useStreaming] Request failed:", error);
      }

      setIsThinking(false);
      addMessageToSession('assistant', `⚠ Failed to connect to server: ${error.message}. Please verify the backend is running and CORS is configured.`);
    } finally {
      setIsStreaming(false);
    }
  };

  return { sendMessage };
};

export default useStreaming;


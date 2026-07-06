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

    try {
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
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
      console.error("Streaming error:", error);
      setIsThinking(false);
      addMessageToSession('assistant', `⚠ Failed to connect to server: ${error.message}. Please verify the backend is running.`);
    } finally {
      setIsStreaming(false);
    }
  };

  return { sendMessage };
};

export default useStreaming;


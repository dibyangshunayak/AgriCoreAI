// =====================================================================
// FILE: frontend/src/pages/ChatPage.jsx
// DESCRIPTION: Clean chat page — sidebar owns session management.
// =====================================================================

import React from 'react';
import AppLayout from '../components/AppLayout';
import MessageList from '../components/MessageList';
import ChatInput from '../components/ChatInput';

export const ChatPage = () => {
  return (
    <AppLayout isChat={true}>
      <div className="flex-1 flex flex-col h-full relative overflow-hidden">
        <MessageList />
        <ChatInput />
      </div>
    </AppLayout>
  );
};

export default ChatPage;

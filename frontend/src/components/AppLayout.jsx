// =====================================================================
// FILE: frontend/src/components/AppLayout.jsx
// DESCRIPTION: Main layout shell with ChatGPT-style sidebar + content area.
// =====================================================================

import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

export const AppLayout = ({ children, isChat = false }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="flex w-screen h-screen overflow-hidden bg-[#0F172A] text-white font-sans relative">
      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        isCollapsed={isSidebarCollapsed}
        onClose={() => setIsSidebarOpen(false)}
        onToggleCollapse={() => setIsSidebarCollapsed(c => !c)}
      />

      {/* Main content area */}
      <div
        className="flex-1 flex flex-col h-full relative overflow-hidden transition-all duration-300"
        style={{ minWidth: 0 }}
      >
        <Header
          onMenuToggle={() => setIsSidebarOpen(!isSidebarOpen)}
          isSidebarCollapsed={isSidebarCollapsed}
        />

        {isChat ? (
          children
        ) : (
          <div className="flex-1 overflow-y-auto p-4 md:p-8">
            {children}
          </div>
        )}
      </div>
    </div>
  );
};

export default AppLayout;

// =====================================================================
// FILE: frontend/src/App.jsx
// DESCRIPTION: Core React Application entrypoint with simplified routing.
// =====================================================================

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import { LocationProvider } from './context/LocationContext';
import { ChatProvider } from './context/ChatContext';
import ChatPage from './pages/ChatPage';
import Dashboard from './pages/Dashboard';
import SettingsPage from './pages/SettingsPage';
import CropHealthPage from './pages/CropHealthPage';

/**
 * Root redirect: goes directly to /chat.
 */
const RootRedirect = () => {
  return <Navigate to="/chat" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <UserProvider>
        <LocationProvider>
          <ChatProvider>
            <Routes>
              {/* Root — auto-redirect */}
              <Route path="/" element={<RootRedirect />} />

              {/* Main Chat Interface */}
              <Route path="/chat" element={<ChatPage />} />

              {/* Farm Dashboard */}
              <Route path="/dashboard" element={<Dashboard />} />

              {/* Dedicated Crop Health Analytics */}
              <Route path="/crop-health" element={<CropHealthPage />} />

              {/* Settings */}
              <Route path="/settings" element={<SettingsPage />} />

              {/* Fallback — redirect any unknown paths to root */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </ChatProvider>
        </LocationProvider>
      </UserProvider>
    </BrowserRouter>
  );
}

export default App;

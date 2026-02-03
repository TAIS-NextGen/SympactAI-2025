import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Cookies from "js-cookie";

import LandingPage from "./templates/Landing";
import SignInPage from "./templates/signIn";
import SignUpPage from "./templates/signUp";
import HomePage from "./templates/Home";
import AnalyticsPage from "./templates/Analytics";
import MonitoringPage from "./templates/Monitoring";
import AlertsPage from "./templates/Alerts";
import PumpAlertsPage from "./templates/PumpAlerts";
import ReportPage from "./templates/Report";
import PumpOChatbotPage from "./templates/Chatbot";
import ChartDetails from "./templates/ChartDetails";
import SettingsPage from "./templates/Settings";
import HelpPage from "./templates/Help";
import ServiceProvidersPage from "./templates/ServicesProviders";

function App() {
  const [token, setToken] = useState(Cookies.get("token") || null);

  // Keep token state updated if cookie changes
  useEffect(() => {
    const interval = setInterval(() => {
      const currentToken = Cookies.get("token") || null;
      setToken(currentToken);
    }, 500); // check every 0.5s

    return () => clearInterval(interval);
  }, []);

  const PrivateRoute = ({ children }) => {
    return token ? children : <Navigate to="/signin" replace />;
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/signin" element={<SignInPage />} />

        {/* Private */}
        <Route
          path="/monitoring/:chartId"
          element={
            <PrivateRoute>
              <ChartDetails />
            </PrivateRoute>
          }
        />
        <Route
          path="/home"
          element={
            <PrivateRoute>
              <HomePage />
            </PrivateRoute>
          }
        />
        <Route
          path="/analytics/*"
          element={
            <PrivateRoute>
              <AnalyticsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/monitoring"
          element={
            <PrivateRoute>
              <MonitoringPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/alerts"
          element={
            <PrivateRoute>
              <AlertsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/pumpalerts"
          element={
            <PrivateRoute>
              <PumpAlertsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/report"
          element={
            <PrivateRoute>
              <ReportPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/chatbot"
          element={
            <PrivateRoute>
              <PumpOChatbotPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <PrivateRoute>
              <SettingsPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/help"
          element={
            <PrivateRoute>
              <HelpPage />
            </PrivateRoute>
          }
        />
        <Route
          path="/providers"
          element={
            <PrivateRoute>
              <ServiceProvidersPage />
            </PrivateRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

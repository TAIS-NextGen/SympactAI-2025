import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import VoiceInputComponent from "./VoiceInput";
import SidebarComponent from "./Sidebar";
import HeaderComponent from "./Header";
import ChatbotButtonComponent from "./ChatbotButton";

export default function AnalyticsPage() {
  const navigate = useNavigate();
  const currentPath = window.location.pathname;
  const [allPumps, setAllPumps] = useState([]);
  const [selectedPump, setSelectedPump] = useState("");
  const [selectedQuarter, setSelectedQuarter] = useState(
    "Fourth Quarter of the month"
  );
  const [user, setUser] = useState(null);

  useEffect(() => {
    async function fetchUser() {
      try {
        const res = await fetch("http://localhost:5000/api/user/profile", {
          credentials: "include",
        });
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();
        setUser(data);
        console.log("User loaded:", data);
      } catch (err) {
        console.error("Failed to load user profile:", err);
      }
    }
    fetchUser();
  }, []);
  useEffect(() => {
    async function fetchPumps() {
      try {
        const res = await fetch("http://localhost:5000/api/pumps", {
          credentials: "include",
        });
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();
        setAllPumps(data);
        console.log("Pumps loaded:", data);
      } catch (err) {
        console.error("Failed to load pumps:", err);
      }
    }
    fetchPumps();
  }, []);

  const manageRoutes = {
    Home: "/home",
    "Audio Detection": "/analytics",
    Monitoring: "/monitoring",
    Alerts: "/alerts",
  };

  const prefRoutes = {
    Settings: "/settings",
    Help: "/help",
    "Our Service Providers": "/providers",
  };

  return (
    <div className="flex h-screen font-sans bg-gray-100">
      <SidebarComponent
        currentPath={currentPath}
        manageRoutes={manageRoutes}
        prefRoutes={prefRoutes}
      />

      {/* Main content */}
      <main className="flex-1 bg-white overflow-y-auto px-8 py-4">
        {/* Header */}
        {user && (
          <HeaderComponent
            username={user.firstName}
            lastname={user.lastName}
            userId={user._id}
          />
        )}
        <section className="flex justify-between items-start mt-4">
          <div>
            <p className="text-lg font-medium">You are now viewing :</p>
            <h2 className="text-2xl font-bold text-blue-900 mt-1">
              {selectedPump?.name || "No pump selected"}{" "}
              <span className="text-sm font-normal text-black">
                {selectedPump?._id}
              </span>
            </h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">
                Select Your Pump:
              </label>
              <select
                value={selectedPump?._id || ""}
                onChange={(e) => {
                  const pump = allPumps.find((p) => p._id === e.target.value);
                  setSelectedPump(pump);
                }}
                className="w-64 px-4 py-2 rounded-md bg-blue-500 text-white font-semibold shadow-md"
              >
                {allPumps.map((pump) => (
                  <option key={pump._id} value={pump._id}>
                    {pump.name}
                  </option>
                ))}
              </select>
            </div>

            {/* <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Specify the duration:</label>
              <select
                value={selectedQuarter}
                onChange={(e) => setSelectedQuarter(e.target.value)}
                className="w-64 px-4 py-2 rounded-md bg-blue-500 text-white font-semibold shadow-md"
              >
                {quarters.map((q) => (
                  <option key={q} value={q}>{q}</option>
                ))}
              </select>
            </div> */}
          </div>
        </section>

        <div className="bg-white  ">
          {/* <h3 className="font-semibold text-lg mb-4">
            Prediction with Operation States - {selectedQuarter}
          </h3> */}
          <div className="h-180 bg-white rounded-md flex items-center justify-center text-gray-500">
            <VoiceInputComponent />
          </div>
        </div>
      </main>
      {/* Reusable Chatbot Button */}
      <ChatbotButtonComponent />
    </div>
  );
}

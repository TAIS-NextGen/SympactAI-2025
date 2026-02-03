import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Bell,
  Search,
  Power,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Zap,
  Settings,
} from "lucide-react";
import Papa from "papaparse";

import SidebarComponent from "./Sidebar";
import HeaderComponent from "./Header";
import ChatbotButtonComponent from "./ChatbotButton";
import ChartCard from "./chartCard";

export default function HomePage() {
  const [user, setUser] = useState(null);
  const [allPumps, setAllPumps] = useState([]);

  const currentPath = window.location.pathname;
  const [selectedPump, setSelectedPump] = useState(
    "Centrifugal Pump 1 (CP-12398)"
  );
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
  const [notifications, setNotifications] = useState(3);
  const [pumpData, setPumpData] = useState([
    {
      name: "Centrifugal Pump 1",
      id: "CP-12036",
      line: 3,
      status: "OFF",
      pressure: 4.99,
      temp: "220°C",
      flow: "128.6",
      vibration: "87.3",
    },
    {
      name: "Centrifugal Pump 2",
      id: "CP-12037",
      line: 2,
      status: "ON",
      pressure: 5.12,
      temp: "222°C",
      flow: "132.4",
      vibration: "92.1",
    },
  ]);
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
  const [currentTime, setCurrentTime] = useState(new Date());

  const navigate = useNavigate();

  const navItemsManage = ["Home", "Analytics", "Monitoring", "Alerts"];

  const handleNavigation = (label) => {
    const path = "/" + label.toLowerCase().replace(/\s+/g, "-");
    navigate(path);
  };

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
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handlePumpToggle = (index) => {
    setPumpData((prev) =>
      prev.map((pump, i) =>
        i === index
          ? { ...pump, status: pump.status === "ON" ? "OFF" : "ON" }
          : pump
      )
    );
  };

  const clearNotifications = () => {
    setNotifications(0);
  };
  const activePumpsCount = allPumps.filter(
    (pump) => pump.status === "active"
  ).length;
  const activePercentage = ((activePumpsCount / allPumps.length) * 100).toFixed(
    0
  ); // rounded to 0 decimals
  const inactivePumpsCount = allPumps.filter(
    (pump) => pump.status === "inactive"
  ).length;
  const inactivePercentage = (
    (inactivePumpsCount / allPumps.length) *
    100
  ).toFixed(0); // rounded to 0 decimals
  const maintenancePumpsCount = allPumps.filter(
    (pump) => pump.status === "maintenance"
  ).length;
  const maintenancePercentage = (
    (maintenancePumpsCount / allPumps.length) *
    100
  ).toFixed(0); // rounded to 0 decimals
  const [pumpSensorData, setPumpSensorData] = useState([]);
  useEffect(() => {
    // Load one CSV file for Home page chart
    fetch("/Flow.csv")
      .then((res) => res.text())
      .then((csvText) => {
        Papa.parse(csvText, {
          header: true,
          dynamicTyping: false,
          complete: (results) => {
            const cleaned = results.data
              .filter(
                (row) =>
                  row.timestamp !== undefined &&
                  row.timestamp !== null &&
                  row.sensor_avg !== undefined
              )
              .map((row) => ({
                ...row,
                timestamp: new Date(row.timestamp).getTime(), // convert to number
              }));
            setPumpSensorData(cleaned);
          },
        });
      });
  }, []);

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
        {/* Overview cards */}
        <section className="grid grid-cols-3 gap-6 mt-4">
          <OverviewCard
            title="Current Pumps ON"
            value={activePumpsCount}
            desc={`${activePercentage}% of total`}
            color="bg-blue-200"
            icon={<CheckCircle className="text-blue-600" size={24} />}
          />
          <OverviewCard
            title="Current Pumps OFF"
            value={inactivePumpsCount}
            desc={`${inactivePercentage}% of total`}
            color="bg-red-200"
            icon={<AlertTriangle className="text-purple-600" size={24} />}
          />

          <OverviewCard
            title="Current Pumps In Maintenance"
            value={maintenancePumpsCount}
            desc={`${maintenancePercentage}% of total`}
            color="bg-indigo-200"
            icon={<Zap className="text-indigo-600" size={24} />}
          />
        </section>

        {/* Graphs and Reports */}
        <section className="grid grid-cols-3 gap-6 mb-8">
          <div className="col-span-2 bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <ChartCard
              title="Pump Vibration Over Operation Time"
              chartId="home-pump-chart"
              data={pumpSensorData} // pass the parsed numeric timestamp data
            />
          </div>

          <div className="bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <h3 className="font-semibold mb-4">Annual System Failure Logs</h3>
            <div className="h-40 bg-gradient-to-t from-blue-100 to-blue-200 flex items-center justify-center rounded-lg">
              <div className="text-center">
                <div className="text-blue-600 text-2xl font-bold">12</div>
                <div className="text-sm text-gray-500">Total Failures</div>
              </div>
            </div>
          </div>
        </section>

        {/* Error Table and Reports */}
        <section className="gap-6">
          <div className=" bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-semibold">Pumps Overview</h3>
              <span className="text-sm text-gray-500 flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Latest Update 30 Sec Ago
              </span>
            </div>
            <table className="w-full text-sm text-left mt-2 table-fixed border-collapse">
              <thead>
                <tr className="text-gray-600 border-b">
                  <th className="pb-2 w-[20%]">Pump Name</th>
                  <th className="pb-2 w-[20%]">Location</th>
                  <th className="pb-2 w-[20%]">Material</th>
                  <th className="pb-2 w-[20%]">Status</th>
                  <th className="pb-2 w-[20%]">Pressure</th>
                  <th className="pb-2 w-[20%]">Action</th>
                </tr>
              </thead>
              <tbody>
                {allPumps.map((pump, i) => (
                  <tr
                    key={i}
                    className="border-b hover:bg-gray-50 transition-colors"
                  >
                    <td className="py-3 px-2 ">{pump.name}</td>
                    <td className="py-3 px-2">{pump.location}</td>
                    <td className="py-3 px-2">{pump.material}</td>
                    <td
                      className={`py-3 px-2 font-semibold ${
                        pump.status === "OFF"
                          ? "text-red-500"
                          : "text-green-600"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            pump.status === "OFF"
                              ? "bg-red-500"
                              : "bg-green-500"
                          }`}
                        ></div>
                        {pump.status}
                      </div>
                    </td>
                    <td className="py-3 px-2">{pump.pressure_rating}</td>
                    <td className="py-3 px-2">
                      <button
                        onClick={() => handlePumpToggle(i)}
                        className={`px-3 py-1 rounded-full text-xs font-medium transition-all transform hover:scale-105 ${
                          pump.status === "OFF"
                            ? "bg-green-100 text-green-800 hover:bg-green-200"
                            : "bg-red-100 text-red-800 hover:bg-red-200"
                        }`}
                      >
                        <Power size={12} className="inline mr-1" />
                        {pump.status === "OFF" ? "Turn ON" : "Turn OFF"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
      {/* Reusable Chatbot Button */}
      <ChatbotButtonComponent />
    </div>
  );
}

function OverviewCard({ title, value, desc, color, icon }) {
  return (
    <div
      className={`p-4 rounded-xl shadow-sm ${color} hover:shadow-md transition-all duration-200 hover:scale-105 cursor-pointer`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="text-gray-800 font-bold text-2xl">{value}</div>
        {icon}
      </div>
      <div className="text-sm font-medium text-gray-700 mt-1">{title}</div>
      <div className="text-xs text-gray-600 mt-1">{desc}</div>
    </div>
  );
}

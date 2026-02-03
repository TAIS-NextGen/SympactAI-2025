import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Papa from "papaparse";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import SidebarComponent from "./Sidebar";
import HeaderComponent from "./Header";
import ChatbotButtonComponent from "./ChatbotButton";

export default function MonitoringPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const currentPath = location.pathname;
  const allOption = "Show All Pumps";

  const [selectedPump, setSelectedPump] = useState(allOption);
  const [data, setData] = useState([]);
  const [allPumpData, setAllPumpData] = useState({});
  const [allPumps, setAllPumps] = useState([]);
  const [user, setUser] = useState(null);
  const [pumpCsvMap, setPumpCsvMap] = useState({});

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

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

        // Create dynamic CSV mapping based on fetched pumps
        const dynamicCsvMap = {};

        data.forEach((pump, index) => {
          if (index === 0) {
            // First pump uses original CSV files
            dynamicCsvMap[pump.name] = {
              Flow: "/Flow.csv",
              Pressure: "/Pressure.csv",
              Temperature: "/Temprature.csv",
            };
          } else if (index === 1) {
            // Second pump uses Pump2 files
            dynamicCsvMap[pump.name] = {
              Flow: "/Pump2_flow.csv",
              Pressure: "/Pump2_pressure.csv",
              Temperature: "/Pump2_temp.csv",
            };
          } else {
            // Additional pumps can reuse existing files or you can add more
            dynamicCsvMap[pump.name] = {
              Flow: "/Flow.csv", // Fallback to original files
              Pressure: "/Pressure.csv",
              Temperature: "/Temprature.csv",
            };
          }
        });

        console.log("Dynamic CSV mapping created:", dynamicCsvMap);
        setPumpCsvMap(dynamicCsvMap);

        // Set first pump as default if we have pumps
        if (data.length > 0) {
          setSelectedPump(data[0].name);
        }
      } catch (err) {
        console.error("Failed to load pumps:", err);
      }
    }
    fetchPumps();
  }, []);

  useEffect(() => {
    // Only proceed if we have pump CSV mapping
    if (Object.keys(pumpCsvMap).length === 0) {
      return;
    }

    console.log(`Loading data for pump: ${selectedPump}`);
    console.log("Available pumps in CSV map:", Object.keys(pumpCsvMap));

    if (selectedPump === allOption) {
      // Show all pumps - combine data from all pumps
      setData([]);
      const allData = {};

      Promise.all(
        Object.entries(pumpCsvMap).flatMap(([pumpName, csvFiles]) =>
          Object.entries(csvFiles).map(([sensorType, csvFile]) => {
            console.log(`Fetching ${csvFile} for ${pumpName} - ${sensorType}`);
            return fetch(csvFile)
              .then((res) => {
                console.log(
                  `Response for ${csvFile}:`,
                  res.status,
                  res.statusText
                );
                if (!res.ok) {
                  throw new Error(`HTTP ${res.status}: ${res.statusText}`);
                }
                return res.text();
              })
              .then((csvText) => {
                console.log(
                  `CSV text received for ${csvFile}, length:`,
                  csvText.length
                );
                // Check if we got HTML instead of CSV
                if (
                  csvText.includes("<!doctype html>") ||
                  csvText.includes("<html")
                ) {
                  console.error(`Received HTML instead of CSV for ${csvFile}`);
                  return [`${pumpName} - ${sensorType}`, []];
                }

                return new Promise((resolve) =>
                  Papa.parse(csvText, {
                    header: true,
                    dynamicTyping: true,
                    complete: (results) => {
                      console.log(`Parse results for ${csvFile}:`, {
                        rows: results.data.length,
                        errors: results.errors.length,
                        headers: results.meta.fields,
                      });

                      const cleaned = results.data.filter(
                        (row) =>
                          row.timestamp !== undefined &&
                          row.timestamp !== null &&
                          row.sensor_avg !== undefined &&
                          row.sensor_avg !== null
                      );
                      console.log(
                        `Cleaned data for ${csvFile}:`,
                        cleaned.length,
                        "rows"
                      );
                      resolve([`${pumpName} - ${sensorType}`, cleaned]);
                    },
                  })
                );
              })
              .catch((err) => {
                console.error(`Failed to load ${csvFile}:`, err);
                return [`${pumpName} - ${sensorType}`, []];
              });
          })
        )
      ).then((results) => {
        console.log("All results processed:", results.length);
        results.forEach(([chartKey, cleaned]) => {
          allData[chartKey] = cleaned;
          console.log(
            `Added to allData: ${chartKey} with ${cleaned.length} rows`
          );
        });
        setAllPumpData(allData);
        console.log("Final allPumpData keys:", Object.keys(allData));
      });
    } else {
      // Show specific pump
      setAllPumpData({});
      const pumpCsvFiles = pumpCsvMap[selectedPump];

      console.log(`CSV files for ${selectedPump}:`, pumpCsvFiles);

      if (pumpCsvFiles) {
        const pumpData = {};

        Promise.all(
          Object.entries(pumpCsvFiles).map(([sensorType, csvFile]) => {
            console.log(`Fetching ${csvFile} for ${sensorType}`);
            return fetch(csvFile)
              .then((res) => {
                console.log(`Response for ${csvFile}:`, res.status);
                if (!res.ok) {
                  throw new Error(`HTTP ${res.status}: ${res.statusText}`);
                }
                return res.text();
              })
              .then((csvText) => {
                console.log(`CSV text for ${csvFile}, length:`, csvText.length);
                // Check if we got HTML instead of CSV
                if (
                  csvText.includes("<!doctype html>") ||
                  csvText.includes("<html")
                ) {
                  console.error(`Received HTML instead of CSV for ${csvFile}`);
                  return [sensorType, []];
                }

                return new Promise((resolve) =>
                  Papa.parse(csvText, {
                    header: true,
                    dynamicTyping: false,
                    complete: (results) => {
                      console.log(
                        `Parse results for ${csvFile}:`,
                        results.data.length,
                        "rows"
                      );
                      const cleaned = results.data.filter(
                        (row) =>
                          row.timestamp !== undefined &&
                          row.timestamp !== null &&
                          row.sensor_avg !== undefined &&
                          row.sensor_avg !== null
                      );
                      console.log(
                        `Cleaned ${csvFile}:`,
                        cleaned.length,
                        "valid rows"
                      );
                      resolve([sensorType, cleaned]);
                    },
                  })
                );
              })
              .catch((err) => {
                console.error(`Failed to load ${csvFile}:`, err);
                return [sensorType, []];
              });
          })
        ).then((results) => {
          console.log(`Results for ${selectedPump}:`, results.length);
          results.forEach(([sensorType, cleaned]) => {
            pumpData[sensorType] = cleaned;
            console.log(`Added ${sensorType}: ${cleaned.length} rows`);
          });
          setAllPumpData(pumpData);
          console.log(
            `Set pump data for ${selectedPump}:`,
            Object.keys(pumpData)
          );
        });
      } else {
        console.error(`No CSV files mapping found for pump: ${selectedPump}`);
      }
    }
  }, [selectedPump, pumpCsvMap]);

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

  // Dropdown options include "Show All Pumps" and fetched pump names
  const pumpOptions = [allOption, ...allPumps.map((pump) => pump.name)];

  return (
    <div className="flex h-screen font-sans bg-[#f7f9fc]">
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
        <div className="flex justify-between items-center mt-4">
          <h2 className="text-2xl font-bold text-[#1e3a8a]">
            {selectedPump === allOption ? "All Pumps" : selectedPump}{" "}
          </h2>
          <select
            value={selectedPump}
            onChange={(e) => setSelectedPump(e.target.value)}
            className="px-4 py-2 rounded-md bg-[#2563eb] text-white font-semibold shadow-md"
          >
            {pumpOptions.map((pump) => (
              <option key={pump} value={pump}>
                {pump}
              </option>
            ))}
          </select>
        </div>

        {/* Live charts */}
        <section className="grid grid-cols-2 gap-6 mt-6">
          {Object.entries(allPumpData).map(([chartKey, pumpData]) => (
            <ChartCard
              key={chartKey}
              title={`Live Sensor Average - ${chartKey}`}
              chartId={chartKey}
              data={pumpData}
              selectedPump={selectedPump}
            />
          ))}
        </section>

        {/* Show message if no data */}
        {Object.keys(allPumpData).length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">Loading pump data...</p>
          </div>
        )}
      </main>

      {/* Reusable Chatbot Button */}
      <ChatbotButtonComponent />
    </div>
  );
}

function StatusCard({ title, value, desc, color }) {
  return (
    <div className={`p-4 rounded-xl text-white shadow-md ${color}`}>
      <h4 className="text-sm mb-1 font-medium">{title}</h4>
      <div className="text-2xl font-bold">{value}</div>
      <p className="text-sm mt-1">{desc}</p>
    </div>
  );
}

function cleanChartId(filename) {
  return filename.replace(/^\//, "").replace(/\.csv$/, "");
}

function ChartCard({ title, chartId, data, selectedPump }) {
  const navigate = useNavigate();

  return (
    <div className="bg-white p-4 rounded-xl shadow-md">
      <h4 className="font-semibold text-sm mb-2">{title}</h4>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="sensor_avg"
              stroke="#2563eb"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <button
        onClick={() => {
          const cleanId = cleanChartId(chartId);
          navigate(`/monitoring/${cleanId}`);
        }}
        className="mt-3 px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded"
      >
        Show More Information
      </button>
    </div>
  );
}

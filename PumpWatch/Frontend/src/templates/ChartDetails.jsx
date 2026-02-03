// src/pages/ChartDetails.jsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
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
import { TrendingUp, Database, Calendar, BarChart3 } from "lucide-react";

export default function ChartDetails() {
  const { chartId } = useParams();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ min: 0, max: 0, avg: 0, count: 0 });

  useEffect(() => {
    fetch(`/${chartId}.csv`)
      .then((response) => response.text())
      .then((csvText) => {
        Papa.parse(csvText, {
          header: true,
          dynamicTyping: false,
          complete: (results) => {
            const cleaned = results.data.filter(
              (row) => row.timestamp && row.sensor_avg !== undefined
            );
            setData(cleaned);

            if (cleaned.length > 0) {
              const values = cleaned.map((row) => row.sensor_avg);
              setStats({
                min: Math.min(...values),
                max: Math.max(...values),
                avg: values.reduce((a, b) => a + b, 0) / values.length,
                count: cleaned.length,
              });
            }
            setLoading(false);
          },
        });
      });
  }, [chartId]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/90 backdrop-blur-sm border border-gray-300 rounded-lg p-3 shadow-md">
          <p className="text-gray-800 text-sm font-medium">{`Time: ${label}`}</p>
          <p className="text-blue-700 text-sm font-semibold">
            {`Value: ${payload[0].value?.toFixed(2)}`}
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-200 via-blue-300 to-blue-400 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-2 border-blue-700 border-t-transparent"></div>
            <span className="ml-3 text-gray-900 text-lg">
              Loading sensor data...
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-200 via-blue-300 to-blue-400 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <div className="p-3 bg-blue-500/30 rounded-full">
              <TrendingUp className="w-8 h-8 text-blue-900" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
              {chartId} Sensor Dashboard
            </h1>
          </div>
          <p className="text-gray-800 text-lg max-w-2xl mx-auto">
            Real-time visualization of sensor average readings over time
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard
            icon={<Database className="w-8 h-8 text-gray-700" />}
            label="Total Records"
            value={stats.count.toLocaleString()}
          />
          <StatCard
            icon={<BarChart3 className="w-8 h-8 text-blue-800" />}
            label="Average"
            value={stats.avg.toFixed(1)}
          />
          <StatCard
            icon={<TrendingUp className="w-8 h-8 text-red-700" />}
            label="Maximum"
            value={stats.max.toFixed(1)}
          />
          <StatCard
            icon={<Calendar className="w-8 h-8 text-yellow-700" />}
            label="Minimum"
            value={stats.min.toFixed(1)}
          />
        </div>

        <div className="bg-white/70 backdrop-blur-md rounded-2xl p-8 border border-gray-300 shadow-md">
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Sensor Readings Timeline
            </h2>
            <p className="text-gray-700">
              Interactive chart showing sensor average values over time
            </p>
          </div>

          {data.length > 0 ? (
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={data}
                  margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                >
                  <defs>
                    <linearGradient
                      id="colorGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#1e40af" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#1e40af" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#cbd5e1"
                    opacity={0.5}
                  />
                  <XAxis
                    dataKey="timestamp"
                    tick={{ fontSize: 12, fill: "#334155" }}
                    stroke="#475569"
                    axisLine={{ stroke: "#cbd5e1" }}
                  />
                  <YAxis
                    tick={{ fontSize: 12, fill: "#334155" }}
                    stroke="#475569"
                    axisLine={{ stroke: "#cbd5e1" }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="sensor_avg"
                    stroke="#1e40af"
                    strokeWidth={3}
                    dot={{ fill: "#1e40af", strokeWidth: 2, r: 4 }}
                    activeDot={{
                      r: 6,
                      stroke: "#1e40af",
                      strokeWidth: 2,
                      fill: "#1e3a8a",
                    }}
                    fill="url(#colorGradient)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <Database className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-700 text-lg">No data available</p>
              </div>
            </div>
          )}
        </div>

        <div className="text-center">
          <p className="text-gray-700 text-sm">
            Data visualization powered by modern web technologies
          </p>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }) {
  return (
    <div className="bg-white/70 backdrop-blur-md rounded-xl p-6 border border-gray-300">
      <div className="flex items-center space-x-3">
        {icon}
        <div>
          <p className="text-gray-700 text-sm">{label}</p>
          <p className="text-gray-900 text-2xl font-bold">{value}</p>
        </div>
      </div>
    </div>
  );
}

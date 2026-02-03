import React from "react";
import { useNavigate } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function ChartCard({ title, chartId, data }) {
  const navigate = useNavigate();

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="timestamp"
          tickFormatter={(ts) => new Date(ts).toLocaleTimeString()}
          tick={{ fontSize: 10 }}
        />
        <YAxis />
        <Tooltip labelFormatter={(ts) => new Date(ts).toLocaleString()} />
        <Line
          type="monotone"
          dataKey="sensor_avg"
          stroke="#2563eb"
          dot={false} // hide points, just line
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

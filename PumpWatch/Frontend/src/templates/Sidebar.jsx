import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Home,
  BarChart,
  Monitor,
  AlertTriangle,
  Settings,
  HelpCircle,
  LogOut
} from "lucide-react";

export default function SidebarComponent({ currentPath, manageRoutes, prefRoutes }) {
  const navigate = useNavigate();

  return (
    <aside className="w-64 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 text-white p-6 flex flex-col justify-between">
      <div>
        {/* Logo Header */}
        <div className="bg-white text-blue-800 px-2 py-1 rounded-full font-black animate-pulse">
          <img src="/public/logo.png" alt="Logo" />
        </div>

        {/* Navigation */}
        <nav className="space-y-6">
          {/* Manage Section */}
          <div>
            <p className="text-sm text-gray-400 mb-1">Manage</p>
            <ul className="space-y-3">
              {Object.entries(manageRoutes).map(([label, path]) => {
                const isActive = currentPath === path;
                const Icon =
                  label === "Home"
                    ? Home
                    : label === "Analytics"
                    ? BarChart
                    : label === "Monitoring"
                    ? Monitor
                    : AlertTriangle;

                return (
                  <li
                    key={label}
                    onClick={() => navigate(path)}
                    className={`flex items-center gap-3 cursor-pointer ${
                      isActive
                        ? "text-blue-300 font-bold"
                        : "hover:text-blue-400"
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {label}
                  </li>
                );
              })}
            </ul>
          </div>

          {/* Preferences Section */}
          <div>
            <p className="text-sm text-gray-400 mt-6 mb-1">Preferences</p>
            <ul className="space-y-3">
              {Object.entries(prefRoutes).map(([label, path]) => {
                const isActive = currentPath === path;
                const Icon =
                  label === "Settings"
                    ? Settings
                    : label === "Help"
                    ? HelpCircle
                    : HelpCircle;

                return (
                  <li
                    key={label}
                    onClick={() => navigate(path)}
                    className={`flex items-center gap-3 cursor-pointer ${
                      isActive
                        ? "text-blue-300 font-bold"
                        : "hover:text-blue-400"
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {label}
                  </li>
                );
              })}
            </ul>
          </div>
        </nav>
      </div>

      {/* Footer */}
      <div>
        <div
          onClick={() => navigate("/login")}
          className="flex items-center gap-3 cursor-pointer hover:text-red-400"
        >
          <LogOut className="w-5 h-5" />
          Log Out
        </div>
        <p className="text-[10px] mt-4 text-gray-400">
          PumpWatch all rights reserved 2024
        </p>
      </div>
    </aside>
  );
}

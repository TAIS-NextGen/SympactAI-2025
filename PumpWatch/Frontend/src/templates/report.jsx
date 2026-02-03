import React from "react";
import { Home, BarChart, Monitor, AlertTriangle, Settings, HelpCircle, LogOut } from "lucide-react";

export default function ReportPage() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 text-white p-6 flex flex-col justify-between">
        <div>
         {/* Logo Header */}
          <div className="bg-white text-blue-800 px-2 py-1 rounded-full font-black animate-pulse">
              <img src="/public/logo.png" alt="" />
            </div>

          {/* Navigation */}

          <nav className="space-y-6">
            <div>
              <p className="text-sm text-gray-400 mb-1">Manage</p>
              <ul className="space-y-3">
                <li className="flex items-center gap-3 cursor-pointer hover:text-blue-400">
                  <Home className="w-5 h-5" />
                  Home
                </li>
                <li className="flex items-center gap-3 cursor-pointer hover:text-blue-400">
                  <BarChart className="w-5 h-5" />
                  Analytics
                </li>
                <li className="flex items-center gap-3 cursor-pointer hover:text-blue-400">
                  <Monitor className="w-5 h-5" />
                  Monitoring
                </li>
                <li className="flex items-center gap-3 text-blue-300 font-bold">
                  <AlertTriangle className="w-5 h-5" />
                  Alerts
                </li>
              </ul>
            </div>
            <div>
              <p className="text-sm text-gray-400 mt-6 mb-1">Preferences</p>
              <ul className="space-y-3">
                <li className="flex items-center gap-3 cursor-pointer hover:text-blue-400">
                  <Settings className="w-5 h-5" />
                  Settings
                </li>
                <li className="flex items-center gap-3 cursor-pointer hover:text-blue-400">
                  <HelpCircle className="w-5 h-5" />
                  Help
                </li>
              </ul>
            </div>
          </nav>
        </div>
        <div className="flex items-center gap-3 cursor-pointer hover:text-red-400">
          <LogOut className="w-5 h-5" />
          Log Out
        </div>
        <p className="text-[10px] mt-4 text-gray-400">PumpWatch all rights reserved 2024</p>
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-white p-8 overflow-y-auto">
        {/* Top Bar */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold">Welcome Back, Ammar!</h1>
            <p className="text-gray-500">Here’s what’s happening with your pumps!</p>
          </div>
          <div className="flex items-center gap-4">
            <button className="text-gray-600 hover:text-black">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8" strokeWidth="2" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" strokeWidth="2" />
              </svg>
            </button>
            <button className="text-gray-600 hover:text-black">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>
            <div className="flex items-center gap-2">
              <img src="https://via.placeholder.com/32" className="rounded-full" alt="User" />
              <div className="text-sm">
                <div className="font-semibold">Ammar Labiedh</div>
                <div className="text-gray-400 text-xs">ID 02943</div>
              </div>
            </div>
          </div>
        </div>

        {/* Report Header */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold">CP-12398 System Failure</h2>
          <p className="text-gray-500">Pump System Failure CP-12398 (10 November 2024 – 11:21 PM GMT+1)</p>
        </div>

        {/* Date Selector */}
        <div className="mb-6">
          <button className="bg-blue-500 text-white px-4 py-1 rounded-full">Saturday 16 November 2024</button>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left */}
          <div>
            <h3 className="font-bold text-lg mb-2">Details</h3>
            <p><strong>Issue:</strong> The pump experienced a failure due to an abnormal rise in temperature, likely caused by excessive friction or a cooling system malfunction.</p>
          </div>

          {/* Right */}
          <div>
            <h3 className="font-bold text-lg mb-2">Temperature Spike</h3>
            <p>Temperature rose above the operational threshold, triggering a shutdown to prevent damage.</p>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-2">Impacts</h3>
            <p><strong>Production Disruption:</strong> Temporary halt in operations for 15 Unit Per Line.</p>
            <p className="mt-2"><strong>Downtime:</strong><br />10th Of November 2024 at 11:21:18 PM GMT+1</p>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-2">Next Steps</h3>
            <p>Immediate inspection and maintenance by the engineering team to identify and rectify the root cause of overheating.</p>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-2">Preventive Measures</h3>
            <p><strong>Monitor Temperature Trends:</strong><br />Adjust thresholds and increase monitoring frequency for early anomaly detection.</p>
          </div>

          <div>
            <h3 className="font-bold text-lg mb-2 invisible">Spacer</h3>
            <p><strong>Review Cooling System:</strong><br />Conduct regular checks on cooling mechanisms and lubrication systems.</p>
          </div>
        </div>

        {/* Download Button */}
        <div className="mt-8">
          <button className="bg-blue-800 text-white px-6 py-2 rounded-full">Download Report as PNG</button>
        </div>
      </main>
    </div>
  );
}

// import React from "react";
// import { Bell, User, ChevronLeft, FileText, LogOut } from "lucide-react";
// import { useNavigate } from "react-router-dom";

// export default function PumpAlertsPage() {
//     const navigate = useNavigate();
//     const navItemsManage = ["Home", "Analytics", "Monitoring", "Alerts"];
//     const navItemsPreferences = ["Settings", "Help", "Our Service Providers"];

//     const handleNavigation = (label) => {
//       const path = "/" + label.toLowerCase().replace(/\s+/g, "-");
//       navigate(path);
//       };

//   return (
//     <div className="flex h-screen font-sans">
//       {/* Sidebar */}
//       <aside className="w-64 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 text-white p-6">
//        <div className="text-3xl font-bold mb-10">
//           <div className="flex items-center gap-2 hover:scale-105 transition-transform cursor-pointer">
//             <div className="bg-white text-blue-800 px-2 py-1 rounded-full font-black animate-pulse">
//               <img src="/public/logo.png" alt="" />
//             </div>
//           </div>
//         </div>

//         <nav className="space-y-2">
//           <p className="text-sm text-gray-300 mb-2">Manage</p>
//           {navItemsManage.map((item) => (
//             <button
//               key={item}
//               onClick={() => handleNavigation(item)}
//               className={`w-full text-left py-2 px-4 rounded-md transition ${
//                 item === "Alerts"
//                   ? "bg-white text-[#1e3a8a] font-semibold"
//                   : "hover:bg-blue-700"
//               }`}
//             >
//               {item}
//             </button>
//           ))}

//           <p className="text-sm text-gray-300 mt-6 mb-2">Preferences</p>
//           {navItemsPreferences.map((item) => (
//             <button
//               key={item}
//               onClick={() => handleNavigation(item)}
//               className="w-full text-left py-2 px-4 rounded-md hover:bg-blue-700"
//             >
//               {item}
//             </button>
//           ))}

//           <button
//             onClick={() => handleNavigation("logout")}
//             className="mt-2 text-sm hover:text-red-400"
//           >
//             Log Out
//           </button>
//         </nav>

//         <footer className="absolute bottom-4 left-6 text-xs text-gray-300">
//           PumpWatch © all rights reserved 2024
//         </footer>
//       </aside>

//       {/* Main Content */}
//       <main className="flex-1 overflow-y-auto bg-gray-100">
//         {/* Header */}
//         <header className="flex items-center justify-between bg-white p-4 shadow">
//           <h1 className="text-xl font-semibold">Welcome Back, username!</h1>
//           <div className="flex items-center gap-4">
//             <Bell className="w-5 h-5 text-gray-600" />
//             <div className="flex items-center gap-2">
//               <User className="w-6 h-6 text-gray-600" />
//               <span className="text-gray-800 text-sm">username</span>
//             </div>
//           </div>
//         </header>

//         {/* Alerts Summary */}
//         <section className="p-6">
//           <div className="flex items-center justify-between">
//             <h2 className="text-lg font-bold">Check Out Your Latest Alerts</h2>
//             <button className="bg-blue-600 text-white text-sm px-3 py-1 rounded">
//               Saturday 16 November 2024
//             </button>
//           </div>

//           <div className="mt-4 bg-white rounded-lg shadow p-4 overflow-x-auto">
//             <table className="w-full text-sm text-left">
//               <thead className="text-gray-500 border-b">
//                 <tr>
//                   <th className="p-2">Pump Name</th>
//                   <th className="p-2">ID</th>
//                   <th className="p-2">Date</th>
//                   <th className="p-2">Time</th>
//                   <th className="p-2">Status</th>
//                   <th className="p-2">Pressure</th>
//                   <th className="p-2">Vibration</th>
//                   <th className="p-2">Temperature</th>
//                 </tr>
//               </thead>
//               <tbody>
//                 <tr className="bg-red-50">
//                   <td className="p-2">CP-12398</td>
//                   <td className="p-2">12398</td>
//                   <td className="p-2">10 Nov</td>
//                   <td className="p-2">11:21PM</td>
//                   <td className="p-2 text-red-500 font-bold">Error</td>
//                   <td className="p-2">17 PSI</td>
//                   <td className="p-2">9.3</td>
//                   <td className="p-2 text-red-600">121°C</td>
//                 </tr>
//                 {/* Add more rows as needed */}
//               </tbody>
//             </table>
//           </div>

//           {/* Actions and Previous Reports */}
//           <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
//             <div className="bg-white shadow rounded-lg p-4">
//               <h3 className="font-bold text-sm mb-2">Actions Required</h3>
//               <p className="text-blue-600 font-semibold text-lg">Current Status: Error</p>
//               <p className="text-sm text-gray-500 mt-2">Temperature Spike detected in Pump CP-12398</p>
//             </div>
//             <div className="bg-white shadow rounded-lg p-4 md:col-span-2">
//               <h3 className="font-bold text-sm mb-2">View or Download Previous Reports</h3>
//               <div className="grid grid-cols-2 gap-2">
//                 {[...Array(4)].map((_, i) => (
//                   <div
//                     key={i}
//                     className="border p-2 rounded text-xs flex items-center gap-2 hover:bg-gray-100 cursor-pointer"
//                   >
//                     <FileText size={14} /> Report_{i + 1}.pdf
//                   </div>
//                 ))}
//               </div>
//             </div>
//           </div>
//         </section>

//         {/* Detailed Alert Page */}
//         <section className="p-6 pt-0">
//           <div className="flex items-center gap-2 mb-2">
//             <ChevronLeft className="w-5 h-5 text-blue-600" />
//             <h2 className="text-lg font-bold">CP-12398 System Failure</h2>
//           </div>

//           <p className="text-sm text-gray-500 mb-2">Pump System Failure CP-12398 - 10 November 2024</p>

//           <div className="bg-white shadow rounded-lg p-4">
//             <h3 className="font-semibold mb-1">CP-12398 System Failure Recap</h3>
//             <p className="text-sm text-gray-600">
//               The pump experienced a failure due to an abnormal rise in temperature, likely caused by excessive friction
//               or a cooling system malfunction.
//             </p>
//             <p className="text-sm text-gray-600 mt-1">
//               <strong>Temperature Spike:</strong> Temperature rose above the operational threshold, triggering a shutdown
//               to prevent damage.
//             </p>
//             <button className="mt-4 bg-blue-600 text-white px-3 py-1 rounded text-sm">
//               Generate Detailed Report
//             </button>

//             <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
//               {/* Chart placeholders */}
//               {["Temp. Values", "Line Pressure", "Vibration", "Flow Rate"].map((title, index) => (
//                 <div
//                   key={index}
//                   className="border rounded-md p-4 bg-gray-50 text-sm text-center text-gray-600"
//                 >
//                   <p className="mb-2 font-semibold">{title} CP-12398 (10/11/24 - 11:21 PM)</p>
//                   <div className="h-32 bg-white border-dashed border-2 border-gray-300 flex items-center justify-center">
//                     Chart Placeholder
//                   </div>
//                 </div>
//               ))}
//             </div>
//           </div>
//         </section>
//       </main>
//     </div>
//   );
// }
import React from "react";
import { Bell, User, ChevronLeft, FileText, LogOut } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

export default function PumpAlertsPage() {
  const navigate = useNavigate();
  const { pumpId } = useParams(); // Get pump ID from URL
  const navItemsManage = ["Home", "Analytics", "Monitoring", "Alerts"];
  const navItemsPreferences = ["Settings", "Help", "Our Service Providers"];

  const handleNavigation = (label) => {
    const path = "/" + label.toLowerCase().replace(/\s+/g, "-");
    navigate(path);
  };

  return (
    <div className="flex h-screen font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 text-white p-6">
        <div className="text-3xl font-bold mb-10">
          <div className="flex items-center gap-2 hover:scale-105 transition-transform cursor-pointer">
            <div className="bg-white text-blue-800 px-2 py-1 rounded-full font-black animate-pulse">
              <img src="/public/logo.png" alt="" />
            </div>
          </div>
        </div>

        <nav className="space-y-2">
          <p className="text-sm text-gray-300 mb-2">Manage</p>
          {navItemsManage.map((item) => (
            <button
              key={item}
              onClick={() => handleNavigation(item)}
              className={`w-full text-left py-2 px-4 rounded-md transition ${
                item === "Alerts"
                  ? "bg-white text-[#1e3a8a] font-semibold"
                  : "hover:bg-blue-700"
              }`}
            >
              {item}
            </button>
          ))}

          <p className="text-sm text-gray-300 mt-6 mb-2">Preferences</p>
          {navItemsPreferences.map((item) => (
            <button
              key={item}
              onClick={() => handleNavigation(item)}
              className="w-full text-left py-2 px-4 rounded-md hover:bg-blue-700"
            >
              {item}
            </button>
          ))}

          <button
            onClick={() => handleNavigation("logout")}
            className="mt-2 text-sm hover:text-red-400"
          >
            Log Out
          </button>
        </nav>

        <footer className="absolute bottom-4 left-6 text-xs text-gray-300">
          PumpWatch © all rights reserved 2024
        </footer>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-gray-100">
        {/* Header */}
        <header className="flex items-center justify-between bg-white p-4 shadow">
          <h1 className="text-xl font-semibold">Welcome Back, username!</h1>
          <div className="flex items-center gap-4">
            <Bell className="w-5 h-5 text-gray-600" />
            <div className="flex items-center gap-2">
              <User className="w-6 h-6 text-gray-600" />
              <span className="text-gray-800 text-sm">username</span>
            </div>
          </div>
        </header>

        {/* Alerts Summary */}
        <section className="p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">Check Out Your Latest Alerts</h2>
            <button className="bg-blue-600 text-white text-sm px-3 py-1 rounded">
              Saturday 16 November 2024
            </button>
          </div>

          <div className="mt-4 bg-white rounded-lg shadow p-4 overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-gray-500 border-b">
                <tr>
                  <th className="p-2">Pump Name</th>
                  <th className="p-2">ID</th>
                  <th className="p-2">Date</th>
                  <th className="p-2">Time</th>
                  <th className="p-2">Status</th>
                  <th className="p-2">Pressure</th>
                  <th className="p-2">Vibration</th>
                  <th className="p-2">Temperature</th>
                </tr>
              </thead>
              <tbody>
                <tr className="bg-red-50">
                  <td className="p-2">{pumpId?.toUpperCase()}</td>
                  <td className="p-2">{pumpId?.split("-")[1]}</td>
                  <td className="p-2">10 Nov</td>
                  <td className="p-2">11:21PM</td>
                  <td className="p-2 text-red-500 font-bold">Error</td>
                  <td className="p-2">17 PSI</td>
                  <td className="p-2">9.3</td>
                  <td className="p-2 text-red-600">121°C</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Actions and Previous Reports */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-white shadow rounded-lg p-4">
              <h3 className="font-bold text-sm mb-2">Actions Required</h3>
              <p className="text-blue-600 font-semibold text-lg">
                Current Status: Error
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Temperature Spike detected in Pump {pumpId?.toUpperCase()}
              </p>
            </div>
            <div className="bg-white shadow rounded-lg p-4 md:col-span-2">
              <h3 className="font-bold text-sm mb-2">
                View or Download Previous Reports
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {[...Array(4)].map((_, i) => (
                  <div
                    key={i}
                    className="border p-2 rounded text-xs flex items-center gap-2 hover:bg-gray-100 cursor-pointer"
                  >
                    <FileText size={14} /> Report_{i + 1}.pdf
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Detailed Alert Page */}
        <section className="p-6 pt-0">
          <div className="flex items-center gap-2 mb-2">
            <ChevronLeft className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-bold">{pumpId?.toUpperCase()} System Failure</h2>
          </div>

          <p className="text-sm text-gray-500 mb-2">
            Pump System Failure {pumpId?.toUpperCase()} - 10 November 2024
          </p>

          <div className="bg-white shadow rounded-lg p-4">
            <h3 className="font-semibold mb-1">{pumpId?.toUpperCase()} System Failure Recap</h3>
            <p className="text-sm text-gray-600">
              The pump experienced a failure due to an abnormal rise in temperature,
              likely caused by excessive friction or a cooling system malfunction.
            </p>
            <p className="text-sm text-gray-600 mt-1">
              <strong>Temperature Spike:</strong> Temperature rose above the
              operational threshold, triggering a shutdown to prevent damage.
            </p>
            <button className="mt-4 bg-blue-600 text-white px-3 py-1 rounded text-sm">
              Generate Detailed Report
            </button>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              {["Temp. Values", "Line Pressure", "Vibration", "Flow Rate"].map(
                (title, index) => (
                  <div
                    key={index}
                    className="border rounded-md p-4 bg-gray-50 text-sm text-center text-gray-600"
                  >
                    <p className="mb-2 font-semibold">
                      {title} {pumpId?.toUpperCase()} (10/11/24 - 11:21 PM)
                    </p>
                    <div className="h-32 bg-white border-dashed border-2 border-gray-300 flex items-center justify-center">
                      Chart Placeholder
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

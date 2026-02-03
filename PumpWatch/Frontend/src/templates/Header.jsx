import React from "react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Bell } from "lucide-react";


export default function HeaderComponent({ username , lastname, userId }) {
  const navigate = useNavigate();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [notifications, setNotifications] = useState(3);
  useEffect(() => {
      const timer = setInterval(() => {
        setCurrentTime(new Date());
      }, 1000);
      return () => clearInterval(timer);
    }, []);
    const clearNotifications = () => {
    setNotifications(0);
  };

  return (
    <div className="flex items-center justify-between border-b pb-4">
      <div>
        <h2 className="text-2xl font-semibold">Welcome Back, {username}!</h2>
        <p className="text-gray-500 text-sm">Here's what's happening with your pumps!</p>
        <p className="text-xs text-gray-400 mt-1">
              {currentTime.toLocaleTimeString()} - {currentTime.toLocaleDateString()}
            </p>
      </div>
      <div className="flex items-center gap-4">
        <button className="rounded-full p-2 bg-gray-200 hover:bg-gray-300 transition-colors hover:scale-110 transform">
              <Search size={20} />
            </button>
            <button 
              onClick={clearNotifications}
              className="rounded-full p-2 bg-gray-200 hover:bg-gray-300 transition-all transform hover:scale-110 relative"
            >
              <Bell size={20} />
              {notifications > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-bounce">
                  {notifications}
                </span>
              )}
            </button>
        <div className="flex items-center gap-2 cursor-pointer">
          <div className="text-sm">
            <p>{username} {lastname}</p>
            <p className="text-gray-400 text-xs">ID {userId}</p>
          </div>
          <span className="text-lg">▾</span>
        </div>
      </div>
    </div>
  );
}

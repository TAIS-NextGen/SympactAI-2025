import React, { useEffect, useState } from "react";
import {
  User,
  Bell,
  Shield,
  Palette,
  Database,
  Globe,
  Save,
  RotateCcw,
  Eye,
  EyeOff,
  Lock,
  Mail,
  Phone,
  CheckCircle,
} from "lucide-react";
import HeaderComponent from "./Header";
import SidebarComponent from "./Sidebar";
import ChatbotButtonComponent from "./ChatbotButton";

// Mock components - replace with your actual imports

export default function SettingsPage() {
  const currentPath = "/settings";
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
  // Settings states
  const [profile, setProfile] = useState({
    firstName: "John",
    lastName: "Doe",
    email: "john.doe@company.com",
    phone: "+1 (555) 123-4567",
    department: "Operations",
  });

  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    smsAlerts: false,
    pushNotifications: true,
    weeklyReports: true,
    criticalAlerts: true,
  });

  const [security, setSecurity] = useState({
    twoFactorAuth: false,
    sessionTimeout: "30",
    passwordExpiry: "90",
  });

  const [system, setSystem] = useState({
    theme: "light",
    language: "en",
    timezone: "UTC-5",
    dateFormat: "MM/DD/YYYY",
    dataRetention: "12",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleProfileChange = (field, value) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleNotificationChange = (field) => {
    setNotifications((prev) => ({ ...prev, [field]: !prev[field] }));
    setHasChanges(true);
  };

  const handleSecurityChange = (field, value) => {
    setSecurity((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleSystemChange = (field, value) => {
    setSystem((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleSave = () => {
    // Save logic here
    setHasChanges(false);
    alert("Settings saved successfully!");
  };

  const handleReset = () => {
    // Reset to defaults
    setHasChanges(false);
    alert("Settings reset to defaults!");
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

        <div className="flex justify-between items-center mt-4 mb-6">
          <h2 className="text-2xl font-bold text-[#1e3a8a]">Settings</h2>
          <div className="flex gap-3">
            {hasChanges && (
              <button
                onClick={handleReset}
                className="px-4 py-2 text-[#2563eb] bg-gray-100 hover:bg-gray-200 rounded-lg transition-all flex items-center gap-2"
              >
                <RotateCcw size={16} />
                Reset
              </button>
            )}
            <button
              onClick={handleSave}
              disabled={!hasChanges}
              className={`px-6 py-2 rounded-lg transition-all flex items-center gap-2 ${
                hasChanges
                  ? "bg-[#2563eb] hover:bg-[#1e3a8a] text-white shadow-md"
                  : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
            >
              <Save size={16} />
              Save Changes
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Profile Settings */}
          <SettingsSection
            title="Profile Information"
            icon={<User className="text-[#2563eb]" size={20} />}
          >
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={profile.firstName}
                    onChange={(e) =>
                      handleProfileChange("firstName", e.target.value)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={profile.lastName}
                    onChange={(e) =>
                      handleProfileChange("lastName", e.target.value)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <div className="relative">
                  <Mail
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                    size={16}
                  />
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) =>
                      handleProfileChange("email", e.target.value)
                    }
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone
                </label>
                <div className="relative">
                  <Phone
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                    size={16}
                  />
                  <input
                    type="tel"
                    value={profile.phone}
                    onChange={(e) =>
                      handleProfileChange("phone", e.target.value)
                    }
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <select
                  value={profile.department}
                  onChange={(e) =>
                    handleProfileChange("department", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                >
                  <option value="Operations">Operations</option>
                  <option value="Engineering">Engineering</option>
                  <option value="Maintenance">Maintenance</option>
                  <option value="Management">Management</option>
                </select>
              </div>
            </div>
          </SettingsSection>

          {/* Notification Settings */}
          <SettingsSection
            title="Notification Preferences"
            icon={<Bell className="text-[#2563eb]" size={20} />}
          >
            <div className="space-y-4">
              {Object.entries(notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700 cursor-pointer">
                    {key
                      .replace(/([A-Z])/g, " $1")
                      .replace(/^./, (str) => str.toUpperCase())}
                  </label>
                  <button
                    onClick={() => handleNotificationChange(key)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      value ? "bg-[#2563eb]" : "bg-gray-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        value ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </SettingsSection>

          {/* Security Settings */}
          <SettingsSection
            title="Security & Privacy"
            icon={<Shield className="text-[#2563eb]" size={20} />}
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">
                  Two-Factor Authentication
                </label>
                <button
                  onClick={() =>
                    handleSecurityChange(
                      "twoFactorAuth",
                      !security.twoFactorAuth
                    )
                  }
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    security.twoFactorAuth ? "bg-[#2563eb]" : "bg-gray-300"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      security.twoFactorAuth ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Session Timeout (minutes)
                </label>
                <select
                  value={security.sessionTimeout}
                  onChange={(e) =>
                    handleSecurityChange("sessionTimeout", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                >
                  <option value="15">15 minutes</option>
                  <option value="30">30 minutes</option>
                  <option value="60">1 hour</option>
                  <option value="120">2 hours</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password Expiry (days)
                </label>
                <select
                  value={security.passwordExpiry}
                  onChange={(e) =>
                    handleSecurityChange("passwordExpiry", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                >
                  <option value="30">30 days</option>
                  <option value="60">60 days</option>
                  <option value="90">90 days</option>
                  <option value="never">Never expire</option>
                </select>
              </div>
              <button className="w-full px-4 py-2 bg-gradient-to-r from-[#7c3aed] to-[#8b5cf6] text-white rounded-lg hover:shadow-md transition-all flex items-center justify-center gap-2">
                <Lock size={16} />
                Change Password
              </button>
            </div>
          </SettingsSection>

          {/* System Preferences */}
          <SettingsSection
            title="System Preferences"
            icon={<Palette className="text-[#2563eb]" size={20} />}
          >
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Theme
                </label>
                <select
                  value={system.theme}
                  onChange={(e) => handleSystemChange("theme", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Language
                </label>
                <select
                  value={system.language}
                  onChange={(e) =>
                    handleSystemChange("language", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                >
                  <option value="en">English</option>
                  <option value="fr">French</option>
                  <option value="es">Spanish</option>
                  <option value="de">German</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Timezone
                </label>
                <select
                  value={system.timezone}
                  onChange={(e) =>
                    handleSystemChange("timezone", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                >
                  <option value="UTC-5">Eastern Time (UTC-5)</option>
                  <option value="UTC-6">Central Time (UTC-6)</option>
                  <option value="UTC-7">Mountain Time (UTC-7)</option>
                  <option value="UTC-8">Pacific Time (UTC-8)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date Format
                </label>
                <select
                  value={system.dateFormat}
                  onChange={(e) =>
                    handleSystemChange("dateFormat", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                >
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>
            </div>
          </SettingsSection>
        </div>

        {/* Data Management Section */}
        <div className="mt-8">
          <SettingsSection
            title="Data Management"
            icon={<Database className="text-[#2563eb]" size={20} />}
            fullWidth
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-r from-blue-100 to-blue-200 p-4 rounded-xl">
                <h4 className="font-semibold text-[#1e3a8a] mb-2">
                  Data Retention
                </h4>
                <p className="text-sm text-gray-600 mb-3">
                  How long to keep pump data
                </p>
                <select
                  value={system.dataRetention}
                  onChange={(e) =>
                    handleSystemChange("dataRetention", e.target.value)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
                >
                  <option value="6">6 months</option>
                  <option value="12">12 months</option>
                  <option value="24">24 months</option>
                  <option value="36">36 months</option>
                </select>
              </div>

              <div className="bg-gradient-to-r from-purple-100 to-purple-200 p-4 rounded-xl">
                <h4 className="font-semibold text-[#1e3a8a] mb-2">
                  Export Data
                </h4>
                <p className="text-sm text-gray-600 mb-3">
                  Download your pump data
                </p>
                <button className="w-full px-4 py-2 bg-gradient-to-r from-[#7c3aed] to-[#8b5cf6] text-white rounded-lg hover:shadow-md transition-all">
                  Export CSV
                </button>
              </div>

              <div className="bg-gradient-to-r from-indigo-100 to-indigo-200 p-4 rounded-xl">
                <h4 className="font-semibold text-[#1e3a8a] mb-2">
                  Backup Settings
                </h4>
                <p className="text-sm text-gray-600 mb-3">
                  Automatic data backup
                </p>
                <button className="w-full px-4 py-2 bg-gradient-to-r from-[#4f46e5] to-[#6366f1] text-white rounded-lg hover:shadow-md transition-all">
                  Configure Backup
                </button>
              </div>
            </div>
          </SettingsSection>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-[#1e3a8a] mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <QuickActionCard
              title="System Health Check"
              desc="Run diagnostics"
              color="bg-gradient-to-r from-[#32d296] to-[#0fa9a3]"
              icon={<CheckCircle className="text-white" size={20} />}
            />
            <QuickActionCard
              title="Generate Report"
              desc="Monthly summary"
              color="bg-gradient-to-r from-[#2563eb] to-[#1e3a8a]"
              icon={<Database className="text-white" size={20} />}
            />
            <QuickActionCard
              title="Update Firmware"
              desc="Check for updates"
              color="bg-gradient-to-r from-[#7c3aed] to-[#8b5cf6]"
              icon={<Globe className="text-white" size={20} />}
            />
            <QuickActionCard
              title="Contact Support"
              desc="Get help"
              color="bg-gradient-to-r from-[#4f46e5] to-[#6366f1]"
              icon={<Bell className="text-white" size={20} />}
            />
          </div>
        </div>
      </main>

      <ChatbotButtonComponent />
    </div>
  );
}

function SettingsSection({ title, icon, children, fullWidth = false }) {
  return (
    <div
      className={`bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6 ${
        fullWidth ? "col-span-full" : ""
      }`}
    >
      <div className="flex items-center gap-3 mb-4 pb-3 border-b border-gray-100">
        {icon}
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function QuickActionCard({ title, desc, color, icon }) {
  return (
    <button
      className={`${color} p-4 rounded-xl text-white shadow-sm hover:shadow-md transition-all duration-200 hover:scale-105 cursor-pointer text-left`}
    >
      <div className="flex items-center justify-between mb-2">{icon}</div>
      <div className="text-sm font-medium">{title}</div>
      <div className="text-xs opacity-90">{desc}</div>
    </button>
  );
}

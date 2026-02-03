import React, { useEffect, useState } from "react";
import {
  Star,
  MapPin,
  Phone,
  Mail,
  Globe,
  Calendar,
  CheckCircle,
  Clock,
  DollarSign,
  Award,
  Filter,
  Search,
} from "lucide-react";
import ChatbotButtonComponent from "./ChatbotButton";
import HeaderComponent from "./Header";
import SidebarComponent from "./Sidebar";

export default function ServiceProvidersPage() {
  const currentPath = "/providers";
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

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedProvider, setSelectedProvider] = useState(null);
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
  const serviceProviders = [
    {
      id: 1,
      name: "PumpTech Solutions",
      category: "Maintenance",
      rating: 4.8,
      reviews: 127,
      location: "New York, NY",
      phone: "+1 (555) 123-4567",
      email: "contact@pumptech.com",
      website: "www.pumptech.com",
      services: [
        "Emergency Repair",
        "Preventive Maintenance",
        "Parts Replacement",
      ],
      responseTime: "2 hours",
      availability: "24/7",
      price: "$150/hour",
      certification: "ISO 9001",
      description:
        "Leading pump maintenance specialists with over 20 years of experience in industrial pump systems.",
      image: "../assets/Pumptech-logo.png",
    },
    {
      id: 2,
      name: "Industrial Pump Experts",
      category: "Installation",
      rating: 4.6,
      reviews: 89,
      location: "Chicago, IL",
      phone: "+1 (555) 987-6543",
      email: "info@pumpexperts.com",
      website: "www.pumpexperts.com",
      services: ["New Installation", "System Design", "Consultation"],
      responseTime: "4 hours",
      availability: "Mon-Fri 8AM-6PM",
      price: "$200/hour",
      certification: "ASME Certified",
      description:
        "Specialized in complex pump installations and system optimization for maximum efficiency.",
      image: "./assets/Pumpexperts-logo.png",
    },
    {
      id: 3,
      name: "Reliable Pump Services",
      category: "Parts & Supply",
      rating: 4.9,
      reviews: 203,
      location: "Houston, TX",
      phone: "+1 (555) 456-7890",
      email: "sales@reliablepump.com",
      website: "www.reliablepump.com",
      services: ["OEM Parts", "Custom Components", "Inventory Management"],
      responseTime: "1 day",
      availability: "Mon-Sat 7AM-7PM",
      price: "Market Rate",
      certification: "Authorized Dealer",
      description:
        "Comprehensive parts supplier with extensive inventory and fast delivery nationwide.",
      image: "https://via.placeholder.com/100x100/32d296/ffffff?text=RPS",
    },
    {
      id: 4,
      name: "Emergency Pump Response",
      category: "Emergency",
      rating: 4.7,
      reviews: 156,
      location: "Dallas, TX",
      phone: "+1 (555) 911-PUMP",
      email: "emergency@pumpresponse.com",
      website: "www.pumpresponse.com",
      services: [
        "Emergency Repair",
        "24/7 Support",
        "Critical Failure Recovery",
      ],
      responseTime: "30 minutes",
      availability: "24/7/365",
      price: "$300/hour",
      certification: "Emergency Response Certified",
      description:
        "Rapid response team for critical pump failures and emergency situations.",
      image: "https://via.placeholder.com/100x100/ef4444/ffffff?text=EPR",
    },
  ];

  const categories = [
    "All",
    "Maintenance",
    "Installation",
    "Parts & Supply",
    "Emergency",
  ];

  const filteredProviders = serviceProviders.filter((provider) => {
    const matchesSearch =
      provider.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      provider.services.some((service) =>
        service.toLowerCase().includes(searchQuery.toLowerCase())
      );
    const matchesCategory =
      selectedCategory === "All" || provider.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

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
          <h2 className="text-2xl font-bold text-[#1e3a8a]">
            Our Service Providers
          </h2>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">
              {filteredProviders.length} providers available
            </span>
          </div>
        </div>

        {/* Stats Overview */}
        <section className="grid grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Providers"
            value="24"
            desc="Verified partners"
            color="bg-gradient-to-r from-[#2563eb] to-[#1e3a8a]"
            icon={<CheckCircle className="text-white" size={24} />}
          />
          <StatCard
            title="Average Rating"
            value="4.7"
            desc="Based on 1,200+ reviews"
            color="bg-gradient-to-r from-[#32d296] to-[#0fa9a3]"
            icon={<Star className="text-white" size={24} />}
          />
          <StatCard
            title="Avg Response Time"
            value="2.5h"
            desc="Emergency services"
            color="bg-gradient-to-r from-[#7c3aed] to-[#8b5cf6]"
            icon={<Clock className="text-white" size={24} />}
          />
          <StatCard
            title="Service Areas"
            value="15"
            desc="States covered"
            color="bg-gradient-to-r from-[#4f46e5] to-[#6366f1]"
            icon={<MapPin className="text-white" size={24} />}
          />
        </section>

        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              size={20}
            />
            <input
              type="text"
              placeholder="Search providers by name or service..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="text-gray-400" size={20} />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Service Providers Grid */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredProviders.map((provider) => (
            <ProviderCard
              key={provider.id}
              provider={provider}
              onSelect={() => setSelectedProvider(provider)}
              isSelected={selectedProvider?.id === provider.id}
            />
          ))}
        </section>
      </main>

      <ChatbotButtonComponent />
    </div>
  );
}

function StatCard({ title, value, desc, color, icon }) {
  return (
    <div
      className={`p-4 rounded-xl text-white shadow-md ${color} hover:shadow-lg transition-all duration-200 hover:scale-105`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="text-2xl font-bold">{value}</div>
        {icon}
      </div>
      <h4 className="text-sm font-medium opacity-90">{title}</h4>
      <p className="text-xs opacity-80 mt-1">{desc}</p>
    </div>
  );
}

function ProviderCard({ provider, onSelect, isSelected }) {
  return (
    <div
      className={`bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer border-2 ${
        isSelected
          ? "border-[#2563eb] shadow-lg"
          : "border-transparent hover:border-gray-200"
      }`}
      onClick={onSelect}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start gap-4 mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-gray-800">{provider.name}</h3>
              <span className="px-2 py-1 bg-blue-100 text-[#2563eb] text-xs rounded-full font-medium">
                {provider.category}
              </span>
            </div>
            <div className="flex items-center gap-2 mb-2">
              <div className="flex items-center gap-1">
                <Star className="text-yellow-400 fill-current" size={16} />
                <span className="text-sm font-medium">{provider.rating}</span>
                <span className="text-xs text-gray-500">
                  ({provider.reviews} reviews)
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1 text-sm text-gray-600">
              <MapPin size={14} />
              {provider.location}
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-semibold text-[#2563eb]">
              {provider.price}
            </div>
            <div className="text-xs text-gray-500">Starting rate</div>
          </div>
        </div>

        {/* Services */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Services Offered
          </h4>
          <div className="flex flex-wrap gap-2">
            {provider.services.map((service, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
              >
                {service}
              </span>
            ))}
          </div>
        </div>

        {/* Key Info */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center p-2 bg-green-50 rounded-lg">
            <Clock className="text-green-600 mx-auto mb-1" size={16} />
            <div className="text-xs font-medium text-green-700">Response</div>
            <div className="text-xs text-green-600">
              {provider.responseTime}
            </div>
          </div>
          <div className="text-center p-2 bg-blue-50 rounded-lg">
            <Calendar className="text-blue-600 mx-auto mb-1" size={16} />
            <div className="text-xs font-medium text-blue-700">
              Availability
            </div>
            <div className="text-xs text-blue-600">{provider.availability}</div>
          </div>
          <div className="text-center p-2 bg-purple-50 rounded-lg">
            <Award className="text-purple-600 mx-auto mb-1" size={16} />
            <div className="text-xs font-medium text-purple-700">Certified</div>
            <div className="text-xs text-purple-600">
              {provider.certification}
            </div>
          </div>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 mb-4">{provider.description}</p>

        {/* Contact Actions */}
        <div className="flex gap-2">
          <button className="flex-1 px-4 py-2 bg-[#2563eb] hover:bg-[#1e3a8a] text-white rounded-lg transition-all flex items-center justify-center gap-2 text-sm font-medium">
            <Phone size={14} />
            Call Now
          </button>
          <button className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-all flex items-center justify-center gap-2 text-sm font-medium">
            <Mail size={14} />
            Email
          </button>
          <button className="px-4 py-2 bg-gradient-to-r from-[#7c3aed] to-[#8b5cf6] hover:shadow-md text-white rounded-lg transition-all flex items-center justify-center gap-2 text-sm font-medium">
            <Globe size={14} />
            Visit
          </button>
        </div>
      </div>
    </div>
  );
}

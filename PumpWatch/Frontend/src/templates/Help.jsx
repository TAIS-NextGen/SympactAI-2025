import React, { useEffect, useState } from "react";
import {
  Search,
  Book,
  MessageCircle,
  Video,
  FileText,
  HelpCircle,
  ChevronRight,
  ChevronDown,
  ExternalLink,
  Phone,
  Mail,
  Clock,
} from "lucide-react";
import HeaderComponent from "./Header";
import SidebarComponent from "./Sidebar";
import ChatbotButtonComponent from "./ChatbotButton";

export default function HelpPage() {
  const currentPath = "/help";
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
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedFaq, setExpandedFaq] = useState(null);

  const helpCategories = [
    {
      title: "Getting Started",
      icon: <Book className="text-[#2563eb]" size={20} />,
      items: [
        "System Overview",
        "Setting Up Your First Pump",
        "Understanding the Dashboard",
        "Basic Navigation",
      ],
    },
    {
      title: "Pump Management",
      icon: <HelpCircle className="text-[#7c3aed]" size={20} />,
      items: [
        "Adding New Pumps",
        "Configuring Pump Settings",
        "Monitoring Pump Status",
        "Troubleshooting Common Issues",
      ],
    },
    {
      title: "Analytics & Reports",
      icon: <FileText className="text-[#32d296]" size={20} />,
      items: [
        "Reading Performance Charts",
        "Generating Reports",
        "Exporting Data",
        "Setting Up Alerts",
      ],
    },
    {
      title: "Technical Support",
      icon: <MessageCircle className="text-[#4f46e5]" size={20} />,
      items: [
        "System Requirements",
        "API Documentation",
        "Integration Guide",
        "Error Codes Reference",
      ],
    },
  ];

  const faqs = [
    {
      question: "How do I monitor multiple pumps simultaneously?",
      answer:
        "Navigate to the Monitoring page and select 'Show All Pumps' from the dropdown menu. This will display all connected pumps with their real-time data in a unified view.",
    },
    {
      question: "What should I do if a pump shows an error status?",
      answer:
        "First, check the pump's individual monitoring page for detailed error information. If it's a critical error, the system will automatically send an alert. For non-critical issues, you can often resolve them by checking the pump's physical connections and restarting if necessary.",
    },
    {
      question: "How can I export pump performance data?",
      answer:
        "Go to Analytics page, select your desired time range and pump(s), then click the 'Export' button. You can choose between CSV, PDF, or Excel formats for your data export.",
    },
    {
      question: "How do I set up custom alerts for my pumps?",
      answer:
        "Navigate to the Alerts page, click 'Add New Alert', select your pump, set the parameter thresholds (pressure, temperature, vibration), and choose your notification preferences.",
    },
    {
      question: "Can I control pumps remotely through the system?",
      answer:
        "Yes, you can turn pumps ON/OFF remotely from the Home page or individual monitoring pages. However, for safety reasons, certain critical operations may require physical access or additional authorization.",
    },
  ];

  const contactOptions = [
    {
      type: "Live Chat",
      desc: "Available 24/7",
      icon: <MessageCircle className="text-[#2563eb]" size={20} />,
      action: "Start Chat",
      color: "bg-gradient-to-r from-[#2563eb] to-[#1e3a8a]",
    },
    {
      type: "Phone Support",
      desc: "+1 (555) 123-PUMP",
      icon: <Phone className="text-[#32d296]" size={20} />,
      action: "Call Now",
      color: "bg-gradient-to-r from-[#32d296] to-[#0fa9a3]",
    },
    {
      type: "Email Support",
      desc: "support@pumpcontrol.com",
      icon: <Mail className="text-[#7c3aed]" size={20} />,
      action: "Send Email",
      color: "bg-gradient-to-r from-[#7c3aed] to-[#8b5cf6]",
    },
  ];

  const toggleFaq = (index) => {
    setExpandedFaq(expandedFaq === index ? null : index);
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
          <h2 className="text-2xl font-bold text-[#1e3a8a]">Help & Support</h2>
          <div className="flex items-center gap-3 text-sm text-gray-500">
            <Clock size={16} />
            <span>Last updated: Today</span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <div className="relative max-w-2xl">
            <Search
              className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"
              size={20}
            />
            <input
              type="text"
              placeholder="Search help articles, guides, and FAQs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent shadow-sm"
            />
          </div>
        </div>

        {/* Quick Help Categories */}
        <section className="mb-8">
          <h3 className="text-lg font-semibold text-[#1e3a8a] mb-4">
            Browse by Category
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {helpCategories.map((category, index) => (
              <div
                key={index}
                className="bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 hover:scale-105 cursor-pointer border border-gray-100"
              >
                <div className="flex items-center gap-3 mb-3">
                  {category.icon}
                  <h4 className="font-medium text-gray-800">
                    {category.title}
                  </h4>
                </div>
                <ul className="space-y-2">
                  {category.items.map((item, itemIndex) => (
                    <li
                      key={itemIndex}
                      className="text-sm text-gray-600 hover:text-[#2563eb] cursor-pointer flex items-center gap-2 transition-colors"
                    >
                      <ChevronRight size={12} />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* FAQ Section */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-semibold text-[#1e3a8a] mb-4">
              Frequently Asked Questions
            </h3>
            <div className="space-y-3">
              {faqs.map((faq, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
                >
                  <button
                    onClick={() => toggleFaq(index)}
                    className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <span className="font-medium text-gray-800">
                      {faq.question}
                    </span>
                    {expandedFaq === index ? (
                      <ChevronDown className="text-[#2563eb]" size={20} />
                    ) : (
                      <ChevronRight className="text-gray-400" size={20} />
                    )}
                  </button>
                  {expandedFaq === index && (
                    <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
                      <p className="text-gray-700 text-sm leading-relaxed">
                        {faq.answer}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Contact Support */}
          <div>
            <h3 className="text-lg font-semibold text-[#1e3a8a] mb-4">
              Contact Support
            </h3>
            <div className="space-y-4">
              {contactOptions.map((option, index) => (
                <div
                  key={index}
                  className={`${option.color} p-4 rounded-xl text-white shadow-sm hover:shadow-md transition-all duration-200 hover:scale-105 cursor-pointer`}
                >
                  <div className="flex items-center gap-3 mb-2">
                    {option.icon}
                    <div>
                      <div className="font-medium">{option.type}</div>
                      <div className="text-xs opacity-90">{option.desc}</div>
                    </div>
                  </div>
                  <button className="w-full mt-2 bg-white/20 hover:bg-white/30 px-3 py-2 rounded-lg text-sm font-medium transition-colors">
                    {option.action}
                  </button>
                </div>
              ))}
            </div>

            {/* Additional Resources */}
            <div className="mt-6 bg-white p-4 rounded-xl shadow-sm border border-gray-100">
              <h4 className="font-medium text-gray-800 mb-3">
                Additional Resources
              </h4>
              <div className="space-y-2">
                <a
                  href="#"
                  className="flex items-center justify-between p-2 hover:bg-blue-50 rounded-lg transition-colors group"
                >
                  <div className="flex items-center gap-2">
                    <Video className="text-[#2563eb]" size={16} />
                    <span className="text-sm text-gray-700">
                      Video Tutorials
                    </span>
                  </div>
                  <ExternalLink
                    className="text-gray-400 group-hover:text-[#2563eb]"
                    size={14}
                  />
                </a>
                <a
                  href="#"
                  className="flex items-center justify-between p-2 hover:bg-blue-50 rounded-lg transition-colors group"
                >
                  <div className="flex items-center gap-2">
                    <FileText className="text-[#2563eb]" size={16} />
                    <span className="text-sm text-gray-700">
                      User Manual (PDF)
                    </span>
                  </div>
                  <ExternalLink
                    className="text-gray-400 group-hover:text-[#2563eb]"
                    size={14}
                  />
                </a>
                <a
                  href="#"
                  className="flex items-center justify-between p-2 hover:bg-blue-50 rounded-lg transition-colors group"
                >
                  <div className="flex items-center gap-2">
                    <Book className="text-[#2563eb]" size={16} />
                    <span className="text-sm text-gray-700">
                      API Documentation
                    </span>
                  </div>
                  <ExternalLink
                    className="text-gray-400 group-hover:text-[#2563eb]"
                    size={14}
                  />
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
      <ChatbotButtonComponent />
    </div>
  );
}

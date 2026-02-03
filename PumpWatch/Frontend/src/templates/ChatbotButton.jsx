// ChatbotButton.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MessageCircle, Bot } from "lucide-react";

export default function ChatbotButtonComponent() {
  const navigate = useNavigate();
  const [chatbotPulse, setChatbotPulse] = useState(true);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setChatbotPulse(false), 5000);
    return () => clearTimeout(timer);
  }, []);

  function handleClick() {
    navigate("/chatbot");
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {showTooltip && (
        <div className="absolute bottom-20 right-0 mb-2 px-4 py-3 bg-[#1e3a8a] text-white text-sm rounded-xl shadow-2xl whitespace-nowrap animate-fade-in border border-[#2563eb]/20 backdrop-blur-sm">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-blue-300" />
            <span className="font-medium">AI Pump Assistant</span>
          </div>
          <p className="text-xs text-blue-100 mt-1">
            Ask about pump performance & analytics
          </p>
          <div className="absolute top-full right-6 w-0 h-0 border-l-4 border-r-4 border-t-6 border-l-transparent border-r-transparent border-t-[#1e3a8a]"></div>
        </div>
      )}

      <div className="relative">
        {chatbotPulse && (
          <div className="absolute inset-0 rounded-full bg-[#2563eb] animate-ping opacity-20 scale-110"></div>
        )}

        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[#2563eb] to-[#1e3a8a] blur-xl opacity-0 group-hover:opacity-30 transition-all duration-500"></div>

        <button
          onClick={handleClick}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          className="group relative w-16 h-16 bg-gradient-to-r from-[#2563eb] to-[#1e3a8a] rounded-full shadow-xl hover:shadow-2xl hover:shadow-[#2563eb]/25 transition-all duration-300 hover:scale-110 active:scale-95 border border-white/10"
          aria-label="Open AI Pump Assistant Chatbot"
        >
          <div className="absolute inset-2 rounded-full bg-gradient-to-r from-[#3b82f6] to-[#2563eb] opacity-60 group-hover:opacity-80 transition-opacity duration-300"></div>

          <div className="relative w-full h-full rounded-full flex items-center justify-center overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,rgba(255,255,255,0.1),transparent)]"></div>

            <div className="relative z-10">
              <MessageCircle className="w-7 h-7 text-white group-hover:scale-110 transition-transform duration-200 drop-shadow-sm" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-yellow-300 rounded-full animate-bounce opacity-80 shadow-sm"></div>
              <div className="absolute -bottom-1 -left-1 w-1.5 h-1.5 bg-blue-200 rounded-full animate-pulse shadow-sm"></div>
            </div>
          </div>
        </button>

        <div className="absolute -top-1 -right-1 w-4 h-4 bg-[#32d296] border-2 border-white rounded-full flex items-center justify-center shadow-sm">
          <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></div>
        </div>

        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 bg-white text-[#2563eb] text-xs px-2 py-1 rounded-full shadow-md border border-[#2563eb]/20 font-medium">
          AI
        </div>
      </div>

      {/* Include these styles globally once, or add to your tailwind config if possible */}
      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }

        @keyframes subtle-bounce {
          0%,
          100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-3px);
          }
        }

        .animate-subtle-bounce {
          animation: subtle-bounce 2s ease-in-out infinite;
        }

        .group:hover .animate-bounce {
          animation-duration: 0.8s;
        }
      `}</style>
    </div>
  );
}

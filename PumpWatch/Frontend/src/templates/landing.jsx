import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';

function LandingPage() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [scrollY, setScrollY] = useState(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setIsLoaded(true);
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const features = [
    {
      title: "Real-Time Monitoring",
      desc: "Monitor pump health with live sensor data and audio analysis to detect anomalies instantly.",
      icon: "📊",
      color: "from-blue-500 to-cyan-500",
      delay: "0ms"
    },
    {
      title: "AI Chatbot Assistant",
      desc: "Get instant troubleshooting guidance with our RAG-based chatbot, powered by a comprehensive knowledge base.",
      icon: "🤖",
      color: "from-purple-500 to-cyan-500",
      delay: "200ms"
    },
    {
      title: "History & Profiles",
      desc: "Access pump performance history and manage user/company profiles for personalized insights.",
      icon: "📈",
      color: "from-green-500 to-cyan-500",
      delay: "400ms"
    },
  ];

  const stats = [
    { number: "99.9%", label: "Uptime Guarantee", icon: "🛡️" },
    { number: "50ms", label: "Response Time", icon: "⚡" },
    { number: "40%", label: "Cost Reduction", icon: "📈" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 overflow-hidden">
      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrollY > 50 ? 'bg-slate-900/95 backdrop-blur-lg border-b border-cyan-600/40' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
<div className="flex items-center space-x-2">
  <div className="w-22 h-20 bg-gradient-to-br from-cyan-200 to-cyan-400 rounded-xl flex items-center justify-center ">
    <img src="/public/logo.png" alt="" />
  </div>
  <span className="text-2xl font-bold text-white">
    Pump<span className="text-cyan-400">Watch</span>
  </span>
</div>


            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium">
                Features
              </a>
              <a href="#pricing" className="text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium">
                Pricing
              </a>
              <a href="#about" className="text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium">
                About
              </a>
              <a href="#contact" className="text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium">
                Contact
              </a>
            </div>

            {/* Desktop CTA Buttons */}
            <div className="hidden md:flex items-center space-x-4">
              <button
                onClick={() => navigate('/signin')}
                className="text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium"
              >
                Sign In
              </button>
              <button
                onClick={() => navigate('/signup')}
                className="bg-gradient-to-r from-cyan-500 to-cyan-600 text-white px-6 py-2 rounded-lg font-medium hover:from-cyan-600 hover:to-cyan-700 transition-all duration-200 transform hover:scale-105"
              >
                Get Started
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden w-8 h-8 flex flex-col items-center justify-center space-y-1 group"
            >
              <div className={`w-6 h-0.5 bg-white transition-all duration-300 ${isMobileMenuOpen ? 'rotate-45 translate-y-2' : ''}`}></div>
              <div className={`w-6 h-0.5 bg-white transition-all duration-300 ${isMobileMenuOpen ? 'opacity-0' : ''}`}></div>
              <div className={`w-6 h-0.5 bg-white transition-all duration-300 ${isMobileMenuOpen ? '-rotate-45 -translate-y-2' : ''}`}></div>
            </button>
          </div>

          {/* Mobile Menu */}
          <div className={`md:hidden overflow-hidden transition-all duration-300 ${isMobileMenuOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
            <div className="pt-6 pb-4 space-y-4">
              <a href="#features" className="block text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium py-2">
                Features
              </a>
              <a href="#pricing" className="block text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium py-2">
                Pricing
              </a>
              <a href="#about" className="block text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium py-2">
                About
              </a>
              <a href="#contact" className="block text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium py-2">
                Contact
              </a>
              <div className="pt-4 space-y-3">
                <button
                  onClick={() => navigate('/signin')}
                  className="block w-full text-left text-white/80 hover:text-cyan-400 transition-colors duration-200 font-medium py-2"
                >
                  Sign In
                </button>
                <button
                  onClick={() => navigate('/signup')}
                  className="block w-full bg-gradient-to-r from-cyan-500 to-cyan-600 text-white px-6 py-3 rounded-lg font-medium hover:from-cyan-600 hover:to-cyan-700 transition-all duration-200 text-center"
                >
                  Get Started
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-blue-700/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-3/4 left-3/4 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 pt-32">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Hero Text */}
          <div className={`space-y-8 transform transition-all duration-1000 ${isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            <div className="space-y-6">
              <h1 className="text-6xl lg:text-7xl font-black leading-tight">
                <span className="bg-gradient-to-r from-white to-cyan-300 bg-clip-text text-transparent">
                  Welcome to
                </span>
                <br />
                <span className="bg-gradient-to-r from-cyan-400 to-cyan-600 bg-clip-text text-transparent animate-pulse">
                  PumpWatch
                </span>
              </h1>

              <p className="text-xl text-cyan-200 leading-relaxed max-w-lg">
                Monitor <span className="font-bold text-cyan-400">pump health</span> in real-time, prevent
                failures, and ensure <span className="font-bold text-cyan-300">optimal performance</span> using AI.
              </p>

              <p className="text-lg text-cyan-200">
                Designed for industries that can't afford downtime — stay one step ahead.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <button
                onClick={() => navigate('/signup')}
                className="group relative bg-gradient-to-r from-cyan-500 to-cyan-600 text-white text-lg font-semibold px-8 py-4 rounded-xl shadow-2xl hover:shadow-cyan-500/30 transition-all duration-300 transform hover:scale-105 hover:-translate-y-1"
              >
                <span className="relative z-10">Get Started Free</span>
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-cyan-500 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>

              <button
                onClick={() => navigate('/signin')}
                className="group bg-white/10 backdrop-blur-sm border border-white/20 text-white text-lg font-semibold px-8 py-4 rounded-xl shadow-xl hover:bg-white/20 transition-all duration-300 transform hover:scale-105 hover:-translate-y-1"
              >
                Sign In
              </button>
            </div>
          </div>

          {/* Pump Image with Enhanced Design */}
          <div className={`relative transform transition-all duration-1000 delay-300 ${isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
            <div className="relative">
              {/* Glowing ring effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-600/20 to-blue-700/20 rounded-full blur-3xl animate-pulse"></div>

              {/* Main pump container */}
              <div className="relative w-full h-[500px] bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20 rounded-3xl overflow-hidden shadow-2xl">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-600/10 to-blue-700/10"></div>

                {/* Pump placeholder with rotating element */}
                <div className="flex items-center justify-center h-full">
                  <div className="text-center space-y-4">
                    <div className="w-32 h-32 bg-gradient-to-br from-cyan-400 to-blue-700 rounded-full flex items-center justify-center mx-auto animate-spin-slow">
                      <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center">
                        <div className="w-8 h-8 bg-gradient-to-br from-cyan-600 to-blue-800 rounded-full"></div>
                      </div>
                    </div>
                    <div className="text-white/80 font-medium">Industrial Pump System</div>
                  </div>
                </div>

                {/* Floating data points */}
                <div className="absolute top-6 right-6 bg-green-500/90 backdrop-blur-sm rounded-lg px-3 py-2 text-white text-sm font-medium animate-bounce">
                  ✓ Online
                </div>

                <div className="absolute bottom-6 left-6 bg-cyan-600/90 backdrop-blur-sm rounded-lg px-3 py-2 text-white text-sm font-medium" style={{ animationDelay: '1s' }}>
                  📊 Monitoring
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-8 h-8 border-2 border-white/60 rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-white/60 rounded-full"></div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {stats.map((stat, i) => (
              <div
                key={i}
                className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:bg-white/10 transition-all duration-300 transform hover:scale-105"
                style={{ animationDelay: `${i * 200}ms` }}
              >
                <div className="text-4xl mb-4">{stat.icon}</div>
                <div className="text-4xl font-bold text-white mb-2">{stat.number}</div>
                <div className="text-cyan-200">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-bold mb-6">
              <span className="text-white">Why Choose </span>
              <span className="bg-gradient-to-r from-cyan-400 to-cyan-600 bg-clip-text text-transparent">
                PumpWatch
              </span>
              <span className="text-white">?</span>
            </h2>
            <p className="text-xl text-cyan-200 max-w-3xl mx-auto">
              Experience the future of pump monitoring with our cutting-edge AI technology
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, i) => (
              <div
                key={i}
                className={`group relative p-8 bg-white/5 backdrop-blur-sm rounded-3xl border border-white/10 hover:bg-white/10 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2`}
                style={{ animationDelay: feature.delay }}
              >
                {/* Gradient overlay */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 rounded-3xl transition-opacity duration-500`}></div>

                {/* Icon */}
                <div className={`relative w-20 h-20 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <span className="text-3xl">{feature.icon}</span>
                </div>

                {/* Content */}
                <div className="relative">
                  <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-cyan-300 transition-colors duration-300">
                    {feature.title}
                  </h3>
                  <p className="text-cyan-200 leading-relaxed group-hover:text-cyan-100 transition-colors duration-300">
                    {feature.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Enhanced CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm rounded-3xl border border-white/20 p-12 text-center overflow-hidden">
            {/* Background effects */}
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-600/10 to-blue-700/10 rounded-3xl"></div>
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-600 to-blue-700"></div>

            <div className="relative z-10 space-y-8">
              <h2 className="text-4xl font-bold text-white mb-4">
                Ready to Transform Your Operations?
              </h2>

              <p className="text-xl text-cyan-200 max-w-2xl mx-auto">
                Join <span className="font-bold text-cyan-400" onClick={() => navigate('/signup')}>PumpWatch</span> today and experience
                the power of predictive maintenance with cutting-edge AI technology.
              </p>

              <div className="flex flex-col sm:flex-row justify-center gap-6 pt-4">
                <button
                  onClick={() => window.location.href = '#signup'}
                  className="group relative bg-gradient-to-r from-cyan-600 to-cyan-700 text-white text-lg font-semibold px-10 py-4 rounded-xl shadow-2xl hover:shadow-cyan-600/40 transition-all duration-300 transform hover:scale-105 hover:-translate-y-1"
                >
                  <span className="relative z-10" onClick={() => navigate('/signup')}>Start Free Trial</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </button>

                <button
                  onClick={() => window.location.href = '#demo'}
                  className="group bg-white/10 backdrop-blur-sm border border-white/20 text-white text-lg font-semibold px-10 py-4 rounded-xl shadow-xl hover:bg-white/20 transition-all duration-300 transform hover:scale-105 hover:-translate-y-1"
                >
                  Watch Demo
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center">
        <p className="text-cyan-200">
          © 2024 PumpWatch. Revolutionizing industrial monitoring with AI.
        </p>
      </footer>
    </div>
  );
}

export default LandingPage;

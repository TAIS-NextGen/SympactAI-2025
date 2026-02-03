import React, { useState } from "react";
import { Mail, Lock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api"; // import from your api.js

export default function SignInPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false); // keep if you want UI toggle
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(""); // clear previous errors

    try {
      // Use the loginUser helper
      const response = await loginUser({
        email,
        password,
        // rememberMe,  // remove if backend does not expect it
      });

      console.log(response); // or user data/token
      // TODO: Save user info/token here if needed
      navigate("/home"); // or wherever you want after login
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || "Login failed");
    }
  };

  return (
    <div className="flex h-screen animate-fadeIn">
      {/* Left Panel */}
      <div className="w-1/3 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 relative flex items-center justify-center transition-all duration-700 ease-in-out">
        <div className="absolute top-1/2 right-[-112px] transform -translate-y-1/2 rotate-90 flex items-center gap-4">
          <button
            style={{ fontSize: "20px" }}
            onClick={() => navigate("/signup")}
            className="px-6 py-2 border border-[#6c88e8] text-[#6c88e8] rounded-full text-sm font-bold transform rotate-180-translate-x-4 hover:bg-blue hover:text-white hover:border-[#f44336] transition-all duration-300"
          >
            SIGN UP
          </button>
          <div
            style={{ fontSize: "20px" }}
            className="bg-white rounded-full px-6 py-2 shadow-md"
          >
            <span className="text-[#6c88e8] font-bold">SIGN IN</span>
          </div>
        </div>
        <div className="absolute bottom-4 text-xs text-white">
          PumpWatch all rights reserved 2024
        </div>
      </div>

      {/* Right Side Form */}
      <div className="w-2/3 flex items-center justify-center bg-white animate-slideInRight">
        <form
          onSubmit={handleLogin}
          className="w-[350px] animate-fadeUp transition-all duration-700 ease-in-out space-y-4"
        >
          {/* Logo */}
          <div className="flex justify-center mb-4">
            <div className="w-75 h-75 rectangle-full bg-white-200 flex items-center justify-center text-white-500 text-sm font-semibold">
              <img src="/public/logo.png" alt="PumpWatch Logo" />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="flex items-center gap-2 text-sm text-gray-800 ">
              <Mail size={16} />
              <span>Email</span>
            </label>
            <input
              type="email"
              placeholder="email@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border-b border-gray-400 focus:outline-none mt-1 focus:border-[#f44336] placeholder:text-gray-400 text-sm transition-colors"
            />
          </div>

          {/* Password */}
          <div>
            <label className="flex items-center gap-2 text-sm text-gray-800">
              <Lock size={16} />
              <span>Password</span>
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full border-b border-gray-400 focus:outline-none mt-1 focus:border-[#f44336] placeholder:text-gray-400 text-sm transition-colors"
            />
          </div>

          {/* Error Message */}
          {error && <p className="text-red-500 text-sm">{error}</p>}

          {/* Remember Me */}
          <div className="mb-4">
            <label className="flex items-center text-sm text-gray-800">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={() => setRememberMe(!rememberMe)}
                className="mr-2 accent-[#f44336]"
              />
              Remember Me
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="bg-[#6c88e8] text-white px-6 py-2 rounded-full w-full hover:bg-[#f44336] transition-colors duration-300"
          >
            SIGN IN
          </button>
        </form>
      </div>
    </div>
  );
}

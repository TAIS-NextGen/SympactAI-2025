import React, { useState, useEffect } from 'react';
import { User, Lock, Mail } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function SignUpPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [companyId, setCompanyId] = useState('');
  const [role, setRole] = useState('technician');
  const [rememberMe, setRememberMe] = useState(false);
  const [companies, setCompanies] = useState([]);

  useEffect(() => {
    async function fetchCompanies() {
      try {
        const res = await fetch('http://localhost:5000/api/company/all'); 
        const data = await res.json();
        setCompanies(data);
        console.log('Companies loaded:', data);
      } catch (err) {
        console.error('Failed to load companies:', err);
      }
    }

    fetchCompanies();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch('http://localhost:5000/api/auth/register', { // <- Updated URL
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          firstName,
          lastName,
          password,
          companyId,
          role,
          rememberMe,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        alert('Inscription réussie !');
        navigate('/signin');
      } else {
        alert(data.errors?.[0]?.msg || data.message || 'Erreur lors de l’inscription');
      }
    } catch (err) {
      console.error(err);
      alert('Erreur serveur');
    }
  };

  return (
    <div className="flex h-screen animate-fadeIn">
      {/* Left side minimal gradient panel */}
      <div className="w-1/3 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 relative flex items-center justify-center transition-all duration-700 ease-in-out">

        {/* SIGN UP label and rotated SIGN IN button */}
        <div className="absolute top-1/2 right-[-112px] transform -translate-y-1/2 rotate-90 flex items-center gap-4">
          <div style={{ fontSize: '20px' }} className="bg-white rounded-full px-6 py-2 shadow-md">
            <span className="text-[#6c88e8] font-bold">SIGN UP</span>
          </div>

          <button
            style={{ fontSize: '20px' }}
            onClick={() => navigate('/signin')}
            className="px-6 py-2 border border-[#6c88e8] text-[#6c88e8] rounded-full text-sm font-bold transform rotate-180-translate-x-4 hover:bg-blue hover:text-white hover:border-[#f44336] transition-all duration-300"
          >
            SIGN IN
          </button>
        </div>

        <div className="absolute bottom-4 text-xs text-white">
          PumpWatch all rights reserved 2024
        </div>
      </div>

      {/* Right side form */}
      <div className="w-2/3 flex items-center justify-center bg-white animate-slideInRight">
        <form onSubmit={handleSubmit} className="w-[350px] animate-fadeUp transition-all duration-700 ease-in-out space-y-4">
          <div className="flex justify-center mb-4">
            <div className="w-75 h-75 rectangle-full bg-white-200 flex items-center justify-center text-white-500 text-sm font-semibold ">
              <img src="/public/logo.png" alt="" />
            </div>
          </div>

          <div className="flex gap-4">
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-800">
                <User size={16} />
                <span>FirstName</span>
              </label>
              <input
                type="text"
                placeholder="FirstName"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
                className="w-full border-b border-gray-400 focus:outline-none mt-1 focus:border-[#f44336] placeholder:text-gray-400 text-sm transition-colors"
              />
            </div>
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-800">
                <User size={16} />
                <span>LastName</span>
              </label>
              <input
                type="text"
                placeholder="LastName"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
                className="w-full border-b border-gray-400 focus:outline-none mt-1 focus:border-[#f44336] placeholder:text-gray-400 text-sm transition-colors"
              />
            </div>
          </div>

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

          <div>
            <label className="flex items-center gap-2 text-sm text-gray-800">
              <Lock size={16} />
              <span>Password</span>
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border-b border-gray-400 focus:outline-none mt-1 focus:border-[#f44336] placeholder:text-gray-400 text-sm transition-colors"
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-800 text-sm font-medium mb-1">
              Role
            </label>
            <select
              className="w-full border-b border-gray-400 focus:outline-none text-sm placeholder:text-gray-400 transition-colors"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              required
            >
              <option value="technician">Technician</option>
              <option value="inspector">Inspector</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <label className="block text-gray-800 text-sm font-medium mb-1">
            Company
          </label>
          <select
            className="w-full border-b border-gray-400 focus:outline-none text-sm"
            value={companyId}
            onChange={(e) => setCompanyId(e.target.value)}
            required
          >
            <option value="">Select a company</option>
            {companies.map((company) => (
              <option key={company._id} value={company._id}>
                {company.name}
              </option>
            ))}
          </select>

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

          <button
            type="submit"
            className="bg-[#6c88e8] text-white px-6 py-2 rounded-full w-full hover:bg-[#f44336] transition-colors duration-300"
          >
            SIGN UP
          </button>
        </form>
      </div>
    </div>
  );
}

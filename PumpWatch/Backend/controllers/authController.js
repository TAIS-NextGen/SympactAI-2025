const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const { validationResult } = require("express-validator");
const User = require("../models/User");
const Company = require("../models/Company");
require("dotenv").config();
const JWT_SECRET = process.env.JWT_SECRET;

exports.register = async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { firstName, lastName, email, password, companyId, role, rememberMe } =
    req.body;
  try {
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: "User already exists" });
    }

    const existingCompany = await Company.findById(companyId);
    if (!existingCompany) {
      return res.status(400).json({ message: "Company does not exist" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = new User({
      firstName,
      lastName,
      email,
      password: hashedPassword,
      companyId,
      role,
    });

    await newUser.save();

    const token = jwt.sign(
      { id: newUser._id, role: newUser.role, companyId: newUser.companyId },
      JWT_SECRET,
      { expiresIn: rememberMe ? "1d" : "1h" }
    );

    res.cookie("token", token, {
      httpOnly: false,
      maxAge: rememberMe ? 24 * 60 * 60 * 1000 : 60 * 60 * 1000,
      sameSite: "Strict",
      secure: true,
    });

    res.status(201).json({ message: "User registered successfully" });
  } catch (error) {
    console.error("Register error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
};

exports.login = async (req, res) => {
  const { email, password, rememberMe } = req.body;

  try {
    const existingUser = await User.findOne({ email });

    if (!existingUser) {
      return res.status(400).json({ message: "Invalid email" });
    }

    const isMatch = await bcrypt.compare(password, existingUser.password);
    if (!isMatch) {
      return res.status(400).json({ message: "Invalid password" });
    }

    const token = jwt.sign(
      {
        id: existingUser._id,
        role: existingUser.role,
        companyId: existingUser.companyId,
      },
      JWT_SECRET,
      { expiresIn: rememberMe ? "1d" : "1h" }
    );

    res.cookie("token", token, {
      httpOnly: false,
      maxAge: rememberMe ? 24 * 60 * 60 * 1000 : 60 * 60 * 1000,
      sameSite: "Strict",
      secure: true,
    });

    res.status(200).json({ message: "Login successful" });
  } catch (error) {
    console.error("Login error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
};

exports.logout = (req, res) => {
  res.clearCookie("token");
  res.status(200).json({ message: "Logout successful" });
};

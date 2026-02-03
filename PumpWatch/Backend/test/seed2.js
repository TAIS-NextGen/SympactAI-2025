require("dotenv").config();
const mongoose = require("mongoose");
const bcrypt = require("bcrypt");
const Pump = require("../models/pump");
const Failure = require("../models/failure");
const User = require("../models/User");
const Company = require("../models/Company");

const MONGO_URI = process.env.MONGO_URI;

async function seed() {
  try {
    // 1. Connect to MongoDB
    await mongoose.connect(MONGO_URI);
    console.log("Connected to MongoDB");
    await User.deleteMany();
    await Failure.deleteMany();
    await Pump.deleteMany();
    await Company.deleteMany();

    // Create multiple companies
    const companies = await Company.insertMany([
      {
        name: "HydroTech Industries",
        address: "456 Industrial Blvd, Manufacturing District",
        contact_email: "operations@hydrotech.com",
        admin: null,
      },
      {
        name: "FlowMaster Solutions",
        address: "789 Pipeline Ave, Water Treatment Facility",
        contact_email: "admin@flowmaster.com",
        admin: null,
      },
      {
        name: "AquaDyne Corporation",
        address: "321 Reservoir Road, Pumping Station Complex",
        contact_email: "maintenance@aquadyne.com",
        admin: null,
      },
    ]);

    // 2. Create users across different companies
    const hashedPasswords = await Promise.all([
      bcrypt.hash("admin123", 10),
      bcrypt.hash("tech123", 10),
      bcrypt.hash("inspector123", 10),
      bcrypt.hash("supervisor456", 10),
      bcrypt.hash("engineer789", 10),
      bcrypt.hash("operator321", 10),
      bcrypt.hash("manager654", 10),
      bcrypt.hash("specialist987", 10),
    ]);

    const users = await User.insertMany([
      // HydroTech Industries users
      {
        firstName: "Marcus",
        lastName: "Rodriguez",
        email: "marcus.rodriguez@hydrotech.com",
        password: hashedPasswords[0],
        role: "admin",
        companyId: companies[0]._id,
      },
      {
        firstName: "Elena",
        lastName: "Chen",
        email: "elena.chen@hydrotech.com",
        password: hashedPasswords[1],
        role: "technician",
        companyId: companies[0]._id,
      },
      {
        firstName: "David",
        lastName: "Thompson",
        email: "david.thompson@hydrotech.com",
        password: hashedPasswords[2],
        role: "inspector",
        companyId: companies[0]._id,
      },

      // FlowMaster Solutions users
      {
        firstName: "Priya",
        lastName: "Patel",
        email: "priya.patel@flowmaster.com",
        password: hashedPasswords[3],
        role: "admin",
        companyId: companies[1]._id,
      },
      {
        firstName: "Ahmed",
        lastName: "Hassan",
        email: "ahmed.hassan@flowmaster.com",
        password: hashedPasswords[4],
        role: "technician",
        companyId: companies[1]._id,
      },

      // AquaDyne Corporation users
      {
        firstName: "Jennifer",
        lastName: "Kim",
        email: "jennifer.kim@aquadyne.com",
        password: hashedPasswords[5],
        role: "admin",
        companyId: companies[2]._id,
      },
      {
        firstName: "Carlos",
        lastName: "Mendoza",
        email: "carlos.mendoza@aquadyne.com",
        password: hashedPasswords[6],
        role: "technician",
        companyId: companies[2]._id,
      },
      {
        firstName: "Fatima",
        lastName: "Al-Zahra",
        email: "fatima.alzahra@aquadyne.com",
        password: hashedPasswords[7],
        role: "inspector",
        companyId: companies[2]._id,
      },
    ]);

    // Update company admins
    companies[0].admin = users.find(
      (u) => u.companyId.equals(companies[0]._id) && u.role === "admin"
    )._id;
    companies[1].admin = users.find(
      (u) => u.companyId.equals(companies[1]._id) && u.role === "admin"
    )._id;
    companies[2].admin = users.find(
      (u) => u.companyId.equals(companies[2]._id) && u.role === "admin"
    )._id;

    await Promise.all(companies.map((company) => company.save()));

    // 3. Create diverse pumps across companies
    const pumps = await Pump.insertMany([
      // HydroTech Industries pumps
      {
        name: "Centrifugal Pump Unit Alpha-7",
        age: 4,
        companyId: companies[0]._id,
        location: "Main Processing Plant - Building A",
        diameter: 16,
        length: 24,
        material: "Stainless Steel 316",
        pressure_rating: 150,
        installation_date: new Date("2021-02-15"),
        last_inspection_date: new Date("2024-08-15"),
        last_inspection_by: users[1]._id,
        next_inspection_due_date: new Date("2025-08-15"),
        notes: "High-efficiency unit for primary cooling system.",
        status: "active",
      },
      {
        name: "Submersible Pump Delta-3",
        age: 7,
        companyId: companies[0]._id,
        location: "Underground Reservoir - Sector 12",
        diameter: 14,
        length: 32,
        material: "Duplex Stainless Steel",
        pressure_rating: 200,
        installation_date: new Date("2018-09-10"),
        last_inspection_date: new Date("2024-07-20"),
        last_inspection_by: users[2]._id,
        next_inspection_due_date: new Date("2025-01-20"),
        notes: "Deep well pump - monitor for sand infiltration.",
        status: "active",
      },
      {
        name: "Booster Pump Gamma-12",
        age: 2,
        companyId: companies[0]._id,
        location: "Secondary Distribution Line",
        diameter: 10,
        length: 18,
        material: "Carbon Steel with Epoxy Coating",
        pressure_rating: 125,
        installation_date: new Date("2023-03-05"),
        last_inspection_date: new Date("2024-09-10"),
        last_inspection_by: users[1]._id,
        next_inspection_due_date: new Date("2025-03-10"),
        notes: "Recently installed for pressure optimization.",
        status: "maintenance",
      },

      // FlowMaster Solutions pumps
      {
        name: "Industrial Slurry Pump Beta-9",
        age: 6,
        companyId: companies[1]._id,
        location: "Waste Treatment Facility - East Wing",
        diameter: 20,
        length: 28,
        material: "High Chrome Iron",
        pressure_rating: 175,
        installation_date: new Date("2019-11-22"),
        last_inspection_date: new Date("2024-06-30"),
        last_inspection_by: users[4]._id,
        next_inspection_due_date: new Date("2024-12-30"),
        notes: "Heavy-duty pump for abrasive materials handling.",
        status: "active",
      },
      {
        name: "Chemical Transfer Pump Epsilon-5",
        age: 3,
        companyId: companies[1]._id,
        location: "Chemical Processing Unit - Lab Section",
        diameter: 8,
        length: 15,
        material: "PTFE Lined Steel",
        pressure_rating: 100,
        installation_date: new Date("2022-07-14"),
        last_inspection_date: new Date("2024-07-14"),
        last_inspection_by: users[3]._id,
        next_inspection_due_date: new Date("2025-07-14"),
        notes: "Specialized for corrosive chemical transfer.",
        status: "active",
      },
      {
        name: "Fire Suppression Pump Zeta-1",
        age: 8,
        companyId: companies[1]._id,
        location: "Emergency Systems Building",
        diameter: 12,
        length: 22,
        material: "Cast Iron with Protective Coating",
        pressure_rating: 250,
        installation_date: new Date("2017-01-30"),
        last_inspection_date: new Date("2024-05-15"),
        last_inspection_by: users[4]._id,
        next_inspection_due_date: new Date("2025-05-15"),
        notes: "Critical safety system - quarterly testing required.",
        status: "inactive",
      },

      // AquaDyne Corporation pumps
      {
        name: "Municipal Water Pump Theta-4",
        age: 5,
        companyId: companies[2]._id,
        location: "Central Water Distribution Station",
        diameter: 18,
        length: 26,
        material: "Ductile Iron with Ceramic Coating",
        pressure_rating: 180,
        installation_date: new Date("2020-04-18"),
        last_inspection_date: new Date("2024-08-01"),
        last_inspection_by: users[7]._id,
        next_inspection_due_date: new Date("2025-02-01"),
        notes: "Primary supply pump for downtown district.",
        status: "active",
      },
      {
        name: "Irrigation Pump Kappa-11",
        age: 1,
        companyId: companies[2]._id,
        location: "Agricultural Zone - Field Station 7",
        diameter: 14,
        length: 20,
        material: "Aluminum Bronze",
        pressure_rating: 120,
        installation_date: new Date("2024-01-10"),
        last_inspection_date: new Date("2024-09-01"),
        last_inspection_by: users[6]._id,
        next_inspection_due_date: new Date("2025-09-01"),
        notes: "New installation for expanded irrigation network.",
        status: "active",
      },
      {
        name: "Drainage Pump Lambda-8",
        age: 9,
        companyId: companies[2]._id,
        location: "Storm Water Management Facility",
        diameter: 22,
        length: 30,
        material: "Stainless Steel 304",
        pressure_rating: 90,
        installation_date: new Date("2016-08-25"),
        last_inspection_date: new Date("2024-04-10"),
        last_inspection_by: users[7]._id,
        next_inspection_due_date: new Date("2024-10-10"),
        notes: "Aging unit - consider replacement planning.",
        status: "maintenance",
      },
      {
        name: "Backup Generator Coolant Pump Sigma-2",
        age: 4,
        companyId: companies[2]._id,
        location: "Emergency Power Station",
        diameter: 6,
        length: 12,
        material: "Bronze",
        pressure_rating: 80,
        installation_date: new Date("2021-12-03"),
        last_inspection_date: new Date("2024-06-03"),
        last_inspection_by: users[6]._id,
        next_inspection_due_date: new Date("2024-12-03"),
        notes: "Auxiliary system for emergency power cooling.",
        status: "active",
      },
    ]);

    // 4. Create diverse failure records
    await Failure.insertMany([
      // HydroTech Industries failures
      {
        type: "Bearing Failure",
        date: new Date("2024-07-22"),
        pumpId: pumps[0]._id,
      },
      {
        type: "Seal Degradation",
        date: new Date("2024-06-15"),
        pumpId: pumps[1]._id,
      },
      {
        type: "Cavitation Damage",
        date: new Date("2024-08-30"),
        pumpId: pumps[2]._id,
      },

      // FlowMaster Solutions failures
      {
        type: "Impeller Wear",
        date: new Date("2024-05-18"),
        pumpId: pumps[3]._id,
      },
      {
        type: "Corrosion Detected",
        date: new Date("2024-07-08"),
        pumpId: pumps[4]._id,
      },
      {
        type: "Motor Overheating",
        date: new Date("2024-04-25"),
        pumpId: pumps[5]._id,
      },

      // AquaDyne Corporation failures
      {
        type: "Vibration Anomaly",
        date: new Date("2024-08-12"),
        pumpId: pumps[6]._id,
      },
      {
        type: "Flow Rate Drop",
        date: new Date("2024-09-02"),
        pumpId: pumps[7]._id,
      },
      {
        type: "Electrical Fault",
        date: new Date("2024-03-28"),
        pumpId: pumps[8]._id,
      },
      {
        type: "Coupling Misalignment",
        date: new Date("2024-06-20"),
        pumpId: pumps[9]._id,
      },

      // Additional historical failures for pattern analysis
      {
        type: "Pressure Surge",
        date: new Date("2024-02-14"),
        pumpId: pumps[0]._id,
      },
      {
        type: "Pump Stall",
        date: new Date("2024-01-30"),
        pumpId: pumps[3]._id,
      },
      {
        type: "Seal Leakage",
        date: new Date("2024-05-05"),
        pumpId: pumps[6]._id,
      },
      {
        type: "Temperature Spike",
        date: new Date("2024-07-03"),
        pumpId: pumps[8]._id,
      },
      {
        type: "Suction Line Blockage",
        date: new Date("2024-08-17"),
        pumpId: pumps[1]._id,
      },
    ]);

    console.log("🎯 Database seeded successfully with expanded data!");
    console.log(
      `📊 Created: ${companies.length} companies, ${users.length} users, ${pumps.length} pumps, 15 failure records`
    );
    console.log(
      "🏢 Companies: HydroTech Industries, FlowMaster Solutions, AquaDyne Corporation"
    );
    console.log(
      "🔧 Pump Types: Centrifugal, Submersible, Booster, Slurry, Chemical Transfer, Fire Suppression, Municipal, Irrigation, Drainage, Coolant"
    );
    console.log(
      "⚠️  Failure Types: Bearing, Seal, Cavitation, Impeller, Corrosion, Motor, Vibration, Flow, Electrical, Coupling, Pressure, Stall, Temperature, Blockage"
    );

    process.exit();
  } catch (err) {
    console.error("Seeding error:", err);
    process.exit(1);
  }
}

seed();

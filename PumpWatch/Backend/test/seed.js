require('dotenv').config();
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const Pump = require('../models/pump');
const Failure = require('../models/failure');
const User = require('../models/User');
const Company = require('../models/Company');

const MONGO_URI = process.env.MONGO_URI;

async function seed() {
  try {
    // 1. Connect to MongoDB
    await mongoose.connect(MONGO_URI);
    console.log('Connected to MongoDB');
    await User.deleteMany();
    await Failure.deleteMany();
    await Pump.deleteMany();
    await Company.deleteMany();

    const company = await Company.create({
      name: 'AquaFlow Corp',
      address: '123 Waterway Ave',
      contact_email: 'contact@aquaflow.com',
      admin: null, // we'll update admin after creating user
    });

    // 2. Create users with companyId set
    const hashedPasswords = await Promise.all([
      bcrypt.hash('admin123', 10),
      bcrypt.hash('tech123', 10),
      bcrypt.hash('inspector123', 10),
      bcrypt.hash('tech456', 10),
    ]);

    const users = await User.insertMany([
      {
        firstName: 'Admin',
        lastName: 'User',
        email: 'admin@example.com',
        password: hashedPasswords[0],
        role: 'admin',
        companyId: company._id,
      },
      {
        firstName: 'Sarah',
        lastName: 'Tech',
        email: 'sarah.tech@example.com',
        password: hashedPasswords[1],
        role: 'technician',
        companyId: company._id,
      },
      {
        firstName: 'Tom',
        lastName: 'Inspector',
        email: 'tom.inspector@example.com',
        password: hashedPasswords[2],
        role: 'inspector',
        companyId: company._id,
      },
      {
        firstName: 'Jake',
        lastName: 'Tech',
        email: 'jake.tech@example.com',
        password: hashedPasswords[3],
        role: 'technician',
        companyId: company._id,
      },
    ]);

    // 3. Update company.admin to admin user id
    const adminUser = users.find(u => u.role === 'admin');
    company.admin = adminUser._id;
    await company.save();

    // 4. Create pumps as before
    const pumps = await Pump.insertMany([
      {
        name: 'Pump A',
        age: 3,
        companyId: company._id,
        location: 'Zone A',
        diameter: 12,
        length: 20,
        material: 'Steel',
        pressure_rating: 100,
        installation_date: new Date('2022-01-15'),
        last_inspection_date: new Date('2024-06-10'),
        last_inspection_by: adminUser._id,
        next_inspection_due_date: new Date('2025-06-10'),
        notes: 'All good.',
        status: 'active',
      },
      {
        name: 'Pump B',
        age: 5,
        companyId: company._id,
        location: 'Zone B',
        diameter: 10,
        length: 18,
        material: 'PVC',
        pressure_rating: 80,
        installation_date: new Date('2020-03-10'),
        last_inspection_date: new Date('2024-03-01'),
        last_inspection_by: adminUser._id,
        next_inspection_due_date: new Date('2025-03-01'),
        notes: 'Monitor seal condition.',
        status: 'maintenance',
      },
      {
        name: 'Pump C',
        age: 2,
        companyId: company._id,
        location: 'Zone C',
        diameter: 8,
        length: 15,
        material: 'Cast Iron',
        pressure_rating: 90,
        installation_date: new Date('2023-05-20'),
        last_inspection_date: new Date('2024-05-01'),
        last_inspection_by: adminUser._id,
        next_inspection_due_date: new Date('2025-05-01'),
        notes: '',
        status: 'inactive',
      },
    ]);

    // 5. Create failures for pumps
    await Failure.insertMany([
      {
        type: 'Leakage',
        date: new Date('2024-07-01'),
        pumpId: pumps[0]._id,
      },
      {
        type: 'Pressure Drop',
        date: new Date('2024-06-20'),
        pumpId: pumps[1]._id,
      },
      {
        type: 'Overheating',
        date: new Date('2024-07-15'),
        pumpId: pumps[0]._id,
      },
    ]);

    console.log('Database seeded successfully ✅');
    process.exit();
  } catch (err) {
    console.error('Seeding error:', err);
    process.exit(1);
  }
}

seed();

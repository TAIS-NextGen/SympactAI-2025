const express = require('express');
const company= require('../models/Company');
const User = require('../models/User');
const Pump = require('../models/Pump');

exports.getCompanyDetails = async (req, res) => {
    try {
        const companyId = req.user.companyId;
        const companyDetails = await company.findById(companyId);
        const totalUsers = await User.countDocuments({ companyId: company._id });
        res.status(200).json({companyDetails,  totalUsers });
    } catch (error) {
        console.error('Error fetching company details:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
}

exports.getCompanyDashboard = async (req, res) => {
    try {
        const companyId = req.user.companyId;
        const companyDetails = await company.findById(companyId);
        const totalUsers = await User.countDocuments({ companyId });
        const totalPumps = await Pump.countDocuments({ companyId });
        const activePumps = await Pump.countDocuments({ companyId, status: 'active' });
        const inactivePumps = await Pump.countDocuments({ companyId, status: 'inactive' });
        const maintenancePumps = await Pump.countDocuments({ companyId, status: 'maintenance' });
        res.status(200).json({
            companyDetails,
            totalUsers,
            totalPumps,
            activePumps,
            inactivePumps,
            maintenancePumps
        });
    } catch (error) {
        console.error('Error fetching company dashboard:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
}


exports.updateCompanyDetails = async (req, res) => {
    try {
        const companyId = req.user.companyId;
        const updateFields = {};
        const allowedUpdates = ['address', 'contact_email'];

        allowedUpdates.forEach(field => {
            if (req.body[field]) {
                updateFields[field] = req.body[field];
            }
        });

        const updatedCompany = await company.findByIdAndUpdate(
            companyId,
            { $set: updateFields },
            { new: true, runValidators: true }
        );
        res.status(200).json(updatedCompany);
    } catch (error) {
        console.error('Error updating company details:', error);
        res.status(500).json({ message: 'Internal server error' });
    } 
}

exports.getCompanyUsers = async (req, res) => {
    try{
        const companyId = req.user.companyId;
        const { role } = req.query;
        const filter = { companyId };
        if (role) {
            filter.role = role;
        }
        const users = await User.find(filter).select('-password');
        res.status(200).json(users);
    }catch (error) {
        console.error('Error fetching company users:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
}
exports.getAllCompanies = async (req, res) => {
  try {
    const companies = await company.find().select('name _id'); 
    res.status(200).json(companies);
  } catch (error) {
    console.error('Error fetching all companies:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

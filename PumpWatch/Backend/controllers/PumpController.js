const express = require('express');
const pump = require('../models/Pump');
const Failure = require('../models/failure');

exports.getAllPumps = async (req, res) => {
    try {
        const companyId = req.user.companyId;
        const pumps = await pump.find({ companyId }).populate('companyId')
        res.status(200).json(pumps);
    } catch (error) {
        res.status(500).json({ message: 'Error fetching pumps', error: error.message
        });
    }  
}

exports.addPump = async (req, res) => {
    try{
        const newPump= new pump(req.body);
        await newPump.save();
        res.status(201).json({ message: 'Pump added successfully', pump: newPump
        });
    }catch (error) {
        res.status(500).json({ message: 'Error adding pump', error: error.message });
    }
}

exports.getPumpDashboard = async (req, res) => {
    try{
        const pumpId = req.params.id;
        const companyId = req.user.companyId;
        const pumpData = await pump.findOne({ _id: pumpId, companyId });
        const totalFailures = await Failure.countDocuments({ pumpId });
        const FailuresHistory = await Failure.find({ pumpId }).sort({ reportedAt: -1 });
        res.status(200).json({pumpData, totalFailures, FailuresHistory});
    } catch (error) {
        res.status(500).json({ message: 'Error fetching pump dashboard', error: error.message });
    }
}

exports.getPumpsDashboard = async (req, res) => {
    try{
        const companyId = req.user.companyId;
        const totalPumps = await pump.countDocuments({ companyId });
        const activePumps = await pump.countDocuments({ companyId, status: 'active' });
        const inactivePumps = await pump.countDocuments({ companyId, status: 'inactive' });
        const maintenancePumps = await pump.countDocuments({ companyId, status: 'maintenance' });   
        const totalFailures = await Failure.countDocuments({ pumpId: { $in: await pump.find({ companyId }).distinct('_id') } });
        const pumps = await pump.find({ companyId });
        res.status(200).json({ totalPumps, activePumps, inactivePumps, maintenancePumps, totalFailures, pumps });
    }catch (error) {
        res.status(500).json({ message: 'Error fetching pumps dashboard', error: error.message });
    }
}

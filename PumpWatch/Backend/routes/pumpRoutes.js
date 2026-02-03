const express = require('express');
const Router = express.Router();
const { authenticate, isAdmin } = require('../middleware/authMiddleware');

const pumpController = require('../controllers/pumpController');

Router.get('/', authenticate, pumpController.getAllPumps);
Router.post('/add', authenticate, isAdmin, pumpController.addPump);
Router.get('/dashboard/:id', authenticate, pumpController.getPumpDashboard);
Router.get('/dashboard', authenticate, pumpController.getPumpDashboard);

module.exports = Router;
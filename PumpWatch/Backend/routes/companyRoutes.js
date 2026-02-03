const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const companyController = require('../controllers/companyController');
const {authenticate, isAdmin} = require('../middleware/authMiddleware');

router.get('/all', companyController.getAllCompanies);
router.get('/info', authenticate, isAdmin, companyController.getCompanyDetails);
router.put('/update', authenticate, isAdmin, companyController.updateCompanyDetails);
router.get('/users', authenticate, isAdmin, companyController.getCompanyUsers);
router.get('/dashboard', authenticate, isAdmin, companyController.getCompanyDashboard);

module.exports = router;
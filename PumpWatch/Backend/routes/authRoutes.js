const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const authController = require('../controllers/authController');
const { authenticate } = require('../middleware/authMiddleware');

router.post('/register',
    [
        body('firstName').notEmpty().withMessage('firstname is required'),
        body('lastName').notEmpty().withMessage('lastname is required'),
        body('email').isEmail().withMessage('Invalid email format'),
        body('password').isLength({ min: 8 }).withMessage('Password must be at least 8 characters long'),
        body('companyId').notEmpty().withMessage('Company ID is required'),
        body('role').isIn(['technician', 'inspector', 'admin']).withMessage('Role must be technician, inspector, or admin'),
        body('rememberMe').optional().isBoolean().withMessage('Remember Me must be a boolean value')
    ], authController.register
);

router.post('/login', authController.login);
router.post('/logout', authenticate, authController.logout);

module.exports = router;


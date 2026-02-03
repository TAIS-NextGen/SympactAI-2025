const express=require('express');
const Router = express.Router();
const userController = require('../controllers/userController');
const {authenticate} = require('../middleware/authMiddleware');

Router.get('/profile', authenticate, userController.getProfile);

module.exports = Router;
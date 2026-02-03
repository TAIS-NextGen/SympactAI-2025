const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  firstName: { type: String, required: true },
  lastName: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, enum: ['technician', 'inspector','admin'], default: 'technician' },
  companyId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Company',
    required: true
  },
  deletedAt: { type: Date, default: null },
}, { timestamps: true });

const User = mongoose.models.User || mongoose.model('User', userSchema);
module.exports = User;

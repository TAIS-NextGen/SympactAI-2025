const mongoose = require('mongoose');

const companySchema = new mongoose.Schema({
    name: { type: String, required: true },
    address: { type: String, required: true },
    contact_email: { type: String, required: true },
    admin:{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
    },
    deletedAt: { type: Date, default: null  },
    }, { timestamps: true });

const company = mongoose.models.Company || mongoose.model('Company', companySchema);
module.exports = company;
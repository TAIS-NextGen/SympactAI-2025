const mongoose = require('mongoose');

const PumpSchema = new mongoose.Schema({
    name: { type: String, required: true },
    age: { type: Number, required: true },
    companyId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Company',
        required: true
    },
    location: { type: String, required: true },
    diameter: { type: Number, required: true },
    length: { type: Number, required: true },
    material: { type: String, required: true },
    pressure_rating: { type: Number, required: true },
    installation_date: { type: Date, required: true },
    last_inspection_date: { type: Date, required: true },
    last_inspection_by: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    },
    next_inspection_due_date: { type: Date, required: true },
    notes: { type: String, default: '' },
    status: { type: String, enum: ['active', 'inactive', 'maintenance'], default: 'active' }
    }, { timestamps: true });

const Pump = mongoose.models.Pump || mongoose.model('Pump', PumpSchema);
module.exports = Pump;


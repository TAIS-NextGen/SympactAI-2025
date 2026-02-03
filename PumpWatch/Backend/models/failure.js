const mongoose = require('mongoose');

const failureSchema = new mongoose.Schema({
    deletedAt: { type: Date, default: null },
    type: { type: String, required: true },
    date: { type: Date, required: true },
    pumpId: { type: mongoose.Schema.Types.ObjectId,
        ref: 'Pump',
        required: true }
}, { timestamps: true });

const Failure = mongoose.models.Failure || mongoose.model('Failure', failureSchema);
module.exports = Failure;
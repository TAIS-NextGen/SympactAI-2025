const mongoose = require('mongoose');

const conversationSchema = new mongoose.Schema({
    title:{ type: String, required: true },
    userId : { type: mongoose.Schema.Types.ObjectId,
         ref: 'User',
        required: true }
}, { timestamps: true });

const Conversation = mongoose.models.Conversation || mongoose.model('Conversation', conversationSchema);
module.exports = Conversation;
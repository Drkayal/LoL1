// MongoDB Initialization Script
// سكريبت تهيئة قاعدة البيانات

// Create database
db = db.getSiblingDB('bot_factory');

// Create collections
db.createCollection('users');
db.createCollection('chats');
db.createCollection('broadcasts');
db.createCollection('devs');
db.createCollection('bots');
db.createCollection('factory_settings');
db.createCollection('blocked');

// Create indexes for better performance
db.users.createIndex({ "user_id": 1 }, { unique: true });
db.users.createIndex({ "username": 1 });
db.users.createIndex({ "date": 1 });

db.chats.createIndex({ "chat_id": 1 }, { unique: true });
db.chats.createIndex({ "type": 1 });

db.broadcasts.createIndex({ "user_id": 1, "bot_id": 1 });
db.broadcasts.createIndex({ "status": 1 });
db.broadcasts.createIndex({ "date": 1 });

db.devs.createIndex({ "user_id": 1 }, { unique: true });
db.devs.createIndex({ "date": 1 });

db.bots.createIndex({ "username": 1 }, { unique: true });
db.bots.createIndex({ "dev_id": 1 });
db.bots.createIndex({ "status": 1 });
db.bots.createIndex({ "date": 1 });

db.factory_settings.createIndex({ "key": 1 }, { unique: true });

db.blocked.createIndex({ "user_id": 1 }, { unique: true });
db.blocked.createIndex({ "date": 1 });

// Insert initial factory settings
db.factory_settings.insertOne({
    key: "factory_enabled",
    value: false,
    date: new Date()
});

db.factory_settings.insertOne({
    key: "max_bots_per_dev",
    value: 1,
    date: new Date()
});

db.factory_settings.insertOne({
    key: "bot_timeout",
    value: 120,
    date: new Date()
});

// Create admin user (optional)
// db.devs.insertOne({
//     user_id: 985612253,
//     username: "admin",
//     date: new Date(),
//     is_owner: true
// });

print("Database initialization completed successfully!");
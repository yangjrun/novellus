// MongoDB Initialization Script for Novellus MCP Server
// This script runs when the MongoDB container starts for the first time

print('Starting MongoDB initialization for Novellus MCP Server...');

// Switch to the novellus database
db = db.getSiblingDB('novellus');

// Create application user
db.createUser({
  user: 'novellus_user',
  pwd: 'novellus_password',
  roles: [
    {
      role: 'readWrite',
      db: 'novellus'
    },
    {
      role: 'dbAdmin',
      db: 'novellus'
    }
  ]
});

print('Created application user: novellus_user');

// Create demo collections with sample data
// Demo users collection
db.demo_users.insertMany([
  {
    name: 'Alice Johnson',
    email: 'alice@example.com',
    age: 28,
    department: 'Engineering',
    skills: ['Python', 'JavaScript', 'MongoDB'],
    salary: 85000,
    created_at: new Date('2024-01-15T10:30:00Z'),
    updated_at: new Date('2024-01-15T10:30:00Z')
  },
  {
    name: 'Bob Smith',
    email: 'bob@example.com',
    age: 35,
    department: 'Marketing',
    skills: ['Analytics', 'Content', 'Social Media'],
    salary: 72000,
    created_at: new Date('2024-01-16T09:15:00Z'),
    updated_at: new Date('2024-01-16T09:15:00Z')
  },
  {
    name: 'Charlie Brown',
    email: 'charlie@example.com',
    age: 42,
    department: 'Sales',
    skills: ['Negotiation', 'CRM', 'Networking'],
    salary: 68000,
    created_at: new Date('2024-01-17T14:45:00Z'),
    updated_at: new Date('2024-01-17T14:45:00Z')
  },
  {
    name: 'Diana Prince',
    email: 'diana@example.com',
    age: 31,
    department: 'Engineering',
    skills: ['Java', 'Spring', 'Microservices'],
    salary: 92000,
    created_at: new Date('2024-01-18T11:20:00Z'),
    updated_at: new Date('2024-01-18T11:20:00Z')
  },
  {
    name: 'Eve Wilson',
    email: 'eve@example.com',
    age: 29,
    department: 'HR',
    skills: ['Recruitment', 'Training', 'Performance Management'],
    salary: 65000,
    created_at: new Date('2024-01-19T08:30:00Z'),
    updated_at: new Date('2024-01-19T08:30:00Z')
  }
]);

print('Inserted demo users data');

// Create indexes for demo_users collection
db.demo_users.createIndex({ email: 1 }, { unique: true });
db.demo_users.createIndex({ department: 1 });
db.demo_users.createIndex({ skills: 1 });
db.demo_users.createIndex({ created_at: 1 });

print('Created indexes for demo_users collection');

// Demo products collection
db.demo_products.insertMany([
  {
    name: 'Laptop Pro 15',
    category: 'Electronics',
    price: 1299.99,
    stock: 25,
    description: 'High-performance laptop for professionals',
    tags: ['laptop', 'computer', 'electronics'],
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Wireless Headphones',
    category: 'Electronics',
    price: 199.99,
    stock: 50,
    description: 'Premium noise-canceling wireless headphones',
    tags: ['headphones', 'audio', 'wireless'],
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    name: 'Office Chair',
    category: 'Furniture',
    price: 299.99,
    stock: 15,
    description: 'Ergonomic office chair with lumbar support',
    tags: ['chair', 'furniture', 'office'],
    created_at: new Date(),
    updated_at: new Date()
  }
]);

print('Inserted demo products data');

// Create indexes for demo_products collection
db.demo_products.createIndex({ name: 1 });
db.demo_products.createIndex({ category: 1 });
db.demo_products.createIndex({ tags: 1 });
db.demo_products.createIndex({ price: 1 });

print('Created indexes for demo_products collection');

// Demo logs collection (for application logs)
db.demo_logs.insertMany([
  {
    level: 'info',
    message: 'Application started successfully',
    timestamp: new Date(),
    service: 'mcp-server',
    metadata: { version: '1.0.0', environment: 'development' }
  },
  {
    level: 'warning',
    message: 'Database connection slow',
    timestamp: new Date(),
    service: 'database',
    metadata: { response_time: 2500, threshold: 1000 }
  }
]);

print('Inserted demo logs data');

// Create indexes for demo_logs collection
db.demo_logs.createIndex({ timestamp: 1 });
db.demo_logs.createIndex({ level: 1 });
db.demo_logs.createIndex({ service: 1 });

print('Created indexes for demo_logs collection');

// Create a view for user statistics
db.createView(
  'user_stats',
  'demo_users',
  [
    {
      $group: {
        _id: '$department',
        count: { $sum: 1 },
        avg_age: { $avg: '$age' },
        avg_salary: { $avg: '$salary' },
        total_salary: { $sum: '$salary' }
      }
    },
    {
      $sort: { count: -1 }
    }
  ]
);

print('Created user_stats view');

print('MongoDB initialization completed successfully!');
print('Database: novellus');
print('User: novellus_user');
print('Collections created: demo_users, demo_products, demo_logs');
print('View created: user_stats');
print('All indexes created successfully');
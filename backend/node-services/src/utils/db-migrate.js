require('dotenv').config();
const fs = require('fs');
const path = require('path');
// Using built-in fetch API available in newer Node.js versions

// Function to execute SQL directly via the REST API
async function executeSql(sql) {
  const response = await fetch(`${process.env.SUPABASE_URL}/rest/v1/sql`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': process.env.SUPABASE_KEY,
      'Authorization': `Bearer ${process.env.SUPABASE_KEY}`
    },
    body: JSON.stringify({ query: sql })
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`SQL execution failed: ${errorText}`);
  }
  
  return await response.json();
}

// Function to run migrations
async function runMigrations() {
  try {
    console.log('Starting database migrations...');
    
    // Get list of migration files
    const migrationsDir = path.join(__dirname, '..', 'migrations');
    const migrationFiles = fs.readdirSync(migrationsDir)
      .filter(file => file.endsWith('.sql'))
      .sort(); // Ensure migrations run in order
    
    console.log(`Found ${migrationFiles.length} migration files`);
    
    // Process each migration file
    for (const file of migrationFiles) {
      console.log(`Processing migration: ${file}`);
      
      // Read migration file
      const migrationSql = fs.readFileSync(path.join(migrationsDir, file), 'utf8');
      
      try {
        console.log(`Executing migration ${file}...`);
        
        // Execute the migration SQL directly
        await executeSql(migrationSql);
        
        console.log(`Successfully applied migration: ${file}`);
      } catch (err) {
        console.error(`Error applying migration ${file}:`, err.message);
        throw err;
      }
    }
    console.log('Database migrations completed successfully.');
  } catch (error) {
    console.error('Error running migrations:', error.message);
    process.exit(1);
  }
}

// Run migrations
runMigrations();

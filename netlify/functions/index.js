// Netlify function to redirect to the Python API handler
const { spawn } = require('child_process');
const path = require('path');

exports.handler = async function(event, context) {
  try {
    // Pass the request to the Python handler
    const pythonPath = process.env.PYTHON_PATH || 'python';
    const scriptPath = path.join(__dirname, '../../api/index.py');
    
    // Create a process to run the Python script
    const pythonProcess = spawn(pythonPath, ['-c', `
import sys
import json
import importlib.util

# Load the Python handler
spec = importlib.util.spec_from_file_location("api_handler", "${scriptPath.replace(/\\/g, '/')}")
api_handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_handler)

# Parse the event data
event_data = json.loads("""${JSON.stringify(event)}""")

# Call the handler function
result = api_handler.handler(event_data, {})

# Output the result
print(json.dumps(result))
`]);
    
    let responseData = '';
    let errorData = '';
    
    pythonProcess.stdout.on('data', (data) => {
      responseData += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
    });
    
    return new Promise((resolve, reject) => {
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error(`Python process exited with code ${code}`);
          console.error(`Error: ${errorData}`);
          resolve({
            statusCode: 500,
            body: JSON.stringify({ error: 'Internal Server Error', details: errorData }),
          });
        } else {
          try {
            const result = JSON.parse(responseData);
            resolve(result);
          } catch (e) {
            console.error(`Error parsing Python response: ${e.message}`);
            console.error(`Response data: ${responseData}`);
            resolve({
              statusCode: 500,
              body: JSON.stringify({ error: 'Error parsing response', details: responseData }),
            });
          }
        }
      });
    });
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal Server Error', message: error.message }),
    };
  }
};

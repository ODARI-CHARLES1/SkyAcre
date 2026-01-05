// This file sets up the main Express server for the backend.
// It handles API routes, spawns the AI microservice (Flask), connects to MongoDB, and starts the server.

// Import Express framework for building the web server
import express from "express";
// Import spawn from child_process to run the Python Flask app
import { spawn } from "child_process";
// Import path module for handling file paths
import path from "path";
// Import UserRegistration service for database connection
import UserRegistration from "./Services/UserRegistration.js";
// Import config from dotenv to load environment variables
import { config } from "dotenv";
// Import user router for user-related routes
import UserRouter from "./Routes/userRouter.js";
// Import cors for handling Cross-Origin Resource Sharing
import cors from "cors";
// Import farmer router for farmer-related routes
import farmerRouter from "./Routes/farmerRoute.js";

// Load environment variables from .env file
config();

// Create an Express application instance
const app = express();

// Middleware to parse incoming JSON requests
app.use(express.json());

// Middleware to enable CORS for specified origins
// app.use(
//   cors({
//     origin: ["http://localhost:5173", "https://sky-acre-58t9.vercel.app/"], // Allowed origins (dev and production)
//     methods: ["GET", "POST", "PUT", "DELETE"], // Allowed HTTP methods
//     credentials: true, // Allow credentials (cookies, auth headers)
//   })
// );

// Get MongoDB URL from environment variables
const mongo_url = process.env.MONGO_URL;
// Get port from environment variables or default to 3000
const PORT = process.env.PORT || 3000;

// Log that the Flask AI microservice is starting
console.log("Starting Flask AI microservice...");

// Resolve the path to the Python executable in the virtual environment (Windows-specific)
const pythonPath = path.resolve("../AI-Models/venv/Scripts/python.exe"); // Windows
// Resolve the path to the Flask app.py file
const appPath = path.resolve("../AI-Models/app.py");

// Spawn the Flask process using the Python executable and app.py
const flaskProcess = spawn(pythonPath, [appPath]);

// Listen for stdout data from the Flask process and log it
flaskProcess.stdout.on("data", (data) => {
  console.log(`Flask: ${data.toString().trim()}`);
});

// Listen for stderr data from the Flask process and log errors
flaskProcess.stderr.on("data", (data) => {
  console.error(`Flask Error: ${data.toString().trim()}`);
});

// Listen for the Flask process to close and log the exit code
flaskProcess.on("close", (code) => {
  console.log(`Flask process exited with code ${code}`);
});

// Create a new UserRegistration instance
const register = new UserRegistration();
// Connect to MongoDB using the provided URL
register.connect(mongo_url);

// Use the user router for routes starting with /user
app.use("/user", UserRouter);
// Use the farmer router for routes (mounted at root)
app.use("/",farmerRouter)

// Define a testing route that responds with "Testing..."
app.get("/testing", (req, res) => {
  res.send("Testing...");
});

// Define the root route that responds with "Server is running..."
app.get("/", (req, res) => {
  res.send("Server is running...");
});

// Start the server and listen on the specified port
app.listen(PORT, () => {
  console.log(`✅ Node server running on http://localhost:${PORT}`);
});

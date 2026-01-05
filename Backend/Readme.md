# Backend Workflow Documentation

## Overview

The backend is built with Node.js and Express.js, serving as an API server that integrates user management, farmer prediction services, and email notifications. It communicates with a MongoDB database for data persistence and spawns a separate Flask-based AI microservice for machine learning predictions.

## Server Initialization

- The server starts by loading environment variables from a `.env` file.
- It sets up CORS to allow requests from `http://localhost:5173` (the frontend development server) and `https://sky-acre-58t9.vercel.app/` (production frontend).
- It spawns a child process running a Python Flask application located at `../AI-Models/app.py` using the virtual environment at `../AI-Models/venv/Scripts/python.exe`. This Flask service handles AI/ML predictions and runs on `http://127.0.0.1:5000`.
- The server connects to MongoDB using a URL from environment variables.
- It mounts two main route groups: `/user` for user management and `/` (root) for farmer-related operations.

## User Management Workflow

### 1. User Registration (`POST /user/register`)

- Accepts `name`, `email`, and `password` in the request body.
- Validates that all fields are provided.
- Checks if a user with the given email already exists in the database.
- If not, creates a new user document in MongoDB using the User model (which includes name, email, and password fields).
- Sends a welcome email to the new user using Nodemailer with a custom HTML template.
- Returns success response with user data or conflict response if user exists.

### 2. Fetch All Users (`GET /user/users`)

- Retrieves all user documents from MongoDB.
- Returns them in a JSON response.

### 3. Fetch User by ID (`GET /user/users/:id`)

- Takes a user ID from the URL parameter.
- Queries MongoDB for the user with that ID.
- Returns the user data or a 404 if not found.

### 4. Update User (`POST /user/users/update/:id`)

- Accepts updated `name` and `email` in the request body.
- Updates the user document in MongoDB by ID.
- Sends an email notification (using the same welcome template, adapted for updates).
- Returns the updated user information.

## Farmer Prediction Workflow

### 1. Prediction Request (`POST /farmer/predict`)

- Accepts prediction request data in the request body (likely crop/fertilizer data based on the AI models).
- Forwards the request to the Flask AI service at `http://127.0.0.1:5000/farmer/predict` using Axios.
- Returns the prediction results from the Flask service to the client.
- Handles errors if the Flask service is unreachable.

## Supporting Services

- **Database Connection**: Uses Mongoose to connect to MongoDB. The connection is established once during server startup.
- **Email Service**: Configured with Gmail SMTP. Sends HTML emails using Nodemailer, with templates stored in `Assets/userEmails.js`.
- **AI Integration**: The Flask child process provides ML predictions. The Node.js backend acts as a proxy, forwarding requests and responses between the frontend and the AI service.

## Error Handling

- All routes include try-catch blocks for database operations and external service calls.
- Returns appropriate HTTP status codes (400 for bad requests, 404 for not found, 409 for conflicts, 500 for server errors).
- Logs errors to the console for debugging.

## Security and Configuration

- Uses environment variables for sensitive data (MongoDB URL, email credentials, port).
- CORS is configured to restrict origins.
- Passwords are stored in plain text in the database (note: this is not secure; consider hashing in production).

This workflow supports a farming application where users can register and manage accounts, and farmers can request AI-powered predictions for crops and fertilizers.

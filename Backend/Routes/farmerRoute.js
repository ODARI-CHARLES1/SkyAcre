// This file defines the routes for farmer-related API endpoints.
// It handles requests for crop and fertilizer predictions.

// Import the Express framework for creating the router
import express from 'express'
// Import the predict function from the farmer controller
import {predict} from '../Controllers/farmerController.js'
// Import requireAuth middleware from Clerk to protect routes
import { requireAuth } from '@clerk/express';

// Create a new Express router instance for farmer routes
const farmerRouter=express.Router()

// Define a POST route for /farmer/predict that requires authentication
// When a POST request is made to this endpoint, it calls the predict function
farmerRouter.post("/farmer/predict",predict)

// Export the farmerRouter as the default export
export default farmerRouter;
import express from 'express'
import {predict} from '../Controllers/farmerController.js'
import { requireAuth } from '@clerk/express';
const farmerRouter=express.Router()
farmerRouter.post("/farmer/predict", requireAuth(), predict)

export default farmerRouter
import express from 'express'
import {predict} from '../Controllers/farmerController.js'
const farmerRouter=express.Router()
farmerRouter.post("/farmer/predict",predict)

export default farmerRouter
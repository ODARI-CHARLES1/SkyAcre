import express from 'express';
import { saveNewUser,getRegisteredUsers, updateUserById,getRegisteredUserById } from '../Controllers/userController.js';

const UserRouter = express.Router();

UserRouter.post("/register", saveNewUser);
UserRouter.get("/users",getRegisteredUsers)
UserRouter.get("/users/:id",getRegisteredUserById)
UserRouter.post("/users/update/:id",updateUserById)
export default UserRouter;

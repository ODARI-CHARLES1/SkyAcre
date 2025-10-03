import mongoose from "mongoose";
import User from "../Models/userModel.js";
import dbConnect from "../Config/db.js";
class UserRegistration {
  constructor() {
  }

  async connect(mongo_url) {
    await dbConnect(mongo_url);
  }

  async saveUser(body) {
    try {
      const { name, email,password } = body;

      const existingUser = await User.findOne({ email });
      if (existingUser) {
        return { status: false, user: "User Already Exists." };
      }

      const newUser = new User({ name, email,password });
      await newUser.save();

      return { status: true, user: newUser };
    } catch (err) {
      console.error("Failed to save user:", err);
      throw new Error("Database error while saving user.");
    }
  }

  async getUsers() {
    try {
      const users = await User.find();
      return users;
    } catch (error) {
      console.error("Failed to retrieve users:", error);
      throw new Error("Database error while retrieving users.");
    }
  }

  async getUserById(prompt){
    try{
      const user=User.findOne({_id:prompt})
      return user;
    }
    catch(error){
      console.error("Failed to retrieve user",err)
      throw new Error("Database error while retrieving user.")
    }
  }

  async updateUserById(id,userData){
    try {
      const {name,email}=userData
       const updatedUser=await User.findByIdAndUpdate(id,{name:userData.name,email:userData.email})
       console.log(updatedUser)
       return updatedUser;

    } catch (error) {
      console.error("Failed to Update User Info",error)
      throw new Error("Database error while updating user info")
    }
  }
}

export default UserRegistration;

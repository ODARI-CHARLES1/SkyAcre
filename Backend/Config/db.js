 import mongoose from "mongoose";
 
 const dbConnect =async (mongo_url)=>{
     try {
          await mongoose.connect(mongo_url);
          console.log("Connected to DB.");
        } catch (err) {
          console.log("Failed to connect to DB.", err);
        }
 }

 export default dbConnect
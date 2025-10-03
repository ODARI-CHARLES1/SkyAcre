import express from 'express';
import UserRegistration from './Services/UserRegistration.js';
import { config } from 'dotenv';
import UserRouter from './Routes/userRouter.js';
import cors from 'cors'
const app = express();
app.use(cors())
app.use(express.json())
config()


const mongo_url=process.env.MONGO_URL
const PORT = process.env.PORT || 3000;
const register=new UserRegistration()

register.connect(mongo_url)

app.use("/user",UserRouter)
app.get("/testing",(req,res)=>{
  res.send("Testing...")
})

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
import express from "express";
import { spawn } from "child_process";
import path from "path";
import UserRegistration from "./Services/UserRegistration.js";
import { config } from "dotenv";
import UserRouter from "./Routes/userRouter.js";
import cors from "cors";
import farmerRouter from "./Routes/farmerRoute.js";
config();
const app = express();
app.use(express.json());
app.use(
  cors({
    origin: ["http://localhost:5173", "https://sky-acre-58t9.vercel.app/"],
    methods: ["GET", "POST", "PUT", "DELETE"],
    credentials: true,
  })
);

const mongo_url = process.env.MONGO_URL;
const PORT = process.env.PORT || 3000;

console.log("Starting Flask AI microservice...");


const pythonPath = path.resolve("../AI-Models/venv/Scripts/python.exe"); // Windows
const appPath = path.resolve("../AI-Models/app.py");

const flaskProcess = spawn(pythonPath, [appPath]);

flaskProcess.stdout.on("data", (data) => {
  console.log(`Flask: ${data.toString().trim()}`);
});

flaskProcess.stderr.on("data", (data) => {
  console.error(`Flask Error: ${data.toString().trim()}`);
});

flaskProcess.on("close", (code) => {
  console.log(`Flask process exited with code ${code}`);
});

const register = new UserRegistration();
register.connect(mongo_url);
app.use("/user", UserRouter);
app.use("/",farmerRouter)
app.get("/testing", (req, res) => {
  res.send("Testing...");
});

app.get("/", (req, res) => {
  res.send("Server is running...");
});

app.listen(PORT, () => {
  console.log(`✅ Node server running on http://localhost:${PORT}`);
});

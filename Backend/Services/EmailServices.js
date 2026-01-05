import nodemailer from "nodemailer";
import dotenv from "dotenv";
import { welcomeTemplate } from "../Assets/userEmails.js"; 
dotenv.config();

const transporter = nodemailer.createTransport({
  host: "smtp.gmail.com", 
  port: 587,                
  secure: false,            
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

export const sendMail = async (userInfo) => {
  try {
    const htmlContent = welcomeTemplate(userInfo.name); 

    const info = await transporter.sendMail({
      from: `"SkyAcre" <${process.env.EMAIL_USER}>`,
      to:userInfo.email,
      subject: `Welcome to SkyAcre Company`,
      html:`${htmlContent}`
    });

    console.log("✅ Message sent: %s", info.messageId);
  } catch (error) {
    console.error("❌ Error sending email:", error);
  }
};

export default sendMail;


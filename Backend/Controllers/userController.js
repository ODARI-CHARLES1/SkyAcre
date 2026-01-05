import UserRegistration from "../Services/UserRegistration.js";
import User from "../Models/userModel.js";
import sendMail from "../Services/EmailServices.js";

// Save new user
export const saveNewUser = async (req, res) => {
  try {
    const { name, email,password} = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ error: "Name and email are required." });
    }

    const register = new UserRegistration();
    const registeredUser = await register.saveUser(req.body);
    console.log(registeredUser.user)
    sendMail(registeredUser.user)

    if (registeredUser.status) {
      return res.status(201).json({
        message: "User Registered Successfully.",
        user: registeredUser.user,
      });
    } else {
      return res.status(409).json({
        message: "User Already Exists",
        user: "already exists",
      });
    }
  } catch (error) {
    return res.status(500).json({ error: "Failed to register new user." });
  }
};

export const getRegisteredUsers = async (req, res) => {
  try {
    const register = new UserRegistration();
    const users = await register.getUsers();

    return res.status(200).json({ message: "Stored users", users });
  } catch (err) {
    console.error("Error fetching users:", err);
    return res.status(500).json({ error: "Failed to retrieve users." });
  }
};

// Get user by ID
export const getRegisteredUserById = async (req, res) => {
  try {
    const register = new UserRegistration();
    const user = await register.getUserById(req.params.id);

    if (user) {
      return res.status(200).json({ message: "Stored user", user });
    } else {
      return res.status(404).json({ message: "User doesn't exist", user: "None" });
    }
  } catch (error) {
    console.error("Error Fetching user", error);
    return res.status(500).json({ error: "Failed to retrieve user" });
  }
};

// Update user by ID and provide the user information to update...
export const updateUserById = async (req, res) => {
  try {
    const register = new UserRegistration();
    const updatedUser = await register.updateUserById(req.params.id, req.body);
    if (updatedUser) {
      const updatedUserInfo=await User.findById({_id:req.params.id})
      console.log(process.env.EMAIL_USER)
      sendMail(updatedUserInfo);
      return res.status(200).json({
        message: "User Info Updated Successfully",
        updatedUserInfo,
      }
    );
    } else {
      return res.status(404).json({
        message: "User Not Found",
        user: "None",
      });
    }
  } catch (error) {
    console.error("Error Updating user info", error);
    return res.status(500).json({ error: "Failed to update user" });
  }
};



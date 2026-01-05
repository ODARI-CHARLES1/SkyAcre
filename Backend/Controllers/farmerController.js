import { predictService } from "../Services/ChildProcess.js";

export const predict = async (req, res) => {
  try {
    const response = await predictService(req.body);
    res.status(200).json({
      message: "Prediction Success",
      predicts: response,
    });
  } catch (error) {
    console.error("❌ Prediction failed:", error.message);
    return res.status(500).json({ error: "Failed to fetch prediction." });
  }
};

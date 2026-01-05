import axios from "axios";
export const predictService = async (request) => {
  try {
    const response = await axios.post(
      "http://127.0.0.1:5000/farmer/predict",
      request
    );
    return response.data;
  } catch (error) {
    console.error("❌ Flask communication error:", error.message);
    throw new Error("Failed to connect to Flask server");
  }
};

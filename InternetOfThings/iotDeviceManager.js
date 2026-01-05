// IoT Device Manager Module
// This module provides functionality for managing IoT devices in the SkyAcre agricultural platform.
// It integrates with the Backend services to collect sensor data for AI-driven crop and fertilizer recommendations.

class IoTDeviceManager {
  constructor() {
    this.devices = new Map(); // Store connected devices
    this.dataBuffer = []; // Buffer for collected sensor data
  }

  // Connect to an IoT device
  async connectDevice(deviceId, deviceConfig) {
    try {
      // Simulate device connection (replace with actual IoT protocol like MQTT)
      console.log(`Connecting to IoT device: ${deviceId}`);
      this.devices.set(deviceId, {
        id: deviceId,
        config: deviceConfig,
        connected: true,
        lastSeen: new Date()
      });
      return { success: true, message: `Device ${deviceId} connected successfully` };
    } catch (error) {
      console.error(`Failed to connect to device ${deviceId}:`, error);
      return { success: false, message: error.message };
    }
  }

  // Disconnect from an IoT device
  async disconnectDevice(deviceId) {
    try {
      if (this.devices.has(deviceId)) {
        this.devices.delete(deviceId);
        console.log(`Disconnected from IoT device: ${deviceId}`);
        return { success: true, message: `Device ${deviceId} disconnected` };
      } else {
        return { success: false, message: `Device ${deviceId} not found` };
      }
    } catch (error) {
      console.error(`Failed to disconnect device ${deviceId}:`, error);
      return { success: false, message: error.message };
    }
  }

  // Collect sensor data from a device
  async collectSensorData(deviceId) {
    try {
      const device = this.devices.get(deviceId);
      if (!device || !device.connected) {
        throw new Error(`Device ${deviceId} is not connected`);
      }

      // Simulate sensor data collection (replace with actual sensor readings)
      const sensorData = {
        deviceId,
        timestamp: new Date(),
        soilMoisture: Math.random() * 100, // Percentage
        temperature: 20 + Math.random() * 20, // Celsius
        humidity: 30 + Math.random() * 50, // Percentage
        phLevel: 5.5 + Math.random() * 2, // pH scale
        nitrogen: Math.random() * 50, // mg/kg
        phosphorus: Math.random() * 30, // mg/kg
        potassium: Math.random() * 40 // mg/kg
      };

      this.dataBuffer.push(sensorData);
      device.lastSeen = new Date();

      console.log(`Collected sensor data from ${deviceId}:`, sensorData);
      return { success: true, data: sensorData };
    } catch (error) {
      console.error(`Failed to collect data from device ${deviceId}:`, error);
      return { success: false, message: error.message };
    }
  }

  // Get buffered data for processing by AI models
  getBufferedData() {
    const data = [...this.dataBuffer];
    this.dataBuffer = []; // Clear buffer after retrieval
    return data;
  }

  // Send data to Backend for AI processing
  async sendDataToBackend(data) {
    try {
      // This would integrate with Backend routes/controllers
      // For now, simulate sending to AI model service
      console.log('Sending data to Backend for AI processing:', data);
      // In a real implementation, make HTTP request to Backend API
      return { success: true, message: 'Data sent to Backend successfully' };
    } catch (error) {
      console.error('Failed to send data to Backend:', error);
      return { success: false, message: error.message };
    }
  }

  // Get list of connected devices
  getConnectedDevices() {
    return Array.from(this.devices.values()).filter(device => device.connected);
  }

  // Monitor device health
  async checkDeviceHealth(deviceId) {
    const device = this.devices.get(deviceId);
    if (!device) {
      return { status: 'disconnected' };
    }

    const timeSinceLastSeen = Date.now() - device.lastSeen.getTime();
    const isHealthy = timeSinceLastSeen < 300000; // 5 minutes

    return {
      deviceId,
      status: device.connected && isHealthy ? 'healthy' : 'unhealthy',
      lastSeen: device.lastSeen
    };
  }
}

module.exports = new IoTDeviceManager();
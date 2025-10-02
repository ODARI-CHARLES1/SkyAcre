import React from 'react'

const services = [
  {
    title: "Aerial Crop Monitoring",
    description: "Monitor crop health with NDVI and multispectral imaging for better decision-making.",
  },
  {
    title: "Pesticide & Fertilizer Spraying",
    description: "Efficient and targeted drone spraying reduces chemical waste and saves time.",
  },
  {
    title: "Irrigation Analysis",
    description: "Detect dry zones and optimize water usage with precision drone analysis.",
  },
  {
    title: "Soil & Plant Health Mapping",
    description: "High-resolution mapping helps identify nutrient deficiencies and plan yields.",
  },
  {
    title: "Field Survey & 3D Mapping",
    description: "Accurate aerial surveys for land management and farm planning.",
  },
  {
    title: "Data-Driven Insights",
    description: "AI-powered analytics from drone data for smarter, data-driven farming.",
  },
];

const ServicesProvided = () => {
  return (
    <>
      
      <section className="py-16 px-6 md:px-12 lg:px-24 bg-gray-50">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-2xl shadow hover:shadow-lg transition duration-300 text-center"
            >
              <h2 className="text-xl font-semibold mb-2">{service.title}</h2>
              <p className="text-gray-600 mb-4">{service.description}</p>
              <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition">
                Learn More
              </button>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}

export default ServicesProvided

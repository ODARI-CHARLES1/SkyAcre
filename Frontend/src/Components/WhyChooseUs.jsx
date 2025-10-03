import React from 'react'

const WhyChooseUs = () => {
  return (
    <>
      <section className="bg-white py-16 text-center px-6 md:px-20">
        <h2 className="text-3xl font-bold mb-6">Why Choose SkyAcre?</h2>
        <p className="text-gray-700 max-w-3xl mx-auto mb-8">
          SkyAcre combines drone technology, AI, and sustainability to empower farmers with actionable insights.
          Our services reduce costs, save time, and maximize crop yield.
        </p>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-6 text-gray-600">
          <li>✔ Precision Farming with Advanced Drones</li>
          <li>✔ Eco-Friendly & Sustainable Practices</li>
          <li>✔ Reduced Costs & Increased Efficiency</li>
          <li>✔ AI-Powered Data Insights</li>
        </ul>
      </section>
    </>
  )
}

export default WhyChooseUs

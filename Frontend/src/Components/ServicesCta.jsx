import React from 'react'

const ServicesCta = () => {
  return (
    <>
       <section className="bg-green-700 text-white py-12 text-center">
        <h2 className="text-2xl font-semibold mb-4">Ready to revolutionize your farming?</h2>
        <p className="mb-6">Get in touch with AgriFly and take your agriculture to the next level.</p>
        <a
          href="/contact"
          className="px-6 py-3 bg-white text-green-700 font-semibold rounded-lg shadow hover:bg-gray-100 transition"
        >
          Contact Us
        </a>
      </section>
    </>
  )
}

export default ServicesCta

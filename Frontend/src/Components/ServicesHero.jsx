import React from 'react'

const ServicesHero = () => {
  return (
    <>
  <section className="text-gray-600 body-font">
  <div className="container mx-auto flex px-5 py-24 items-center justify-center flex-col">
    <div className="text-center lg:w-2/3 w-full">
      <h1 className="title-font sm:text-6xl text-4xl mb-4 font-medium text-gray-900">Our Services</h1>
      <p className="mb-8 leading-relaxed">Take a look at the variety of services we have to offer</p>
      </div>
  <img 
 className="w-full max-w-7xl h-[650px] mx-auto mb-10 object-cover object-center rounded-2xl shadow-2xl"
  src="https://fnb.tech/wp-content/uploads/2025/03/Smart-Farming-Tools.jpeg"
  alt="Drone flying over green farmland for analysis"
  />
  </div>
  </section>
    </>
  )
}

export default ServicesHero

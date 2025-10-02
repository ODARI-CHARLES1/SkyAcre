import React from 'react'
import { useNavigate } from 'react-router-dom';
const Hero = () => {
  const navigate=useNavigate();
  return (
    <section
      className="h-screen flex items-center justify-center bg-cover bg-center relative"
      style={{
        backgroundImage:
          "url('https://i.pinimg.com/1200x/7b/94/9c/7b949ce6357106bb9647f793a0a97343.jpg')",
      }}
    >
      <div className="absolute inset-0 bg-black/50"></div>

      <div className="container mx-auto px-5 py-24 relative z-10 text-center text-white">
        <h1 className="sm:text-5xl text-3xl mb-6 font-bold">
          Stay ahead with smart farming.
        </h1>
        <p className="mb-8 leading-relaxed max-w-2xl mx-auto">
          Sky<span className='text-green-500'>A</span>cre ,we harness the power of drones and smart sensors to scan fields from above,detecting early signs of crop 
          diseases and analyzing soil properties such as pH,temperature and moisture with precision.
        </p>
        <div className="flex justify-center gap-4">
          <button onClick={()=>navigate("/services")} className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg text-lg">
            Book a Service
          </button>
          <button onClick={()=>navigate("/about")} className="px-6 py-3 bg-white text-gray-800 hover:bg-gray-200 rounded-lg text-lg">
            Learn More
          </button>
        </div>
      </div>
    </section>
  )
}

export default Hero

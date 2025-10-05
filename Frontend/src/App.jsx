import { Route, Routes } from 'react-router-dom'
import { motion, useAnimation } from "framer-motion"
import { useEffect } from "react"
import { SignUp as ClerkSignUp, SignIn as ClerkSignIn } from '@clerk/clerk-react'

import Home from './Pages/PublicPage/Home'
import FAQ from './Pages/PublicPage/FAQ'
import AboutUs from './Pages/PublicPage/AboutUs'
import Contact from './Pages/PublicPage/Contact'
import PricingPlans from './Pages/PublicPage/PricingPlans'
import Services from './Pages/PublicPage/Services'
import Blog from "./Pages/PublicPage/Blog"
import Farmer from './Pages/Farmers/Farmer'
const App = () => {
  const controls = useAnimation()

  useEffect(() => {
    const flyRandom = () => {
      const randomX = Math.random() * (window.innerWidth - 200)
      const randomY = Math.random() * (window.innerHeight - 200)

      controls.start({
        x: randomX,
        y: randomY,
        rotate: [0, -5, 5, 0],
        transition: {
          duration: 5,
          ease: "easeInOut"
        }
      })
    }

    flyRandom() 
    const interval = setInterval(flyRandom, 5500)

    return () => clearInterval(interval)
  }, [controls])

  return (
    <div className="relative overflow-x-hidden">
      <motion.img
        className="w-56 h-56 absolute z-30 pointer-events-none"
        src="/drone1.png"
        alt="Drone"
        animate={controls}
      />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<AboutUs />} />
        <Route path="/faqs" element={<FAQ />} />
        <Route path="/services" element={<Services />} />
        <Route path="/pricing" element={<PricingPlans />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/resources" element={<Blog />} />
        <Route path="/signup" element={<div className="flex justify-center items-center min-h-screen"><ClerkSignUp /></div>} />
        <Route path="/signin" element={<div className="flex justify-center items-center min-h-screen"><ClerkSignIn /></div>} />
        <Route path="/farmer" element={<Farmer/>}/>
      </Routes>
    </div>
  )
}

export default App

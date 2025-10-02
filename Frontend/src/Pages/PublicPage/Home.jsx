import React from 'react'
import Navbar from '../../Components/Navbar'
import Hero from '../../Components/Hero'
import Cta from '../../Components/Cta'
import Features from '../../Components/Features'
import HowItWorks from '../../Components/HowItWorks'
import Team from '../../Components/Team'
import Testimonials from '../../Components/Testimonials'
import Footer from '../../Components/Footer'
import WhyUs from '../../Components/WhyUs'
import Gallery from '../../Components/Gallery'
import Statistic from '../../Components/statistic'
import Pricing from "../../Components/Pricing"
const Home = () => {
  return (
    <div>
      <Navbar/>
      <Hero/>
      <Features/>
      <WhyUs/>
      <HowItWorks/>
      <Gallery/>
      <Team/>
      <Testimonials/>
      <Statistic/>
      <Pricing/>
      <Cta/>
      <Footer/>
    </div>
  )
}

export default Home

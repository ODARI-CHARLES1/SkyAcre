import React from "react";
import Navbar from "../../Components/Navbar";
import ServicesHero from "../../Components/ServicesHero";
import Gallery from "../../Components/Gallery"
import ServicesCta from "../../Components/ServicesCta"
import HowItWorks from "../../Components/HowItWorks";
import BreadCrumb from "../../Components/BreadCrumb"
import Footer from "../../Components/Footer"
import Pricing from "../../Components/Pricing"
const Services = () => {
  return (
    <>
      <Navbar />
      <ServicesHero/>
      <Gallery/>
       <HowItWorks/>
       <Pricing/>
      <ServicesCta/>
      <Footer/>
    </>
  );
};

export default Services;

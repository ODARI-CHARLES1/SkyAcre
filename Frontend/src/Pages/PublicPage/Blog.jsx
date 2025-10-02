import React from 'react'
import Navbar from '../../Components/Navbar'
import BlogSection from '../../Components/BlogSection'
import BreadCrumb from "../../Components/BreadCrumb"
import Content from "../../Components/Content"
import ResourceSteps from "../../Components/ResourceSteps"
import BlogCta from "../../Components/BlogCta"
import Footer from "../../Components/Footer"
import BlogHero from "../../Components/BlogHero"
const Blog = () => {
  return (
    <div>
      <Navbar/>
      <BlogHero/>
      <BlogSection/>
      <Content/>
      <ResourceSteps/>
      <BlogCta/>
      <Footer/>
    </div>
  )
}

export default Blog

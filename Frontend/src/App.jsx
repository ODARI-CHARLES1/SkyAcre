// This file defines the main App component for the React application.
// It sets up routing for different pages and includes an animated drone image that moves randomly across the screen.
// The app uses React Router for navigation and Framer Motion for animations.
// Clerk is used for authentication (sign up and sign in).

// Import Route and Routes from react-router-dom to handle client-side routing
import { Route, Routes } from 'react-router-dom'
// Import motion and useAnimation from framer-motion for animating the drone image
import { motion, useAnimation } from "framer-motion"
// Import useEffect hook from React for side effects like setting up intervals
import { useEffect } from "react"
// Import SignUp and SignIn components from Clerk for user authentication
import { SignUp as ClerkSignUp, SignIn as ClerkSignIn } from '@clerk/clerk-react'

// Import page components for different routes
import Home from './Pages/PublicPage/Home'
import FAQ from './Pages/PublicPage/FAQ'
import AboutUs from './Pages/PublicPage/AboutUs'
import Contact from './Pages/PublicPage/Contact'
import PricingPlans from './Pages/PublicPage/PricingPlans'
import Services from './Pages/PublicPage/Services'
import Blog from "./Pages/PublicPage/Blog"
import Farmer from './Pages/Farmers/Farmer'

// Define the main App component as an arrow function
const App = () => {
  // Create an animation controller using Framer Motion's useAnimation hook
  const controls = useAnimation()

  // useEffect hook runs side effects after the component mounts
  // It sets up an interval to animate the drone randomly every 5.5 seconds
  useEffect(() => {
    // Define a function to move the drone to a random position
    const flyRandom = () => {
      // Calculate random x and y positions within the window bounds, leaving some margin
      const randomX = Math.random() * (window.innerWidth - 200)
      const randomY = Math.random() * (window.innerHeight - 200)
      // Log the random positions for debugging (can be removed in production)
      console.log(randomX)
      console.log(randomY)
      // Start the animation with the calculated positions and a rotation effect
      controls.start({
        x: randomX,
        y: randomY,
        rotate: [0, -5, 5, 0], // Rotate slightly back and forth
        transition: {
          duration: 5, // Animation duration in seconds
          ease: "easeInOut" // Easing function for smooth animation
        }
      })
    }

    // Call flyRandom immediately to start the animation
    flyRandom()
    // Set up an interval to call flyRandom every 5500 milliseconds (5.5 seconds)
    const interval = setInterval(flyRandom, 5500)

    // Cleanup function to clear the interval when the component unmounts
    return () => clearInterval(interval)
  }, [controls]) // Dependency array includes controls to re-run if it changes

  // Return the JSX to render the component
  return (
    // Main container div with relative positioning and hidden horizontal overflow
    <div className="relative overflow-x-hidden">
      {/* Animated drone image using Framer Motion's motion.img */}
      <motion.img
        className="w-56 h-56 absolute z-30 pointer-events-none" // Styling: size, absolute position, high z-index, no pointer events
        src="/drone1.png" // Source of the drone image from public folder
        alt="Drone" // Alt text for accessibility
        animate={controls} // Connect to the animation controls
      />
      {/* Routes component to define the application's routing */}
      <Routes>
        {/* Define routes for different pages */}
        <Route path="/" element={<Home />} /> {/* Home page at root path */}
        <Route path="/about" element={<AboutUs />} /> {/* About Us page */}
        <Route path="/faqs" element={<FAQ />} /> {/* FAQ page */}
        <Route path="/services" element={<Services />} /> {/* Services page */}
        <Route path="/pricing" element={<PricingPlans />} /> {/* Pricing page */}
        <Route path="/contact" element={<Contact />} /> {/* Contact page */}
        <Route path="/resources" element={<Blog />} /> {/* Blog/Resources page */}
        {/* Authentication routes using Clerk components, centered on screen */}
        <Route path="/signup" element={<div className="flex justify-center items-center min-h-screen"><ClerkSignUp /></div>} />
        <Route path="/signin" element={<div className="flex justify-center items-center min-h-screen"><ClerkSignIn /></div>} />
        <Route path="/farmer" element={<Farmer/>}/> {/* Farmer dashboard page */}
      </Routes>
    </div>
  )
}

// Export the App component as the default export
export default App

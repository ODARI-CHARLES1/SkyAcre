import React from 'react'

const Footer = () => {
  return (
    <footer className="text-gray-600 body-font">
      <div className="container  px-5 py-24 mx-auto">
        <div className="flex-grow flex flex-wrap space-between md:pl-20 -mb-10 mt-10 md:mt-0">


          {/* Pages */}
          <div className="lg:w-1/6 md:w-1/2 w-full px-4">
            <h2 className="title-font font-medium text-gray-900 tracking-widest text-sm mb-3">PAGES</h2>
            <nav className="list-none mb-10">
              <li><a className="text-gray-600 hover:text-gray-800" href="/">Home</a></li>
              <li><a className="text-gray-600 hover:text-gray-800" href="/about">About</a></li>
              <li><a className="text-gray-600 hover:text-gray-800" href="/faqs">FAQs</a></li>
              <li><a className="text-gray-600 hover:text-gray-800" href="/services">Services</a></li>
              <li><a className="text-gray-600 hover:text-gray-800" href="/contact">Contact</a></li>
            </nav>
          </div>

          {/* Features */}
          <div className="lg:w-1/6 md:w-1/2 w-full px-4">
            <h2 className="title-font font-medium text-gray-900 tracking-widest text-sm mb-3">FEATURES</h2>
            <nav className="list-none mb-10">
              <li><span className="text-gray-600 hover:text-gray-800">Drone Surveillance</span></li>
              <li><span className="text-gray-600 hover:text-gray-800">Soil Analysis</span></li>
              <li><span className="text-gray-600 hover:text-gray-800">AI-powered Insights</span></li>
            </nav>
          </div>

          {/* Services */}
          <div className="lg:w-1/6 md:w-1/2 w-full px-4">
            <h2 className="title-font font-medium text-gray-900 tracking-widest text-sm mb-3">SERVICES</h2>
            <nav className="list-none mb-10">
              <li><span className="text-gray-600 hover:text-gray-800">IoT</span></li>
              <li><span className="text-gray-600 hover:text-gray-800">Smartphone Integration</span></li>
              <li><span className="text-gray-600 hover:text-gray-800">Artificial Intelligence</span></li>
              <li><span className="text-gray-600 hover:text-gray-800">Drone Technology</span></li>
              <li><span className="text-gray-600 hover:text-gray-800">Crop Analysis</span></li>
              <li><span className="text-gray-600 hover:text-gray-800">Real-time Messaging</span></li>
            </nav>
          </div>

        
          {/* About Us */}
          <div className="lg:w-1/6 md:w-1/2 w-full px-4">
            <h2 className="title-font font-medium text-gray-900 tracking-widest text-sm mb-3">ABOUT US</h2>
            <p className="text-gray-600 text-sm">
              Agrifly delivers AI, IoT, and drone-powered solutions to revolutionize modern farming practices.
            </p>
          </div>

          {/* Contact Info */}
          <div className="lg:w-1/6 md:w-1/2 w-full px-4">
            <h2 className="title-font font-medium text-gray-900 tracking-widest text-sm mb-3">CONTACT</h2>
            <p className="text-gray-600 text-sm">📍 Nairobi, Kenya</p>
            <p className="text-gray-600 text-sm">📞 +254 700 123 456</p>
            <p className="text-gray-600 text-sm">✉️ support@agrifly.com</p>
          </div>
        </div>
      </div>

      {/* Newsletter + Socials */}
      <div className="border-t border-gray-200">
        <div className="container px-5 py-8 flex flex-wrap mx-auto items-center">
          <div className="flex md:flex-nowrap flex-wrap justify-center items-end md:justify-start">
            <div className="relative sm:w-64 w-40 sm:mr-4 mr-2">
              <label htmlFor="footer-field" className="leading-7 text-sm text-gray-600">Newsletter</label>
              <input
                type="text"
                id="footer-field"
                name="footer-field"
                placeholder="Enter your email"
                className="w-full bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:ring-2 focus:bg-transparent focus:ring-green-200 focus:border-green-500 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
              />
            </div>
            <button className="inline-flex text-white bg-green-500 border-0 py-2 px-6 focus:outline-none hover:bg-green-600 rounded">
              Subscribe
            </button>
            <p className="text-gray-500 text-sm md:ml-6 md:mt-0 mt-2 sm:text-left text-center">
              Subscribe to our <br className="lg:block hidden"/> farming insights and blogs.
            </p>
          </div>

          {/* Social icons */}
          <span className="inline-flex lg:ml-auto lg:mt-0 mt-6 w-full justify-center md:justify-start md:w-auto">
            <a className="text-gray-500" href="#"><i className="fab fa-facebook-f"></i></a>
            <a className="ml-3 text-gray-500" href="#"><i className="fab fa-twitter"></i></a>
            <a className="ml-3 text-gray-500" href="#"><i className="fab fa-instagram"></i></a>
            <a className="ml-3 text-gray-500" href="#"><i className="fab fa-linkedin-in"></i></a>
          </span>
        </div>
      </div>

      {/* Copyright */}
      <div className="bg-gray-100">
        <div className="container mx-auto py-4 px-5 flex flex-wrap flex-col sm:flex-row">
          <p className="text-gray-500 text-sm text-center sm:text-left">
            © {new Date().getFullYear()} SkyAcre —
            <a href="#" className="text-gray-600 ml-1" target="_blank" rel="noopener noreferrer">@SkyAcre</a>
          </p>
          <span className="sm:ml-auto sm:mt-0 mt-2 sm:w-auto w-full sm:text-left text-center text-gray-500 text-sm">
            Empowering smart farming with AI & IoT
          </span>
        </div>
      </div>
    </footer>
  )
}

export default Footer

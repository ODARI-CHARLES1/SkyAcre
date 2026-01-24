// This component renders the navigation bar for the application.
// It includes a logo, navigation links, authentication buttons, and a mobile menu toggle.
// The navbar adapts to different screen sizes and shows different content based on user authentication status.

// Import useState hook from React for managing component state
import { useState } from "react";
// Import useNavigate from react-router-dom for programmatic navigation
import { useNavigate } from "react-router-dom";
// Import icons from react-icons for menu toggle buttons
import { FaBars, FaTimes } from "react-icons/fa";
// Import useUser and UserButton from Clerk for user authentication state and UI
import { useUser, UserButton } from "@clerk/clerk-react";

// Define the Navbar functional component
const Navbar = () => {
  // Hook for navigation
  const navigate = useNavigate();
  // State to track if the mobile menu is open
  const [menuOpen, setMenuOpen] = useState(false);
  // Get the signed-in status from Clerk
  const { isSignedIn } = useUser();

  // Function to toggle the mobile menu open/closed
  const toggleMenu = () => setMenuOpen(!menuOpen);

  // Return the JSX for the navbar
  return (
    // Header element with styling for the navbar
    <header className="text-gray-600 shadow-sm w-full bg-white body-font">

      <div className="container mx-auto flex p-5 items-center justify-between">
        {/* Logo section */}
        <a
          onClick={() => navigate("/")} // Navigate to home page on click
          className="flex title-font font-medium items-center text-gray-900 cursor-pointer"
        >
          <span className="ml-3 text-3xl">
            Sky<span className="text-green-500">A</span>cre // Logo text with green 'A'
          </span>
        </a>

        {/* Desktop navigation menu - hidden on mobile */}
        <nav className="hidden md:flex md:ml-auto md:mr-auto items-center text-base justify-center space-x-6">
          <a onClick={() => navigate("/")} className="cursor-pointer hover:text-green-500">
            Home
          </a>
          <a onClick={() => navigate("/about")} className="cursor-pointer hover:text-green-500">
            About Us
          </a>
          <a onClick={() => navigate("/services")} className="cursor-pointer hover:text-green-500">
            Services
          </a>
          <a onClick={() => navigate("/resources")} className="cursor-pointer hover:text-green-500">
            Resources
          </a>
          <a onClick={() => navigate("/contact")} className="cursor-pointer hover:text-green-500">
            Contact
          </a>
          <a onClick={() => navigate("/faqs")} className="cursor-pointer hover:text-green-500">
            FAQs
          </a>
        </nav>


        {isSignedIn ? (
          <UserButton /> // Clerk's user button for signed-in users
        ) : (
          // Sign in and sign up buttons for desktop
          <div className="hidden md:flex space-x-2">
            <button
              onClick={() => navigate("/signin")} // Navigate to sign in page
              className="text-gray-600 border border-gray-300 py-2 px-4 focus:outline-none hover:bg-gray-100 rounded text-lg"
            >
              Sign In
            </button>
            <button
              onClick={() => navigate("/signup")} // Navigate to sign up page
              className="text-white bg-green-500 border-0 py-2 px-4 focus:outline-none hover:bg-green-600 rounded text-lg"
            >
              Sign Up
            </button>
          </div>
        )}

        {/* Mobile menu toggle button - visible only on mobile */}
        <div className="md:hidden">
          <button onClick={toggleMenu}> // Toggle menu on click
            {menuOpen ? <FaTimes size={24} /> : <FaBars size={24} />} // Show close or hamburger icon
          </button>
        </div>
      </div>

      {/* Mobile dropdown menu - shown when menuOpen is true */}
      {menuOpen && (
        <div className="md:hidden bg-white shadow-md">
          // Navigation links in a column for mobile
          <nav className="flex flex-col items-center space-y-4 py-4">
            <a onClick={() => { navigate("/"); setMenuOpen(false); }} className="cursor-pointer hover:text-green-500">
              Home
            </a>
            <a onClick={() => { navigate("/about"); setMenuOpen(false); }} className="cursor-pointer hover:text-green-500">
              About Us
            </a>
            <a onClick={() => { navigate("/services"); setMenuOpen(false); }} className="cursor-pointer hover:text-green-500">
              Services
            </a>
            <a onClick={() => { navigate("/resources"); setMenuOpen(false); }} className="cursor-pointer hover:text-green-500">
              Resources
            </a>
            <a onClick={() => { navigate("/contact"); setMenuOpen(false); }} className="cursor-pointer hover:text-green-500">
              Contact
            </a>
            <a onClick={() => { navigate("/faqs"); setMenuOpen(false); }} className="cursor-pointer hover:text-green-500">
              FAQs
            </a>
            // Conditional auth buttons for mobile
            {isSignedIn ? (
              <UserButton />
            ) : (
              <div className="flex flex-col space-y-2">
                <button
                  onClick={() => { navigate("/signin"); setMenuOpen(false); }} // Navigate and close menu
                  className="text-gray-600 border border-gray-300 py-2 px-4 focus:outline-none hover:bg-gray-100 rounded text-lg"
                >
                  Sign In
                </button>
                <button
                  onClick={() => { navigate("/signup"); setMenuOpen(false); }} // Navigate and close menu
                  className="text-white bg-green-500 border-0 py-2 px-4 focus:outline-none hover:bg-green-600 rounded text-lg"
                >
                  Sign Up
                </button>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
};

// Export the Navbar component as default
export default Navbar;

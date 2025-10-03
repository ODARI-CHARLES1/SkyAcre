import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaBars, FaTimes } from "react-icons/fa";

const Navbar = () => {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => setMenuOpen(!menuOpen);

  return (
    <header className="text-gray-600 shadow-sm w-full bg-white body-font">
      <div className="container mx-auto flex p-5 items-center justify-between">
        {/* Logo */}
        <a
          onClick={() => navigate("/")}
          className="flex title-font font-medium items-center text-gray-900 cursor-pointer"
        >
          <span className="ml-3 text-3xl">
            Sky<span className="text-green-500">A</span>cre
          </span>
        </a>

        {/* Desktop Menu */}
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

        <button
          onClick={() => navigate("/signup")}
          className="hidden md:inline-flex text-white bg-green-500 border-0 py-2 px-7 focus:outline-none hover:bg-green-600 rounded text-lg"
        >
          SignUp
        </button>

        {/* Mobile Menu Button */}
        <div className="md:hidden">
          <button onClick={toggleMenu}>
            {menuOpen ? <FaTimes size={24} /> : <FaBars size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Dropdown Menu */}
      {menuOpen && (
        <div className="md:hidden bg-white shadow-md">
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
            <button
              onClick={() => { navigate("/signup"); setMenuOpen(false); }}
              className="text-white bg-green-500 border-0 py-2 px-7 focus:outline-none hover:bg-green-600 rounded text-lg"
            >
              SignUp
            </button>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Navbar;

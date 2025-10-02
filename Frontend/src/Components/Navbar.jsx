import { useNavigate } from "react-router-dom"

const Navbar = () => {
  const navigate=useNavigate()
  return (
    <>
      <header className="text-gray-600 h-24 shadow-sm w-full bg-white  body-font">
  <div className="container mx-auto flex flex-wrap p-5 flex-col md:flex-row items-center">
    <a className="flex title-font font-medium items-center text-gray-900 mb-4 md:mb-0">
      <span className="ml-3 text-3xl">Sky<span className="text-green-500">A</span>cre</span>
    </a>
    <nav className="md:ml-auto md:mr-auto flex flex-wrap items-center text-base justify-center">
      <a onClick={()=>navigate("/")} className="mr-5 cursor-pointer hover:text-green-500">Home</a>
      <a onClick={()=>navigate("/about")} className="mr-5 cursor-pointer hover:text-green-500">About Us</a>
      <a onClick={()=>navigate("/services")} className="mr-5 cursor-pointer hover:text-green-500">Services</a>
      <a onClick={()=>navigate("/resources")} className="mr-5 cursor-pointer hover:text-green-500">Resources</a>
      <a onClick={()=>navigate("/contact")} className="mr-5 cursor-pointer hover:text-green-500">Contact</a>
      <a onClick={()=>navigate("/faqs")} className="mr-5 cursor-pointer hover:text-green-500">FAQs</a>
      
      
    </nav>
       <button onClick={()=>navigate('/signup')} className="inline-flex text-white bg-green-500 border-0 py-2 px-7 focus:outline-none hover:bg-green-600 rounded text-lg">SignUp</button>
  </div>
</header>
    </>
  )
}

export default Navbar

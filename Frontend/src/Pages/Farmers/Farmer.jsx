import React from 'react'
import Spinner from '../../Components/Spinner'
const Farmer = () => {
  return (
    <div className='w-full h-screen flex items-center flex-col  justify-center'>
        <h1 className="sm:text-5xl text-3xl mb-6 font-bold">
          {localStorage.getItem("name")}  Welcome to Sky<span className='text-green-500'>A</span>cre
        </h1>
        <p>Preparing your Data</p>
        <Spinner/>
    </div>
  )
}

export default Farmer

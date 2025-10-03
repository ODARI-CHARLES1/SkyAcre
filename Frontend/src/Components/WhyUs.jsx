import React from 'react'

const WhyUs = () => {
  return (
    <>
      <section class="text-gray-600 body-font">
  <div class="container px-5 py-24 mx-auto">
    <div class="flex flex-col text-center w-full mb-20">
      {/* <h2 class="text-xs text-green-500 tracking-widest font-medium title-font mb-1">ROOF PARTY POLAROID</h2> */}
      <h1 class="sm:text-3xl text-2xl font-medium title-font mb-4 text-gray-900">Why choose Sky<span className='text-green-500'>A</span>cre?</h1>
      <p class="lg:w-2/3 mx-auto leading-relaxed text-base">At Skycare we offer these quality modern solutions to fit your agricultural needs.</p>
    </div>
    <div class="flex flex-wrap">
      <div class="xl:w-1/4 lg:w-1/2 md:w-full px-8 py-6 border-l-2 border-gray-200 border-opacity-60">
        <h2 class="text-lg sm:text-xl text-gray-900 font-medium title-font mb-2">AI-powered analysis</h2>
        <p class="leading-relaxed text-base mb-4">Get access to AI powered agricultural models that prevent crop disease and soil infertility before they occur</p>
        <a class="text-green-500 inline-flex items-center" href='/services'>Learn More
          <svg fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="w-4 h-4 ml-2" viewBox="0 0 24 24">
            <path d="M5 12h14M12 5l7 7-7 7"></path>
          </svg>
        </a>
      </div>
      <div class="xl:w-1/4 lg:w-1/2 md:w-full px-8 py-6 border-l-2 border-gray-200 border-opacity-60">
        <h2 class="text-lg sm:text-xl text-gray-900 font-medium title-font mb-2">Remote Access</h2>
        <p class="leading-relaxed text-base mb-4">Access insights to data on your farm from anywhere you are with the touch of your smartphone.</p>
        <a class="text-green-500 inline-flex items-center" href='/services'>Learn More
          <svg fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="w-4 h-4 ml-2" viewBox="0 0 24 24">
            <path d="M5 12h14M12 5l7 7-7 7"></path>
          </svg>
        </a>
      </div>
      <div class="xl:w-1/4 lg:w-1/2 md:w-full px-8 py-6 border-l-2 border-gray-200 border-opacity-60">
        <h2 class="text-lg sm:text-xl text-gray-900 font-medium title-font mb-2">Customer Support</h2>
        <p class="leading-relaxed text-base mb-4">24/7 customer support on hwo to use our product as well as expert agricultural advice.</p>
        <a class="text-green-500 inline-flex items-center" href='/services'>Learn More
          <svg fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="w-4 h-4 ml-2" viewBox="0 0 24 24">
            <path d="M5 12h14M12 5l7 7-7 7"></path>
          </svg>
        </a>
      </div>
      <div class="xl:w-1/4 lg:w-1/2 md:w-full px-8 py-6 border-l-2 border-gray-200 border-opacity-60">
        <h2 class="text-lg sm:text-xl text-gray-900 font-medium title-font mb-2">Community and partnerships</h2>
        <p class="leading-relaxed text-base mb-4">Interact with other farmers around the globe and get market for your products as well as additional agricultural insights.</p>
        <a class="text-green-500 inline-flex items-center" href='/services'>Learn More
          <svg fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="w-4 h-4 ml-2" viewBox="0 0 24 24">
            <path d="M5 12h14M12 5l7 7-7 7"></path>
          </svg>
        </a>
      </div>
    </div>
    <button class="flex mx-auto mt-16 text-white bg-green-500 border-0 py-2 px-8 focus:outline-none hover:bg-green-600 rounded text-lg"><a href="/services">See what we offer</a></button>
  </div>
</section>
    </>
  )
}

export default WhyUs

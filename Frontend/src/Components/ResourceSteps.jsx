import React, { useState } from "react";

const steps = [
{
title: "STEP 1",
heading: "Our Vision",
desc: "Revolutionize agriculture with technology to ensure healthy crops and higher yields.",
img: "https://i.pinimg.com/1200x/3f/6c/f0/3f6cf0b2a86a27532f00e670c8a7f1f9.jpg", // placeholder
icon: ( <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
),
},
{
title: "STEP 2",
heading: "Smart Monitoring",
desc: "Track soil health, water usage, and crop growth with advanced sensors.",
img: "https://i.pinimg.com/1200x/0a/ba/4a/0aba4a7537bccd1d20423518f7cb5551.jpg", // placeholder
icon: ( <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
),
},
{
title: "STEP 3",
heading: "Automation",
desc: "Automated irrigation and fertilization systems for precision farming.",
img: "https://i.pinimg.com/736x/ae/df/a5/aedfa50418bcbc40287a19fdf2cb89d2.jpg", // placeholder
icon: (
<> <circle cx="12" cy="5" r="3"></circle> <path d="M12 22V8M5 12H2a10 10 0 0020 0h-3"></path>
</>
),
},
{
title: "STEP 4",
heading: "Community Impact",
desc: "Empowering farmers with knowledge and sustainable solutions.",
img: "https://i.pinimg.com/736x/0f/a9/da/0fa9da2536e456c97da2e24d1246d826.jpg", // placeholder
icon: (
<> <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path> <circle cx="12" cy="7" r="4"></circle>
</>
),
},
];

const ResourceSteps = () => {
const [activeStep, setActiveStep] = useState(0);

return ( <section className="text-gray-600 body-font"> <div className="container px-5 py-24 mx-auto flex flex-col">
{/* Top step navigation with icons */} <div className="flex mx-auto flex-wrap mb-10">
{steps.map((step, index) => (
<button
key={index}
onClick={() => setActiveStep(index)}
className={`sm:px-6 py-3 w-1/2 sm:w-auto justify-center sm:justify-start border-b-2 title-font font-medium inline-flex items-center leading-none tracking-wider transition-all duration-300 ${
                activeStep === index
                  ? "border-green-500 text-green-500 bg-gray-100 rounded-t"
                  : "border-gray-200 text-gray-500 hover:text-gray-900"
              }`}
> <svg
             fill="none"
             stroke="currentColor"
             strokeLinecap="round"
             strokeLinejoin="round"
             strokeWidth="2"
             className="w-5 h-5 mr-3"
             viewBox="0 0 24 24"
           >
{step.icon} </svg>
{step.title} </button>
))} </div>

```
    {/* Content changes based on selection */}
    <img
      className="xl:w-1/4 lg:w-1/3 md:w-1/2 w-2/3 block mx-auto mb-10 object-cover object-center rounded shadow-lg transition-all duration-300"
      alt={steps[activeStep].title}
      src={steps[activeStep].img}
    />
    <div className="flex flex-col text-center w-full">
      <h1 className="text-xl font-medium title-font mb-4 text-gray-900">
        {steps[activeStep].heading}
      </h1>
      <p className="lg:w-2/3 mx-auto leading-relaxed text-base">
        {steps[activeStep].desc}
      </p>
    </div>
  </div>
</section>


);
};

export default ResourceSteps;

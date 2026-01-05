import React from "react";

const steps = [
  {
    title: "Drone Scanning",
    description: "Our drones fly over farms capturing high-resolution images and sensor data.",
    svg: (
      <svg
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        className="w-10 h-10 mx-auto mb-4"
        viewBox="0 0 24 24"
      >
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
      </svg>
    ),
  },
  {
    title: "Smart Analysis",
    description: "AI-driven software interprets data identifying crop health issues and soil conditions.",
    svg: (
      <svg
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        className="w-10 h-10 mx-auto mb-4"
        viewBox="0 0 24 24"
      >
        <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
      </svg>
    ),
  },
  {
    title: "Actionable Reports",
    description: "Farmers receive clear recommendations for better planning and management.",
    svg: (
      <svg
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        className="w-10 h-10 mx-auto mb-4"
        viewBox="0 0 24 24"
      >
        <circle cx="12" cy="5" r="3"></circle>
        <path d="M12 22V8M5 12H2a10 10 0 0020 0h-3"></path>
      </svg>
    ),
  },
  {
    title: "Smarter Decisions",
    description: "Take timely action to boost yields, reduce costs, and practice sustainable farming.",
    svg: (
      <svg
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        className="w-10 h-10 mx-auto mb-4"
        viewBox="0 0 24 24"
      >
        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    ),
  },
  {
    title: "Finish",
    description: "Complete your farm analysis and start optimizing operations immediately.",
    svg: (
      <svg
        fill="none"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        className="w-10 h-10 mx-auto mb-4"
        viewBox="0 0 24 24"
      >
        <path d="M22 11.08V12a10 10 0 11-5.93-9.14"></path>
        <path d="M22 4L12 14.01l-3-3"></path>
      </svg>
    ),
  },
];

const HowItWorks = () => {
  return (
    <section className="text-gray-600 body-font py-24">
      <div className="container mx-auto px-5">
        {/* Title */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900">
            How We Work
          </h1>
          <p className="mt-4 text-gray-600 text-lg">
            Step by step guide to managing your farm smarter and easier
          </p>
        </div>

        {/* Steps arranged horizontally */}
        <div className="flex flex-wrap justify-center gap-8">
          {steps.map((step, index) => (
            <div key={index} className="text-center max-w-xs">
              {step.svg}
              <h2 className="text-xl font-semibold mb-2">{step.title}</h2>
              <p className="text-gray-500 text-sm mb-2">{step.description}</p>
              <a
                href="/services"
                className="text-green-500 inline-flex items-center hover:underline"
              >
                Learn More
                <svg
                  fill="none"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  className="w-4 h-4 ml-1"
                  viewBox="0 0 24 24"
                >
                  <path d="M5 12h14M12 5l7 7-7 7"></path>
                </svg>
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;

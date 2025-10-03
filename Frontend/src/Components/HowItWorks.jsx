import React from "react";
import { motion } from "framer-motion";

const steps = [
  {
    title: "STEP 1",
    desc: "VHS cornhole pop-up, try-hard 8-bit iceland helvetica. Kinfolk bespoke try-hard cliche palo santo offal.",
    icon: (
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
    ),
  },
  {
    title: "STEP 2",
    desc: "Vice migas literally kitsch +1 pok pok. Truffaut hot chicken slow-carb health goth, vape typewriter.",
    icon: (
      <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
    ),
  },
  {
    title: "STEP 3",
    desc: "Coloring book narwhal glossier master cleanse umami. Salvia +1 master cleanse blog taiyaki.",
    icon: (
      <>
        <circle cx="12" cy="5" r="3"></circle>
        <path d="M12 22V8M5 12H2a10 10 0 0020 0h-3"></path>
      </>
    ),
  },
  {
    title: "STEP 4",
    desc: "VHS cornhole pop-up, try-hard 8-bit iceland helvetica. Kinfolk bespoke try-hard cliche palo santo offal.",
    icon: (
      <>
        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </>
    ),
  },
  {
    title: "FINISH",
    desc: "Pitchfork ugh tattooed scenester echo park gastropub whatever cold-pressed retro.",
    icon: (
      <>
        <path d="M22 11.08V12a10 10 0 11-5.93-9.14"></path>
        <path d="M22 4L12 14.01l-3-3"></path>
      </>
    ),
  },
];

const HowItWorks = () => {
  return (
    <section className="text-gray-600 body-font">
      <div className="container px-5 py-24 mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="flex flex-col w-full max-w-2xl mx-auto"
        >
          {steps.map((step, index) => (
            <motion.div
              key={index}
              className={`flex relative pb-12 ${
                index === steps.length - 1 ? "pb-0" : ""
              }`}
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              viewport={{ once: true }}
            >
              {/* Connector Line */}
              {index !== steps.length - 1 && (
                <div className="h-full w-10 absolute inset-0 flex items-center justify-center">
                  <div className="h-full w-1 bg-gray-300"></div>
                </div>
              )}

              {/* Icon */}
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-500 inline-flex items-center justify-center text-white relative z-10">
                <svg
                  fill="none"
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  className="w-5 h-5"
                  viewBox="0 0 24 24"
                >
                  {step.icon}
                </svg>
              </div>

              {/* Text */}
              <div className="flex-grow pl-4">
                <h2 className="font-medium title-font text-sm text-gray-900 mb-1 tracking-wider">
                  {step.title}
                </h2>
                <p className="leading-relaxed">{step.desc}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default HowItWorks;

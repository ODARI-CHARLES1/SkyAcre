import React, { useState } from "react";

const faqs = [
  {
    question: "What is SkyAcre?",
    answer:
      "SkyAcre is a smart farming solution that uses drones to monitor crops, optimize yields, and provide farmers with real-time insights using tested and approved AI-models.",
  },
  {
    question: "How can drones improve farming?",
    answer:
      "Drones can map fields, monitor plant health, detect irrigation issues, and reduce the need for manual inspections—saving time and resources.",
  },
  {
    question: "Is SkyAcre suitable for small farms?",
    answer:
      "Yes, SkyAcre is designed to help both small-scale and large-scale farms adopt precision agriculture techniques affordably.",
  },
  {
    question: "Do I need technical expertise to use SkyAcre?",
    answer:
      "Not at all.SkyAcre provides an easy-to-use platform, and our team supports farmers with setup, training, and ongoing assistance.",
  },
];

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className="bg-gray-50 py-16 px-6">
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-3xl font-bold text-green-700 mb-6">
          Frequently Asked Questions
        </h2>
        <p className="text-gray-600 mb-12">
          Everything you need to know about SkyAcre and how it can transform
          your farming experience.
        </p>
      </div>

      <div className="max-w-3xl mx-auto space-y-4">
        {faqs.map((faq, index) => (
          <div
            key={index}
            className="bg-white rounded-lg shadow p-4 cursor-pointer transition"
            onClick={() => toggleFAQ(index)}
          >
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">
                {faq.question}
              </h3>
              <span className="text-green-700 font-bold text-xl">
                {openIndex === index ? "−" : "+"}
              </span>
            </div>
            {openIndex === index && (
              <p className="mt-3 text-gray-600">{faq.answer}</p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

export default FAQ;

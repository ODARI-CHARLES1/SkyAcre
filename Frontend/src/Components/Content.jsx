
import React from "react";
import { motion } from "framer-motion";

const categories = [
  {
    title: "Mobile Apps in Agriculture",
    subtitle: "FARMING ON THE GO",
    img: "https://i.pinimg.com/1200x/a4/e4/70/a4e4702967cbacd4e21ff3be8496146d.jpg",
    desc: "Mobile apps empower farmers with real-time weather updates, market prices, pest alerts, and farm management tools — bridging the digital divide for smallholder farmers.",
    link: "https://keenethics.com/blog/mobile-apps-in-agricultural-business-enhanced-automation-in-farming-activities",
  },
  {
    title: "IoT & Smart Farming",
    subtitle: "CONNECTED FARMS",
    img: "https://i.pinimg.com/736x/96/d7/dc/96d7dc3e7f83258cba1a896b21ff5d2d.jpg",
    desc: "IoT devices track soil moisture, livestock health, and crop growth, providing data-driven decisions through mobile dashboards and cloud platforms.",
    link: "https://www.digi.com/blog/post/iot-in-agriculture",
  },
  {
    title: "AI in Agriculture",
    subtitle: "INTELLIGENT FARMING",
    img: "https://i.pinimg.com/736x/71/b8/fb/71b8fbfdf4dae569f77eaf45cf10f390.jpg",
    desc: "Artificial intelligence models predict yields, detect crop diseases, optimize irrigation, and help automate farming at scale, improving both productivity and sustainability.",
    link: "https://www.mdpi.com/2077-0472/13/2/373",
  },
  {
    title: "Mobile, IoT & Market Access",
    subtitle: "DIGITAL MARKETPLACE",
    img: "https://i.pinimg.com/1200x/3a/dc/9d/3adc9d771b6f29d4d48899a415b54b70.jpg",
    desc: "Integration of mobile apps with IoT and cloud platforms connects farmers directly to buyers and agronomists, enhancing transparency and profitability.",
    link: "https://ripenapps.com/blog/agritech-how-iot-mobile-apps-accelerate-agriculture-industry-digitally/",
  },
];

const Content = () => {
  return (
    <section className="text-gray-600 body-font">
      <div className="container px-5 py-24 mx-auto">
        {/* Header */}
        <div className="flex flex-wrap w-full mb-20">
          <div className="lg:w-1/2 w-full mb-6 lg:mb-0">
            <h1 className="sm:text-3xl text-2xl font-medium title-font mb-2 text-gray-900">
              Digital Agriculture Resources
            </h1>
            <div className="h-1 w-20 bg-green-500 rounded"></div>
          </div>
          <p className="lg:w-1/2 w-full leading-relaxed text-gray-500">
            Explore blogs, case studies, and articles on how technology
            — mobile apps, IoT, and AI — is transforming modern agriculture.
          </p>
        </div>

        {/* Cards */}
        <div className="flex flex-wrap -m-4">
          {categories.map((item, index) => (
            <motion.div
              key={index}
              className="xl:w-1/4 md:w-1/2 p-4"
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
            >
              <div className="bg-gray-100 p-6 rounded-lg shadow hover:shadow-xl transition duration-300">
                <img
                  className="h-40 rounded w-full object-cover object-center mb-6"
                  src={item.img}
                  alt={item.title}
                />
                <h3 className="tracking-widest text-green-500 text-xs font-medium title-font uppercase">
                  {item.subtitle}
                </h3>
                <h2 className="text-lg text-gray-900 font-medium title-font mb-4">
                  {item.title}
                </h2>
                <p className="leading-relaxed text-base mb-3">{item.desc}</p>
                <a
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-600 hover:text-green-800 text-sm font-semibold"
                >
                  Read More →
                </a>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Content;


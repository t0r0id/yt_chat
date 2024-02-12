"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const testimonials = [
  {
    name: "Ayush",
    avatar: "A",
    title: "Enterprise Sales",
    description:
      "Invaluable Insights! This app revolutionizes my approach to enterprise sales by seamlessly integrating wisdom from top business influencers. Now, I stay ahead in the game, refining my sales strategies with every chat session. Truly a game-changer in my professional journey!",
  },
  {
    name: "Neha",
    avatar: "N",
    title: "Data Scientist",
    description:
      "This app keeps me at the forefront of the latest LLM technologies. Chatting about cutting-edge developments with the leading LLM influencers makes staying updated effortless. A must-have for any data scientist aiming for excellence in the dynamic world of machine learning!",
  },
  {
    name: "Tanmay",
    avatar: "T",
    title: "Content Creator",
    description:
      "This app is my secret weapon for content creation. Chatting with YouTube influencers, I gather invaluable tips and tricks that elevate my creative game. It's like having a direct line to the pulse of the content creation world. Highly recommended for fellow creators!",
  },
  {
    name: "Madhuri",
    avatar: "T",
    title: "House Wife",
    description:
      "This app is my kitchen companion, connecting me with top-notch cooking influencers. From recipe hacks to flavor trends, I chat my way to culinary perfection. A delightful experience for any cooking enthusiast!",
  },
];

export const LandingContent = () => {
  return (
    <div className="px-10 pb-20">
      <h2 className="text-center text-4xl text-white font-extrabold mb-10 ">
        Testimonials
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {testimonials.map((testimonial) => (
          <Card
            key={testimonial.description}
            className="bg-[#192339] border-none text-white"
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-x-2">
                <div>
                  <p className="text-lg">{testimonial.name}</p>
                  <p className="text-zinc-400 text-sm">{testimonial.title}</p>
                </div>
              </CardTitle>
              <CardContent className="pt-4 px-0">
                {testimonial.description}
              </CardContent>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  );
};

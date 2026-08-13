import { Hero } from "@/components/marketing/Hero";
import { StatsBar } from "@/components/marketing/StatsBar";
import { MethodCards } from "@/components/marketing/MethodCards";
import { Testimonials } from "@/components/marketing/Testimonials";
import { CTASection } from "@/components/marketing/CTASection";

export default function LandingPage() {
  return (
    <>
      <Hero />
      <StatsBar />
      <MethodCards />
      <Testimonials />
      <CTASection />
    </>
  );
}

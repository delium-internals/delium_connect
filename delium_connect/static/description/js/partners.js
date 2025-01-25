import {setupNavbar} from './common.js';

const setupFeatureObservers = () => {
  const features = document.querySelectorAll(".animate-slide-in");
  const options = { threshold: 0.1 };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("opacity-100", "translate-y-0");
      }
    });
  }, options);

  features.forEach((feature) => {
    observer.observe(feature);
  });
}

const setupSectionObservers = () => {
  const sections = document.querySelectorAll("section");
  const observerOptions = {
    root: null,
    threshold: 0.1,
  };

  const scrollInObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("opacity-100", "animate-visible");
        entry.target.classList.remove("opacity-0", "animate-hidden");
      } else {
        entry.target.classList.remove("opacity-100", "animate-visible");
        entry.target.classList.add("opacity-0", "animate-hidden");
      }
    });
  }, observerOptions);

  sections.forEach((section) => {
    scrollInObserver.observe(section);
  });
}
const setupBackToTopAction = () => {
  const backToTopButton = document.getElementById("back-to-top");

  window.addEventListener("scroll", () => {
    if (window.scrollY > 200) {
      backToTopButton.style.display = "block";
    } else {
      backToTopButton.style.display = "none";
    }
  });

  backToTopButton.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}


document.addEventListener("DOMContentLoaded", () => {
  setupFeatureObservers();
  setupSectionObservers();
  setupBackToTopAction();
  setupNavbar();
});

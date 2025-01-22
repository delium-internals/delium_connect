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
const setupVideoModal = () => {
  const watchVideoBtn = document.getElementById("watchVideo");
  const videoModal = document.getElementById("videoModal");
  const closeModalBtn = document.getElementById("closeModal");
  const youtubeIframe = document.getElementById("youtubeIframe");

  const youtubeVideoUrl =
    "https://www.youtube.com/embed/xXHVk0tXkto?autoplay=1";

  watchVideoBtn.addEventListener("click", () => {
    youtubeIframe.src = youtubeVideoUrl;
    videoModal.classList.remove("hidden");
  });

  closeModalBtn.addEventListener("click", () => {
    youtubeIframe.src = "";
    videoModal.classList.add("hidden");
  });

  videoModal.addEventListener("click", (event) => {
    if (event.target === videoModal) {
      youtubeIframe.src = "";
      videoModal.classList.add("hidden");
    }
  });
}
const setupProvenSolutionCards = () => {
  const cards = document.querySelectorAll(".card");
  const cardSection = document.getElementById("card-section");
  const expandedContent = document.getElementById("expanded-content");
  const expandedTitle = document.getElementById("expanded-title");
  const expandedWhatEl = document.getElementById("expanded-what");
  const expandedSubtitle = document.getElementById("expanded-subtitle");
  const expandedIcon = document.getElementById("expanded-icon");
  const expandedDetails = document.getElementById("expanded-details");
  const closeExpandedCard = document.getElementById("close-expanded-card");
  const expandedCard = document.getElementById("expanded-card");
  const betaTag = document.getElementById("beta-tag");

  const cardDetails = {
    miner: {
      title: "Miner",
      beta: false,
      subtitle: "Better Bottomline!",
      icon: "/static/images/miner.png",
      bgClass:
        "bg-gradient-to-br from-blue-100 to-blue-200 text-gray-900 rounded-lg shadow-lg",
      expandedWhat:
        "Miner, your inventory copilot, learns from past data to optimize daily reorders and replenishment. Save your inventory capital with accurate forecasting and automated planning.",
      details: [
        "Performs unmatched analysis.",
        "Takes decisive autonomous actions.",
        "Perform accurate demand forecasting.",
        "Reorder with precision.",
        "Machine driven auto reorders/replenishment.",
        "Identify and eliminate non moving inventory.",
        "Stock balancing via stock transfers.",
        "Identify reasons for stockouts",
        "Automatic course corrections.",
        "Autopilot mode.",
      ],
    },
    marketer: {
      title: "Marketer",
      beta: true,
      subtitle: "Better Topline!",
      icon: "/static/images/marketer.png",
      bgClass:
        "relative bg-gradient-to-br from-green-100 to-green-200 text-gray-900 rounded-lg shadow-lg",
      expandedWhat:
        "The marketer, your customer insights copilot learns from your past data customer buying patterns and plans user promotion offers and smart pricing levels to improve margins and topline. Increase and customer lifetime value by 20-25% and save 2-2.5% of your margins with AI driven smart pricing.",
      details: [
        "Create customer additiction.",
        "Forecast promotion outcomes.",
        "Automatic customer segmentations.",
        "Infer monthly/periodic customer baskets and LTV.",
        "Product combos.",
        "Brand laddering, stickiness and substitutions.",
        "Continuous customer communications and omnichannel context.",
        "Machine made promotion calendar for planning and tracking.",
        "Automatic course corrections.",
        "Price point recommendations",
      ],
    },
    manager: {
      title: "Manager",
      beta: true,
      subtitle: "Better Targeting!",
      icon: "/static/images/manager.png",
      bgClass:
        "relative bg-gradient-to-br from-purple-100 to-purple-200 text-gray-900 rounded-lg shadow-lg",
      expandedWhat:
        "The manager, your assortment copilot analyses your past data and decodes your product mix and classifies your products based on different business and customer dimensions. Keep assortment effective and customer relavent thus saving time in operations and money in inventory capital.",
      details: [
        "Assortment classification (continuous, festive, seasonal, fresh etc.)",
        "Planograms and presentation stock.",
        "Top down planning via budgets.",
        "Cash flow analysis and automatic optimizers.",
        "New article introductions - auto limits.",
        "Product - name study and variant classifications.",
        "SKU rationalization (article delisting).",
        "SKU substitutions and stock carry forward.",
        "New article incubation center.",
        "New store mirrors.",
      ],
    },
    mentor: {
      title: "Mentor",
      beta: false,
      subtitle: "Better Guidance!",
      icon: "/static/images/manager.png",
      bgClass:
        "relative bg-gradient-to-br from-yellow-100 to-yellow-200 text-gray-900 rounded-lg shadow-lg",
      expandedWhat:
        "The mentor, a sounding board like copilot collaborates with the other copilots and allows you to access your business data and infered insights using a natural language interface. When in doubt, as The mentor to play out and analyse scenarios for you before taking action",
      details: [
        "Tell me why on recommendations.",
        "Adhoc purchase simulations.",
        "Interstore transfers and smart stock allocation.",
        "Stock redistribution (using graph balancing).",
        "What if's on supplier schemes.",
        "Stock out doctor and automatic adjustments.",
        "Business desk (Revenues, Availability and Stock Turns).",
        "Conversations and incontext help.",
        "Automatic data correction (masters), Surveillance center.",
        "Supply chain tracking and alternate purchasing.",
      ],
    },
  };

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      const cardType = card.getAttribute("data-card");
      if (!cardType) return;
      const { title, icon, details, subtitle, bgClass, expandedWhat, beta } =
        cardDetails[cardType];

      cardSection.classList.add("hidden");
      if (beta) {
        betaTag.classList.remove("hidden");
      } else {
        betaTag.classList.add("hidden");
      }
      expandedTitle.textContent = title;
      expandedSubtitle.textContent = subtitle;
      expandedIcon.src = icon;
      expandedWhatEl.textContent = expandedWhat;
      expandedCard.className = `mt-12 sm:mt-24 w-full max-w-6xl mx-auto shadow-2xl border border-gray-200 p-4 sm:p-12 relative flex flex-col sm:flex-row ${bgClass} `;
      expandedDetails.innerHTML = details
        .map(
          (point, index) => `
            <li class="grid grid-cols-[auto_1fr] gap-4 items-start">
              <!-- Number Container -->
              <div class="flex items-center justify-center w-10 font-bold text-lg">
                ${index + 1}.
              </div>
              <!-- Text Content -->
              <span class="text-gray-700 text-lg">${point}</span>
            </li>`
        )
        .join("");

      expandedContent && expandedContent.classList.remove("hidden");
      expandedContent && expandedContent.scrollIntoView({ behavior: "smooth" });
    });
  });

  closeExpandedCard.addEventListener("click", () => {
    cardSection.classList.remove("hidden");
    expandedCard.classList.add("hidden");
  });
}
const setupCarouselCards = () => {
  const carousel = document.getElementById("carousel");
  const carouselItems = document.getElementById("carousel-items");
  const carouselCards = document.querySelectorAll(".carousel-card");
  const carouselExpandedCard = document.getElementById("carousel-expanded-card");
  const carouselCloseExpandedCard = document.getElementById("carousel-close-expanded-card");
  const moveLeftBtn = document.getElementById("move-left");
  const moveRightBtn = document.getElementById("move-right");

  let currentIndex = 0;
  const scrollInterval = 5000;

  const updateCarousel = () => {
    const cardWidth = carouselCards[0].offsetWidth;
    const cardGap = parseInt(getComputedStyle(carouselItems).gap) || 0;
    const totalWidth = cardWidth + cardGap;
    const totalCards = carouselCards.length;
    const viewportWidth = window.innerWidth;
    const visibleCards = viewportWidth > 1368 ? 4 : viewportWidth > 1024 ? 3 : 2;
    if (currentIndex > totalCards - visibleCards + 1) {
      currentIndex = 0;
    }
  
    const scrollPosition = -(currentIndex * totalWidth);

    carouselItems.style.transform = `translateX(${scrollPosition}px)`;
  };
  const scrollCarousel = () => {
    currentIndex += 1;
    updateCarousel()
  };

  moveLeftBtn.addEventListener("click", () => {
    currentIndex = currentIndex === 0 ? 0 : currentIndex - 1;
    updateCarousel();
  });

  moveRightBtn.addEventListener("click", () => {
    currentIndex = (currentIndex + 1) % carouselItems.children.length;
    updateCarousel();
  });

  let autoScrollInterval = setInterval(scrollCarousel, scrollInterval);

  carousel.addEventListener("mouseenter", () => {
    clearInterval(autoScrollInterval);
  });

  carousel.addEventListener("mouseleave", () => {
    autoScrollInterval = setInterval(scrollCarousel, scrollInterval);
  });

  carouselCards.forEach((card) => {
    card.addEventListener("click", () => {
      const cardType = card.getAttribute("data-card");
      if (!cardType) return;

      const cardDetails = {
        trashToCash: {
          title: "Trash to Cash",
          subtitle: "A Tomato Story!",
          image: "/static/images/success-stories/trash-to-cash.png",
          descriptionTitle: "Tomato: A Daily Staple, A Delicate Challenge.",
          description: [
            "A fast-moving, perishable staple in Indian households, <span class='font-bold'>tomatoes have a shelf life of just one day and a highly variable sales pattern</span>(days in the same week see sales of both 2.7 tons and 6 tons).",
            "Getting it wrong is one of daily wastage or business loss due to stockout. With Delium’s Retail Copilot managing reordering, one supermarket chain in Chennai <span class='font-bold'>slashed monthly wastage by an incredible 1,000 kgs—on tomatoes alone!</span>",
            "Demand forecasting for such SKUs is among the most challenging task, requiring insights derived from numerous parameters. The Miner empowers supermarkets by automatically planning daily reorders for all perishables. <span class='font-bold'>With savings at this scale from just one SKU, supermarkets often cover the cost of our copilot through savings generated from a few such SKUs</span>—out of the thousands they manage."
          ]
        },
        charmingProfits: {
          title: "Charming Profits",
          subtitle: "In Charminar City!",
          image: "/static/images/success-stories/charming-profits.png",
          descriptionTitle: "Smart Stock Redistribution Saves ₹50 Lakhs (a third) per Store",
          description: [
            "Business that open <span class='font-bold'>new stores regularly</span> use Delium's Miner to smartly pull out and allocate inventory from their existing stores to the new store, thus optimizing inventory and <span class='font-bold'>reducing the need of working capital and additional credit.</span>",
            "A supermarket chain in Hyderabad, with a habit of opening 1-2 stores every quarter, uses Delium’s Miner to <span class='font-bold'>self-finance 20-30% of the inventory capital required for new stores</span> by focusing on transfers from other stores.",
            "The Miner’s new store onboarding process, <span class='font-bold'>leveraging smart mirrors, Kickstarter interstore transfers, and Kickstarter purchases</span>, enables business owners to prepare inventory plans for their new stores within minutes and execute them in just a few days."
          ]
        },
        cashmirToKanyakumari: {
          title: "Cash-mir to Kanyakumari",
          subtitle: "Delium drives 1 in 12 ATMs!",
          image: "/static/images/success-stories/cashmir-kanyakumari.png",
          descriptionTitle: "Getting the basics right at scale - Lower cash in the network, lower service trips!",
          description: [
            "<span class='font-bold'>1 in every 12 ATMs</span> in India use Delium's miner to plan daily cash loading, This is <span class='font-bold'>1800+ cities/towns, 12+ banks and 2300+ cash replenishment trucks.</span>",
            "The Miner’s Precision: 12% Network Cash Reduction and 15% Fewer Service Routes <span class='font-bold'>Saving ₹150Cr in Cash (network cash) and ₹3Cr in Fuel Annually</span>",
            "ATMs exhibit <span class='font-bold'>high variance in daily cash dispense patterns, strongly influenced by their deployment location.</span> For instance, ATMs at hospitals, commercial streets, colleges, and malls display rich and complex behaviors, dispensing anywhere between <span class='font-bold'>₹5L to ₹50L daily</span>, depending on various seasonal and temporal factors.",
            "Similar to forecasting for perishables like tomatoes, <span class='font-bold'>demand forecasting for these locations is one of the most challenging tasks</span>, requiring insights derived from numerous parameters."
          ]
        },
      };

      const { title, subtitle, image, descriptionTitle, description } =
        cardDetails[cardType];

      document.getElementById("carousel-expanded-title").textContent = title;
      document.getElementById("carousel-expanded-subtitle").textContent = subtitle;
      document.getElementById("carousel-expanded-image").src = image;
      document.getElementById("carousel-expanded-description-title").textContent = descriptionTitle;
      document.getElementById("carousel-expanded-description").innerHTML = description.map(detail => {
        return `<p>${detail}</p>`
      }).join("<br/>");
      carousel.classList.add("hidden");
      carouselExpandedCard.classList.remove("hidden");
    });
  });

  carouselCloseExpandedCard.addEventListener("click", () => {
    carousel.classList.remove("hidden");
    carouselExpandedCard.classList.add("hidden");
  });
}
const prepLogoStrips = () => {
  const logoStrip = document.getElementById("logo-strip").querySelector(".logo-marquee");

  let animationPaused = false;
  const pauseAnimation = () => {
    if (!animationPaused) {
      const computedStyle = getComputedStyle(logoStrip);
      const matrix = new DOMMatrix(computedStyle.transform);
      const currentTranslateX = matrix.m41;
      logoStrip.style.transform = `translateX(${currentTranslateX}px)`;
      logoStrip.style.animationPlayState = 'paused';
      animationPaused = true;
    }
  };

  const resumeAnimation = () => {
    if (animationPaused) {
      logoStrip.style.animationPlayState = 'running';
      animationPaused = false;
    }
  };

  logoStrip.addEventListener("mouseenter", pauseAnimation);
  logoStrip.addEventListener("mouseleave", resumeAnimation);

  const generateLogos = () => {
    let logosHTML = "";
    for (let i = 10; i <= 38; i++) {
      logosHTML += `<img src="/static/images/clientele/${i}.png" class="clientele-logo object-contain">`;
    }
    return logosHTML;
  };

  const logosHTML = generateLogos();
  logoStrip.innerHTML = logosHTML + logosHTML;
}

document.addEventListener("DOMContentLoaded", () => {
  setupFeatureObservers();
  setupSectionObservers();
  setupBackToTopAction();
  setupVideoModal();
  setupProvenSolutionCards();
  setupCarouselCards();
  prepLogoStrips();
  setupNavbar();
});

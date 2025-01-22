const setupNavbar = () => {
  const navbar = document.getElementById("navbar");
  window.addEventListener("scroll", () => {
    if (window.scrollY > window.innerHeight * 0.4) {
      navbar.classList.add("show");
    } else {
      navbar.classList.remove("show");
    }
  });
}

export {setupNavbar};
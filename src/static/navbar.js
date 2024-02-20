// Get necessary elements
const navbarToggler = document.querySelector('.navbar-toggler');
const navbarCollapse = document.querySelector('.navbar-collapse');

// Function to handle collapse after clicking outside
const collapseNavbarOnClickOutside = (e) => {
  if (navbarCollapse.classList.contains('show') &&
      !e.target.closest('.navbar-collapse') && 
      !e.target.closest('.navbar-toggler')) {
    navbarToggler.click(); 
  }
}

// Event listener for navbar toggler
navbarToggler.addEventListener('click', () => {
  navbarCollapse.classList.toggle('show');
});

// Close the navbar when clicking outside of it
document.addEventListener('click', collapseNavbarOnClickOutside);

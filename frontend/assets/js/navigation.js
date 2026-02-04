// navigation.js - Navigation Specific Functions

// Mobile menu toggle
function toggleMobileMenu() {
    const nav = document.querySelector('nav ul');
    const hamburger = document.querySelector('.hamburger-menu');
    
    if (nav) {
        nav.classList.toggle('mobile-open');
    }
}

// Set active navigation based on current page
function setActiveNavigation() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('nav a, .category-list a, .secondary-nav-links a');
    
    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        
        // Remove any existing active classes
        link.classList.remove('active');
        
        // Check if link matches current page
        if (linkHref === currentPage || 
            linkHref === `./${currentPage}` ||
            linkHref.endsWith(currentPage)) {
            link.classList.add('active');
        }
    });
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const headerOffset = 180;
        const elementPosition = section.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
}

// Highlight navigation on scroll
function highlightNavigationOnScroll() {
    const sections = document.querySelectorAll('section[id]');
    const scrollY = window.pageYOffset;

    sections.forEach(section => {
        const sectionHeight = section.offsetHeight;
        const sectionTop = section.offsetTop - 200;
        const sectionId = section.getAttribute('id');
        
        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            document.querySelectorAll(`.secondary-nav-links a[href*=${sectionId}]`).forEach(link => {
                link.classList.add('active');
            });
        } else {
            document.querySelectorAll(`.secondary-nav-links a[href*=${sectionId}]`).forEach(link => {
                link.classList.remove('active');
            });
        }
    });
}

// Initialize navigation
function initNavigation() {
    setActiveNavigation();
    
    // Add scroll listener for highlighting
    window.addEventListener('scroll', highlightNavigationOnScroll);
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        const nav = document.querySelector('nav ul');
        const hamburger = document.querySelector('.hamburger-menu');
        
        if (nav && hamburger) {
            if (!nav.contains(e.target) && !hamburger.contains(e.target)) {
                nav.classList.remove('mobile-open');
            }
        }
    });
}

// Export functions for use in main.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        toggleMobileMenu,
        setActiveNavigation,
        scrollToSection,
        initNavigation
    };
}
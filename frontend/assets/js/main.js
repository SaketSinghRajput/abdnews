// main.js - Main JavaScript File

document.addEventListener('DOMContentLoaded', async function() {
    // Initialize all modules
    initHamburgerMenu();
    initSmoothScroll();
    initBackToTop();
    initSearchBar();
    updateDateTime();
    
    // Load dynamic content based on page
    const currentPage = window.location.pathname;
    
    try {
        if (currentPage.includes('index.html') || currentPage === '/' || currentPage.endsWith('/newshub/frontend/')) {
            await loadHomePage();
            await loadBreakingNews();
        } else if (currentPage.includes('trending.html')) {
            await loadTrendingPage();
            await loadBreakingNews();
            initTrendingFilters();
        } else if (currentPage.includes('categories.html')) {
            await loadCategoriesPage();
            await loadBreakingNews();
        } else if (currentPage.includes('article.html')) {
            await loadArticlePage();
            await loadBreakingNews();
        } else if (currentPage.includes('videos.html')) {
            await loadVideosPage();
            await loadBreakingNews();
        } else if (currentPage.includes('editorial.html')) {
            await loadEditorialPage();
            await loadBreakingNews();
        } else {
            // Load common CMS elements for all pages
            const cmsData = await loadCMSData();
            renderHeader(cmsData.siteSettings, cmsData.categories);
            renderFooter(cmsData.footerSettings, cmsData.socialLinks);
            renderSEO(cmsData.seoSettings);
        }
    } catch (error) {
        console.error('Page initialization failed:', error);
    }
    
    console.log('NewsHub initialized successfully!');
});

// Hamburger menu toggle
function initHamburgerMenu() {
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const categoryList = document.querySelector('.category-list');
    
    if (hamburgerMenu && categoryList) {
        hamburgerMenu.addEventListener('click', function() {
            categoryList.classList.toggle('show');
            this.querySelector('i').classList.toggle('fa-bars');
            this.querySelector('i').classList.toggle('fa-times');
        });
    }
}

// Smooth scrolling for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Back to top button functionality
function initBackToTop() {
    const fab = document.querySelector('.fab');
    
    if (fab) {
        // Click handler
        fab.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        // Show/hide based on scroll position
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                fab.classList.add('show');
            } else {
                fab.classList.remove('show');
            }
        });
    }
}

// Search bar functionality
function initSearchBar() {
    const searchInput = document.querySelector('.search-bar input');
    const searchButton = document.querySelector('.search-bar button');
    
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            const searchTerm = searchInput.value.trim();
            if (!searchTerm) return;
            if (typeof window.NEWSHUB_SEARCH_HANDLER === 'function') {
                window.NEWSHUB_SEARCH_HANDLER(searchTerm);
                return;
            }
            console.log('Searching for:', searchTerm);
        });
    }
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchButton.click();
            }
        });
    }
}

// Update date and time
function updateDateTime() {
    const dateTimeElement = document.querySelector('.date-time');
    if (dateTimeElement) {
        const now = new Date();
        const options = { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        dateTimeElement.textContent = now.toLocaleDateString('en-US', options) + ' IST';
    }
}

// Call once on load and then every minute
updateDateTime();
setInterval(updateDateTime, 60000);

// Add active class to current page navigation
function setActiveNavigation() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('nav a, .category-list a');
    
    navLinks.forEach(link => {
        const linkPage = link.getAttribute('href');
        if (linkPage === currentPage || linkPage === `./${currentPage}`) {
            link.classList.add('active');
        }
    });
}

setActiveNavigation();
/**
 * Ekʞo Navigation System
 * Handles dropdown menus, mobile navigation, and smooth interactions
 */

(function() {
    'use strict';
    
    // =========================================================================
    // Dropdown Menu Management
    // =========================================================================
    
    function initDropdowns() {
        const dropdowns = document.querySelectorAll('.nav-dropdown');
        
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.nav-dropdown-toggle');
            const menu = dropdown.querySelector('.nav-dropdown-menu');
            
            if (!toggle || !menu) return;
            
            // Toggle dropdown on click
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                
                // Close other dropdowns
                dropdowns.forEach(other => {
                    if (other !== dropdown) {
                        other.classList.remove('active');
                        const otherMenu = other.querySelector('.nav-dropdown-menu');
                        if (otherMenu) otherMenu.classList.remove('active');
                    }
                });
                
                // Toggle current dropdown
                dropdown.classList.toggle('active');
                menu.classList.toggle('active');
            });
        });
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.nav-dropdown')) {
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                    const menu = dropdown.querySelector('.nav-dropdown-menu');
                    if (menu) menu.classList.remove('active');
                });
            }
        });
        
        // Close dropdowns on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                    const menu = dropdown.querySelector('.nav-dropdown-menu');
                    if (menu) menu.classList.remove('active');
                });
            }
        });
    }
    
    // =========================================================================
    // Mobile Navigation
    // =========================================================================
    
    function initMobileNav() {
        const mobileToggle = document.querySelector('.nav-mobile-toggle');
        const navLinks = document.querySelector('.nav-links');
        
        if (!mobileToggle || !navLinks) return;
        
        // Toggle mobile menu
        mobileToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            navLinks.classList.toggle('active');
            
            // Update toggle icon
            const icon = mobileToggle.querySelector('span');
            if (icon) {
                icon.textContent = navLinks.classList.contains('active') ? '✕' : '☰';
            }
            
            // Prevent body scroll when menu is open
            if (navLinks.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.nav-links') && 
                !e.target.closest('.nav-mobile-toggle') &&
                navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
                document.body.style.overflow = '';
                
                const icon = mobileToggle.querySelector('span');
                if (icon) icon.textContent = '☰';
            }
        });
        
        // Close mobile menu on link click (for better UX)
        const links = navLinks.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    navLinks.classList.remove('active');
                    document.body.style.overflow = '';
                    
                    const icon = mobileToggle.querySelector('span');
                    if (icon) icon.textContent = '☰';
                }
            });
        });
    }
    
    // =========================================================================
    // Scroll Behavior
    // =========================================================================
    
    function initScrollBehavior() {
        const nav = document.querySelector('.unified-nav');
        if (!nav) return;
        
        let lastScroll = 0;
        
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            // Add scrolled class for shadow effect
            if (currentScroll > 10) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
            
            lastScroll = currentScroll;
        });
    }
    
    // =========================================================================
    // Keyboard Navigation
    // =========================================================================
    
    function initKeyboardNav() {
        const dropdowns = document.querySelectorAll('.nav-dropdown');
        
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.nav-dropdown-toggle');
            const menu = dropdown.querySelector('.nav-dropdown-menu');
            const links = menu ? menu.querySelectorAll('a') : [];
            
            if (!toggle || !menu) return;
            
            // Make toggle focusable
            toggle.setAttribute('tabindex', '0');
            
            // Toggle on Enter/Space
            toggle.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggle.click();
                    
                    // Focus first link when opening
                    if (dropdown.classList.contains('active') && links[0]) {
                        setTimeout(() => links[0].focus(), 100);
                    }
                }
            });
            
            // Arrow key navigation within dropdown
            links.forEach((link, index) => {
                link.addEventListener('keydown', (e) => {
                    if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        const next = links[index + 1] || links[0];
                        next.focus();
                    } else if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        const prev = links[index - 1] || links[links.length - 1];
                        prev.focus();
                    }
                });
            });
        });
    }
    
    // =========================================================================
    // Smooth Scroll for Internal Links
    // =========================================================================
    
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const navHeight = document.querySelector('.unified-nav')?.offsetHeight || 60;
                    const targetPosition = target.offsetTop - navHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
    
    // =========================================================================
    // Initialize Everything
    // =========================================================================
    
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        initDropdowns();
        initMobileNav();
        initScrollBehavior();
        initKeyboardNav();
        initSmoothScroll();
        
        console.log('✨ Ekʞo Navigation initialized');
    }
    
    // Start initialization
    init();
    
})();


// Portfolio Website Main JavaScript
// GSAP Animations and WebSocket functionality

// Initialize GSAP plugins
gsap.registerPlugin(ScrollTrigger, TextPlugin);

// Global variables
let authToken = localStorage.getItem('access_token');
let chatSocket = null;
let notificationSocket = null;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function () {
    initAnimations();
    initNavbar();
    initParticles();
    initScrollAnimations();
    initThemeToggle();
});

// Navbar scroll effect
function initNavbar() {
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
}

// GSAP Animations
function initAnimations() {
    // Hero section animations
    gsap.timeline()
        .from('.hero-title', {
            opacity: 0,
            y: 50,
            duration: 1,
            ease: 'power3.out'
        })
        .from('.typing-text', {
            opacity: 0,
            duration: 0.8,
            ease: 'power3.out'
        }, '-=0.5')
        .from('.hero-subtitle', {
            opacity: 0,
            y: 30,
            duration: 0.8,
            ease: 'power3.out'
        }, '-=0.3')
        .from('.hero-buttons', {
            opacity: 0,
            y: 30,
            duration: 0.8,
            ease: 'power3.out'
        }, '-=0.3');

    // Typing animation
    const typingElement = document.querySelector('.typing-text');
    if (typingElement) {
        const texts = ['Backend Developer', 'Django Expert', 'API Specialist', 'Full Stack Engineer'];
        let textIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let typingSpeed = 100;

        function typeText() {
            const currentText = texts[textIndex];

            if (isDeleting) {
                typingElement.textContent = currentText.substring(0, charIndex - 1);
                charIndex--;
                typingSpeed = 50;
            } else {
                typingElement.textContent = currentText.substring(0, charIndex + 1);
                charIndex++;
                typingSpeed = 100;
            }

            if (!isDeleting && charIndex === currentText.length) {
                isDeleting = true;
                typingSpeed = 2000; // Pause at end
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                textIndex = (textIndex + 1) % texts.length;
                typingSpeed = 500; // Pause before new word
            }

            setTimeout(typeText, typingSpeed);
        }

        typeText();
    }

    // Button hover animations
    document.querySelectorAll('.btn-primary, .btn-outline-primary').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            gsap.to(btn, {
                scale: 1.05,
                duration: 0.3,
                ease: 'power2.out'
            });
        });

        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, {
                scale: 1,
                duration: 0.3,
                ease: 'power2.out'
            });
        });
    });
}

// Scroll animations
function initScrollAnimations() {
    // Fade in animations
    gsap.utils.toArray('.fade-in').forEach(element => {
        const delay = element.getAttribute('data-animation-delay') || 0;

        gsap.to(element, {
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: delay * 0.1,
            ease: 'power2.out',
            scrollTrigger: {
                trigger: element,
                start: 'top 80%',
                end: 'bottom 20%',
                toggleActions: 'play none none reverse',
                onEnter: () => element.classList.add('visible')
            }
        });
    });

    // Slide up animations
    gsap.utils.toArray('.slide-up').forEach(element => {
        gsap.to(element, {
            opacity: 1,
            y: 0,
            duration: 0.8,
            ease: 'power2.out',
            scrollTrigger: {
                trigger: element,
                start: 'top 80%',
                end: 'bottom 20%',
                toggleActions: 'play none none reverse',
                onEnter: () => element.classList.add('visible')
            }
        });
    });

    // Scale in animations
    gsap.utils.toArray('.scale-in').forEach(element => {
        gsap.to(element, {
            opacity: 1,
            scale: 1,
            duration: 0.8,
            ease: 'back.out(1.7)',
            scrollTrigger: {
                trigger: element,
                start: 'top 80%',
                end: 'bottom 20%',
                toggleActions: 'play none none reverse',
                onEnter: () => element.classList.add('visible')
            }
        });
    });

    // Skill bar animations
    gsap.utils.toArray('.skill-progress').forEach(bar => {
        const width = bar.getAttribute('data-width') || '0%';

        ScrollTrigger.create({
            trigger: bar,
            start: 'top 80%',
            onEnter: () => {
                gsap.to(bar, {
                    width: width,
                    duration: 1.5,
                    ease: 'power2.out'
                });
            }
        });
    });
}

// Particle background
function initParticles() {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let particleCount = 50;

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            radius: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.2
        };
    }

    function initParticles() {
        particles = [];
        for (let i = 0; i < particleCount; i++) {
            particles.push(createParticle());
        }
    }

    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(particle => {
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(99, 102, 241, ${particle.opacity})`;
            ctx.fill();

            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;

            // Wrap around edges
            if (particle.x < 0) particle.x = canvas.width;
            if (particle.x > canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = canvas.height;
            if (particle.y > canvas.height) particle.y = 0;
        });

        // Draw connections
        particles.forEach((p1, i) => {
            particles.slice(i + 1).forEach(p2 => {
                const distance = Math.sqrt(
                    Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2)
                );

                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(99, 102, 241, ${0.1 * (1 - distance / 100)})`;
                    ctx.stroke();
                }
            });
        });

        requestAnimationFrame(drawParticles);
    }

    resizeCanvas();
    initParticles();
    drawParticles();

    window.addEventListener('resize', () => {
        resizeCanvas();
        initParticles();
    });
}

// Theme Toggle Functionality
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) {
        console.log('Theme toggle button not found');
        return;
    }

    const body = document.body;
    const icon = themeToggle.querySelector('i');

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    console.log('Loading saved theme:', savedTheme);

    // Remove existing theme classes
    body.classList.remove('light-theme', 'dark-theme');

    if (savedTheme === 'light') {
        body.classList.add('light-theme');
    } else {
        body.classList.add('dark-theme');
    }
    updateToggleIcon(icon, savedTheme);

    // Toggle theme on click
    themeToggle.addEventListener('click', () => {
        console.log('Theme toggle clicked');
        const isLight = body.classList.contains('light-theme');
        const newTheme = isLight ? 'dark' : 'light';
        console.log('Switching to theme:', newTheme);

        // Remove existing theme classes
        body.classList.remove('light-theme', 'dark-theme');

        // Add new theme class
        if (newTheme === 'light') {
            body.classList.add('light-theme');
        } else {
            body.classList.add('dark-theme');
        }

        localStorage.setItem('theme', newTheme);
        updateToggleIcon(icon, newTheme);
        console.log('Theme switched to:', newTheme);
    });
}

function updateToggleIcon(icon, theme) {
    icon.className = theme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
}


// WebSocket functionality
function initWebSocket() {
    if (!authToken) return;

    // Initialize notification socket
    initNotificationSocket();
}

function initNotificationSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;

    notificationSocket = new WebSocket(wsUrl);

    notificationSocket.onopen = function (e) {
        console.log('Notification socket connected');
    };

    notificationSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        if (data.type === 'notification') {
            showNotification(data.notification);
        }
    };

    notificationSocket.onclose = function (e) {
        console.log('Notification socket disconnected');
        // Attempt to reconnect after 5 seconds
        setTimeout(initNotificationSocket, 5000);
    };

    notificationSocket.onerror = function (e) {
        console.error('Notification socket error:', e);
    };
}

function showNotification(notification) {
    // Create notification element
    const notificationEl = document.createElement('div');
    notificationEl.className = 'alert alert-info alert-dismissible fade show position-fixed';
    notificationEl.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 300px;';
    notificationEl.innerHTML = `
        <strong>${notification.title}</strong><br>
        ${notification.message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notificationEl);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notificationEl.parentNode) {
            notificationEl.parentNode.removeChild(notificationEl);
        }
    }, 5000);
}

// API Helper Functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (authToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (response.status === 401 && authToken) {
        // Token expired, try to refresh
        await refreshToken();
        // Retry the request
        defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
        return fetch(url, { ...defaultOptions, ...options });
    }

    return response;
}

async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return;

    try {
        const response = await fetch('/api/auth/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            authToken = data.access;
        } else {
            // Refresh failed, logout
            logout();
        }
    } catch (error) {
        console.error('Token refresh error:', error);
        logout();
    }
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

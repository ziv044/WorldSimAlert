/**
 * Animation Manager - Reusable animation infrastructure for World Sim
 * Provides subtle CSS-based animations: pulses, fades, and count transitions
 */
const AnimationManager = {
    activeAnimations: new Map(),

    /**
     * Generate unique animation ID
     */
    generateId() {
        return `anim_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    },

    /**
     * Pulsing effect for elements (CSS-based for performance)
     * @param {HTMLElement} element - Element to animate
     * @param {Object} options - Animation options
     * @returns {string} Animation ID
     */
    pulseAnimation(element, options = {}) {
        const {
            minScale = 1.0,
            maxScale = 1.15,
            duration = 1000,
            loop = true,
            className = 'pulse-animation'
        } = options;

        const animId = this.generateId();

        // Add CSS animation class
        element.style.animation = `${className} ${duration}ms ease-in-out ${loop ? 'infinite' : '1'}`;
        element.style.setProperty('--pulse-min', minScale);
        element.style.setProperty('--pulse-max', maxScale);

        if (!loop) {
            // Remove animation after completion
            const timeout = setTimeout(() => {
                element.style.animation = '';
                this.activeAnimations.delete(animId);
            }, duration);
            this.activeAnimations.set(animId, { timeout, element });
        } else {
            this.activeAnimations.set(animId, { element });
        }

        return animId;
    },

    /**
     * Fade in/out animation
     * @param {HTMLElement} element - Element to animate
     * @param {boolean} fadeIn - True to fade in, false to fade out
     * @param {number} duration - Duration in ms
     * @param {Function} onComplete - Callback on completion
     * @returns {string} Animation ID
     */
    fadeAnimation(element, fadeIn = true, duration = 300, onComplete = null) {
        const animId = this.generateId();
        const startOpacity = fadeIn ? 0 : 1;
        const endOpacity = fadeIn ? 1 : 0;

        element.style.opacity = startOpacity;
        element.style.transition = `opacity ${duration}ms ease-out`;

        // Trigger reflow for transition to work
        element.offsetHeight;

        element.style.opacity = endOpacity;

        const timeout = setTimeout(() => {
            element.style.transition = '';
            if (onComplete) onComplete();
            this.activeAnimations.delete(animId);
        }, duration);

        this.activeAnimations.set(animId, { timeout, element });
        return animId;
    },

    /**
     * Number counting animation (for troop count changes)
     * @param {HTMLElement} element - Element containing the number
     * @param {number} fromValue - Starting value
     * @param {number} toValue - Ending value
     * @param {number} duration - Duration in ms
     * @param {Function} formatter - Optional formatter function
     * @returns {string} Animation ID
     */
    countAnimation(element, fromValue, toValue, duration = 800, formatter = null) {
        const animId = this.generateId();
        let startTime = null;

        const formatValue = formatter || ((val) => Math.round(val).toLocaleString());

        const animate = (timestamp) => {
            if (!startTime) startTime = timestamp;
            const elapsed = timestamp - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Ease out cubic
            const easedProgress = 1 - Math.pow(1 - progress, 3);
            const currentValue = fromValue + (toValue - fromValue) * easedProgress;

            element.textContent = formatValue(currentValue);

            if (progress < 1) {
                this.activeAnimations.set(animId, requestAnimationFrame(animate));
            } else {
                this.activeAnimations.delete(animId);
            }
        };

        this.activeAnimations.set(animId, requestAnimationFrame(animate));
        return animId;
    },

    /**
     * Flash effect for attention (border/background pulse)
     * @param {HTMLElement} element - Element to flash
     * @param {string} color - Flash color
     * @param {number} duration - Duration in ms
     */
    flashAnimation(element, color = '#ff4444', duration = 500) {
        const animId = this.generateId();
        const originalBoxShadow = element.style.boxShadow;

        element.style.boxShadow = `0 0 20px ${color}`;
        element.style.transition = `box-shadow ${duration}ms ease-out`;

        const timeout = setTimeout(() => {
            element.style.boxShadow = originalBoxShadow;
            setTimeout(() => {
                element.style.transition = '';
                this.activeAnimations.delete(animId);
            }, duration);
        }, 100);

        this.activeAnimations.set(animId, { timeout, element });
        return animId;
    },

    /**
     * Slide in animation
     * @param {HTMLElement} element - Element to slide
     * @param {string} direction - 'left', 'right', 'up', 'down'
     * @param {number} duration - Duration in ms
     * @param {Function} onComplete - Callback on completion
     */
    slideIn(element, direction = 'left', duration = 300, onComplete = null) {
        const animId = this.generateId();

        const transforms = {
            left: 'translateX(-100%)',
            right: 'translateX(100%)',
            up: 'translateY(-100%)',
            down: 'translateY(100%)'
        };

        element.style.transform = transforms[direction] || transforms.left;
        element.style.opacity = '0';
        element.style.transition = `transform ${duration}ms ease-out, opacity ${duration}ms ease-out`;

        // Trigger reflow
        element.offsetHeight;

        element.style.transform = 'translate(0, 0)';
        element.style.opacity = '1';

        const timeout = setTimeout(() => {
            element.style.transition = '';
            if (onComplete) onComplete();
            this.activeAnimations.delete(animId);
        }, duration);

        this.activeAnimations.set(animId, { timeout, element });
        return animId;
    },

    /**
     * Cancel a specific animation
     * @param {string} animId - Animation ID to cancel
     */
    cancelAnimation(animId) {
        const anim = this.activeAnimations.get(animId);
        if (anim) {
            if (typeof anim === 'number') {
                cancelAnimationFrame(anim);
            } else if (anim.timeout) {
                clearTimeout(anim.timeout);
            }
            if (anim.element) {
                anim.element.style.animation = '';
                anim.element.style.transition = '';
            }
            this.activeAnimations.delete(animId);
        }
    },

    /**
     * Cancel all active animations
     */
    cancelAll() {
        this.activeAnimations.forEach((anim, animId) => {
            this.cancelAnimation(animId);
        });
        this.activeAnimations.clear();
    },

    /**
     * Apply CSS class animation and remove after completion
     * @param {HTMLElement} element - Element to animate
     * @param {string} className - CSS class with animation
     * @param {number} duration - Animation duration in ms
     */
    applyClassAnimation(element, className, duration = 1000) {
        const animId = this.generateId();

        element.classList.add(className);

        const timeout = setTimeout(() => {
            element.classList.remove(className);
            this.activeAnimations.delete(animId);
        }, duration);

        this.activeAnimations.set(animId, { timeout, element });
        return animId;
    },

    /**
     * Format large numbers for display
     * @param {number} count - Number to format
     * @returns {string} Formatted string (e.g., "15K", "1.2M")
     */
    formatTroopCount(count) {
        if (count >= 1000000) {
            return (count / 1000000).toFixed(1) + 'M';
        }
        if (count >= 1000) {
            return Math.floor(count / 1000) + 'K';
        }
        return count.toString();
    }
};

// Make globally available
window.AnimationManager = AnimationManager;

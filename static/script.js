
<script>
    document.addEventListener('DOMContentLoaded', function () {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();

                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });

        // Content reveal on scroll
        const testimonials = document.querySelectorAll('.testimonial-item');
        const revealOnScroll = () => {
            testimonials.forEach(testimonial => {
                const bounding = testimonial.getBoundingClientRect();
                if (bounding.top >= 0 && bounding.bottom <= window.innerHeight) {
                    testimonial.classList.add('show');
                }
            });
        };

        window.addEventListener('scroll', revealOnScroll);
        revealOnScroll(); // Trigger on page load
    });
</script>

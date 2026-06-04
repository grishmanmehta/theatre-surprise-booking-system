// Additional JavaScript for enhanced functionality
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;

            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
});
// Movie tag selection functionality
document.addEventListener('DOMContentLoaded', function() {
    // Movie tag selection
    const movieTags = document.querySelectorAll('.movie-tag');
    const movieInput = document.getElementById('movie_preference');

    movieTags.forEach(tag => {
        tag.addEventListener('click', function() {
            const movie = this.getAttribute('data-movie');
            movieInput.value = movie;

            // Visual feedback
            movieTags.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // Scroll to input
            movieInput.focus();
        });
    });

    // Clear active class when typing manually
    movieInput.addEventListener('input', function() {
        movieTags.forEach(tag => tag.classList.remove('active'));
    });
});
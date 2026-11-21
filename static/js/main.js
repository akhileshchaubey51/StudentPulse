// Student Pulse - Advanced 3D & Modern UI Interactions
document.addEventListener('DOMContentLoaded', function () {
    // 1. Page Loader Fade-Out (3D Orbit Loader)
    const loader = document.getElementById('pageLoader');
    if (loader) {
        setTimeout(function () {
            loader.classList.add('fade-out');
            setTimeout(() => {
                if (loader.parentNode) {
                    loader.style.display = 'none';
                }
            }, 500);
        }, 350);
    }

    // 2. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.app-sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    // 3. Auto-dismiss Alert Toasts
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 4. Gentle, Stable Card Hover (No aggressive tilt or content hiding)
    // Cards now remain completely flat and readable without clipping text.

    // 5. Stat Counter Animation on Load
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(el => {
        const text = el.innerText.trim();
        const num = parseFloat(text.replace(/[^0-9.]/g, ''));
        if (!isNaN(num) && num > 0 && num < 10000 && !text.includes(':')) {
            const isPercent = text.includes('%');
            const isFloat = text.includes('.');
            let start = 0;
            const duration = 800; // ms
            const stepTime = 20;
            const steps = duration / stepTime;
            const increment = num / steps;

            const timer = setInterval(() => {
                start += increment;
                if (start >= num) {
                    start = num;
                    clearInterval(timer);
                }
                el.innerText = (isFloat ? start.toFixed(1) : Math.floor(start)) + (isPercent ? '%' : '');
            }, stepTime);
        }
    });

    // 6. Heatmap Cell Click Inspection
    const heatmapCells = document.querySelectorAll('.heatmap-day-cell');
    heatmapCells.forEach(cell => {
        cell.addEventListener('click', function () {
            const dateStr = this.getAttribute('data-date');
            const count = this.getAttribute('data-count');
            const minutes = this.getAttribute('data-minutes');
            if (dateStr) {
                const displayTarget = document.getElementById('selectedDayDetails');
                if (displayTarget) {
                    displayTarget.innerHTML = `
                        <div class="alert alert-light border border-success mb-0 d-flex align-items-center gap-2">
                            <i class="bi bi-calendar-check-fill text-success fs-5"></i>
                            <div>
                                <strong>${dateStr}</strong>: ${count} qualifying learning activity(s) &bull; 
                                <strong>Duration:</strong> ${minutes} mins logged.
                            </div>
                        </div>
                    `;
                }
            }
        });
    });
});

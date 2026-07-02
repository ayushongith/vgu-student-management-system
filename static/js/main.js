$(document).ready(function() {
    // Initialize Theme Switcher
    initTheme();

    // DataTables Initialization
    if ($.fn.DataTable) {
        $('table.datatable').DataTable({
            pageLength: 10,
            ordering: true,
            responsive: true,
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
            }
        });
    }

    // Sidebar Toggler
    $('#menu-toggle').click(function(e) {
        e.preventDefault();
        $('#sidebar').toggleClass('active');
        $('#page-content-wrapper').toggleClass('active');
    });

    // Tooltips
    if ($.fn.tooltip) {
        $('[data-bs-toggle="tooltip"]').tooltip();
    }

    // Intercept standard alerts and show premium toasts instead
    $('.alert').each(function() {
        let text = $(this).text().replace(/×/g, '').trim();
        let type = 'info';
        if ($(this).hasClass('alert-success')) type = 'success';
        else if ($(this).hasClass('alert-danger')) type = 'error';
        else if ($(this).hasClass('alert-warning')) type = 'warning';
        
        showToast(text, type);
        $(this).remove();
    });

    // Run Count-Up Animations
    animateCounters();
});

// Toast System
function showToast(message, type = 'info') {
    let container = $('#toast-container');
    if (container.length === 0) {
        $('body').append('<div id="toast-container"></div>');
        container = $('#toast-container');
    }

    let iconClass = 'bi-info-circle-fill';
    if (type === 'success') iconClass = 'bi-check-circle-fill';
    else if (type === 'error') iconClass = 'bi-exclamation-circle-fill';
    else if (type === 'warning') iconClass = 'bi-exclamation-triangle-fill';

    let toastHtml = `
        <div class="custom-toast toast-${type}">
            <div class="d-flex align-items-center gap-2">
                <i class="bi ${iconClass} fs-5 text-${type === 'error' ? 'danger' : type === 'success' ? 'success' : type}"></i>
                <span class="small fw-semibold">${message}</span>
            </div>
            <button type="button" class="btn-close ms-3" style="font-size:10px;"></button>
        </div>
    `;

    let $toast = $(toastHtml);
    container.append($toast);

    // Manual Dismiss
    $toast.find('.btn-close').click(function() {
        dismissToast($toast);
    });

    // Auto Dismiss after 4s
    setTimeout(function() {
        dismissToast($toast);
    }, 4500);
}

function dismissToast($toast) {
    $toast.css('transform', 'translateX(120%) scale(0.9)');
    $toast.css('opacity', '0');
    setTimeout(function() {
        $toast.remove();
    }, 300);
}

// KPI Counters Count-Up
function animateCounters() {
    $('.stat-value').each(function() {
        let $this = $(this);
        let txt = $this.text().trim();
        let val = parseInt(txt.replace(/[^\d]/g, ''), 10);
        if (isNaN(val)) return;

        let suffix = txt.replace(/[\d]/g, '');
        $({ countNum: 0 }).animate({
            countNum: val
        }, {
            duration: 1000,
            easing: 'swing',
            step: function() {
                $this.text(Math.floor(this.countNum) + suffix);
            },
            complete: function() {
                $this.text(this.countNum + suffix);
            }
        });
    });
}

// Theme Handling
function initTheme() {
    let currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', currentTheme);
    updateThemeUI(currentTheme);

    $(document).on('click', '#theme-toggle', function(e) {
        e.preventDefault();
        let theme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        updateThemeUI(theme);
    });
}

function updateThemeUI(theme) {
    let icon = $('#theme-toggle i');
    if (theme === 'dark') {
        icon.removeClass('bi-moon-fill').addClass('bi-sun-fill');
    } else {
        icon.removeClass('bi-sun-fill').addClass('bi-moon-fill');
    }
}

// Delete Confirmation
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this?');
}

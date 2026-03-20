/* HRMS Main JavaScript — jQuery-powered interactions */

$(document).ready(function () {

    // === Sidebar Toggle ===
    $('#sidebarToggle').on('click', function (e) {
        e.stopPropagation();
        if (window.innerWidth <= 768) {
            $('#sidebar').toggleClass('open');
        } else {
            $('body').toggleClass('sidebar-collapsed');
        }
    });

    // Close sidebar on mobile when clicking outside
    $(document).on('click', function (e) {
        if (window.innerWidth <= 768 && $('#sidebar').hasClass('open')) {
            if (!$(e.target).closest('#sidebar').length) {
                $('#sidebar').removeClass('open');
            }
        }
    });

    // === Auto-dismiss alerts ===
    setTimeout(function () {
        $('.alert.fade.show').fadeOut(500, function () {
            $(this).remove();
        });
    }, 4500);

    // === Live search filter (client-side) on Enter ===
    $('#filterForm input[name="q"]').on('keypress', function (e) {
        if (e.which === 13) {
            $(this).closest('form').submit();
        }
    });

    // === Payroll form: Live gross/net calculation ===
    function recalculatePayroll() {
        var basic = parseFloat($('#id_basic_salary').val()) || 0;
        var hra = parseFloat($('#id_hra').val()) || 0;
        var ta = parseFloat($('#id_travel_allowance').val()) || 0;
        var other = parseFloat($('#id_other_allowances').val()) || 0;
        var ot = parseFloat($('#id_overtime_pay').val()) || 0;
        var pf = parseFloat($('#id_pf_deduction').val()) || 0;
        var tds = parseFloat($('#id_tax_deduction').val()) || 0;
        var od = parseFloat($('#id_other_deductions').val()) || 0;
        var ld = parseFloat($('#id_leave_deductions').val()) || 0;

        var gross = basic + hra + ta + other + ot;
        var deductions = pf + tds + od + ld;
        var net = gross - deductions;

        if ($('#liveGross').length) {
            $('#liveGross').text('₹' + gross.toFixed(2));
            $('#liveNet').text('₹' + net.toFixed(2));
            $('#liveDeductions').text('₹' + deductions.toFixed(2));
        }
    }

    if ($('#payrollForm').length) {
        // Inject live preview
        var previewHtml = '<div class="card card-dash mt-4 p-3"><h6 class="mb-3 text-muted fw-bold" style="font-size:12px">LIVE PREVIEW</h6><div class="d-flex justify-content-between mb-2"><span class="text-muted">Gross Salary</span><strong id="liveGross" class="text-primary">₹0.00</strong></div><div class="d-flex justify-content-between mb-2"><span class="text-muted">Total Deductions</span><strong id="liveDeductions" class="text-danger">₹0.00</strong></div><hr style="margin:8px 0"><div class="d-flex justify-content-between"><span class="fw-bold">Net Pay</span><strong id="liveNet" class="text-success fs-5">₹0.00</strong></div></div>';
        $('.form-actions').before(previewHtml);

        $('#payrollForm input[type="number"]').on('input', recalculatePayroll);
        recalculatePayroll();
    }

    // === Employee form: Show/hide hourly rate based on type ===
    function toggleHourlyRate() {
        var type = $('#id_employee_type').val();
        if (type === 'full_time') {
            $('#hourlyRateField').hide();
        } else {
            $('#hourlyRateField').show();
        }
    }
    if ($('#id_employee_type').length) {
        toggleHourlyRate();
        $('#id_employee_type').on('change', toggleHourlyRate);
    }

    // === Tooltip init ===
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // === Leave review: Update button text from dropdown ===
    $('#reviewForm select[name="status"]').on('change', function () {
        var val = $(this).val();
        if (val === 'approved') {
            $('.review-btn').text('Approve').removeClass('btn-danger').addClass('btn-success');
        } else {
            $('.review-btn').text('Reject').removeClass('btn-success').addClass('btn-danger');
        }
    });

    // === Confirm delete with AJAX-style alert ===
    $('form[action*="delete"]').on('submit', function (e) {
        // Allow native confirmation pages to handle it
    });

    // === Realtime Activity Polling ===
    function fetchActivities() {
        if ($('#activityFeed').length === 0) return;

        $.ajax({
            url: '/api/activities/',
            method: 'GET',
            success: function(response) {
                // Update badge
                if (response.unread_count > 0) {
                    $('#notificationBadge').text(response.unread_count).show();
                } else {
                    $('#notificationBadge').hide();
                }

                // Update feed
                var html = '';
                if (response.activities.length === 0) {
                    html = '<li><span class="dropdown-item text-muted small text-center py-3">No recent activity</span></li>';
                } else {
                    response.activities.forEach(function(act) {
                        html += `
                            <li>
                                <div class="dropdown-item py-2" style="white-space: normal;">
                                    <div class="d-flex w-100 justify-content-between">
                                        <strong class="mb-1 text-primary" style="font-size:0.85rem;">${act.user}</strong>
                                        <small class="text-muted" style="font-size:0.75rem;">${act.timesince}</small>
                                    </div>
                                    <p class="mb-0 small" style="font-size:0.85rem;"><span class="badge bg-secondary me-1">${act.action}</span> ${act.description}</p>
                                </div>
                            </li>
                            <li><hr class="dropdown-divider m-0"></li>
                        `;
                    });
                }
                $('#activityFeed').html(html);
            }
        });
    }

    // Mark read on dropdown open
    $('#notificationDropdown').on('show.bs.dropdown', function () {
        var count = parseInt($('#notificationBadge').text());
        if (count > 0) {
            $.ajax({
                url: '/api/activities/mark-read/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function() {
                    $('#notificationBadge').hide().text('0');
                }
            });
        }
    });

    // Run immediately, then every 10 seconds
    fetchActivities();
    setInterval(fetchActivities, 10000);

    // Helper for CSRF
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

});

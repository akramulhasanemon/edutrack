// EduTrack Modern Desktop UI Application Controller
// Interacts with DesktopBridgeAPI via PyWebView

var currentRole = 'student';
var currentUserId = '20255103311';
var currentUserInitials = 'MS';
var showPw = false;
var activeStudentData = null;
var activeFacultyData = null;
var chartsInited = false;
var chartInstances = {};

function showToast(message, type) {
  type = type || 'info';
  var container = document.getElementById('toast-container');
  if (!container) return;
  var toast = document.createElement('div');
  toast.className = 'toast-msg ' + type;
  var icon = type === 'success' ? '✔' : (type === 'danger' ? '✖' : 'ℹ');
  toast.innerHTML = '<span style="font-size:14px;font-weight:700;">' + icon + '</span><span>' + message + '</span>';
  container.appendChild(toast);
  setTimeout(function() {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(function() { toast.remove(); }, 400);
  }, 3500);
}

function setRole(r) {
  currentRole = r;
  var sBtn = document.getElementById('role-student');
  var fBtn = document.getElementById('role-faculty');
  if (sBtn) sBtn.classList.toggle('active', r === 'student');
  if (fBtn) fBtn.classList.toggle('active', r === 'faculty');
  var lbl = document.getElementById('id-label');
  if (lbl) lbl.textContent = r === 'student' ? 'Student ID' : 'Faculty ID';
  var inp = document.getElementById('login-id');
  if (inp) inp.value = r === 'student' ? '20255103311' : 'FACULTY001';
}

function togglePw() {
  showPw = !showPw;
  var el = document.getElementById('login-pw');
  if (el) el.type = showPw ? 'text' : 'password';
}

function demoLogin(role) {
  setRole(role);
  var idInput = document.getElementById('login-id');
  var pwInput = document.getElementById('login-pw');
  if (role === 'student') {
    if (idInput) idInput.value = '20255103311';
    if (pwInput) pwInput.value = 'EduTrack2026!';
  } else {
    if (idInput) idInput.value = 'FACULTY001';
    if (pwInput) pwInput.value = 'EduTrack2026!';
  }
  doLogin();
}

async function doLogin() {
  var idEl = document.getElementById('login-id');
  var pwEl = document.getElementById('login-pw');
  var id = idEl ? idEl.value.trim() : '20255103311';
  var pw = pwEl ? pwEl.value : 'EduTrack2026!';
  var btn = document.querySelector('.login-card .btn-primary');
  var origText = btn ? btn.innerHTML : 'Sign In';
  if (btn) {
    btn.innerHTML = 'Connecting to SQLite...';
    btn.disabled = true;
  }

  try {
    var res = null;
    if (window.pywebview && window.pywebview.api) {
      res = await window.pywebview.api.authenticate(id, pw, currentRole);
    } else {
      res = {
        success: true,
        role: currentRole,
        user: { user_id: id, display_name: currentRole === 'student' ? 'Mahabub Shaddhow' : 'Faculty Member' }
      };
    }

    if (res && !res.success) {
      showToast(res.error || 'Authentication failed. Please verify credentials.', 'danger');
      if (btn) {
        btn.innerHTML = origText;
        btn.disabled = false;
      }
      return;
    }

    currentUserId = id;
    if (res && res.role === 'student' && res.student_data) {
      activeStudentData = res.student_data;
      applyStudentData(res.student_data, res.user);
    } else if (res && res.role === 'faculty' && res.faculty_data) {
      activeFacultyData = res.faculty_data;
      applyFacultyData(res.faculty_data, res.user);
    }

    var loginPage = document.getElementById('login-page');
    var appPage = document.getElementById('app-page');
    if (loginPage) loginPage.classList.remove('active');
    if (appPage) appPage.classList.add('active');

    var sNav = document.getElementById('student-nav');
    var fNav = document.getElementById('faculty-nav');
    if (currentRole === 'faculty') {
      if (sNav) sNav.style.display = 'none';
      if (fNav) fNav.style.display = 'block';
      showSection('faculty-dashboard');
    } else {
      if (sNav) sNav.style.display = 'block';
      if (fNav) fNav.style.display = 'none';
      showSection('dashboard');
    }

    initCharts();
    showToast('Signed in successfully!', 'success');
  } catch (err) {
    console.error('Login error:', err);
    showToast('Sign in error: ' + err, 'danger');
  } finally {
    if (btn) {
      btn.innerHTML = origText;
      btn.disabled = false;
    }
  }
}

async function signOut() {
  if (window.pywebview && window.pywebview.api) {
    try { await window.pywebview.api.sign_out(); } catch(e){}
  }
  document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
  var loginPage = document.getElementById('login-page');
  if (loginPage) loginPage.classList.add('active');
  currentRole = 'student';
  var sNav = document.getElementById('student-nav');
  var fNav = document.getElementById('faculty-nav');
  if (sNav) sNav.style.display = 'block';
  if (fNav) fNav.style.display = 'none';
  showToast('Signed out of EduTrack.', 'info');
}

function showSection(id) {
  document.querySelectorAll('.section').forEach(function(s) { s.classList.remove('active'); });
  document.querySelectorAll('.nav-item').forEach(function(n) { n.classList.remove('active'); });
  var sec = document.getElementById('section-' + id);
  if (sec) sec.classList.add('active');

  var titles = {
    'dashboard': ['Your academic journey', 'A clear view of your progress, goals, and next steps.', 'EduTrack › Student Workspace › Dashboard'],
    'trajectory': ['Trajectory Planner', 'AI-powered GPA forecasting and graduation targeting.', 'EduTrack › Student Workspace › Trajectory Planner'],
    'cgpa': ['CGPA Calculator', 'Calculate and project your cumulative GPA.', 'EduTrack › Student Workspace › CGPA Calculator'],
    'advisor': ['AI Advisor', 'Your intelligent academic planning assistant.', 'EduTrack › Student Workspace › AI Advisor'],
    'analytics': ['Analytics', 'Deep dive into your academic performance data.', 'EduTrack › Student Workspace › Analytics'],
    'attendance': ['Attendance & Schedule', 'Track attendance and manage your class schedule.', 'EduTrack › Student Workspace › Attendance & Schedule'],
    'settings': ['Settings', 'Manage your profile and preferences.', 'EduTrack › Student Workspace › Settings'],
    'faculty-dashboard': ['Faculty Control Panel', 'Review students and manage academic records in your assigned sections.', 'EduTrack › Faculty Workspace › Dashboard'],
    'section-assignments': ['Section Assignments', 'Your assigned course sections and rosters.', 'EduTrack › Faculty Workspace › Section Assignments']
  };

  if (titles[id]) {
    var pTitle = document.getElementById('page-title');
    var pSub = document.getElementById('page-sub');
    var bc = document.getElementById('breadcrumb');
    if (pTitle) pTitle.textContent = titles[id][0];
    if (pSub) pSub.textContent = titles[id][1];
    if (bc) bc.innerHTML = titles[id][2].replace(/›/g, '› <span>').replace(/^/, '<span>') + '</span>';
  }

  var navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(function(n) {
    if (n.getAttribute('onclick') && n.getAttribute('onclick').indexOf("'" + id + "'") !== -1) {
      n.classList.add('active');
    }
  });

  if (id === 'cgpa') {
    var cContainer = document.getElementById('courses-container');
    if (cContainer && cContainer.children.length === 0) {
      addCourse(); addCourse(); addCourse();
    }
  }
}

function getInitials(name) {
  if (!name) return 'ST';
  var parts = name.trim().split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  return name.slice(0, 2).toUpperCase();
}

function applyStudentData(data, user) {
  if (!data) return;
  var name = (user && user.display_name) || (data.profile && data.profile.name) || 'Mahabub Shaddhow';
  var sid = (data.profile && data.profile.student_id) || '20255103311';
  currentUserInitials = getInitials(name);

  var sName = document.getElementById('sidebar-name');
  var sRole = document.getElementById('sidebar-role');
  var sAva = document.getElementById('sidebar-avatar');
  if (sName) sName.textContent = name;
  if (sRole) sRole.textContent = 'Student / ' + sid;
  if (sAva) sAva.textContent = currentUserInitials;

  var wAva = document.querySelector('.welcome-banner .avatar');
  if (wAva) wAva.textContent = currentUserInitials;
  var wName = document.querySelector('.welcome-banner .w-name');
  if (wName) wName.textContent = 'Welcome back, ' + name;
  var wMeta = document.querySelector('.welcome-banner .w-meta');
  var pct = Math.round((data.completed_credits / (data.program_credits || 142)) * 100);
  if (wMeta) {
    wMeta.textContent = 'ID: ' + sid + ' · ' + (data.profile.current_semester || 'Fall 2026') + ' · ' + data.completed_credits + '/' + data.program_credits + ' Credits (' + pct + '% Completed)';
  }
  var wBar = document.querySelector('.welcome-banner div[style*="width:17%"]');
  if (wBar) wBar.style.width = pct + '%';

  var statVals = document.querySelectorAll('.stats-grid .stat-val');
  if (statVals.length >= 4) {
    statVals[0].textContent = data.cgpa.toFixed(2);
    statVals[1].textContent = data.completed_credits;
    statVals[2].textContent = data.target_cgpa.toFixed(2);
    statVals[3].textContent = data.watch_courses_count;
  }
  var statHints = document.querySelectorAll('.stats-grid .stat-hint');
  if (statHints.length >= 4) {
    statHints[0].textContent = data.cgpa.toFixed(2) + ' / 4.00 (' + (data.standing_title || 'Good Standing') + ')';
    statHints[1].textContent = data.remaining_credits + ' credits remaining';
  }

  var trajVals = document.querySelectorAll('.traj-stats .stat-val');
  if (trajVals.length >= 3) {
    trajVals[0].textContent = data.cgpa.toFixed(2);
    trajVals[1].textContent = data.target_cgpa.toFixed(2);
    trajVals[2].textContent = data.completed_credits + '/' + data.program_credits;
  }

  var settingId = document.getElementById('setting-student-id');
  if (settingId) settingId.value = sid;
  var settingName = document.getElementById('setting-display-name');
  if (settingName) settingName.value = name;
  var settingGoal = document.getElementById('setting-target-cgpa');
  if (settingGoal) settingGoal.value = data.target_cgpa;

  renderSchedule(data.routines);
  renderAttendance(data.attendance, data.overall_attendance);
  updateCharts(data);
}

function applyFacultyData(data, user) {
  if (!data) return;
  var name = (user && user.display_name) || 'Faculty Member';
  var fid = data.faculty_id || 'FACULTY001';
  currentUserInitials = getInitials(name);

  var sName = document.getElementById('sidebar-name');
  var sRole = document.getElementById('sidebar-role');
  var sAva = document.getElementById('sidebar-avatar');
  if (sName) sName.textContent = name;
  if (sRole) sRole.textContent = 'Faculty / ' + fid;
  if (sAva) sAva.textContent = currentUserInitials;

  var facStats = document.querySelectorAll('.faculty-stats-grid .stat-val');
  if (facStats.length >= 4) {
    facStats[0].textContent = data.total_students || 1;
    facStats[1].textContent = (data.batch_avg_cgpa || 3.22).toFixed(2);
    facStats[2].textContent = data.at_risk_count || 0;
    facStats[3].textContent = (data.students || []).filter(function(s) { return (s.cgpa || 0) >= 3.75; }).length;
  }

  var tbody = document.querySelector('.roster-table tbody');
  if (tbody && data.students && data.students.length > 0) {
    tbody.innerHTML = '';
    data.students.forEach(function(s) {
      var tr = document.createElement('tr');
      var isAtRisk = (s.cgpa || 0) < 2.5;
      var statusBadge = isAtRisk
        ? '<span class="status-badge at-risk">● At Risk</span>'
        : '<span class="status-badge on-track">● On Track</span>';
      tr.innerHTML = '<td style="color:var(--accent2);">' + s.student_id + '</td>' +
        '<td style="font-weight:600;">' + s.name + '</td>' +
        '<td>' + (s.section || '06') + '</td>' +
        '<td style="color:' + (isAtRisk ? 'var(--danger)' : 'var(--success)') + ';font-weight:600;">' + (s.cgpa ? s.cgpa.toFixed(2) : '3.22') + '</td>' +
        '<td>' + statusBadge + '</td>' +
        '<td><button class="btn-sm" onclick="exportStudentTranscript(\'' + s.student_id + '\')">Transcript 📄</button></td>';
      tbody.appendChild(tr);
    });
  }
}

function renderSchedule(routines) {
  if (!routines || routines.length === 0) return;
  var firstItem = document.querySelector('.glass-card .schedule-item');
  var previewContainer = firstItem ? firstItem.parentElement : null;
  if (previewContainer) {
    var items = previewContainer.querySelectorAll('.schedule-item');
    items.forEach(function(i) { i.remove(); });
    routines.slice(0, 3).forEach(function(r) {
      var div = document.createElement('div');
      div.className = 'schedule-item';
      div.innerHTML = '<div>' +
        '<div class="schedule-time">' + (r.time || '10:00 - 11:30') + ' (' + (r.day || 'Mon') + ')</div>' +
        '<div class="schedule-course">' + (r.course_code || 'CSE101') + ' · ' + (r.room || 'Room 501') + '</div>' +
        '<div class="schedule-desc">' + (r.course_title || 'Introduction to Computer Science') + '</div>' +
        '</div>';
      var btn = previewContainer.querySelector('button');
      if (btn) previewContainer.insertBefore(div, btn);
      else previewContainer.appendChild(div);
    });
  }
}

function renderAttendance(attendanceRecords, overallPct) {
  if (!attendanceRecords || attendanceRecords.length === 0) return;
  var attList = document.getElementById('att-list');
  if (attList) {
    attList.innerHTML = '';
    attendanceRecords.forEach(function(rec) {
      var pct = Math.round(rec.attendance_percentage || ((rec.attended_classes / (rec.total_classes || 1)) * 100));
      var color = pct >= 85 ? 'var(--success)' : (pct >= 75 ? 'var(--accent2)' : 'var(--warning)');
      var div = document.createElement('div');
      div.className = 'att-row';
      div.innerHTML = '<div class="att-course-name">' + rec.course_code + ' <span style="font-size:11px;color:var(--text3);">(' + rec.attended_classes + '/' + rec.total_classes + ' classes)</span></div>' +
        '<div class="att-bar"><div class="att-fill" style="width:' + pct + '%;background:' + color + ';"></div></div>' +
        '<div class="att-pct" style="color:' + color + ';">' + pct + '%</div>';
      attList.appendChild(div);
    });
  }
}

function updateCharts(data) {
  if (!data) return;
  if (chartInstances['trend'] && data.trend_labels && data.trend_gpas) {
    chartInstances['trend'].data.labels = data.trend_labels;
    chartInstances['trend'].data.datasets[0].data = data.trend_gpas;
    chartInstances['trend'].update();
  }
  if (chartInstances['analyticsTrend'] && data.trend_labels && data.trend_gpas) {
    chartInstances['analyticsTrend'].data.labels = data.trend_labels;
    chartInstances['analyticsTrend'].data.datasets[0].data = data.trend_gpas;
    chartInstances['analyticsTrend'].update();
  }
  if (chartInstances['gradeDist'] && data.grade_distribution) {
    chartInstances['gradeDist'].data.datasets[0].data = Object.values(data.grade_distribution);
    chartInstances['gradeDist'].update();
  }
}

function drawPill(ctx, x, y, w, h, r, fillColor, strokeColor) {
  ctx.save();
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
  if (fillColor) { ctx.fillStyle = fillColor; ctx.fill(); }
  if (strokeColor) { ctx.strokeStyle = strokeColor; ctx.lineWidth = 1.2; ctx.stroke(); }
  ctx.restore();
}

function initLoginChart() {
  if (chartInstances['login'] || typeof Chart === 'undefined') return;
  var lc = document.getElementById('login-chart');
  if (!lc) return;

  var gridOpts = {
    color: 'rgba(255,255,255,0.05)',
    drawBorder: false,
    tickLength: 0
  };

  var annotationsPlugin = {
    id: 'loginAnnotations',
    afterDatasetsDraw: function(chart) {
      try {
        var ctx = chart.ctx;
        var yScale = chart.scales.y;
        var xScale = chart.scales.x;
        var meta = chart.getDatasetMeta(0);
        if (!meta || !meta.data || !meta.data.length) return;

        // 1. Draw orange benchmark line & text at 3.75
        var y375 = yScale.getPixelForValue(3.75);
        ctx.save();
        ctx.setLineDash([5, 4]);
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.85)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(xScale.left, y375);
        ctx.lineTo(xScale.right, y375);
        ctx.stroke();
        ctx.restore();

        ctx.save();
        ctx.fillStyle = '#f59e0b';
        ctx.font = '600 10px "Segoe UI", sans-serif';
        ctx.fillText("★ Dean's Honor Benchmark (3.75)", xScale.left + 12, y375 - 6);
        ctx.restore();

        // 2. Vertical dashed guide line from S4 (index 3) to bottom
        var ptS4 = meta.data[3];
        if (ptS4) {
          ctx.save();
          ctx.setLineDash([3, 3]);
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)';
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(ptS4.x, ptS4.y);
          ctx.lineTo(ptS4.x, yScale.bottom);
          ctx.stroke();
          ctx.restore();

          // Callout box: CURRENT • 3.52
          var text1 = 'CURRENT • 3.52';
          ctx.save();
          ctx.font = '700 9.5px "Segoe UI", sans-serif';
          var tWidth1 = ctx.measureText(text1).width;
          var bWidth1 = tWidth1 + 14;
          var bHeight1 = 20;
          var bX1 = ptS4.x - bWidth1 / 2;
          var bY1 = ptS4.y - bHeight1 - 6;

          drawPill(ctx, bX1, bY1, bWidth1, bHeight1, 5, '#060d1a', '#38bdf8');
          ctx.fillStyle = '#ffffff';
          ctx.fillText(text1, bX1 + 7, bY1 + 13.5);
          ctx.restore();
        }

        // 3. Callout box: ★ GOAL • 3.88 at S6 (index 5)
        var ptS6 = meta.data[5];
        if (ptS6) {
          var text2 = '★ GOAL • 3.88';
          ctx.save();
          ctx.font = '700 9.5px "Segoe UI", sans-serif';
          var tWidth2 = ctx.measureText(text2).width;
          var bWidth2 = tWidth2 + 14;
          var bHeight2 = 20;
          var bX2 = ptS6.x - bWidth2 - 4;
          var bY2 = ptS6.y - bHeight2 + 4;

          drawPill(ctx, bX2, bY2, bWidth2, bHeight2, 5, '#060d1a', '#10b981');
          ctx.fillStyle = '#10b981';
          ctx.fillText(text2, bX2 + 7, bY2 + 13.5);
          ctx.restore();
        }
      } catch (err) {
        console.error('Error drawing annotations:', err);
      }
    }
  };

  chartInstances['login'] = new Chart(lc, {
    type: 'line',
    data: {
      labels: ['S1', 'S2', 'S3', 'S4', 'S5', 'S6 (Proj)'],
      datasets: [
        {
          label: 'Predictive GPA Curve',
          data: [2.35, 2.55, 2.78, 3.52, 3.72, 3.88],
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56, 189, 248, 0.08)',
          borderWidth: 2.2,
          pointBackgroundColor: '#060d1a',
          pointBorderColor: '#38bdf8',
          pointBorderWidth: 2,
          pointRadius: 4.5,
          pointHoverRadius: 6,
          tension: 0.35,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(6, 13, 26, 0.95)',
          titleColor: '#f0f4ff',
          bodyColor: '#38bdf8',
          borderColor: 'rgba(56, 189, 248, 0.3)',
          borderWidth: 1,
          padding: 8,
          displayColors: false
        }
      },
      scales: {
        x: {
          grid: gridOpts,
          ticks: {
            color: 'rgba(255,255,255,0.45)',
            font: { size: 10, family: "'Segoe UI', sans-serif" }
          }
        },
        y: {
          grid: gridOpts,
          min: 2.0,
          max: 4.0,
          ticks: {
            stepSize: 0.5,
            color: 'rgba(255,255,255,0.45)',
            font: { size: 10, family: "'Segoe UI', sans-serif" },
            callback: function(v) { return Number(v).toFixed(1); }
          }
        }
      }
    },
    plugins: [annotationsPlugin]
  });
}

document.addEventListener('DOMContentLoaded', initLoginChart);
setTimeout(initLoginChart, 200);

function initCharts() {
  if (chartsInited) return;
  if (typeof Chart === 'undefined') return;
  chartsInited = true;

  initLoginChart();

  var defaults = { color: 'rgba(255,255,255,0.7)', font: { family: "'Segoe UI', system-ui, sans-serif", size: 11 } };
  Chart.defaults.color = defaults.color;
  Chart.defaults.font = defaults.font;
  var gridOpts = { color: 'rgba(255,255,255,0.04)', drawBorder: false };

  var tc = document.getElementById('trend-chart');
  if (tc) {
    chartInstances['trend'] = new Chart(tc, {
      type: 'line',
      data: {
        labels: (activeStudentData && activeStudentData.trend_labels) || ['S1', 'S2', 'S3'],
        datasets: [{
          data: (activeStudentData && activeStudentData.trend_gpas) || [3.25, 3.08, 3.38],
          borderColor: '#00d4a8',
          backgroundColor: 'rgba(0,212,168,0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#00d4a8',
          pointRadius: 5,
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { grid: gridOpts }, y: { grid: gridOpts, min: 2.5, max: 4 } }
      }
    });
  }

  var tjc = document.getElementById('traj-chart');
  if (tjc) {
    chartInstances['traj'] = new Chart(tjc, {
      type: 'line',
      data: {
        labels: ['S1', 'S2', 'S3', 'S4', 'S5', 'S6 (Proj)'],
        datasets: [
          {
            label: 'GPA Trajectory',
            data: [2.4, 2.6, 2.9, 3.52, 3.72, 3.88],
            borderColor: '#00d4a8',
            backgroundColor: 'rgba(0,212,168,0.1)',
            borderWidth: 2.5,
            pointBackgroundColor: '#00d4a8',
            pointRadius: 5,
            tension: 0.4,
            fill: true
          },
          {
            label: "Dean's Benchmark (3.75)",
            data: [3.75, 3.75, 3.75, 3.75, 3.75, 3.75],
            borderColor: '#f59e0b',
            borderWidth: 1.5,
            borderDash: [6, 4],
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: 'rgba(255,255,255,0.5)', font: { size: 11 } } } },
        scales: { x: { grid: gridOpts }, y: { grid: gridOpts, min: 2, max: 4.1 } }
      }
    });
  }

  var at = document.getElementById('analytics-trend');
  if (at) {
    chartInstances['analyticsTrend'] = new Chart(at, {
      type: 'bar',
      data: {
        labels: (activeStudentData && activeStudentData.trend_labels) || ['S1', 'S2', 'S3'],
        datasets: [{
          data: (activeStudentData && activeStudentData.trend_gpas) || [3.25, 3.08, 3.38],
          backgroundColor: ['rgba(0,212,168,0.5)', 'rgba(0,212,168,0.6)', 'rgba(0,212,168,0.8)'],
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { grid: gridOpts }, y: { grid: gridOpts, min: 2.5, max: 4.1 } }
      }
    });
  }

  var gd = document.getElementById('grade-dist');
  if (gd) {
    chartInstances['gradeDist'] = new Chart(gd, {
      type: 'doughnut',
      data: {
        labels: ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'D', 'F'],
        datasets: [{
          data: (activeStudentData && Object.values(activeStudentData.grade_distribution)) || [2, 3, 4, 5, 3, 1, 0, 0, 0, 0],
          backgroundColor: ['#00d4a8', '#0ea5e9', '#7c3aed', '#f59e0b', '#10b981', '#ef4444', '#a855f7', '#6366f1', '#ec4899', '#64748b'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'right',
            labels: { color: 'rgba(255,255,255,0.6)', font: { size: 11 }, padding: 10 }
          }
        }
      }
    });
  }
}

// CGPA Calculator
var courses = [];
var gradeMap = { 'A+': 4.0, 'A': 3.75, 'A-': 3.5, 'B+': 3.25, 'B': 3.0, 'B-': 2.75, 'C+': 2.5, 'C': 2.25, 'D': 2.0, 'F': 0.0 };

function addCourse() {
  var id = Date.now() + Math.floor(Math.random() * 1000);
  courses.push(id);
  var div = document.createElement('div');
  div.className = 'course-row';
  div.id = 'cr-' + id;
  div.innerHTML = '<input class="field-input" style="font-size:12px;padding:6px 10px;" placeholder="Course code" value="CSE' + (200 + courses.length) + '">' +
    '<select class="select-sm" id="grade-' + id + '"><option>A+</option><option>A</option><option selected>A-</option><option>B+</option><option>B</option><option>B-</option><option>C+</option><option>C</option><option>D</option><option>F</option></select>' +
    '<input class="input-sm" id="cr-val-' + id + '" value="3" type="number" min="1" max="6">' +
    '<button onclick="rmCourse(' + id + ')" style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);color:#ef4444;padding:5px 8px;border-radius:6px;cursor:pointer;font-size:12px;">✕</button>';
  var container = document.getElementById('courses-container');
  if (container) container.appendChild(div);
}

function rmCourse(id) {
  var el = document.getElementById('cr-' + id);
  if (el) el.remove();
  courses = courses.filter(function(c) { return c !== id; });
}

function calcGPA() {
  var total = 0, cr = 0;
  courses.forEach(function(id) {
    var g = document.getElementById('grade-' + id);
    var c = document.getElementById('cr-val-' + id);
    if (g && c) {
      var pts = gradeMap[g.value] || 0;
      var credits = parseFloat(c.value) || 0;
      total += pts * credits;
      cr += credits;
    }
  });
  var gpa = cr > 0 ? (total / cr) : 0;
  var gVal = document.getElementById('gpa-val');
  var gRes = document.getElementById('gpa-result');
  if (gVal) gVal.textContent = gpa.toFixed(2);
  if (gRes) gRes.style.display = 'block';
  showToast('Semester GPA: ' + gpa.toFixed(2) + ' across ' + cr + ' credits', 'success');
}

function projectCGPA() {
  var currentCgpa = (activeStudentData && activeStudentData.cgpa) || 3.22;
  var doneCrEl = document.getElementById('done-cr');
  var totalCrEl = document.getElementById('total-cr');
  var doneCr = doneCrEl ? (parseFloat(doneCrEl.value) || 24) : 24;
  var totalCr = totalCrEl ? (parseFloat(totalCrEl.value) || 142) : 142;
  var remainingCr = Math.max(0, totalCr - doneCr);
  var targetGpa = 3.50;
  var proj = ((currentCgpa * doneCr) + (targetGpa * remainingCr)) / totalCr;
  var projEl = document.getElementById('proj-cgpa');
  if (projEl) projEl.textContent = proj.toFixed(2);
}

async function exportTranscript() {
  exportStudentTranscript(currentUserId);
}

async function exportStudentTranscript(sid) {
  showToast('Generating official ReportLab PDF transcript...', 'info');
  try {
    if (window.pywebview && window.pywebview.api) {
      var res = await window.pywebview.api.export_pdf_transcript(sid);
      if (res && res.success) {
        showToast(res.message || 'Official transcript opened in viewer!', 'success');
      } else {
        showToast('Export failed: ' + (res.error || 'Unknown error'), 'danger');
      }
    } else {
      showToast('PDF Export is active when running in desktop application.', 'info');
    }
  } catch (err) {
    showToast('Export error: ' + err, 'danger');
  }
}

async function saveSettings() {
  var goalEl = document.getElementById('setting-target-cgpa');
  var nameEl = document.getElementById('setting-display-name');
  var keyEl = document.getElementById('setting-gemini-key');

  var targetCgpa = goalEl ? (parseFloat(goalEl.value) || 3.85) : 3.85;
  var displayName = nameEl ? nameEl.value : '';
  var geminiKey = keyEl ? keyEl.value : '';
  showToast('Saving changes to SQLite...', 'info');

  try {
    if (window.pywebview && window.pywebview.api) {
      var res = await window.pywebview.api.save_settings({
        target_cgpa: targetCgpa,
        display_name: displayName,
        gemini_api_key: geminiKey
      });
      if (res && res.success) {
        showToast('Profile & preferences saved successfully!', 'success');
        if (activeStudentData) activeStudentData.target_cgpa = targetCgpa;
      } else {
        showToast('Save failed: ' + (res.error || 'Error'), 'danger');
      }
    } else {
      showToast('Settings saved locally.', 'success');
    }
  } catch (err) {
    showToast('Save error: ' + err, 'danger');
  }
}

var aiReplies = [
  'Based on your current 3.22 CGPA and 24 completed credits, you need approximately a 3.47 average in remaining semesters to reach Magna Cum Laude (3.75+). Focus on your CSE core courses for maximum grade weight.',
  'For next semester, I recommend prioritizing Data Structures & Algorithms (CSE201) — it is foundational and heavily weighted. Also consider Discrete Mathematics to strengthen logical reasoning.',
  'Your attendance record looks strong at 87.5% overall. Ensure MAT101 attendance improves above 75% threshold to safeguard marks.',
  'To improve your CGPA efficiently: (1) Focus on 3-4 credit courses for maximum impact, (2) Target A or A- in core CSE subjects, (3) Use professor office hours.'
];
var replyIdx = 0;

function escapeHtml(text) {
  var div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

function formatMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/•/g, '&bull;');
}

function sendPromptMsg(text) {
  var input = document.getElementById('chat-input');
  if (input) input.value = text;
  sendChatMsg();
}

async function sendChatMsg() {
  var input = document.getElementById('chat-input');
  if (!input) return;
  var msg = input.value.trim();
  if (!msg) return;
  var box = document.getElementById('chat-box');
  if (!box) return;

  box.innerHTML += '<div class="msg user"><div class="msg-ava">' + currentUserInitials + '</div><div class="msg-bubble">' + escapeHtml(msg) + '</div></div>';
  input.value = '';
  box.scrollTop = box.scrollHeight;

  var thinkId = 'think-' + Date.now();
  box.innerHTML += '<div class="msg ai" id="' + thinkId + '"><div class="msg-ava">AI</div><div class="msg-bubble" style="opacity:0.7;"><em>Analyzing your BUBT CSE records...</em></div></div>';
  box.scrollTop = box.scrollHeight;

  try {
    var reply = '';
    if (window.pywebview && window.pywebview.api) {
      reply = await window.pywebview.api.ask_ai_advisor(msg, currentUserId);
    } else {
      reply = aiReplies[replyIdx % aiReplies.length];
      replyIdx++;
    }
    var thinkEl = document.getElementById(thinkId);
    if (thinkEl) {
      thinkEl.querySelector('.msg-bubble').innerHTML = formatMarkdown(reply);
      thinkEl.querySelector('.msg-bubble').style.opacity = '1';
    }
  } catch (err) {
    var thinkEl = document.getElementById(thinkId);
    if (thinkEl) {
      thinkEl.querySelector('.msg-bubble').textContent = 'Advisor unavailable: ' + err;
    }
  }
  box.scrollTop = box.scrollHeight;
}

window.addEventListener('pywebviewready', function() {
  console.log('PyWebView bridge initialized and ready.');
});

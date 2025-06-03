function startModule(mod) { fetch('/start/' + mod).then(() => {}); }
function stopModule(mod) { fetch('/stop/' + mod).then(() => {}); }

function updateStatsAndCharts() {
  fetch('/stats').then(r => r.json()).then(data => {
    document.getElementById("stat-attacks").textContent = data.attacks;
    document.getElementById("stat-success").textContent = data.success;
    document.getElementById("stat-blocked").textContent = data.blocked;
    document.getElementById("stat-emails").textContent = data.emails_sent;
    document.getElementById("stat-most-email").textContent = data.most_targeted_email;
    document.getElementById("stat-most-pwd").textContent = data.most_used_pwd;
    document.getElementById("stat-most-ip").textContent = data.most_aggressive_ip;
    document.getElementById("stat-most-ip-geo").textContent = data.geoip_country + ", " + data.geoip_city;
    document.getElementById("stat-last-hour").textContent = data.total_last_hour;

    // Recent Attacks
    let tbody = document.getElementById("attack-table");
    tbody.innerHTML = "";
    data.recent.forEach(row => {
      let tr = `<tr>
        <td>${row.time}</td><td>${row.user}</td><td>${row.ip}</td><td>${row.pwd||""}</td>
        <td><span class="badge ${row.status === 'SUCCESS' ? 'bg-success' : (row.status === 'BLOCKED' ? 'bg-secondary' : 'bg-danger')}">${row.status}</span></td>
      </tr>`;
      tbody.innerHTML += tr;
    });

    // --- Custom Chart Logic ---
    // 1. Attempts Over Time (Bar Chart): Show all attempts per hour (BLOCKED, SUCCESS, FAIL)
    const allAttemptsPerHour = Array(24).fill(0);
    if (Array.isArray(data.recent)) {
      data.recent.forEach(row => {
        const hour = parseInt(row.time.split(':')[0], 10);
        if (!isNaN(hour)) allAttemptsPerHour[hour]++;
      });
    }
    if (!window.hourChart) {
      window.hourChart = new Chart(document.getElementById('hourChart'), {
        type: 'bar',
        data: {
          labels: Array.from({length:24},(_,i)=>i+":00"),
          datasets: [{
            data: allAttemptsPerHour,
            label: 'Attempts/Hour',
            backgroundColor: '#6366f1',
            borderRadius: 6,
          }]
        },
        options: {
          animation: { duration: 600, easing: 'easeOutQuart' },
          plugins: { legend: { display: false }},
          scales: {
            x: { grid: { display: false }},
            y: { grid: { color: "#e3e7ed" }, beginAtZero: true }
          }
        }
      });
    } else if (
      window.hourChart &&
      window.hourChart.data &&
      window.hourChart.data.datasets &&
      window.hourChart.data.datasets[0]
    ) {
      window.hourChart.data.datasets[0].data = allAttemptsPerHour;
      window.hourChart.update();
    } else {
      if (window.hourChart && typeof window.hourChart.destroy === 'function') window.hourChart.destroy();
      window.hourChart = new Chart(document.getElementById('hourChart'), {
        type: 'bar',
        data: {
          labels: Array.from({length:24},(_,i)=>i+":00"),
          datasets: [{
            data: allAttemptsPerHour,
            label: 'Attempts/Hour',
            backgroundColor: '#6366f1',
            borderRadius: 6,
          }]
        },
        options: {
          animation: { duration: 600, easing: 'easeOutQuart' },
          plugins: { legend: { display: false }},
          scales: {
            x: { grid: { display: false }},
            y: { grid: { color: "#e3e7ed" }, beginAtZero: true }
          }
        }
      });
    }

    // 2. IP Distribution Horizontal Bar: Show top 10 IPs by number of attempts (all statuses)
    let ipCountMap = {};
    if (Array.isArray(data.recent)) {
      data.recent.forEach(row => {
        ipCountMap[row.ip] = (ipCountMap[row.ip] || 0) + 1;
      });
    }
    const sortedIPs = Object.entries(ipCountMap).sort((a,b)=>b[1]-a[1]).slice(0,10);
    const ipLabels = sortedIPs.length ? sortedIPs.map(i=>i[0]) : [];
    const ipCounts = sortedIPs.length ? sortedIPs.map(i=>i[1]) : [];
    if (!window.ipPie) {
      window.ipPie = new Chart(document.getElementById('ipPie'), {
        type:'bar',
        data:{
          labels: ipLabels,
          datasets:[{
            data: ipCounts,
            backgroundColor:["#7c3aed","#f59e42","#f56565","#4299e1","#ecc94b","#34d399","#ef4444","#f9fafb","#6366f1","#fbbf24"]
          }]
        },
        options: {
          indexAxis: 'y',
          animation: { duration: 600, easing: 'easeOutQuart' },
          plugins: {
            legend: { display: false },
            tooltip: { enabled: true },
            title: { display: true, text: 'Top 10 IPs by Attempts', font: { size: 18 } },
            datalabels: {
              anchor: 'end',
              align: 'right',
              color: '#222',
              font: { weight: 'bold', size: 14 },
              formatter: function(value) { return value; }
            }
          },
          scales: {
            x: { beginAtZero: true, grid: { color: "#e3e7ed" }, title: { display: true, text: 'Attempts', font: { size: 14 } } },
            y: { grid: { display: false }, title: { display: true, text: 'IP Address', font: { size: 14 } } }
          }
        },
        plugins: window.ChartDataLabels ? [ChartDataLabels] : []
      });
    } else if (
      window.ipPie &&
      window.ipPie.data &&
      window.ipPie.data.datasets &&
      window.ipPie.data.datasets[0]
    ) {
      window.ipPie.data.labels = ipLabels;
      window.ipPie.data.datasets[0].data = ipCounts;
      window.ipPie.update();
    } else {
      if (window.ipPie && typeof window.ipPie.destroy === 'function') window.ipPie.destroy();
      window.ipPie = new Chart(document.getElementById('ipPie'), {
        type:'bar',
        data:{
          labels: ipLabels,
          datasets:[{
            data: ipCounts,
            backgroundColor:["#7c3aed","#f59e42","#f56565","#4299e1","#ecc94b","#34d399","#ef4444","#f9fafb","#6366f1","#fbbf24"]
          }]
        },
        options: {
          indexAxis: 'y',
          animation: { duration: 600, easing: 'easeOutQuart' },
          plugins: {
            legend: { display: false },
            tooltip: { enabled: true },
            title: { display: true, text: 'Top 10 IPs by Attempts', font: { size: 18 } },
            datalabels: {
              anchor: 'end',
              align: 'right',
              color: '#222',
              font: { weight: 'bold', size: 14 },
              formatter: function(value) { return value; }
            }
          },
          scales: {
            x: { beginAtZero: true, grid: { color: "#e3e7ed" }, title: { display: true, text: 'Attempts', font: { size: 14 } } },
            y: { grid: { display: false }, title: { display: true, text: 'IP Address', font: { size: 14 } } }
          }
        },
        plugins: window.ChartDataLabels ? [ChartDataLabels] : []
      });
    }
    // If no data, show a message
    if (ipLabels.length === 0) {
      document.getElementById('ipPie').parentNode.querySelector('.nodata-msg')?.remove();
      const msg = document.createElement('div');
      msg.className = 'nodata-msg';
      msg.style = 'text-align:center;color:#888;margin-top:-30px;';
      msg.textContent = 'No IP data available.';
      document.getElementById('ipPie').parentNode.appendChild(msg);
    } else {
      document.getElementById('ipPie').parentNode.querySelector('.nodata-msg')?.remove();
    }

    // 3. Attack Trends Donut: Show count of BLOCKED, SUCCESS, FAIL
    let statusCounts = {BLOCKED:0, SUCCESS:0, FAIL:0};
    if (Array.isArray(data.recent)) {
      data.recent.forEach(row => {
        if (row.status in statusCounts) statusCounts[row.status]++;
      });
    }
    const trendLabels = ["BLOCKED", "SUCCESS", "FAIL"];
    const trendCounts = trendLabels.map(l=>statusCounts[l]);
    if (!window.attackChart) {
      window.attackChart = new Chart(document.getElementById('attackChart'), {
        type: 'doughnut',
        data: {
          labels: trendLabels,
          datasets: [{
            data: trendCounts,
            backgroundColor: ['#6366f1','#22c55e','#ef4444']
          }]
        },
        options: {
          animation: { duration: 600, easing: 'easeOutQuart' },
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      });
    } else if (
      window.attackChart &&
      window.attackChart.data &&
      window.attackChart.data.datasets &&
      window.attackChart.data.datasets[0]
    ) {
      window.attackChart.data.labels = trendLabels;
      window.attackChart.data.datasets[0].data = trendCounts;
      window.attackChart.update();
    } else {
      if (window.attackChart && typeof window.attackChart.destroy === 'function') window.attackChart.destroy();
      window.attackChart = new Chart(document.getElementById('attackChart'), {
        type: 'doughnut',
        data: {
          labels: trendLabels,
          datasets: [{
            data: trendCounts,
            backgroundColor: ['#6366f1','#22c55e','#ef4444']
          }]
        },
        options: {
          animation: { duration: 600, easing: 'easeOutQuart' },
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      });
    }
  });
}

function fetchMailhogEmails() {
  fetch('/mailhog')
    .then(resp => resp.json())
    .then(data => {
      let table = document.getElementById('email-table');
      table.innerHTML = "";
      data.emails.forEach(msg => {
        let tr = `<tr>
          <td>${msg.time}</td>
          <td>${msg.to}</td>
          <td>${msg.subject}</td>
        </tr>`;
        table.innerHTML += tr;
      });
    });
}
function addWhitelistIP() {
  const ip = prompt('Enter IP to whitelist:');
  if (ip) {
    fetch('/add_whitelist_ip', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ip})
    }).then(()=>refreshBlocked());
  }
}
function removeWhitelistIP(ip) {
  if (!confirm('Remove IP from whitelist?')) return;
  fetch('/remove_whitelist_ip', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ip})
  }).then(()=>refreshBlocked());
}
function refreshBlocked() {
  fetch('/blocked').then(r => r.json()).then(data => {
    let ul = document.getElementById('blocked-list');
    ul.innerHTML = "";
    data.blocked.forEach(item => {
      let li = document.createElement('li');
      li.className = "list-group-item d-flex justify-content-between align-items-center";
      li.textContent = item;
      let btn = document.createElement('button');
      btn.className = "btn btn-sm btn-outline-success";
      btn.textContent = "Unblock";
      btn.onclick = () => fetch('/unblock?user=' + encodeURIComponent(item)).then(refreshBlocked);
      li.appendChild(btn);
      ul.appendChild(li);
    });
  });
  fetch('/whitelist').then(r=>r.json()).then(data=>{
    let ul = document.getElementById('whitelist-list');
    ul.innerHTML = "";
    data.whitelist.forEach(item=>{
      let li = document.createElement('li');
      li.className = "list-group-item d-flex justify-content-between align-items-center";
      li.textContent = item;
      let btn = document.createElement('button');
      btn.className = "btn btn-sm btn-outline-danger ms-2";
      btn.textContent = "Remove";
      btn.onclick = () => removeWhitelistIP(item);
      li.appendChild(btn);
      ul.appendChild(li);
    });
    // Remove the add button from here (was previously appended per refresh)
  });
}
function refreshUsers() {
  fetch('/users').then(r => r.json()).then(data => {
    let ul = document.getElementById('users-list');
    ul.innerHTML = "";
    data.users.forEach(user => {
      let li = document.createElement('li');
      li.className = "list-group-item d-flex justify-content-between align-items-center";
      li.textContent = user;
      let btn = document.createElement('button');
      btn.className = "btn btn-sm btn-outline-danger";
      btn.textContent = "Block";
      btn.onclick = () => blockUser(user);
      li.appendChild(btn);
      ul.appendChild(li);
    });
  });
}
function blockUser(user) {
  fetch('/block_user', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({user})
  }).then(()=>{refreshBlocked();});
}
function refreshPasswords() {
  fetch('/passwords').then(r => r.json()).then(data => {
    let ul = document.getElementById('passwords-list');
    ul.innerHTML = "";
    data.passwords.forEach(pwd => {
      let li = document.createElement('li');
      li.className = "list-group-item";
      li.textContent = pwd;
      ul.appendChild(li);
    });
  });
}
document.getElementById('addUserForm').onsubmit = function(e) {
  e.preventDefault();
  fetch('/add_user', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      username: e.target.username.value,
      password: e.target.password.value
    })
  }).then(()=>{refreshUsers();});
};
document.getElementById('addPasswordForm').onsubmit = function(e) {
  e.preventDefault();
  fetch('/add_password', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({password: e.target.password.value})
  }).then(()=>{refreshPasswords();});
};
function setAttackSpeed() {
  fetch('/set_attack_speed', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({speed:document.getElementById('attackSpeed').value})
  });
}
document.getElementById('uploadListForm').onsubmit = function(e){
  e.preventDefault();
  const formData = new FormData(this);
  fetch('/upload_list', {method:'POST', body:formData}).then(()=>{});
};
function resetStats() {
  if (!confirm("Are you sure you want to reset all statistics?")) return;
  fetch('/reset_stats', {method: 'POST'}).then(r => r.json()).then(data => {
    if(data.status==="reset") {
      alert("Statistics reset.");
      updateStatsAndCharts();
      refreshBlocked();
    }
  });
}
function toggleDarkMode() {
  document.body.classList.toggle('dark');
  localStorage.setItem('darkmode', document.body.classList.contains('dark'));
}
document.getElementById('newPwd').oninput = function() {
  const val = this.value;
  let score = 0;
  if(val.length>=8) score++;
  if(/[A-Z]/.test(val)) score++;
  if(/[0-9]/.test(val)) score++;
  if(/[^A-Za-z0-9]/.test(val)) score++;
  let msg = ["Very Weak","Weak","Medium","Strong","Very Strong"];
  document.getElementById('pwdStrength').textContent = msg[score];
  document.getElementById('pwdStrength').style.color = ["#c00","#e90","#d9d900","#0c0","#090"][score];
};
setInterval(updateStatsAndCharts, 1500);
setInterval(fetchMailhogEmails, 2500);
setInterval(refreshBlocked, 4000);
setInterval(refreshUsers, 4000);
setInterval(refreshPasswords, 4000);

window.onload = function() {
  if(localStorage.getItem('darkmode')==='true') document.body.classList.add('dark');
  updateStatsAndCharts();
  fetchMailhogEmails();
  refreshBlocked();
  refreshUsers();
  refreshPasswords();
};

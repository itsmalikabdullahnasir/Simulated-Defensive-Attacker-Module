/**
 * CrackDefend Cybersecurity Dashboard
 * Advanced JavaScript Features & Functionality
 */

class CyberSecurityDashboard {
  constructor() {
    this.isInitialized = false;
    this.realTimeData = new Map();
    this.charts = new Map();
    this.notifications = [];
    this.filters = {
      timeRange: '24h',
      severity: 'all',
      status: 'all'
    };
    this.websocket = null;
    this.updateInterval = null;
    this.animationFrameId = null;
    
    this.init();
  }

  async init() {
    try {
      await this.setupEventListeners();
      await this.initializeCharts();
      await this.startRealTimeUpdates();
      await this.loadInitialData();
      this.setupKeyboardShortcuts();
      this.initializeAnimations();
      this.setupThemeToggle();
      this.initializeNotifications();
      this.setupDataExport();
      this.initializeSearch();
      this.setupPerformanceMonitoring();
      
      this.isInitialized = true;
      this.showNotification('Dashboard initialized successfully', 'success');
      console.log('🚀 CrackDefend Dashboard initialized');
    } catch (error) {
      console.error('❌ Dashboard initialization failed:', error);
      this.showNotification('Dashboard initialization failed', 'error');
    }
  }

  // ==================== REAL-TIME DATA MANAGEMENT ====================
  
  async startRealTimeUpdates() {
    // Simulate WebSocket connection for real-time data
    this.websocket = {
      connected: true,
      send: (data) => console.log('📡 Sending:', data),
      close: () => console.log('🔌 WebSocket closed')
    };

    // Update data every 5 seconds
    this.updateInterval = setInterval(() => {
      this.updateRealTimeData();
    }, 5000);

    // Initial data load
    this.updateRealTimeData();
  }

  updateRealTimeData() {
    const timestamp = new Date().toISOString();
    
    // Generate realistic cybersecurity metrics
    const newData = {
      timestamp,
      threats: {
        blocked: Math.floor(Math.random() * 50) + 150,
        detected: Math.floor(Math.random() * 30) + 80,
        quarantined: Math.floor(Math.random() * 20) + 45
      },
      network: {
        bandwidth: Math.floor(Math.random() * 100) + 200,
        connections: Math.floor(Math.random() * 500) + 1200,
        latency: Math.floor(Math.random() * 50) + 10
      },
      system: {
        cpu: Math.floor(Math.random() * 40) + 30,
        memory: Math.floor(Math.random() * 30) + 50,
        disk: Math.floor(Math.random() * 20) + 60
      },
      security: {
        score: Math.floor(Math.random() * 20) + 80,
        vulnerabilities: Math.floor(Math.random() * 10) + 5,
        patches: Math.floor(Math.random() * 5) + 15
      }
    };

    this.realTimeData.set(timestamp, newData);
    this.updateDashboardElements(newData);
    this.updateCharts(newData);
    this.checkAlerts(newData);
  }

  updateDashboardElements(data) {
    // Update stat cards with smooth animations
    this.animateValue('threats-blocked', data.threats.blocked);
    this.animateValue('threats-detected', data.threats.detected);
    this.animateValue('threats-quarantined', data.threats.quarantined);
    this.animateValue('network-bandwidth', data.network.bandwidth);
    this.animateValue('active-connections', data.network.connections);
    this.animateValue('system-health', data.security.score);
    
    // Update progress bars
    this.updateProgressBar('cpu-usage', data.system.cpu);
    this.updateProgressBar('memory-usage', data.system.memory);
    this.updateProgressBar('disk-usage', data.system.disk);
    
    // Update status indicators
    this.updateStatusIndicator('system-status', data.security.score);
    this.updateNetworkMap(data.network);
  }

  animateValue(elementId, targetValue, duration = 1000) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const startValue = parseInt(element.textContent) || 0;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for smooth animation
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutCubic);
      
      element.textContent = currentValue.toLocaleString();
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }

  updateProgressBar(elementId, percentage) {
    const progressBar = document.querySelector(`#${elementId} .progress-fill`);
    const percentageText = document.querySelector(`#${elementId} .percentage`);
    
    if (progressBar && percentageText) {
      progressBar.style.width = `${percentage}%`;
      percentageText.textContent = `${percentage}%`;
      
      // Color coding based on percentage
      progressBar.className = 'progress-fill';
      if (percentage > 80) progressBar.classList.add('danger');
      else if (percentage > 60) progressBar.classList.add('warning');
      else progressBar.classList.add('success');
    }
  }

  updateStatusIndicator(elementId, score) {
    const indicator = document.getElementById(elementId);
    if (!indicator) return;

    indicator.className = 'status-indicator';
    if (score >= 80) {
      indicator.classList.add('status-good');
      indicator.textContent = 'SECURE';
    } else if (score >= 60) {
      indicator.classList.add('status-warning');
      indicator.textContent = 'CAUTION';
    } else {
      indicator.classList.add('status-danger');
      indicator.textContent = 'ALERT';
    }
  }

  // ==================== INTERACTIVE CHARTS ====================
  
  async initializeCharts() {
    // Threat Timeline Chart
    this.charts.set('threat-timeline', this.createThreatTimelineChart());
    
    // Network Activity Chart
    this.charts.set('network-activity', this.createNetworkActivityChart());
    
    // Security Score Gauge
    this.charts.set('security-gauge', this.createSecurityGaugeChart());
    
    // Geographic Threat Map
    this.charts.set('geo-threats', this.createGeographicThreatMap());
    
    // System Performance Chart
    this.charts.set('system-performance', this.createSystemPerformanceChart());
  }

  createThreatTimelineChart() {
    const canvas = document.getElementById('threat-timeline-chart');
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(0, 255, 136, 0.3)');
    gradient.addColorStop(1, 'rgba(0, 255, 136, 0.05)');

    return {
      canvas,
      ctx,
      data: [],
      draw: function() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid
        this.drawGrid();
        
        // Draw threat data
        this.drawThreatLine();
        
        // Draw glow effect
        this.drawGlowEffect();
      },
      
      drawGrid: function() {
        this.ctx.strokeStyle = 'rgba(0, 255, 136, 0.1)';
        this.ctx.lineWidth = 1;
        
        // Vertical lines
        for (let i = 0; i <= 10; i++) {
          const x = (this.canvas.width / 10) * i;
          this.ctx.beginPath();
          this.ctx.moveTo(x, 0);
          this.ctx.lineTo(x, this.canvas.height);
          this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let i = 0; i <= 5; i++) {
          const y = (this.canvas.height / 5) * i;
          this.ctx.beginPath();
          this.ctx.moveTo(0, y);
          this.ctx.lineTo(this.canvas.width, y);
          this.ctx.stroke();
        }
      },
      
      drawThreatLine: function() {
        if (this.data.length < 2) return;
        
        this.ctx.strokeStyle = '#00ff88';
        this.ctx.lineWidth = 3;
        this.ctx.shadowColor = '#00ff88';
        this.ctx.shadowBlur = 10;
        
        this.ctx.beginPath();
        this.data.forEach((point, index) => {
          const x = (this.canvas.width / (this.data.length - 1)) * index;
          const y = this.canvas.height - (point.value / 100) * this.canvas.height;
          
          if (index === 0) {
            this.ctx.moveTo(x, y);
          } else {
            this.ctx.lineTo(x, y);
          }
        });
        this.ctx.stroke();
        
        // Reset shadow
        this.ctx.shadowBlur = 0;
      },
      
      drawGlowEffect: function() {
        // Add pulsing glow effect
        const time = Date.now() * 0.005;
        const alpha = 0.3 + Math.sin(time) * 0.2;
        
        this.ctx.strokeStyle = `rgba(0, 255, 136, ${alpha})`;
        this.ctx.lineWidth = 6;
        this.ctx.shadowColor = '#00ff88';
        this.ctx.shadowBlur = 20;
        
        if (this.data.length >= 2) {
          this.ctx.beginPath();
          this.data.forEach((point, index) => {
            const x = (this.canvas.width / (this.data.length - 1)) * index;
            const y = this.canvas.height - (point.value / 100) * this.canvas.height;
            
            if (index === 0) {
              this.ctx.moveTo(x, y);
            } else {
              this.ctx.lineTo(x, y);
            }
          });
          this.ctx.stroke();
        }
        
        this.ctx.shadowBlur = 0;
      }
    };
  }

  createNetworkActivityChart() {
    return {
      element: document.getElementById('network-activity-chart'),
      data: {
        incoming: [],
        outgoing: [],
        blocked: []
      },
      
      update: function(newData) {
        // Add new data point
        const timestamp = Date.now();
        this.data.incoming.push({ time: timestamp, value: newData.incoming || 0 });
        this.data.outgoing.push({ time: timestamp, value: newData.outgoing || 0 });
        this.data.blocked.push({ time: timestamp, value: newData.blocked || 0 });
        
        // Keep only last 50 data points
        if (this.data.incoming.length > 50) {
          this.data.incoming.shift();
          this.data.outgoing.shift();
          this.data.blocked.shift();
        }
        
        this.render();
      },
      
      render: function() {
        if (!this.element) return;
        
        // Create SVG visualization
        const svg = this.createSVGChart();
        this.element.innerHTML = '';
        this.element.appendChild(svg);
      },
      
      createSVGChart: function() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '300');
        svg.setAttribute('viewBox', '0 0 800 300');
        
        // Add gradient definitions
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
        gradient.setAttribute('id', 'networkGradient');
        gradient.setAttribute('x1', '0%');
        gradient.setAttribute('y1', '0%');
        gradient.setAttribute('x2', '0%');
        gradient.setAttribute('y2', '100%');
        
        const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop1.setAttribute('offset', '0%');
        stop1.setAttribute('stop-color', '#00ff88');
        stop1.setAttribute('stop-opacity', '0.3');
        
        const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop2.setAttribute('offset', '100%');
        stop2.setAttribute('stop-color', '#00ff88');
        stop2.setAttribute('stop-opacity', '0.05');
        
        gradient.appendChild(stop1);
        gradient.appendChild(stop2);
        defs.appendChild(gradient);
        svg.appendChild(defs);
        
        return svg;
      }
    };
  }

  createSecurityGaugeChart() {
    return {
      element: document.getElementById('security-gauge'),
      value: 85,
      
      update: function(newValue) {
        this.value = newValue;
        this.render();
      },
      
      render: function() {
        if (!this.element) return;
        
        const svg = this.createGaugeSVG();
        this.element.innerHTML = '';
        this.element.appendChild(svg);
      },
      
      createGaugeSVG: function() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '200');
        svg.setAttribute('height', '200');
        svg.setAttribute('viewBox', '0 0 200 200');
        
        // Background circle
        const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        bgCircle.setAttribute('cx', '100');
        bgCircle.setAttribute('cy', '100');
        bgCircle.setAttribute('r', '80');
        bgCircle.setAttribute('fill', 'none');
        bgCircle.setAttribute('stroke', 'rgba(0, 255, 136, 0.2)');
        bgCircle.setAttribute('stroke-width', '10');
        
        // Progress circle
        const progressCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        progressCircle.setAttribute('cx', '100');
        progressCircle.setAttribute('cy', '100');
        progressCircle.setAttribute('r', '80');
        progressCircle.setAttribute('fill', 'none');
        progressCircle.setAttribute('stroke', '#00ff88');
        progressCircle.setAttribute('stroke-width', '10');
        progressCircle.setAttribute('stroke-linecap', 'round');
        
        const circumference = 2 * Math.PI * 80;
        const offset = circumference - (this.value / 100) * circumference;
        progressCircle.setAttribute('stroke-dasharray', circumference);
        progressCircle.setAttribute('stroke-dashoffset', offset);
        progressCircle.setAttribute('transform', 'rotate(-90 100 100)');
        
        // Add glow effect
        progressCircle.setAttribute('filter', 'drop-shadow(0 0 10px #00ff88)');
        
        // Center text
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', '100');
        text.setAttribute('y', '110');
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('fill', '#00ff88');
        text.setAttribute('font-size', '24');
        text.setAttribute('font-weight', 'bold');
        text.textContent = `${this.value}%`;
        
        svg.appendChild(bgCircle);
        svg.appendChild(progressCircle);
        svg.appendChild(text);
        
        return svg;
      }
    };
  }

  createGeographicThreatMap() {
    return {
      element: document.getElementById('geo-threat-map'),
      threats: [],
      
      addThreat: function(lat, lng, severity) {
        this.threats.push({ lat, lng, severity, timestamp: Date.now() });
        
        // Remove old threats (older than 5 minutes)
        const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
        this.threats = this.threats.filter(threat => threat.timestamp > fiveMinutesAgo);
        
        this.render();
      },
      
      render: function() {
        if (!this.element) return;
        
        // Create world map visualization
        this.element.innerHTML = this.createMapHTML();
        this.addThreatMarkers();
      },
      
      createMapHTML: function() {
        return `
          <div class="world-map">
            <div class="map-container">
              <svg viewBox="0 0 1000 500" class="world-svg">
                <!-- Simplified world map paths would go here -->
                <rect width="1000" height="500" fill="rgba(0, 255, 136, 0.05)" stroke="rgba(0, 255, 136, 0.2)"/>
                <text x="500" y="250" text-anchor="middle" fill="#00ff88" font-size="16">Global Threat Map</text>
              </svg>
            </div>
          </div>
        `;
      },
      
      addThreatMarkers: function() {
        const mapContainer = this.element.querySelector('.map-container');
        if (!mapContainer) return;
        
        this.threats.forEach(threat => {
          const marker = document.createElement('div');
          marker.className = `threat-marker severity-${threat.severity}`;
          marker.style.left = `${(threat.lng + 180) / 360 * 100}%`;
          marker.style.top = `${(90 - threat.lat) / 180 * 100}%`;
          
          // Add pulsing animation
          marker.style.animation = 'pulse 2s infinite';
          
          mapContainer.appendChild(marker);
        });
      }
    };
  }

  createSystemPerformanceChart() {
    return {
      element: document.getElementById('system-performance-chart'),
      data: {
        cpu: [],
        memory: [],
        network: []
      },
      
      update: function(systemData) {
        const timestamp = Date.now();
        
        this.data.cpu.push({ time: timestamp, value: systemData.cpu });
        this.data.memory.push({ time: timestamp, value: systemData.memory });
        this.data.network.push({ time: timestamp, value: systemData.network });
        
        // Keep only last 30 data points
        Object.keys(this.data).forEach(key => {
          if (this.data[key].length > 30) {
            this.data[key].shift();
          }
        });
        
        this.render();
      },
      
      render: function() {
        if (!this.element) return;
        
        // Create multi-line chart
        const canvas = this.element.querySelector('canvas') || document.createElement('canvas');
        canvas.width = 400;
        canvas.height = 200;
        
        if (!this.element.querySelector('canvas')) {
          this.element.appendChild(canvas);
        }
        
        const ctx = canvas.getContext('2d');
        this.drawPerformanceChart(ctx, canvas.width, canvas.height);
      },
      
      drawPerformanceChart: function(ctx, width, height) {
        ctx.clearRect(0, 0, width, height);
        
        // Draw grid
        ctx.strokeStyle = 'rgba(0, 255, 136, 0.1)';
        ctx.lineWidth = 1;
        
        for (let i = 0; i <= 10; i++) {
          const x = (width / 10) * i;
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, height);
          ctx.stroke();
        }
        
        for (let i = 0; i <= 5; i++) {
          const y = (height / 5) * i;
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(width, y);
          ctx.stroke();
        }
        
        // Draw performance lines
        this.drawLine(ctx, this.data.cpu, width, height, '#00ff88', 'CPU');
        this.drawLine(ctx, this.data.memory, width, height, '#00ccff', 'Memory');
        this.drawLine(ctx, this.data.network, width, height, '#aa66ff', 'Network');
      },
      
      drawLine: function(ctx, data, width, height, color, label) {
        if (data.length < 2) return;
        
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.shadowColor = color;
        ctx.shadowBlur = 5;
        
        ctx.beginPath();
        data.forEach((point, index) => {
          const x = (width / (data.length - 1)) * index;
          const y = height - (point.value / 100) * height;
          
          if (index === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        ctx.stroke();
        
        ctx.shadowBlur = 0;
      }
    };
  }

  updateCharts(data) {
    // Update threat timeline
    const threatChart = this.charts.get('threat-timeline');
    if (threatChart) {
      threatChart.data.push({
        timestamp: Date.now(),
        value: data.threats.blocked + data.threats.detected
      });
      
      if (threatChart.data.length > 50) {
        threatChart.data.shift();
      }
      
      threatChart.draw();
    }

    // Update network activity
    const networkChart = this.charts.get('network-activity');
    if (networkChart) {
      networkChart.update({
        incoming: data.network.bandwidth * 0.6,
        outgoing: data.network.bandwidth * 0.4,
        blocked: data.threats.blocked
      });
    }

    // Update security gauge
    const securityGauge = this.charts.get('security-gauge');
    if (securityGauge) {
      securityGauge.update(data.security.score);
    }

    // Update system performance
    const performanceChart = this.charts.get('system-performance');
    if (performanceChart) {
      performanceChart.update({
        cpu: data.system.cpu,
        memory: data.system.memory,
        network: data.network.latency
      });
    }

    // Add random geographic threats
    const geoMap = this.charts.get('geo-threats');
    if (geoMap && Math.random() < 0.3) {
      const lat = (Math.random() - 0.5) * 180;
      const lng = (Math.random() - 0.5) * 360;
      const severity = Math.floor(Math.random() * 3) + 1;
      geoMap.addThreat(lat, lng, severity);
    }
  }

  // ==================== ALERT SYSTEM ====================
  
  checkAlerts(data) {
    const alerts = [];
    
    // High threat detection
    if (data.threats.detected > 100) {
      alerts.push({
        type: 'danger',
        title: 'High Threat Activity',
        message: `${data.threats.detected} threats detected in the last update`,
        timestamp: new Date().toISOString()
      });
    }
    
    // System performance alerts
    if (data.system.cpu > 90) {
      alerts.push({
        type: 'warning',
        title: 'High CPU Usage',
        message: `CPU usage at ${data.system.cpu}%`,
        timestamp: new Date().toISOString()
      });
    }
    
    if (data.system.memory > 85) {
      alerts.push({
        type: 'warning',
        title: 'High Memory Usage',
        message: `Memory usage at ${data.system.memory}%`,
        timestamp: new Date().toISOString()
      });
    }
    
    // Security score alerts
    if (data.security.score < 70) {
      alerts.push({
        type: 'danger',
        title: 'Security Score Low',
        message: `Security score dropped to ${data.security.score}%`,
        timestamp: new Date().toISOString()
      });
    }
    
    // Network alerts
    if (data.network.connections > 2000) {
      alerts.push({
        type: 'info',
        title: 'High Network Activity',
        message: `${data.network.connections} active connections`,
        timestamp: new Date().toISOString()
      });
    }
    
    alerts.forEach(alert => this.showNotification(alert.message, alert.type, alert.title));
  }

  // ==================== NOTIFICATION SYSTEM ====================
  
  initializeNotifications() {
    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
      const container = document.createElement('div');
      container.id = 'notification-container';
      container.className = 'notification-container';
      document.body.appendChild(container);
    }
  }

  showNotification(message, type = 'info', title = null, duration = 5000) {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    notification.id = id;
    
    notification.innerHTML = `
      <div class="notification-content">
        ${title ? `<div class="notification-title">${title}</div>` : ''}
        <div class="notification-message">${message}</div>
        <div class="notification-timestamp">${new Date().toLocaleTimeString()}</div>
      </div>
      <button class="notification-close" onclick="dashboard.closeNotification('${id}')">×</button>
    `;
    
    // Add to notifications array
    this.notifications.unshift({
      id,
      message,
      type,
      title,
      timestamp: new Date().toISOString()
    });
    
    // Keep only last 50 notifications
    if (this.notifications.length > 50) {
      this.notifications = this.notifications.slice(0, 50);
    }
    
    container.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Auto remove
    if (duration > 0) {
      setTimeout(() => this.closeNotification(id), duration);
    }
    
    // Update notification badge
    this.updateNotificationBadge();
  }

  closeNotification(id) {
    const notification = document.getElementById(id);
    if (notification) {
      notification.classList.add('hide');
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }
    
    // Remove from notifications array
    this.notifications = this.notifications.filter(n => n.id !== id);
    this.updateNotificationBadge();
  }

  updateNotificationBadge() {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
      const unreadCount = this.notifications.length;
      badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
      badge.style.display = unreadCount > 0 ? 'block' : 'none';
    }
  }

  // ==================== SEARCH & FILTERING ====================
  
  initializeSearch() {
    const searchInput = document.getElementById('dashboard-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.performSearch(e.target.value);
      });
    }
    
    // Initialize filter dropdowns
    const filterElements = document.querySelectorAll('.filter-dropdown');
    filterElements.forEach(filter => {
      filter.addEventListener('change', (e) => {
        this.updateFilter(e.target.name, e.target.value);
      });
    });
  }

  performSearch(query) {
    const searchResults = [];
    const lowerQuery = query.toLowerCase();
    
    // Search through notifications
    this.notifications.forEach(notification => {
      if (notification.message.toLowerCase().includes(lowerQuery) ||
          (notification.title && notification.title.toLowerCase().includes(lowerQuery))) {
        searchResults.push({
          type: 'notification',
          data: notification
        });
      }
    });
    
    // Search through real-time data
    this.realTimeData.forEach((data, timestamp) => {
      // Search logic for data entries
      if (timestamp.includes(lowerQuery)) {
        searchResults.push({
          type: 'data',
          data: { timestamp, ...data }
        });
      }
    });
    
    this.displaySearchResults(searchResults);
  }

  displaySearchResults(results) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    if (results.length === 0) {
      resultsContainer.innerHTML = '<div class="no-results">No results found</div>';
      return;
    }
    
    const resultsHTML = results.map(result => {
      if (result.type === 'notification') {
        return `
          <div class="search-result notification-result">
            <div class="result-type">Notification</div>
            <div class="result-title">${result.data.title || 'Alert'}</div>
            <div class="result-content">${result.data.message}</div>
            <div class="result-timestamp">${new Date(result.data.timestamp).toLocaleString()}</div>
          </div>
        `;
      } else if (result.type === 'data') {
        return `
          <div class="search-result data-result">
            <div class="result-type">Data Entry</div>
            <div class="result-title">System Data</div>
            <div class="result-content">Timestamp: ${result.data.timestamp}</div>
          </div>
        `;
      }
      return '';
    }).join('');
    
    resultsContainer.innerHTML = resultsHTML;
  }

  updateFilter(filterType, value) {
    this.filters[filterType] = value;
    this.applyFilters();
  }

  applyFilters() {
    // Apply filters to dashboard elements
    const cards = document.querySelectorAll('.stat-card, .table-row, .notification');
    
    cards.forEach(card => {
      let shouldShow = true;
      
      // Apply time range filter
      if (this.filters.timeRange !== 'all') {
        const timestamp = card.dataset.timestamp;
        if (timestamp) {
          const cardTime = new Date(timestamp);
          const now = new Date();
          const timeDiff = now - cardTime;
          
          switch (this.filters.timeRange) {
            case '1h':
              shouldShow = timeDiff <= 60 * 60 * 1000;
              break;
            case '24h':
              shouldShow = timeDiff <= 24 * 60 * 60 * 1000;
              break;
            case '7d':
              shouldShow = timeDiff <= 7 * 24 * 60 * 60 * 1000;
              break;
          }
        }
      }
      
      // Apply severity filter
      if (this.filters.severity !== 'all') {
        const severity = card.dataset.severity;
        shouldShow = shouldShow && (severity === this.filters.severity);
      }
      
      // Apply status filter
      if (this.filters.status !== 'all') {
        const status = card.dataset.status;
        shouldShow = shouldShow && (status === this.filters.status);
      }
      
      card.style.display = shouldShow ? '' : 'none';
    });
  }

  // ==================== DATA EXPORT ====================
  
  setupDataExport() {
    const exportBtn = document.getElementById('export-data-btn');
    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.showExportModal());
    }
  }

  showExportModal() {
    const modal = document.createElement('div');
    modal.className = 'export-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>Export Dashboard Data</h3>
          <button class="modal-close" onclick="this.closest('.export-modal').remove()">×</button>
        </div>
        <div class="modal-body">
          <div class="export-options">
            <label>
              <input type="checkbox" checked> Real-time Data
            </label>
            <label>
              <input type="checkbox" checked> Notifications
            </label>
            <label>
              <input type="checkbox" checked> System Metrics
            </label>
            <label>
              <input type="checkbox"> Chart Data
            </label>
          </div>
          <div class="export-format">
            <label>Export Format:</label>
            <select id="export-format">
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="xml">XML</option>
              <option value="pdf">PDF Report</option>
            </select>
          </div>
          <div class="date-range">
            <label>Date Range:</label>
            <input type="datetime-local" id="export-start">
            <input type="datetime-local" id="export-end">
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" onclick="this.closest('.export-modal').remove()">Cancel</button>
          <button class="btn btn-primary" onclick="dashboard.exportData()">Export</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('show'), 100);
  }

  exportData() {
    const format = document.getElementById('export-format').value;
    const startDate = document.getElementById('export-start').value;
    const endDate = document.getElementById('export-end').value;
    
    const exportData = {
      metadata: {
        exportDate: new Date().toISOString(),
        format,
        dateRange: { start: startDate, end: endDate },
        version: '1.0'
      },
      realTimeData: Array.from(this.realTimeData.entries()),
      notifications: this.notifications,
      systemMetrics: this.getSystemMetrics(),
      chartData: this.getChartData()
    };
    
    switch (format) {
      case 'json':
        this.downloadJSON(exportData);
        break;
      case 'csv':
        this.downloadCSV(exportData);
        break;
      case 'xml':
        this.downloadXML(exportData);
        break;
      case 'pdf':
        this.generatePDFReport(exportData);
        break;
    }
    
    // Close modal
    document.querySelector('.export-modal').remove();
    this.showNotification('Data export completed', 'success');
  }

  downloadJSON(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    this.downloadBlob(blob, `dashboard-export-${Date.now()}.json`);
  }

  downloadCSV(data) {
    let csv = 'Timestamp,Type,Value,Details\n';
    
    // Add real-time data
    data.realTimeData.forEach(([timestamp, values]) => {
      Object.entries(values).forEach(([category, categoryData]) => {
        if (typeof categoryData === 'object') {
          Object.entries(categoryData).forEach(([key, value]) => {
            csv += `${timestamp},${category}.${key},${value},Real-time data\n`;
          });
        }
      });
    });
    
    // Add notifications
    data.notifications.forEach(notification => {
      csv += `${notification.timestamp},notification,${notification.type},"${notification.message}"\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    this.downloadBlob(blob, `dashboard-export-${Date.now()}.csv`);
  }

  downloadXML(data) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<dashboard-export>\n';
    xml += `  <metadata>\n`;
    xml += `    <exportDate>${data.metadata.exportDate}</exportDate>\n`;
    xml += `    <format>${data.metadata.format}</format>\n`;
    xml += `  </metadata>\n`;
    
    xml += '  <realTimeData>\n';
    data.realTimeData.forEach(([timestamp, values]) => {
      xml += `    <entry timestamp="${timestamp}">\n`;
      Object.entries(values).forEach(([category, categoryData]) => {
        xml += `      <${category}>\n`;
        if (typeof categoryData === 'object') {
          Object.entries(categoryData).forEach(([key, value]) => {
            xml += `        <${key}>${value}</${key}>\n`;
          });
        }
        xml += `      </${category}>\n`;
      });
      xml += '    </entry>\n';
    });
    xml += '  </realTimeData>\n';
    
    xml += '</dashboard-export>';
    
    const blob = new Blob([xml], { type: 'application/xml' });
    this.downloadBlob(blob, `dashboard-export-${Date.now()}.xml`);
  }

  generatePDFReport(data) {
    // This would typically use a library like jsPDF
    // For now, we'll create a simple HTML report
    const reportHTML = this.generateHTMLReport(data);
    const blob = new Blob([reportHTML], { type: 'text/html' });
    this.downloadBlob(blob, `dashboard-report-${Date.now()}.html`);
  }

  generateHTMLReport(data) {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>CrackDefend Security Report</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { border-bottom: 2px solid #00ff88; padding-bottom: 10px; }
          .section { margin: 20px 0; }
          .metric { display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ccc; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>CrackDefend Security Dashboard Report</h1>
          <p>Generated: ${new Date().toLocaleString()}</p>
        </div>
        
        <div class="section">
          <h2>Summary</h2>
          <div class="metric">
            <strong>Total Notifications:</strong> ${data.notifications.length}
          </div>
          <div class="metric">
            <strong>Data Points:</strong> ${data.realTimeData.length}
          </div>
        </div>
        
        <div class="section">
          <h2>Recent Notifications</h2>
          ${data.notifications.slice(0, 10).map(n => `
            <div class="notification">
              <strong>${n.title || 'Alert'}</strong> - ${n.message}
              <br><small>${new Date(n.timestamp).toLocaleString()}</small>
            </div>
          `).join('')}
        </div>
      </body>
      </html>
    `;
  }

  downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  getSystemMetrics() {
    const latest = Array.from(this.realTimeData.values()).pop();
    return latest ? latest.system : {};
  }

  getChartData() {
    const chartData = {};
    this.charts.forEach((chart, name) => {
      if (chart.data) {
        chartData[name] = chart.data;
      }
    });
    return chartData;
  }

  // ==================== KEYBOARD SHORTCUTS ====================
  
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + combinations
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'r':
            e.preventDefault();
            this.refreshDashboard();
            break;
          case 'e':
            e.preventDefault();
            this.showExportModal();
            break;
          case 'f':
            e.preventDefault();
            document.getElementById('dashboard-search')?.focus();
            break;
          case 's':
            e.preventDefault();
            this.toggleSettings();
            break;
        }
      }
      
      // Function keys
      switch (e.key) {
        case 'F5':
          e.preventDefault();
          this.refreshDashboard();
          break;
        case 'Escape':
          this.closeAllModals();
          break;
      }
    });
  }

  refreshDashboard() {
    this.showNotification('Refreshing dashboard...', 'info');
    this.updateRealTimeData();
    this.showNotification('Dashboard refreshed', 'success');
  }

  toggleSettings() {
    const settingsPanel = document.getElementById('settings-panel');
    if (settingsPanel) {
      settingsPanel.classList.toggle('show');
    }
  }

  closeAllModals() {
    const modals = document.querySelectorAll('.modal, .export-modal');
    modals.forEach(modal => modal.remove());
  }

  // ==================== THEME & CUSTOMIZATION ====================
  
  setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => this.toggleTheme());
    }
  }

  toggleTheme() {
    const body = document.body;
    const currentTheme = body.classList.contains('light-theme') ? 'light' : 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.classList.toggle('light-theme', newTheme === 'light');
    localStorage.setItem('dashboard-theme', newTheme);
    
    this.showNotification(`Switched to ${newTheme} theme`, 'info');
  }

  // ==================== ANIMATIONS & EFFECTS ====================
  
  initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in-up');
        }
      });
    });

    // Observe all dashboard cards
    document.querySelectorAll('.stat-card, .chart-card, .table-card, .management-card').forEach(card => {
      observer.observe(card);
    });

    // Add typing effect to titles
    this.addTypingEffect();
    
    // Start matrix rain effect
    this.startMatrixRain();
  }

  addTypingEffect() {
    const titles = document.querySelectorAll('.typing-effect');
    titles.forEach(title => {
      const text = title.textContent;
      title.textContent = '';
      
      let i = 0;
      const typeInterval = setInterval(() => {
        title.textContent += text[i];
        i++;
        
        if (i >= text.length) {
          clearInterval(typeInterval);
          title.classList.add('typing-complete');
        }
      }, 100);
    });
  }

  startMatrixRain() {
    const matrixElements = document.querySelectorAll('.matrix-bg');
    matrixElements.forEach(element => {
      this.createMatrixRain(element);
    });
  }

  createMatrixRain(container) {
    const characters = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    const drops = [];
    const fontSize = 14;
    const columns = Math.floor(container.offsetWidth / fontSize);
    
    // Initialize drops
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * container.offsetHeight;
    }
    
    const canvas = document.createElement('canvas');
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.pointerEvents = 'none';
    canvas.style.opacity = '0.1';
    
    container.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    ctx.font = `${fontSize}px monospace`;
    ctx.fillStyle = '#00ff88';
    
    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#00ff88';
      
      for (let i = 0; i < drops.length; i++) {
        const text = characters[Math.floor(Math.random() * characters.length)];
        ctx.fillText(text, i * fontSize, drops[i]);
        
        if (drops[i] > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        
        drops[i] += fontSize;
      }
    };
    
    setInterval(draw, 100);
  }

  // ==================== PERFORMANCE MONITORING ====================
  
  setupPerformanceMonitoring() {
    // Monitor frame rate
    let lastTime = performance.now();
    let frameCount = 0;
    let fps = 0;
    
    const measureFPS = (currentTime) => {
      frameCount++;
      
      if (currentTime - lastTime >= 1000) {
        fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        frameCount = 0;
        lastTime = currentTime;
        
        // Update FPS display
        const fpsDisplay = document.getElementById('fps-counter');
        if (fpsDisplay) {
          fpsDisplay.textContent = `${fps} FPS`;
        }
      }
      
      requestAnimationFrame(measureFPS);
    };
    
    requestAnimationFrame(measureFPS);
    
    // Monitor memory usage (if available)
    if (performance.memory) {
      setInterval(() => {
        const memory = performance.memory;
        const memoryDisplay = document.getElementById('memory-usage');
        if (memoryDisplay) {
          const usedMB = Math.round(memory.usedJSHeapSize / 1048576);
          const totalMB = Math.round(memory.totalJSHeapSize / 1048576);
          memoryDisplay.textContent = `${usedMB}/${totalMB} MB`;
        }
      }, 5000);
    }
  }

  // ==================== UTILITY METHODS ====================
  
  async loadInitialData() {
    // Simulate loading initial data
    return new Promise((resolve) => {
      setTimeout(() => {
        this.showNotification('Initial data loaded', 'success');
        resolve();
      }, 1000);
    });
  }

  setupEventListeners() {
    // Window resize handler
    window.addEventListener('resize', () => {
      this.handleResize();
    });
    
    // Visibility change handler
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pauseUpdates();
      } else {
        this.resumeUpdates();
      }
    });
    
    // Before unload handler
    window.addEventListener('beforeunload', () => {
      this.cleanup();
    });
  }

  handleResize() {
    // Redraw charts on resize
    this.charts.forEach(chart => {
      if (chart.render) {
        chart.render();
      }
    });
  }

  pauseUpdates() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  resumeUpdates() {
    if (!this.updateInterval) {
      this.startRealTimeUpdates();
    }
  }

  cleanup() {
    // Clean up intervals and connections
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    
    if (this.websocket && this.websocket.close) {
      this.websocket.close();
    }
    
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }

  // ==================== API METHODS ====================
  
  // Public methods for external interaction
  addCustomNotification(message, type = 'info', title = null) {
    this.showNotification(message, type, title);
  }

  updateCustomMetric(metricId, value) {
    this.animateValue(metricId, value);
  }

  addCustomThreat(lat, lng, severity) {
    const geoMap = this.charts.get('geo-threats');
    if (geoMap) {
      geoMap.addThreat(lat, lng, severity);
    }
  }

  getNotifications() {
    return [...this.notifications];
  }

  getRealTimeData() {
    return new Map(this.realTimeData);
  }

  setUpdateInterval(interval) {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    
    this.updateInterval = setInterval(() => {
      this.updateRealTimeData();
    }, interval);
  }
}

// ==================== INITIALIZATION ====================

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.dashboard = new CyberSecurityDashboard();
});

// Add CSS for new features
const additionalCSS = `
/* Notification System */
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  max-width: 400px;
}

.notification {
  background: var(--bg-card);
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-3);
  padding: var(--space-4);
  box-shadow: var(--glow-green);
  transform: translateX(100%);
  transition: all var(--transition);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.notification.show {
  transform: translateX(0);
}

.notification.hide {
  transform: translateX(100%);
  opacity: 0;
}

.notification-danger {
  border-color: var(--cyber-red);
  box-shadow: var(--glow-red);
}

.notification-warning {
  border-color: var(--cyber-orange);
  box-shadow: var(--glow-orange);
}

.notification-success {
  border-color: var(--cyber-green);
  box-shadow: var(--glow-green);
}

.notification-info {
  border-color: var(--cyber-blue);
  box-shadow: var(--glow-blue);
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.notification-message {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.4;
}

.notification-timestamp {
  color: var(--text-dim);
  font-size: 0.8rem;
  margin-top: var(--space-1);
}

.notification-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  margin-left: var(--space-3);
  transition: color var(--transition);
}

.notification-close:hover {
  color: var(--text-primary);
}

/* Progress Bars */
.progress-container {
  background: var(--bg-surface);
  border-radius: var(--radius);
  height: 8px;
  overflow: hidden;
  margin: var(--space-2) 0;
}

.progress-fill {
  height: 100%;
  transition: width var(--transition);
  border-radius: var(--radius);
}

.progress-fill.success {
  background: linear-gradient(90deg, var(--cyber-green), var(--cyber-green-light));
}

.progress-fill.warning {
  background: linear-gradient(90deg, var(--cyber-orange), var(--cyber-orange-light));
}

.progress-fill.danger {
  background: linear-gradient(90deg, var(--cyber-red), var(--cyber-red-light));
}

/* Status Indicators */
.status-indicator {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: 2px solid;
}

.status-good {
  background: rgba(0, 255, 136, 0.2);
  color: var(--cyber-green);
  border-color: var(--cyber-green);
}

.status-warning {
  background: rgba(255, 136, 51, 0.2);
  color: var(--cyber-orange);
  border-color: var(--cyber-orange);
}

.status-danger {
  background: rgba(255, 68, 102, 0.2);
  color: var(--cyber-red);
  border-color: var(--cyber-red);
}

/* Export Modal */
.export-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  opacity: 0;
  transition: opacity var(--transition);
}

.export-modal.show {
  opacity: 1;
}

.modal-content {
  background: var(--bg-card);
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-xl);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--glow-green);
}

.modal-header {
  padding: var(--space-6);
  border-bottom: 2px solid var(--border-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-surface);
}

.modal-header h3 {
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
}

.modal-body {
  padding: var(--space-6);
}

.modal-footer {
  padding: var(--space-6);
  border-top: 2px solid var(--border-primary);
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
  background: var(--bg-surface);
}

.export-options label {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.export-format,
.date-range {
  margin-top: var(--space-4);
}

.export-format label,
.date-range label {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--text-secondary);
  font-weight: 600;
}

/* Threat Markers */
.threat-marker {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid;
  transform: translate(-50%, -50%);
}

.threat-marker.severity-1 {
  background: var(--cyber-green);
  border-color: var(--cyber-green);
  box-shadow: var(--glow-green);
}

.threat-marker.severity-2 {
  background: var(--cyber-orange);
  border-color: var(--cyber-orange);
  box-shadow: var(--glow-orange);
}

.threat-marker.severity-3 {
  background: var(--cyber-red);
  border-color: var(--cyber-red);
  box-shadow: var(--glow-red);
}

/* Search Results */
.search-result {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  margin-bottom: var(--space-3);
  transition: all var(--transition);
}

.search-result:hover {
  background: var(--bg-elevated);
  border-color: var(--border-accent);
  box-shadow: var(--glow-green);
}

.result-type {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: var(--space-1);
}

.result-title {
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: var(--space-1);
}

.result-content {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.4;
}

.result-timestamp {
  color: var(--text-dim);
  font-size: 0.8rem;
  margin-top: var(--space-2);
}

/* Performance Indicators */
.performance-indicator {
  position: fixed;
  bottom: 20px;
  left: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  font-size: 0.8rem;
  color: var(--text-muted);
  z-index: 1000;
}

/* Animations */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
}

@keyframes matrix-fall {
  0% {
    transform: translateY(-100%);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh);
    opacity: 0;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .notification-container {
    left: 20px;
    right: 20px;
    max-width: none;
  }
  
  .modal-content {
    width: 95%;
    margin: var(--space-4);
  }
  
  .performance-indicator {
    left: 10px;
    bottom: 10px;
    font-size: 0.7rem;
  }
}
`;

// Inject additional CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalCSS;
document.head.appendChild(styleSheet);

// Export for global access
window.CyberSecurityDashboard = CyberSecurityDashboard;

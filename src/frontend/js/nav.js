function renderTopNav() {
  const container = document.getElementById('topNav');
  if (!container) return;

  container.innerHTML = `
    <div class="top-nav">
      <a href="/">Home</a>
      <a href="/options">NIFTY Options</a>
    </div>
  `;
}

function renderOptionsTabs(activeTab) {
  const container = document.getElementById('optionsTabs');
  if (!container) return;

  const tabs = [
    { key: 'hub', label: 'Overview', href: '/options' },
    { key: 'chain', label: 'Option Chain', href: '/options/options-chain' },
    { key: 'playbook', label: 'Greeks-Based Playbook', href: '/options/options-playbook' },
    { key: 'greek-meter', label: 'Greek Risk Meter', href: '/options/greek-meter' },
    { key: 'learn', label: 'Options Lab', href: '/options/learn' },
  ];

  let html = '<div class="options-tabs">';
  tabs.forEach(tab => {
    const cls = tab.key === activeTab ? 'active' : '';
    html += `<a class="${cls}" href="${tab.href}">${tab.label}</a>`;
  });
  html += '</div>';

  container.innerHTML = html;
}

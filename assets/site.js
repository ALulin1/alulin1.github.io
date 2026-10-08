(() => {
  'use strict';
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.main-nav');
  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  });
  nav?.addEventListener('click', event => {
    if (event.target.closest('a')) {
      nav.classList.remove('is-open');
      toggle?.setAttribute('aria-expanded', 'false');
    }
  });

  const items = [...document.querySelectorAll('.publication-item')];
  const search = document.querySelector('#publication-search');
  const filterButtons = [...document.querySelectorAll('.filter-button')];
  const results = document.querySelector('.results-count');
  let category = 'all';
  const filterPublications = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    items.forEach(item => {
      const matchesCategory = category === 'all' || item.dataset.category === category;
      const matchesQuery = !query || item.textContent.toLocaleLowerCase().includes(query);
      item.hidden = !(matchesCategory && matchesQuery);
      if (!item.hidden) visible++;
    });
    document.querySelectorAll('.publication-year').forEach(group => {
      group.hidden = ![...group.querySelectorAll('.publication-item')].some(item => !item.hidden);
    });
    results.textContent = visible === items.length
      ? `All ${items.length} research outputs`
      : `${visible} of ${items.length} research outputs`;
    document.querySelector('.empty-state').hidden = visible !== 0;
  };
  if (items.length && search) {
    document.querySelector('.publications-controls').hidden = false;
    search.addEventListener('input', filterPublications);
    filterButtons.forEach(button => button.addEventListener('click', () => {
      category = button.dataset.filter;
      filterButtons.forEach(other => {
        const active = other === button;
        other.classList.toggle('is-active', active);
        other.setAttribute('aria-pressed', String(active));
      });
      filterPublications();
    }));
  }

  const citationData = document.querySelector('#citation-data');
  const citations = citationData ? JSON.parse(citationData.textContent) : {};
  const dialog = document.querySelector('.citation-dialog');
  const citationText = document.querySelector('#citation-text');
  const copyButton = document.querySelector('#copy-citation');
  let citationTrigger;
  document.querySelectorAll('.citation-button').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => {
      citationTrigger = button;
      citationText.textContent = citations[button.dataset.citation];
      copyButton.textContent = 'Copy BibTeX';
      document.querySelector('#copy-status').textContent = '';
      dialog.showModal();
    });
  });
  document.querySelector('#close-citation')?.addEventListener('click', () => dialog.close());
  dialog?.addEventListener('click', event => {
    const rect = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right
        || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
  });
  dialog?.addEventListener('close', () => citationTrigger?.focus());
  copyButton?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(citationText.textContent);
      copyButton.textContent = 'Copied';
      document.querySelector('#copy-status').textContent = 'Citation copied to clipboard.';
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(citationText);
      selection.removeAllRanges();
      selection.addRange(range);
      document.querySelector('#copy-status').textContent = 'Select and copy the citation text.';
    }
  });

  const topButton = document.querySelector('.back-to-top');
  if (topButton) {
    const update = () => { topButton.hidden = window.scrollY < 700; };
    window.addEventListener('scroll', update, { passive: true });
    topButton.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
      document.querySelector('.brand')?.focus({ preventScroll: true });
    });
    update();
  }
  document.querySelector('#print-cv')?.addEventListener('click', () => window.print());
})();

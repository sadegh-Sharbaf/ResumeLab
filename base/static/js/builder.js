(() => {
  'use strict';

  const toEnglishDigits = value => String(value || '')
    .replace(/[۰-۹]/g, digit => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(digit)))
    .replace(/[٠-٩]/g, digit => String('٠١٢٣٤٥٦٧٨٩'.indexOf(digit)));

  const pad = value => String(value).padStart(2, '0');
  const div = (a, b) => Math.trunc(a / b);
  const mod = (a, b) => a - Math.trunc(a / b) * b;

  // Gregorian/Jalali conversion based on the arithmetic Persian calendar.
  const breaks = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178];
  function jalCal(jy) {
    const bl = breaks.length;
    const gy = jy + 621;
    let leapJ = -14;
    let jp = breaks[0];
    let jump = 0;
    if (jy < jp || jy >= breaks[bl - 1]) throw new Error('Invalid Jalali year');
    for (let i = 1; i < bl; i += 1) {
      const jm = breaks[i];
      jump = jm - jp;
      if (jy < jm) break;
      leapJ += div(jump, 33) * 8 + div(mod(jump, 33), 4);
      jp = jm;
    }
    let n = jy - jp;
    leapJ += div(n, 33) * 8 + div(mod(n, 33) + 3, 4);
    if (mod(jump, 33) === 4 && jump - n === 4) leapJ += 1;
    const leapG = div(gy, 4) - div((div(gy, 100) + 1) * 3, 4) - 150;
    const march = 20 + leapJ - leapG;
    if (jump - n < 6) n = n - jump + div(jump + 4, 33) * 33;
    let leap = mod(mod(n + 1, 33) - 1, 4);
    if (leap === -1) leap = 4;
    return { leap, gy, march };
  }
  function g2d(gy, gm, gd) {
    let d = div((gy + div(gm - 8, 6) + 100100) * 1461, 4)
      + div(153 * mod(gm + 9, 12) + 2, 5) + gd - 34840408;
    d = d - div(div(gy + 100100 + div(gm - 8, 6), 100) * 3, 4) + 752;
    return d;
  }
  function d2g(jdn) {
    let j = 4 * jdn + 139361631;
    j = j + div(div(4 * jdn + 183187720, 146097) * 3, 4) * 4 - 3908;
    const i = div(mod(j, 1461), 4) * 5 + 308;
    const gd = div(mod(i, 153), 5) + 1;
    const gm = mod(div(i, 153), 12) + 1;
    const gy = div(j, 1461) - 100100 + div(8 - gm, 6);
    return { gy, gm, gd };
  }
  function j2d(jy, jm, jd) {
    const r = jalCal(jy);
    return g2d(r.gy, 3, r.march) + (jm - 1) * 31 - div(jm, 7) * (jm - 7) + jd - 1;
  }
  function d2j(jdn) {
    const g = d2g(jdn);
    let jy = g.gy - 621;
    const r = jalCal(jy);
    const jdn1f = g2d(g.gy, 3, r.march);
    let k = jdn - jdn1f;
    let jd;
    let jm;
    if (k >= 0) {
      if (k <= 185) {
        jm = 1 + div(k, 31);
        jd = mod(k, 31) + 1;
        return { jy, jm, jd };
      }
      k -= 186;
    } else {
      jy -= 1;
      k += 179;
      if (r.leap === 1) k += 1;
    }
    jm = 7 + div(k, 30);
    jd = mod(k, 30) + 1;
    return { jy, jm, jd };
  }
  const toGregorian = (jy, jm, jd) => d2g(j2d(jy, jm, jd));
  const toJalali = (gy, gm, gd) => d2j(g2d(gy, gm, gd));
  const isLeap = year => jalCal(year).leap === 0;
  const monthLength = (year, month) => month <= 6 ? 31 : month <= 11 ? 30 : (isLeap(year) ? 30 : 29);

  const monthNames = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'];
  const weekNames = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];

  let activeInput = null;
  let viewYear = 1400;
  let viewMonth = 1;

  const picker = document.createElement('div');
  picker.className = 'jalali-picker-backdrop';
  picker.hidden = true;
  picker.innerHTML = `
    <div class="jalali-picker" role="dialog" aria-modal="true" aria-label="انتخاب تاریخ شمسی">
      <div class="jalali-picker-head">
        <button type="button" data-jp-next aria-label="ماه بعد">‹</button>
        <strong data-jp-title></strong>
        <button type="button" data-jp-prev aria-label="ماه قبل">›</button>
      </div>
      <div class="jalali-weekdays">${weekNames.map(day => `<span>${day}</span>`).join('')}</div>
      <div class="jalali-days" data-jp-days></div>
      <div class="jalali-picker-actions">
        <button type="button" class="btn btn-small" data-jp-clear>پاک کردن</button>
        <button type="button" class="btn btn-small" data-jp-today>امروز</button>
        <button type="button" class="btn btn-small btn-primary" data-jp-close>بستن</button>
      </div>
    </div>`;
  document.body.appendChild(picker);

  const closePicker = () => {
    picker.hidden = true;
    activeInput = null;
    document.body.classList.remove('calendar-open');
  };

  const currentJalali = () => {
    const now = new Date();
    return toJalali(now.getFullYear(), now.getMonth() + 1, now.getDate());
  };

  function parseInput(input) {
    const match = toEnglishDigits(input.value).match(/^(\d{4})\/(\d{1,2})\/(\d{1,2})$/);
    if (!match) return currentJalali();
    return { jy: Number(match[1]), jm: Number(match[2]), jd: Number(match[3]) };
  }

  function renderPicker() {
    picker.querySelector('[data-jp-title]').textContent = `${monthNames[viewMonth - 1]} ${viewYear}`;
    const daysHolder = picker.querySelector('[data-jp-days]');
    daysHolder.innerHTML = '';
    const first = toGregorian(viewYear, viewMonth, 1);
    const firstWeekDay = (new Date(first.gy, first.gm - 1, first.gd).getDay() + 1) % 7;
    for (let i = 0; i < firstWeekDay; i += 1) {
      const blank = document.createElement('span');
      blank.className = 'jalali-day-empty';
      daysHolder.appendChild(blank);
    }
    const selected = activeInput ? parseInput(activeInput) : null;
    const today = currentJalali();
    for (let day = 1; day <= monthLength(viewYear, viewMonth); day += 1) {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = day.toLocaleString('fa-IR', { useGrouping: false });
      button.dataset.day = String(day);
      if (selected && selected.jy === viewYear && selected.jm === viewMonth && selected.jd === day) button.classList.add('selected');
      if (today.jy === viewYear && today.jm === viewMonth && today.jd === day) button.classList.add('today');
      daysHolder.appendChild(button);
    }
  }

  function openPicker(input) {
    if (input.disabled) return;
    activeInput = input;
    const parsed = parseInput(input);
    viewYear = parsed.jy;
    viewMonth = parsed.jm;
    renderPicker();
    picker.hidden = false;
    document.body.classList.add('calendar-open');
  }

  picker.addEventListener('click', event => {
    if (event.target === picker || event.target.closest('[data-jp-close]')) return closePicker();
    if (event.target.closest('[data-jp-prev]')) {
      viewMonth -= 1;
      if (viewMonth < 1) { viewMonth = 12; viewYear -= 1; }
      return renderPicker();
    }
    if (event.target.closest('[data-jp-next]')) {
      viewMonth += 1;
      if (viewMonth > 12) { viewMonth = 1; viewYear += 1; }
      return renderPicker();
    }
    if (event.target.closest('[data-jp-today]')) {
      const today = currentJalali();
      viewYear = today.jy;
      viewMonth = today.jm;
      renderPicker();
      return;
    }
    if (event.target.closest('[data-jp-clear]')) {
      if (activeInput) {
        activeInput.value = '';
        activeInput.dispatchEvent(new Event('change', { bubbles: true }));
      }
      return closePicker();
    }
    const dayButton = event.target.closest('[data-day]');
    if (dayButton && activeInput) {
      activeInput.value = `${viewYear}/${pad(viewMonth)}/${pad(dayButton.dataset.day)}`;
      activeInput.dispatchEvent(new Event('change', { bubbles: true }));
      closePicker();
    }
  });

  document.addEventListener('click', event => {
    const input = event.target.closest('[data-jalali-date]');
    if (input) openPicker(input);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !picker.hidden) closePicker();
  });

  function toggleCurrentEmployment(card, checkbox) {
    const endDate = card.querySelector('[data-end-date]');
    if (!endDate) return;
    if (checkbox.checked) {
      if (endDate.value) endDate.dataset.previousValue = endDate.value;
      endDate.value = '';
      endDate.disabled = true;
      endDate.setAttribute('aria-disabled', 'true');
      endDate.closest('.field')?.classList.add('field-disabled');
    } else {
      endDate.disabled = false;
      endDate.removeAttribute('aria-disabled');
      endDate.closest('.field')?.classList.remove('field-disabled');
      if (!endDate.value && endDate.dataset.previousValue) endDate.value = endDate.dataset.previousValue;
    }
  }

  function initialiseCard(card) {
    const current = card.querySelector('[data-current-toggle]');
    if (current) toggleCurrentEmployment(card, current);
  }

  document.addEventListener('change', event => {
    const current = event.target.closest('[data-current-toggle]');
    if (current) toggleCurrentEmployment(current.closest('[data-form-card]'), current);
  });

  document.querySelectorAll('[data-formset]').forEach(group => {
    const prefix = group.dataset.prefix;
    const list = group.querySelector('[data-form-list]');
    const total = group.querySelector(`#id_${prefix}-TOTAL_FORMS`);
    const template = group.querySelector('[data-empty-form]');

    const visibleCards = () => [...list.querySelectorAll('[data-form-card]')].filter(card => !card.classList.contains('is-deleted'));

    const updateLabels = () => {
      const cards = visibleCards();
      cards.forEach((card, index) => {
        const title = card.querySelector('[data-card-title]');
        if (title) title.textContent = `مورد ${index + 1}`;
      });
      let empty = list.querySelector('[data-empty-message]');
      if (!cards.length && !empty) {
        empty = document.createElement('div');
        empty.className = 'formset-empty';
        empty.dataset.emptyMessage = '';
        empty.textContent = 'هنوز موردی اضافه نشده است.';
        list.appendChild(empty);
      } else if (cards.length && empty) {
        empty.remove();
      }
    };

    const removeCard = card => {
      const deleteInput = card.querySelector('input[name$="-DELETE"]');
      if (!deleteInput) return;
      deleteInput.checked = true;
      card.classList.add('is-deleted');
      card.setAttribute('aria-hidden', 'true');
      card.querySelectorAll('input, textarea, select').forEach(field => {
        if (field !== deleteInput && !field.name.endsWith('-id')) {
          field.required = false;
          field.disabled = true;
        }
      });
      updateLabels();
    };

    list.addEventListener('click', event => {
      const button = event.target.closest('[data-remove-form]');
      if (button) removeCard(button.closest('[data-form-card]'));
    });

    group.querySelectorAll('[data-form-card]').forEach(initialiseCard);
    group.querySelector('[data-add-form]')?.addEventListener('click', () => {
      const index = Number(total.value);
      const html = template.innerHTML.replaceAll('__prefix__', String(index));
      const holder = document.createElement('div');
      holder.innerHTML = html.trim();
      const card = holder.firstElementChild;
      list.querySelector('[data-empty-message]')?.remove();
      list.appendChild(card);
      total.value = index + 1;
      initialiseCard(card);
      updateLabels();
      card.querySelector('input:not([type="hidden"]), textarea, select')?.focus();
    });

    updateLabels();
  });
})();

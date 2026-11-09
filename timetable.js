(() => {
  const rows = document.querySelector('#timetableRows');
  const status = document.querySelector('#timetableStatus');
  const dateFormat = new Intl.DateTimeFormat('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
    timeZone: 'Asia/Kolkata'
  });
  const timeFormat = new Intl.DateTimeFormat('en-IN', {
    hour: 'numeric', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata'
  });
  const formatTime = time => timeFormat.format(new Date('2000-01-01T' + time + ':00+05:30'));

  async function loadTimetable() {
    try {
      const response = await fetch('data/timetable-2027.json', {cache: 'no-store'});
      if (!response.ok) throw Error('Timetable unavailable');
      const timetable = await response.json();
      const fragment = document.createDocumentFragment();
      for (const exam of [...timetable.exams].sort((a, b) => a.date.localeCompare(b.date) || a.start.localeCompare(b.start))) {
        const row = document.createElement('tr');
        const subject = document.createElement('th');
        subject.scope = 'row';
        subject.textContent = exam.subject;
        const code = document.createElement('span');
        code.className = 'timetable-code';
        code.textContent = 'Subject code ' + exam.code;
        subject.append(code);
        row.append(subject);

        const date = document.createElement('td');
        const dateLabel = document.createElement('time');
        dateLabel.dateTime = exam.date;
        dateLabel.textContent = dateFormat.format(new Date(exam.date + 'T00:00:00+05:30'));
        date.append(dateLabel);
        row.append(date);

        const session = document.createElement('td');
        session.textContent = formatTime(exam.start) + ' – ' + formatTime(exam.end);
        row.append(session);

        const source = document.createElement('td');
        const link = document.createElement('a');
        link.href = timetable.document.pdf + '#page=' + exam.sourcePage;
        link.target = '_blank';
        link.rel = 'noopener';
        link.textContent = 'Page ' + exam.sourcePage + ' ↗';
        link.setAttribute('aria-label', exam.subject + ': original timetable page ' + exam.sourcePage);
        source.append(link);
        row.append(source);
        fragment.append(row);
      }
      rows.replaceChildren(fragment);
      status.textContent = 'Six written papers for the subjects in this app. All times are Indian Standard Time (IST, UTC+05:30).';
    } catch {
      status.textContent = 'The dates could not be loaded. Open the original PDF below to view the timetable.';
    }
  }
  loadTimetable();
})();

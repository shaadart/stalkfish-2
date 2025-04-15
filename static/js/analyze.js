let analysis = [], moveIndex = 0;

const tagMap = {
  'Brilliant': 'brilliant-move',
  'Great': 'great-move',
  'Best': 'best-move',
  'Excellent': 'excellent-move',
  'Good': 'good-move',
  'Inaccuracy': 'inaccuracy',
  'Mistake': 'mistake',
  'Blunder': 'blunder',
  'Miss': 'miss',
  'Book': 'book',
  'Opening': 'opening-move'
};

function showMove(i) {
  $('.annotation').remove();
  game.reset();
  for (let j = 0; j <= i; j++) game.move(analysis[j].san);
  board.position(game.fen());

  const a = analysis[i];
  $('#info').text(`Move ${i + 1}: ${a.san} | Eval: ${a.ep_after}`);

  $('#moves-list td').removeClass('selected');
  const col = (i % 2 === 0) ? 'white' : 'black';
  const rowIdx = Math.floor(i / 2);
  $(`#moves-list tr:eq(${rowIdx}) td.${col}`).addClass('selected');

  if (tagMap[a.tag]) {
    $('#better-move').show().html(`
      <h3>Better Move Recommendation</h3>
      <p>Recommended: <strong>${a.recommended || 'N/A'}</strong></p>
    `);
  } else {
    $('#better-move').hide();
  }

  const annotationClass = tagMap[a.tag] || 'undefined';
  const $square = $('.square-' + a.to);
  if ($square.length) {
    $square.append(`<div class="annotation ${annotationClass}"></div>`);
  }
}

function populateMovesTable() {
  const tbody = $('#moves-list').empty();
  for (let i = 0; i < analysis.length; i += 2) {
    const w = analysis[i];
    const b = analysis[i + 1];
    const $tr = $('<tr>');

    const whiteTagClass = tagMap[w.tag] || 'undefined';
    const $w = $('<td class="move-cell white">')
      .append(`<span class="san">${w.san}</span>`)
      .append(`<span class="annotation ${whiteTagClass}"></span>`)
      .append(`<span class="eval">(${w.ep_after})</span>`);

    const $b = $('<td class="move-cell black">');
    if (b) {
      const blackTagClass = tagMap[b.tag] || 'undefined';
      $b.append(`<span class="san">${b.san}</span>`)
        .append(`<span class="annotation ${blackTagClass}"></span>`)
        .append(`<span class="eval">(${b.ep_after})</span>`);
    }

    $tr.append($w, $b).appendTo(tbody);
  }

  // Click handlers
  $('#moves-list .move-cell.white').click(function () {
    const idx = $(this).parent().index() * 2;
    showMove(idx);
  });

  $('#moves-list .move-cell.black').click(function () {
    const idx = $(this).parent().index() * 2 + 1;
    if (analysis[idx]) showMove(idx);
  });
}

function calculateSummary() {
  const counts = {
    'Brilliant': 0,
    'Great': 0,
    'Best': 0,
    'Excellent': 0,
    'Good': 0,
    'Inaccuracy': 0,
    'Mistake': 0,
    'Blunder': 0
  };

  analysis.forEach(m => {
    if (counts[m.tag] !== undefined) counts[m.tag]++;
  });

  $('#brilliant-count').text(counts['Brilliant']);
  $('#great-count').text(counts['Great']);
  $('#best-count').text(counts['Best']);
  $('#excellent-count').text(counts['Excellent']);
  $('#good-count').text(counts['Good']);
  $('#inaccuracy-count').text(counts['Inaccuracy']);
  $('#mistake-count').text(counts['Mistake']);
  $('#blunder-count').text(counts['Blunder']);
}

$('#pgnForm').on('submit', function (e) {
  e.preventDefault();
  $.post('/analyze', $(this).serialize(), data => {
    if (data.error) return alert('Error: ' + data.error);
    analysis = data;
    moveIndex = 0;
    calculateSummary();
    $('#summary-screen').show();
    $('#container, #info, #better-move').hide();
  }, 'json').fail(xhr => {
    alert(`Analyze failed (HTTP ${xhr.status}):\n${xhr.responseJSON?.error || xhr.statusText}`);
  });
});

$('#start-review').click(() => {
  $('#summary-screen').hide();
  $('#container, #info').show();
  populateMovesTable();
  showMove(0);
});

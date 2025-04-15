// analyze.js
let analysis = [], moveIndex = 0;

function showMove(i) {
  // remove old annotations
  $('.annotation').remove();
  // reset & replay up to move i
  game.reset();
  for (let j = 0; j <= i; j++) game.move(analysis[j].san);
  board.position(game.fen());

  // update info bar
  const a = analysis[i];
  $('#info').text(`Move ${i+1}: ${a.san} | Eval: ${a.ep_after}`);

  // highlight current table cell
  $('#moves-list td').removeClass('selected');
  const col = (i % 2 === 0) ? 'white' : 'black';
  const rowIdx = Math.floor(i/2);
  $(`#moves-list tr:eq(${rowIdx}) td.${col}`)
    .addClass('selected');

  // better‑move panel
  if (['Inaccuracy','Mistake','Blunder','Miss','Excellent','Good'].includes(a.tag)) {
    $('#better-move').show().html(`
      <h3>Better Move Recommendation</h3>
      <p>Recommended: <strong>${a.recommended||'N/A'}</strong></p>
    `);
  } else {
    $('#better-move').hide();
  }

  // annotate the destination square
  const cls = a.tag.toLowerCase().replace(/ /g,'-');
  const sq  = $('.square-' + a.to);
  if (sq.length) sq.append(`<div class="annotation ${cls}"></div>`);
}

function populateMovesTable() {
  const tbody = $('#moves-list').empty();
  for (let i = 0; i < analysis.length; i += 2) {
    const w = analysis[i];
    const b = analysis[i+1];
    const $tr = $('<tr>');
    // White cell
    const $w = $('<td class="move-cell white">')
      .append(`<span class="san">${w.san}</span>`)
      .append(`<span class="annotation ${w.tag.toLowerCase().replace(/ /g,'-')}"></span>`)
      .append(`<span class="eval">(${w.ep_after})</span>`);
    // Black cell
    const $b = $('<td class="move-cell black">');
    if (b) {
      $b.append(`<span class="san">${b.san}</span>`)
        .append(`<span class="annotation ${b.tag.toLowerCase().replace(/ /g,'-')}"></span>`)
        .append(`<span class="eval">(${b.ep_after})</span>`);
    }
    $tr.append($w,$b).appendTo(tbody);
  }

  // click handlers
  $('#moves-list .move-cell.white').click(function(){
    const idx = $(this).parent().index()*2;
    showMove(idx);
  });
  $('#moves-list .move-cell.black').click(function(){
    const idx = $(this).parent().index()*2 + 1;
    if (analysis[idx]) showMove(idx);
  });
}

function calculateSummary() {
  const counts = {
    'Brilliant':0,'Great':0,'Best':0,'Excellent':0,
    'Good':0,'Inaccuracy':0,'Mistake':0,'Blunder':0
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

$('#pgnForm').on('submit', function(e){
  e.preventDefault();
  $.post('/analyze', $(this).serialize(), data => {
    if (data.error) return alert('Error: '+data.error);
    analysis = data; moveIndex = 0;
    calculateSummary();
    $('#summary-screen').show();
    $('#container, #info, #better-move').hide();
  }, 'json').fail(xhr => {
    alert(`Analyze failed (HTTP ${xhr.status}):\n${xhr.responseJSON?.error||xhr.statusText}`);
  });
});

$('#start-review').click(() => {
  $('#summary-screen').hide();
  $('#container, #info').show();
  populateMovesTable();
  showMove(0);
});

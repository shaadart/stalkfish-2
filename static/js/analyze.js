// analyze.js
let analysis = [], moveIndex = 0;

function showMove(i) {
  $('.annotation').remove();
  game.reset();
  for (let j = 0; j <= i; j++) game.move(analysis[j].san);
  board.position(game.fen());

  const a = analysis[i];
  $('#info').text(`Move ${i+1}: ${a.san} | Eval: ${a.eval} | ${a.tag}`);
  const sq = $('.square-' + a.to);
  if (sq.length) sq.append(`<div class="annotation">${a.tag}</div>`);
}

$('#pgnForm').on('submit', function(e) {
  e.preventDefault();
  $.post('/analyze', $(this).serialize(), function(data) {
    if (data.error) return alert("Error: " + data.error);
    analysis = data;
    moveIndex = 0;
    showMove(0);
  }, 'json')
  .fail((xhr) => {
    let msg = xhr.responseJSON?.error || xhr.statusText;
    alert(`Analyze failed (HTTP ${xhr.status}):\n${msg}`);
  });
});

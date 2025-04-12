// analyze.js
let analysis = [], moveIndex = 0;

function showMove(i) {
  $('.annotation').remove();
  game.reset();
  for (let j = 0; j <= i; j++) game.move(analysis[j].san);
  board.position(game.fen());

  const a = analysis[i];
  $('#info').text(`Move ${i + 1}: ${a.san} | Eval: ${a.eval}`);

  // Highlight the selected move
  $('#moves-list-container li').removeClass('selected');
  $(`#moves-list-container li[data-index="${i}"]`).addClass('selected');

  const sq = $('.square-' + a.to);
  if (sq.length) {
    let annotationClass = '';
    switch (a.tag) {
      case 'Best Move':
        annotationClass = 'best-move';
        break;
      case 'Inaccuracy':
        annotationClass = 'inaccuracy';
        break;
      case 'Mistake':
        annotationClass = 'mistake';
        break;
      case 'Blunder':
        annotationClass = 'blunder';
        break;
    }
    sq.append(`<div class="annotation ${annotationClass}"></div>`);
  }
}

function populateMovesList() {
  $('#moves-list-container').empty();

  analysis.forEach((move, index) => {
    let annotationClass = '';
    switch (move.tag) {
      case 'Best Move':
        annotationClass = 'best-move';
        break;
      case 'Inaccuracy':
        annotationClass = 'inaccuracy';
        break;
      case 'Mistake':
        annotationClass = 'mistake';
        break;
      case 'Blunder':
        annotationClass = 'blunder';
        break;
    }

    const moveHTML = `
      <li data-index="${index}">
        ${index + 1}. ${move.san}
        <span class="move-annotation ${annotationClass}"></span>
        <span class="move-eval">(${move.eval})</span>
      </li>
    `;
    $('#moves-list-container').append(moveHTML);
  });

  // Add click event to jump to a specific move
  $('#moves-list-container li').on('click', function () {
    const moveIndex = $(this).data('index');
    showMove(moveIndex);
  });
}

function calculateSummary() {
  let brilliant = 0, great = 0, best = 0, good = 0, inaccuracy = 0, mistake = 0, blunder = 0;
  let whiteAccuracy = 0, blackAccuracy = 0;

  analysis.forEach((move, index) => {
    switch (move.tag) {
      case 'Brilliant Move':
        brilliant++;
        break;
      case 'Great Move':
        great++;
        break;
      case 'Best Move':
        best++;
        break;
      case 'Good Move':
        good++;
        break;
      case 'Inaccuracy':
        inaccuracy++;
        break;
      case 'Mistake':
        mistake++;
        break;
      case 'Blunder':
        blunder++;
        break;
    }
  });

  // Calculate accuracy (mock values for now, replace with real logic)
  whiteAccuracy = 100 - (inaccuracy + mistake + blunder) * 2; // Example formula
  blackAccuracy = 100 - (inaccuracy + mistake + blunder) * 2;

  // Update the UI
  $('#brilliant-count').text(brilliant);
  $('#great-count').text(great);
  $('#best-count').text(best);
  $('#good-count').text(good);
  $('#inaccuracy-count').text(inaccuracy);
  $('#mistake-count').text(mistake);
  $('#blunder-count').text(blunder);
  $('#white-accuracy').text(`White: ${whiteAccuracy}%`);
  $('#black-accuracy').text(`Black: ${blackAccuracy}%`);
}

$('#pgnForm').on('submit', function (e) {
  e.preventDefault();
  $.post(
    '/analyze',
    $(this).serialize(),
    function (data) {
      if (data.error) return alert('Error: ' + data.error);
      analysis = data;
      moveIndex = 0;
      calculateSummary(); // Calculate and display the summary
      $('#summary-screen').show(); // Show the summary screen
      $('#container, #info').hide(); // Hide the board and moves list
    },
    'json'
  ).fail((xhr) => {
    let msg = xhr.responseJSON?.error || xhr.statusText;
    alert(`Analyze failed (HTTP ${xhr.status}):\n${msg}`);
  });
});

$('#start-review').on('click', function () {
  $('#summary-screen').hide(); // Hide the summary screen
  $('#container, #info').show(); // Show the board and moves list
  populateMovesList(); // Populate the moves list
  showMove(0); // Start the review from the first move
});

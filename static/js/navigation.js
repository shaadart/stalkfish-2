// navigation.js
$(document).on('keydown', function(e) {
    if (!analysis.length) return;
    if (e.key === 'ArrowRight' && moveIndex < analysis.length - 1) {
      moveIndex++; showMove(moveIndex);
    }
    else if (e.key === 'ArrowLeft' && moveIndex > 0) {
      moveIndex--; showMove(moveIndex);
    }
  });
  
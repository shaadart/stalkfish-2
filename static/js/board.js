// board.js
let board, game;
$(function() {
  game = new Chess();
  board = Chessboard('board', {
    position: 'start',
    pieceTheme: 'http://chessboardjs.com/img/chesspieces/alpha/{piece}.png'
  });
});

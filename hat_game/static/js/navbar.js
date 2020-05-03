if (typeof jQuery === 'undefined') {
  throw new Error('HatGame\'s JavaScript requires jQuery')
}

// Create a new game, returning the location response header.
async function createGame() {
  const response = await fetch("/games", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  });
  return response.headers.get('location');
}

// Join a game - redirect based on the game_id element.
$(function() {
  $('#joinGameButton').click(function() {
    window.location.replace(
      "/game/"
      + document.getElementById("gameIdInput").value
    )
  });

  // Execute a function when the user releases a key on the keyboard
  $('#gameIdInput').keyup(function(event) {
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) {
      // Cancel the default action, if needed
      event.preventDefault();
      // Trigger the button element with a click
      document.getElementById("joinGameButton").click();
    }
  }); 
});

// Hit the Join Game button on enter

// Create a new game and redirect to it if successful.
$(function() {
  $('.newGameButton').click(function() {
    createGame().then((data) => {
      if (data) {
        window.location.replace(data);
      } else {
        console.log("Game create failed");
      }
    });
  });
});

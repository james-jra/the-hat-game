if (typeof jQuery === 'undefined') {
  throw new Error('HatGame\'s JavaScript requires jQuery')
}

class HatPick {
  constructor(id, name, picked, submitter) {
    this.id = id;
    this.name = name;
    this.picked = picked;
    this.submitter = submitter;
  }
  static from(json){
    return Object.assign(new HatPick(), json);
  }
}

async function drawFromHatRequest(gameId) {
  const response = await fetch("/game/" + gameId + "/hat-picks/draw", {
    method: 'POST',
  });
  const responseData = await response.json();
  console.log(responseData);
  if (responseData.hasOwnProperty('hat_pick')) {
    return [true, HatPick.from(responseData.hat_pick)];
  } else if (Object.keys(responseData).length === 0) {
    return [false, null];
  } else {
    throw "Invalid response body";
  }
}

// Return this HatPick to the hat
async function returnToHatRequest(gameId, hatPick) {
  console.log(`Return to hat ${gameId}`, hatPick);

  hatPick.picked = false;
  const response = await fetch("/game/" + gameId + "/hat-pick/" + hatPick.id, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(hatPick)
  });
  return response;
}

function clickBank(cardId, cardName) {
  console.log(`click bank ${cardId} ${cardName}`);

  if (typeof cardId === 'undefined' || typeof cardName === 'undefined') {
    console.log("Null argument");
  } else {
    if (livePair.has(cardId)) {
      console.log(`Bank card ${cardId} ${cardName}`);
      successfulPicks.set(cardId, livePair.get(cardId));
      livePair.delete(cardId);
      drawFromHatRequest(gameId).then(([not_empty, data]) => {
        console.log(`Hat returned value ${not_empty} ${data}`);
        if (not_empty && data) {
          livePair.set(data.id, data);
        } else if (!not_empty && livePair.size == 0) {
          alert("The hat's empty!");
        } else {
          console.log("Failed to draw");
        }
      }).then(() => {
        redrawHatPicks(livePair, successfulPicks);
      }).catch(() => {
        redrawHatPicks(livePair, successfulPicks);
      });
    } else {
      console.log(`Card ${cardId} ${cardName} not in live pair`);
    }
  }
}

function clickPass(cardId, cardName) {
  console.log(`click pass ${cardId} ${cardName}`);

  if (typeof cardId === 'undefined' || typeof cardName === 'undefined') {
    console.log("Null argument");
  } else {
    console.log(`Pass card ${cardId} ${cardName}`);
    if (livePair.size < 2) {
      drawFromHatRequest(gameId).then(([not_empty, data]) => {
        console.log(`Hat returned value ${not_empty} ${data}`);
        if (not_empty && data) {
          livePair.set(data.id, data);
        } else if (!not_empty) {
          alert("The hat's empty!");
        } else {
          console.log("Failed to draw");
        }
      }).then(() => {
        redrawHatPicks(livePair, successfulPicks);
      });
    } else {
      console.log(`Can't pass - already got ${livePair}`);
    }
  }
}

function clickReturn(cardId, cardName) {
  console.log(`click return ${cardId} ${cardName}`);

  if (typeof cardId === 'undefined' || typeof cardName === 'undefined') {
    console.log("Null argument");
  } else {
    if (livePair.has(cardId)) {
      console.log(`Return card ${cardId} ${cardName}`);
      const toReturn = livePair.get(cardId);
      livePair.delete(cardId);

      returnToHatRequest(gameId, toReturn).then(() => {
        console.log("Return succeeded");
        redrawHatPicks(livePair, successfulPicks);
      });
    } else if (successfulPicks.has(cardId)) {
      console.log(`Return card ${cardId} ${cardName}`);
      const toReturn = successfulPicks.get(cardId);
      successfulPicks.delete(cardId);

      returnToHatRequest(gameId, toReturn).then(() => {
        console.log("Return succeeded");
        redrawHatPicks(livePair, successfulPicks);
      });
    } else {
      console.log(`Card ${cardId} ${cardName} not found`);
    }
  }
}

function makeActivePicks(pair) {
  console.log("Make active picks", pair);
  // Create the row element:
  var row = document.createElement('div');
  row.setAttribute('class', 'row');

  if (!pair || pair.length > 2) {
    console.log(`Invalid pair ${pair}`);
    return row;
  }

  // Add a title for the active picks.
  var title = document.createElement('h3');
  title.innerHTML = 'Active picks';
  row.appendChild(title);

  for (var i = 0; i < pair.length; i++) {
    // Create the list item:
    var col = document.createElement('div');
    col.setAttribute('class', 'col');

    // Set its contents:
    col.appendChild(document.createTextNode(pair[i].name));
    col.appendChild(document.createElement('p'));

    // Button Group to draw/pass/return to hat.
    var btnGroup = document.createElement('div');
    btnGroup.setAttribute('class', 'btn-group btn-group-lg');
    btnGroup.setAttribute('role', 'group');
    const cardId = pair[i].id;
    const cardName = pair[i].name;

    var bankBtn = document.createElement('BUTTON');
    bankBtn.setAttribute('class', 'btn btn-primary btn-lg bankButton');
    bankBtn.addEventListener("click", function(event){clickBank(cardId, cardName)});
    bankBtn.innerHTML = 'Got it!';
    var passBtn = document.createElement('BUTTON');
    passBtn.setAttribute('class', 'btn btn-secondary btn-lg passButton');
    passBtn.addEventListener("click", function(event){clickPass(cardId, cardName)});
    passBtn.innerHTML = 'Pass';
    var returnBtn = document.createElement('BUTTON');
    returnBtn.setAttribute('class', 'btn btn-dark btn-lg returnButton');
    returnBtn.addEventListener("click", function(event){clickReturn(cardId, cardName)});
    returnBtn.innerHTML = 'Return';

    btnGroup.appendChild(bankBtn);
    btnGroup.appendChild(passBtn);
    btnGroup.appendChild(returnBtn);
    col.appendChild(btnGroup);

    // Add it to the list:
    row.appendChild(col);
  }

  // Finally, return the constructed list:
  return row;
}

function makeSuccessfulPicks(array) {
  console.log("Make successful picks", array);
  // Create the list element:
  var list = document.createElement('ul');
  if (!array) {
    console.log("Invalid array");
    return row;
  }

  for (var i = 0; i < array.length; i++) {
    // Create the list item:
    var item = document.createElement('li');
    const cardId = array[i].id;
    const cardName = array[i].name;

    // Set its contents:
    item.appendChild(document.createTextNode(array[i].name));
    // Button to return to hat.
    var btn = document.createElement('BUTTON');
    btn.setAttribute('class', 'btn btn-secondary returnButton');
    btn.addEventListener("click", function(event){clickReturn(cardId, cardName)});
    btn.innerHTML = 'Return';
    item.appendChild(btn);

    // Add it to the list:
    list.appendChild(item);
  }
  // Add a title for the active picks.
  var title = document.createElement('h3');
  title.innerHTML = 'Successful picks';

  // Shove it in a row div.
  var row = document.createElement('div');
  row.setAttribute('class', 'row');
  row.appendChild(title);
  row.appendChild(list);

  // Finally, return the constructed list:
  return row;
}

function redrawHatPicks(livePair, successfulPicks) {
  console.log("Redraw hat picks");
  console.log(livePair);
  console.log(successfulPicks);

  $('#hatPicksDisplay').empty()
  $('#hatPicksDisplay').append(
    makeActivePicks(Array.from(livePair.values())),
    makeSuccessfulPicks(Array.from(successfulPicks.values()))
  );
}

function getGameId() {
  var pathSegments = window.location.pathname.split("/");
  const gameId = pathSegments.pop();
  if (gameId) {
    return gameId;
  } else {
    return pathSegments.pop();
  }
}

var livePair = new Map();
var successfulPicks = new Map();
var gameId = "";

$(function() {
  gameId = getGameId();
  if (typeof gameId === 'undefined') {
    throw new Error('Could not load GameId');
  }

  // Handle draw - button present outside of the hat picks elements.
  $('.drawButton').click(function() {
    console.log("Draw card");
    if (livePair.size < 2) {
      drawFromHatRequest(gameId).then(([not_empty, data]) => {
        console.log(`Hat returned value ${not_empty} ${data}`);
        if (not_empty && data) {
          livePair.set(data.id, data);
        } else if (!not_empty) {
          alert("The hat's empty!");
        } else {
          console.log("Failed to draw");
        }
      }).then(() => {
        redrawHatPicks(livePair, successfulPicks);
      });
    } else {
      console.log(`Can't draw another - already got ${livePair}`);
    }
  });

  // Handle end-of-turn - button present outside of the hat picks elements.
  $('.completeTurnButton').click(function() {
    console.log("Complete turn");
    for (let [id, pick] of livePair) {
      console.log(`Return ${pick.id} ${pick.name}`);
      returnToHatRequest(gameId, pick).then(() => {
        console.log("Return succeeded");
      });
      livePair.delete(id);
    }

    redrawHatPicks(livePair, successfulPicks);
  });

  $('.completeRoundButton').click(function() {
    console.log("Complete round");
    for (let [id, pick] of livePair) {
      console.log(`Return ${pick.id} ${pick.name}`);
      returnToHatRequest(gameId, pick).then(() => {
        console.log("Return succeeded");
      });
      livePair.delete(id);
    }
    for (let [id, pick] of successfulPicks) {
      console.log(`Return ${pick.id} ${pick.name}`);
      returnToHatRequest(gameId, pick).then(() => {
        console.log("Return succeeded");
      });
      successfulPicks.delete(id);
    }
    redrawHatPicks(livePair, successfulPicks);
  });

  redrawHatPicks(livePair, successfulPicks);
});

# Hat game online web-app

## Dev / test setup

Install the
[Poetry package manager](https://hackersandslackers.com/python-poetry-package-manager/)

```
# Check out the repo
$ git clone <hat game> && cd hat-game
~/hat-game $

# Init poetry
~/hat-game $ poetry shell

# Install dependencies
~/hat-game $ poetry install --no-root

# Run the app
~/hat-game $ FLASK_APP=hat-game.py flask run --host=0.0.0.0 --port=8080
```

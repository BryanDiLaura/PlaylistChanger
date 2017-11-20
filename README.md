# Playlist Changer
### An automatic Spotify playlist creator

## Synopsis
Playlist Changer is an attempt to fill in functionality that I felt was missing in Spotify, specifically with smart playlists. There are already many tools for doing this hosted online, such as [this powerful tool](http://smarterplaylists.playlistmachinery.com/go.html). Unfortunately, none of them had the ability to create a **recently added** playlist, and didn't provide the granularity of control I was looking for. 

Because of this, I decided to create a simple, locally hosted system, that would allow me to create these smart playlists as I wanted to. 

*Note: this is still a work in progress! Please do not assume that things will remain remotely static with this codebase. If you like it as is, please make a fork. If you want to make improvements, please feel free to send in pull requests.*

## Getting Started

### Dependancies
Playlist Changer depends on a couple of easily installable packages. These packages are: 
- [spotipy](https://github.com/plamere/spotipy)
- [flask](http://flask.pocoo.org/)

These can be installed by running the following:
`python -m pip install spotipy flask`

Everything else should be installed by default. If not, pip and Google are your friend. 

### Setup
In order to get this to work, you have to get the Spotify API to talk to your application. I have tried to make this as easy as possible, while keeping my own API keys safe. Please be careful with your own keys! Do the following:

- Go to the [Spotify developer portal](https://developer.spotify.com/my-applications/#!/applications)
- Agree to tribute your first born on the Spotify altar
- Go to My Applications, and click "Create an app"
- Put in a clever name and description
- Scroll down to the Redirect URI, and add `http://localhost:5000`
- Switch to a file browser and navigate to wherever you downloaded Playlist Changer
- Rename keys_template.py to `keys.py`
- Copy and paste your client ID and client secret into keys.py
- Run playlistChanger.py however you usually run python scripts
- Crack a beer and enjoy!

## License
Licensed under a MIT license. For more details, please see LICENSE.txt.

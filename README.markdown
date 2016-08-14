# pocket command line client

[Pocket](https://getpocket.com/) is a "save for later" service, for URLs.
Useful for saving articles you found but did not have time to read at the moment.

----

## Installation

Copy `pocket.py` to a directory on `$PATH` as `pocket`, and
give it execution rights.

Copy `ui.json` to `~/.local/share/pocket/ui.json`.

Create a configuration directory: `~/.config/pocket`.


----

## Configuration

pocket command line client expects a configuration, in form of a JSON object, stored
in `~/.config/pocket/config.json`.
The configuration must contain two keys:

- `consumer_key`: consumer key of the application (you have to generate it yourself)
- `access_token`: OAuth access token given to you by Pocket


### How to get consumer key?

You have to register a new pocket application to get a consumer key.
Instructions: http://getpocket.com/developer/apps/new


### How to get access token?

You have to authorise the application to access your Pocket account, and
get the access token from Pocket.
Instructions: https://getpocket.com/developer/docs/authentication


----

# License

This is free software published under GNU GPL v3 (or later) license.

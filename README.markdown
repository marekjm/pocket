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

**Why do you have to register a new application?**

This project is just a simple tool to fetch list of saved Pocket articles, and
add new ones; from the command line.
I published this tool in hope that it may be useful, but do not think about it as
a typical "user-friendly" program - so I do not want to bind all the requests to my
consumer key.
I trust that every person interested in a command line Pocket client is also
capable of registering a new pocket application, and handling their own keys.


### How to get access token?

You have to authorise the application to access your Pocket account, and
get the access token from Pocket.
Instructions: https://getpocket.com/developer/docs/authentication

**Why isn't an access token generated automatically by the program?**

I'd be happy to receive a pull request for this.
This is a simple tool, and I just did not want to spend time implementing more
than the useful minimum of functionality.


----

# License

This is free software published under GNU GPL v3 (or later) license.

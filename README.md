About infamitm
======================

A **customizable** transparent HTTP proxy: by default it just behave as a transparent proxy, but it is easy to add custom behaviours like logging, rewriting, banning.

Installation
-------------

Just run `python2 proxy.py config.py` and it will sit on port 8080.
To make it transparent:

    iptables -t nat -A PREROUTING -s $CLIENT_IP -p tcp --dport 80 -j REDIRECT --to-port 8080

If you want to change configuration at runtime, just edit your file, then

    kill -HUP [pid]

Hacking
===========

Code structure
---------------

In `proxy.py` you'll find basic transparent proxy configuration. What you
should really care about is your configuration file (`config.py`): here the
"custom behaviours" are defined. See _Customizing_ for more info.

Theory
-------

For each request, an object Session is created:

Methods:
* `preRequest`: a function that can manipulate the request data (host, url,
  arguments, headers).
* `postResponse`: a function that receives what upstream got, and can edit the
  response (body and headers)

Data:
* `data`: a dictionary
* `pre`: the function that will be called on preRequest
* `post`: the function that will be called on postResponse
* ... you can add fields if you feel so

Each of the functions has access to the whole structure. So, actually the
`preRequest` function can **change** what the `postResponse` will be. Remember,
that structure will be deleted after the request is satisfied, so the changes
are not permanent.

By default, this is just a normal, transparent proxy.

Customizing
------------

In your `config.py` (or whatever you want to call it) you should define your
custom behaviours.

This basically requires defining new "pre" and "post" functions `preRequest` /
`postResponse`

See the `samples/` directory for examples.

TODO
=====

* More/better support for different "layers" of interaction (ie: to support
  logging more easily, and make it easy to "combine" different "modules"
  together)
* Support for "global" data
* Support for tracking an user
  - Based on IP
  - Based on Cookie
    + Give a tracking cookie to user
	+ Use a site-specific tracking cookie (like PHPSESSID) and just checks it

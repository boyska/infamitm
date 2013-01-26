Transparent HTTP proxy
======================

A **customizable** transparent HTTP proxy: by default it just behave as a transparent proxy, but it is easy to add custom behaviours like logging, rewriting, banning.

Installation
-------------

Just run `python2 proxy.py config.py` and it will sit on port 8080.
To make it transparent:

    iptables -t nat -A PREROUTING -s $CLIENT_IP -p tcp --dport 80 -j REDIRECT --to-port 8080

Customizing
---------

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

If you want to be able to run a "custom" one, just set some functions as
preRequest/postResponse

TODO
-----

* More/better support for different "layers" of interaction (ie: to support
  logging more easily, and make it easy to "combine" different "modules"
  together)
* Support for "global" data
* Support for tracking an user
  - Based on IP
  - Based on Cookie
    + Give a tracking cookie to user
	+ Use a site-specific tracking cookie (like PHPSESSID) and just checks it

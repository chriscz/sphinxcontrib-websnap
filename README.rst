Websnap is a sphinx extension that downloads web URLs as single html pages, 
caches them, and allows you to create links to them inside of Sphinx.

Why Websnap
-----------
Journaling and documenting what you learn is good. Here are two
experiences that cemented that for me

   - In 2015 I took a course in game trees and search programming. 
     For the course we had to keep a journal about all the things we experimented with, 
     as well as all of the algorithms we implemented. 

   - Shapfter, a friend of mine always wrote documentation for himself 
     while learning new programming languages or libraries.

So in early 2017 I started doing the same, and have found that a personal
wiki / journal has become invaluable for collecting links and documenting
my own understanding of new software technologies.

I've found that I can get up to speed faster on something a studied a few months
earlier by consulting my own notes than by reading the original tutorials. But,
sometimes you find the one or two exceptional tutorials you'd like to
keep, and this is were Websnap comes in handy.

Project Status
--------------
Websnap is currently in pre-alpha, which means it's highly experimental and
has an unstable API. 

I take no liability for messing up your Sphinx documentation, consuming your 
internet cap or breaking your computer.

Installation
------------
Currently only supports Python 3. Only tested on Python 3.5

::

   pip install sphinxcontrib-websnap

Then include websnap in your extensions:

.. code:: python

   extensions = [ 
      # ...
      'sphinxcontrib.websnap'
   ]



Usage
-----
Websnap (0.2.0) introduces a directive for downloading a webpage:

.. code:: rst
   
   .. websnap:: <website-url>
                <reference-name>
 
The webpage at ``website-url`` will be downloaded as a single page and stored
under ``_static/_websnap/<name-derived-from-title-or-url>.html``. This 
directive **does not** generate any output. Here's an example:

.. code:: rst
   
   .. websnap:: http://www.github.com/chriscz
                my_github
 

Websnap also provides a **role** for referencing downloaded pages. The
role can itself initiate a download. Here's an example of it's different
forms:

.. code:: rst

   Welcome to my website, here's an 
   :websnap:`archived copy of my githubhomepage <my_github>`.

   Here's an archived copy of facebook: :websnap:`http://facebook.com`.

The role use will be replaced by link to the archived copy of the website.

Each unique URL will only be downloaded once. To clear the cache, you can remove the
``_websnap`` directory or edit the ``_websnap/.cache`` (json) file. 

What's planned?
---------------
The following are planned features and functionality:

- [A] Add a lock on the cachefile using https://github.com/WoLpH/portalocker 
- [B] Consider whether it may be good to store URL and other information
  as a comment at the top of the downloaded HTML file.
- [C] Add directive for downloading binary files
- [C] Add command for updating all outdated cached websites

Completed
---------
- [B] Add directive for downloading a URL and assigning it 
  symbolic name that can be used to refer to it.
- [B] Add option to current directive to give it a reusable linkname
- [B] Store more metadata in the .cache file

  - downloaded time and date
  - the generated reference to use for the URL
  - the original title from the html

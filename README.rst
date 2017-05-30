Websnap is a sphinx extension that downloads web URLs as single html pages, 
caches them, and allows you to create links to them inside of Sphinx.

Why Websnap
-----------
In 2015 I took a course in game programming. For the course we had to keep a 
text-document journal about all the things we experimented with, as well
as all of the algorithms we implemented. Shapfter, a programming buddy of 
mine always wrote documentation for himself while learning a new language or
language features.

So in early 2017 I started doing the same, and have found that a personal
wiki / journal has become invaluable for collecting links and documenting
my own understanding of new software technologies.

I've found that I can get up to speed again on something a learnt months
ago much faster by consulting my own notes than that of others. Furthermore,
sometimes you find the exceptionally well-written tutorial you'd like to
keep, and this is were Websnap comes in handy.

Project Status
--------------
Websnap is currently in pre-alpha, which means it's highly experimental and
has an unstable API. 

I take no liability for messing up your Sphinx documentation, consuming your 
internet or breaking your computer.

Installation
------------

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
Websnap (0.1.0) introduces the directive

.. code:: rst
   
   .. websnap-url:: <website-url>
                    <urlname>                  

What's planned?
---------------
The following are planned features and functionality:

- [A] Add a lock on the cachefile using https://github.com/WoLpH/portalocker 
- [B] Refactor and clean up the code
- [B] Add directive for downloading a URL and assigning it 
  symbolic name that can be used to refer to it.
- [B] Add option to current directive to give it a reusable linkname
- [B] Store more metadata in the .cache file
  - downloaded time and date
  - the generated reference to use for the URL
  - the original title from the html
- [B] Consider whether it may be good to store URL and other information
      as a comment at the top of the downloaded HTML file.
- [C] Add directive for downloading binary files
- [C] Add command for updating all outdated cached websites

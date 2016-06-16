solus-sc
--------

Software Center component of Solus.
Currently undergoing an overhaul to drop all the stupidity and slowness that it
managed to gather over the years.


Testing
^^^^^^^

Clone the repo, and then install appstream-glib::

    sudo eopkg it appstream-glib

Now you'll need the appdata (this is going to be packaged soon)::

    git clone https://git.solus-project.com/projects/appstream
    cd appstream
    ./install.sh

Now just run the main launcher in this repo (don't ctrl+c, it'll explode)::

    ./main.py

License
^^^^^^^

Copyright © 2014-2016 Ikey Doherty

This software is available under the terms of the GPL-2.0 license.
Please see `LICENSE <LICENSE>`_ for details.
GPL-3.0

README
++++++

Some assumptions 
================

These are based on my workflow/project layout. 

* Nginx's root is in `/usr/share/nginx`
* Each project exists in `/usr/share/nginx/$PROJECT`
* My virtualenv (`venv`) is located in `$PROJECT/venv`
* Files are being served by `www-data:www-data` (this needs to change)
* I run these commands **ON** the server. While Fabric's strength is remote/SSH
  functionality/support, this is simply a part of my workflow/(bad?)habit.

Based on the above, I think the rest will make sense.  

.. code-block:: python

    def backup_web():
        """ Backup a specified directory/project """
        tar = tarfile.open("/tmp/%s-%s-web-bkup.tar.bz2" % (date, project),
            "w:bz2")
        tar.add("/usr/share/nginx/%s" % (project))
        tar.close()

The above block simply utilizes Python's stdlib `tarfile`_ to create a
compressed archive of the `web_root`. While a part of this is redundant since a
lot of this exists in the git repo, I have more warm fuzzies simply zipping up
the entire project. 

Because I'm a Sys Admin at heart, who managed backups for years, you can never
have too many backups and as such, in addition to the project files, I also
back up the database before anything is done:

.. code-block:: python

    def backup_db():
        """ backup a specified database """
        local("su postgres -c '/usr/bin/pg_dump -Fc %sdb >
            /opt/pg/bkup/%sdb-%s.dump'" % (project, project, date))

What the above is doing is simply switching to the `postgres` user, and doing a
`pg_dump`_ to a `.dump` file. This dump can be restored with `pg_restore`_.  

As mentioned above, because I'm doing a git pull as the `root` user, I need to
change the owner of these files to ensure Nginx can serve them. 

.. code-block:: python

    def change_owner():
        """ This is a hack -- git is ran as root and will own whatever is
        pulled """
        local("chown -R www-data:www-data web_site/")

Something else commonly done in django projects is syncing the database, and if
you use South, migrating these when the schema or data changes.  

.. code-block:: python

    def syncdb():
        local("source venv/bin/activiate && ./manage.py syncdb")

    def migrate_app(app):
        local("source venv/bin/activate && ./manage.py migrate %s" % (app))

    def migrate_all():
        local("source venv/bin/activate && ./manage.py migrate")


`syncdb` is pretty self explanatory I think.  `migrate_app` allows me to do a
`fab migrate_app:app` and it will run a `migrate app`.  `migrate_app` is more
likely to be used if I were managing migrations manually, rather than during a
deployment where it is simply easier to migrate all the databases.  

And here is where it all comes together. 

.. code-block:: python

    def publish():
        backup_web()
        backup_db()
        git_pull()

Simple right? Basically, it will back up the project's files, then the
project's database and then do a git pull.  

As a part of my workflow and `my git hooks`_ the work flow is a little more
like:

* back up project's files
* back up project's database
* do a git pull
* if a requirements.txt file changed, do a `pip install -U
  prod-requirements.txt`
* if a settings or a models file changed, restart uWSGI
* if a migrations file exists, do a `./manage.py syncdb && ./manage.py --migrate`
* change the owner of the files in project's root to `www-data:www-data`


.. _tarfile: http://docs.python.org/2/library/tarfile.html
.. _pg_dump: http://www.postgresql.org/docs/9.1/static/app-pgdump.html
.. _pg_restore: http://www.postgresql.org/docs/9.1/static/app-pgrestore.html
.. _my git hooks: http://www.barrymorrison.com/2013/Mar/07/more-git-hook-greatness/

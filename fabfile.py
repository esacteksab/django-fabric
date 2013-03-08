import os
import tarfile
import datetime
from fabric.api import *

env.hosts = ['localhost']

today = datetime.datetime.today()
date = today.strftime('%Y-%m-%d-%H-%M')

project = os.path.basename(os.getcwd())

def backup_web():
    """ Backup a specified directory/project """
    tar = tarfile.open("/tmp/%s-%s-web-bkup.tar.bz2" % (date, project), "w:bz2")
    tar.add("/usr/share/nginx/%s" % (project))
    tar.close()

def backup_db():
    """ backup a specified database """
    local("su postgres -c '/usr/bin/pg_dump -Fc %sdb > /opt/pg/bkup/%sdb-%s.dump'" % (project, project, date))

def change_owner():
    """ This is a hack -- git is ran as root and will own whatever is pulled """
    local("chown -R www-data:www-data web_site/")

def restart_uwsgi():
    """ Restart uWSGI service """
    local("/usr/sbin/service uwsgi restart")

def syncdb():
    local("source venv/bin/activiate && ./manage.py syncdb")

def migrate_app(app):
    local("source venv/bin/activate && ./manage.py migrate %s" % (app))

def migrate_all():
    local("source venv/bin/activate && ./manage.py migrate")

def git_pull():
    local("git pull")

def publish():
    backup_web()
    backup_db()
    git_pull()

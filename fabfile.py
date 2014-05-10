from fabric.api import run, sudo, local, cd, env

env.hosts = ['orlando.thraxil.org']
env.user = 'anders'
nginx_hosts = ['lolrus.thraxil.org']



def restart_gunicorn():
    sudo("restart maut")

def prepare_deploy():
    local("./manage.py test")

def deploy():
    code_dir = "/var/www/maut/maut"
    with cd(code_dir):
        run("git pull origin master")
        run("make migrate")
        run("make collectstatic")
        for n in nginx_hosts:
            run(("rsync -avp --delete media/ "
                 "%s:/var/www/maut/maut/media/") % n)
    restart_gunicorn()

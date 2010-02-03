import os
import os.path
import sys
from restclient import GET, POST
from simplejson import loads
from pprint import pprint
import urllib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from music.models import Track
from django.core.management.base import BaseCommand

from django.utils.encoding import smart_unicode, force_unicode, smart_str

TSERVE_BASE = "http://tserve.ccnmtl.columbia.edu/"
DIRECT_TAHOE_BASE = "http://behemoth.ccnmtl.columbia.edu:3456/uri/"

def relative_dir(localbase,root):
    return "/" + root[len(localbase):]

def subdirs(dir_data,base="",ids=None):
    if ids is None:
        ids = dict()
    for sd in dir_data['subdirs']:
        ids[base + "/" + sd['name']] = sd['id']
        ids = subdirs(sd,base=base + "/" + sd['name'],ids=ids)
    return ids
        
def info_url(id):
    return TSERVE_BASE + "dir/%d/external/" % id

def mkdir_url(id):
    return TSERVE_BASE + "dir/%d/external/mkdir/" % id
def upload_url(id):
    return TSERVE_BASE + "dir/%d/external/upload/" % id

def get_parent(rdir):
    return "/" + "/".join(rdir.split("/")[1:-1])
def get_child(rdir):
    return rdir.split("/")[-1]

def mkdir(rdir,subdir_ids):
    parent = get_parent(rdir)
    child = get_child(rdir)
    if parent not in subdir_ids:
        subdir_ids = mkdir(parent,subdir_ids)
    parent_id = subdir_ids[parent]
    rdir_id = int(POST(mkdir_url(parent_id),params=dict(name=child),async=False))
    subdir_ids[rdir] = rdir_id
    return subdir_ids

def maut_url(filename):
    return "." + filename

def update_maut(filename,cap):
    print "updating %s in maut" % filename
    url = maut_url(filename)
    try:
        t = Track.objects.get(url=smart_unicode(url,errors='replace'))
        t.url = cap
        t.save()
        return True
    except Track.DoesNotExist:
        print "not found"
        return False

def upload_file(dirid,filename,local_fullpath):
    register_openers()
    dirdata = loads(GET(info_url(dirid)))
    if filename not in [f['filename'] for f in dirdata['files']]:
        print "uploading %s directly to tahoe" % filename
        print maut_url(local_fullpath)
        dircap = dirdata['cap']
        datagen, headers = multipart_encode({"file": open(local_fullpath,"rb"),
                                             "t" : "upload"})
        url = DIRECT_TAHOE_BASE +urllib2.quote(dircap) 
        request = urllib2.Request(url,datagen, headers)
        cap = urllib2.urlopen(request).read()
        id = POST(upload_url(dirid),
                  params=dict(filename=filename,cap=cap),async=False)
        ext = filename.lower().split(".")[-1]
        if update_maut(local_fullpath,cap):
            os.unlink(local_fullpath)
        else:
            if ext not in ["ogg","mp3"]:
                os.unlink(local_fullpath)
    else:
        print "already there"

def recursive_import(tserve_base,local_base):
    dir_data = loads(GET(tserve_base + "external/"))
    subdir_ids = subdirs(dir_data)
    subdir_ids["/"] = dir_data['id']
    pprint(subdir_ids)
    for root, dirs, files in os.walk(local_base):
        rdir = relative_dir(local_base,root)
        print "--- " + rdir
        if rdir not in subdir_ids:
            subdir_ids = mkdir(rdir,subdir_ids)
        dirid = subdir_ids[rdir]
        for name in files:
            upload_file(dirid,name,os.path.join(root,name))


class Command(BaseCommand):
    def handle(self,**options):
            tserve_base = "http://tserve.ccnmtl.columbia.edu/dir/3955/"
            local_base = "/home/anders/MyMusic/"
            register_openers()
            recursive_import(tserve_base,local_base)

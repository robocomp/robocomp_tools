#!/usr/bin/python

import os
import string
import shutil

''' Basic module which defines the workspace class
'''

class Workspace:
    
    workspace_paths = []
    numOfws = 0

    ''' constructor'''
    def __init__(self):
        self.update_pathlist()
    
    def update_pathlist(self):
        home = os.path.expanduser("~")
        if not os.path.exists(os.path.join(home,".config/RoboComp")):
            os.makedirs(os.path.join(home,".config/RoboComp"))
        config_file = open(os.path.join(home,".config/RoboComp/rc_workspace.config"),"r")    
        self.workspace_paths = config_file.readlines()
        self.workspace_paths = [ string.strip(x) for x in self.workspace_paths ]
        config_file.close()

    '''initiate a catkin workspace at the given path'''
    def init_ws(self, ws_path):

        def create_toplevel(src_path):
            src = os.getenv('ROBOCOMP','/opt/robocomp') + '/cmake/toplevel.cmake'
            dst = os.path.join(src_path,"toplevel.cmake")
            
            #test if path exists
            if not os.path.exists(src):
                raise RuntimeError("couldnt find toplevel cmake, make sure ROBOCOMP is properly installed\n")
            
            #try to create simlink
            try:
                os.symlink(src,dst)
            except Exception as symlinkEx:
                try:
                    shutil.copyfiles(src,dst)
                except Exception as copyEx:
                    raise RuntimeError('Could neither copy or simlink %s to %s : \n %s \n %s' % (src,dst,str(symlinkEx),str(copyEx)))

        try:
            os.system('touch %s' % (str(".rc_workspace")))

            dirs = ["src","build","devel"]
            for dir in dirs:
                dir_path = os.path.join(ws_path,dir)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
        except Exception as createEx:
            raise RuntimeError("couldnt create files/folders in current directory: \n %s " % (str(createEx)))

        pathstr = str(os.path.abspath(ws_path))

        #copy all files in the current dir into src dir
        for file in os.listdir(pathstr):
            if file in dirs: continue
            os.system("mv ./" + file + " ./src")

        create_toplevel(ws_path+'/src')

        if string.strip(pathstr) not in self.workspace_paths:
            #update the list of workspaces
            home = os.path.expanduser("~")
            if not os.path.exists(os.path.join(home,".config/RoboComp")):
                os.makedirs(os.path.join(home,".config/RoboComp"))
            config_file = open(os.path.join(home,".config/RoboComp/rc_workspace.config"),"a+")    
            config_file.write(pathstr)
            config_file.write("\n")
            config_file.close()

    ''' find the directory containing component exexutable'''
    def find_component_exec(self, component):
        componentPath = ''
        for path in self.workspace_paths:
            path = string.strip(path) + '/devel'
            for file in os.listdir(path):
                if string.lower(str(file)) == string.lower(component) and os.path.isdir(os.path.join(path,component)):
                    if os.path.exists(os.path.join(path,component,'bin',component) ):
                        componentPath = os.path.join(path,component,'bin')
        if componentPath != '':
            return componentPath
        else:
            return False

    ''' find component soruce directory'''
    def find_component_src(self,component):
        componentPath = ''
        for path in self.workspace_paths:
            path = string.strip(path) + '/src'
            for file in os.listdir(path):
                if lower(str(file)) == lower(component) and os.path.isdir(os.path.join(path,component)):
                    componentPath = os.path.join(path,component)
        return componentPath

rc_ws = Workspace()
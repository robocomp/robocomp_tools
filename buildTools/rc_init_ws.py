#!/usr/bin/python

import os
import argparse
import shutil
import sys

def create_toplevel(ws_path):
    src = os.getenv('ROBOCOMP','/opt/robocomp') + '/cmake/toplevel.cmake'
    dst = os.path.join(ws_path,"toplevel.cmake")
    print src
    print dst

    #test if path exists
    if not os.path.exists(src):
        raise RuntimeError("couldnt find toplevel cmake, make sure ROBOCOMP is properly installed")
    
    #try to create simlink
    try:
        os.symlink(src,dst)
    except Exception as symlinkEx:
        try:
            shutil.copyfiles(src,dst)
        except Exception as copyEx:
            raise RuntimeError('Could neither copy or simlink %s to %s : \n %s \n %s' % (src,dst,str(symlinkEx),str(copyEx)))

def init_ws(ws_path):
    '''initialize a robocomp workspace in the current dorectory
     * search and find the toplevel cmake (not for now)
     * create a smlink/copy the toplevel cmake
     * create src, build, devel folders
    '''
    create_toplevel(ws_path)
    try:
        os.system('touch %s' % (str(".rc_workspace")))

        dirs = ["src","build","devel"]
        for dir in dirs:
            dir_path = os.path.join(ws_path,dir)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
    except Exception as createEx:
        # TODO undo init_ws
        raise RuntimeError("couldnt create files/folders in current directory: \n %s " % (str(createEx)))
    
    #update the list of workspaces
    pathstr = str(os.path.abspath(ws_path))
    home = os.path.expanduser("~")
    if not os.path.exists(os.path.join(home,".config/RoboComp")):
        os.makedirs(os.path.join(home,".config/RoboComp"))
    config_file = open(os.path.join(home,".config/RoboComp/rc_workspace.config"),"a+")    
    print pathstr
    config_file.write(pathstr)
    config_file.write("\n")
    config_file.close()

def main():
    parser = argparse.ArgumentParser(description="initialize a robocomp workspace")
    parser.add_argument('workspace', nargs='?', default='.', help='The path to an existing folder (default: .)')
    args = parser.parse_args()

    # verify that workspace folder exists
    workspace = os.path.abspath(args.workspace)
    if not os.path.isdir(workspace):
        parser.error('Workspace "%s" does not exist' % workspace)

    #verify that this is not an existing workspace
    if os.path.exists( os.path.join(workspace,"toplevel.cmake")):
        parser.error('Workspace "%s" is alreay an workspace' % workspace)

    #try creating a workspace
    try:
        init_ws(workspace)
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(2)

if __name__ == '__main__':
    main()


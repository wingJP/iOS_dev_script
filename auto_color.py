import logging
import os
import json
import sys


def enable():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = "\033[1m"
    
def infog(msg):
    print('\033[92m' + msg + "")

def info(msg):
    print('\033[95m' + msg + "")

def err(msg):
    print('\033[91m' + msg + '')

basedir = os.path.abspath(os.path.dirname(__file__))
colorFileName = 'Colorfile'
trueBasedir = ""

xcassetsDirName = "Color"
configFileName = "ColorConfig"

def findfile(start, name):
    for relpath, dirs, files in os.walk(start):
        if name in files:
            global trueBasedir
            trueBasedir = os.path.normpath(os.path.abspath(os.path.join(start, relpath))) 
            full_path = os.path.join(start, relpath, name)
            return os.path.normpath(os.path.abspath(full_path))

    err("配置文件: %s不存在" % configFileName)

def loadColor(name, color):
    if "#" not in color:
        return None
    if name == "":
        return None
    h = color.lstrip('#')
    if len(h) != 6 and len(h) != 8:
        return None
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return (name, rgb[0], rgb[1], rgb[2])

def loadFile(colorfilePath):
    color_list = []
    f = open(colorfilePath)
    lines = f.readlines()
    global xcassetsDirName
    global configFileName
    for line in lines:
        if 'xcassetsDirName' in line:
            s = line.split()
            xcassetsDirName = s[1]
        if 'configFileName' in line:
            s = line.split()
            configFileName = s[1]
        if '#' in line:
            s = line.split()
            colorDic = loadColor(s[0], s[1])
            if colorDic is None:
                err(line + "   无效")
            else:
                color_list.append(colorDic)
    f.close()
    make_asset_dir(color_list)
    color_to_extension(color_list)

def make_asset_dir(color_list):
    path = os.path.join(trueBasedir, xcassetsDirName + '.xcassets')
    if not os.path.exists(path):
        try:
            os.mkdir(path)
            contents = { "info" : { "author" : "xcode", "version" : 1 }}
            with open(path + '/Contents.json', 'w') as outfile:
                json.dump(contents, outfile, indent=2)
        except OSError:
            err("Creation of the directory %s failed" % path)

    for color in color_list:
        color_to_conents(color)
        

def color_to_extension(color_list):
    path = os.path.join(trueBasedir, configFileName + '.swift')
    with open(path, 'w') as outfile:
        lines = ["import UIKit", "", "extension UIColor {"]
        for color in color_list:
            lines.append('    static var %s = UIColor(named: "%s")' % (color[0], color[0]))
        lines.append("}")
        outfile.write('\n'.join(lines) + '\n')
        

def color_to_conents(color):
    data = {}
    data['colors'] = []
    colorModel = {"color-space" : "srgb"}
    colorModel['components'] = {
        "alpha" : "1.000",
        "blue" : str(color[3]),
        "green" : str(color[2]),
        "red" : str(color[1]),
    }
    data['colors'].append({
        'color': colorModel,
        'idiom': 'universal'
    })
    data['info'] = { "author" : "xcode", "version" : 1}
    path = os.path.join(trueBasedir, xcassetsDirName + '.xcassets', color[0] + '.colorset')
    new_type = 0 # 0: 正常添加 1：替换 2:无变化
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError:
            err("Creation of the directory %s failed" % path)
    else:
        with open(os.path.join(path, 'Contents.json'),'r') as load_f:
            load_dict = json.load(load_f)
            if load_dict == data:
                new_type = 2
            else:
                new_type = 1


    with open(os.path.join(path, 'Contents.json'), 'w') as outfile:
        json.dump(data, outfile, indent=2)
        if new_type == 0:
            infog("成功添加 %s --- r: %d g: %d b: %d" % color)
        elif new_type == 1:
            info("成功替换 %s --- r: %d g: %d b: %d" % color)



if __name__ == '__main__':
    # findfile(sys.argv[1], sys.argv[2])
    # basedir = sys.argv[1]
    print(basedir)
    colorfilePath = findfile(basedir, colorFileName)
    if colorfilePath is not None:
        loadFile(colorfilePath)
        
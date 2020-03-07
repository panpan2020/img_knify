#coding:utf-8
import sys,os
import time,json
from PIL  import Image
import random
import cv2
import threading
import tkinter
import tkinter.messagebox


print(cv2.__version__)

img = {}

class knift(object):
    def __init__(self,args): 
        self._files ={}

        self._readConfig() 
        
        self._cellect()
    
    def _getRandName(self):
        vstr="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = ""
        for i in (1,4):
            n = random.randint(0,len(vstr))            
            result = result +vstr[n]
        ct = int(time.time())
        return "{}_{}".format(result,ct)


    def _isChinese(self,word):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    def _readConfig(self):
         with open("config.json",'r',encoding='utf8') as fp:
            self._data = json.load(fp)
            self._path = self._data["vpath"]
            self._sufix = self._data["suffix"]
    
    def _isSufix(self,sf):
        if isinstance(sf,str): 
            for d in self._sufix:
                if d == sf:
                    return True
        return False

    def _mkDeepPath(self,vname):  
        vname = "{}\\{}".format(self._path,vname)
        if not os.path.exists(vname):
            os.makedirs(vname)
            print("创建目录"+vname+" 成功!")

    def _mkpath(self,vname):  
        vname = "{}\\{}".format(self._path,vname)
        if not os.path.exists(vname):
            os.makedirs(vname)
            print("创建目录"+vname+" 成功!")

    def _isFile(self,vf):
        # vf = "{}\\{}".format(self._path,vf)
        return os.path.isfile(vf)

    def _ifFileExist(self,vf):
        vf = "{}\\{}".format(self._path,vf)
        return os.path.exists(vf)

    def _ifKeyExist(self,vk):
        return vk in self._files

    def _cellect(self):
        vfiles = os.listdir(self._path)
        for ff in vfiles: 
            holeFile = self._path +"\\"+ff
            if self._isFile(holeFile):
                vext = ff.split('.') 
                if self._isSufix(vext[1]) and vext[0] != "config":   
                    if not self._ifKeyExist(ff):  
                        _pngfile = vext[0]+".png"
                        if self._ifFileExist(_pngfile): 
                            self._mkpath(vext[0])
                            self._files[ff] =    vext[0]+".png"  
                            print("==>add file:",ff  )

        print("total file:",len(self._files))

    def _find_last(self,string,str):        
        last_position=-1
        while True:
            position=string.find(str,last_position+1)
            if position==-1:
                return last_position
            last_position=position 

    def _replace(self,vsname):
        return vsname.replace("/","\\")

    def _view(self,imgdata):
        cv2.namedWindow("XXXX",cv2.WINDOW_AUTOSIZE)
        cv2.imshow("png",imgdata)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _show(self,vpng):
        if os.path.exists(vpng):
            src = cv2.imread(vpng)
            self._view(src)

    def _get_red(self,img):
        redImg = img[:,:,2]
        return redImg

    def _get_green(self,img):
        greenImg = img[:,:,1]
        return greenImg

    def _get_blue(self,img):
        blueImg = img[:,:,0]
        return blueImg
 
           

    def _done(self, vname,vimg, data) : 
        # self._view(vimg) 
        x = int( data["x"] )
        y = int(data["y"])
        w = int(data["w"])
        h = int(data["h"])  
        
        print("=>>生成png图片:",vname)

        cropImg = vimg[   y:(y+h) ,x:(x+w)]
        
        # red = self._get_red(img)
        # green = self._get_green(img)
        # blue = self._get_blue(img)

        cv2.imwrite(vname,cropImg, [int(cv2.IMWRITE_PNG_COMPRESSION), 9] )  


    def _start(self, vf,vpng):
        
        vpath = "{}\\{}".format(self._path,vf)
        vpng = "{}\\{}".format(self._path,vpng)

        if not self._isFile(vpath):
            print(vf,"不是json 文件!")
            return
        if not self._isFile(vpng):
            print(vpng,"不是png文件!")
            return    
            
        print("开始读取文件:",vpath," 对应图片文件:", vpng)
        header = vf.split(".")

        img = cv2.imread(vpng,cv2.IMREAD_UNCHANGED) 
        print("图片名:",vpng,"宽:",img.shape[0],"高:",img.shape[1],"像素:",img.shape[2]) 

        # print("r:",self._get_red(img),"g:",self._get_green(img),"b:",self._get_blue(img)) 

        with open(vpath,'r',encoding='utf8') as fp: 
            data = json.load(fp)
            if "mc" in data:
                fr = data["mc"]
                for key in fr:
                    print(key,fr[key]["frameRate"] , len(fr[key]["frames"])  )
                    index = 1
                    for ff in fr[key]["frames"]:
                        creatpath = "{}\\{}".format(  header[0],key )  
                        vsname = "{}\\{}\\{}_{}.png".format(self._path,creatpath,   index,ff["res"])
                        frdata =  data["res"][ ff["res"] ]   
                        
                        self._mkpath(creatpath)

                        self._done(  vsname, img, frdata )  

                        index = index + 1 
            elif "frames" in data:
                fr = data["frames"]
                for key in fr:
                    print(data["file"],"===>",key) 
                    vname = "{}\\{}\\{}.png".format(self._path,header[0],key)
                    self._done(  vname, img, fr[key] )  
            elif "SubTexture" in data:
                index = 1
                st = data["SubTexture"]
                for vd in st:
                    name = vd["name"]
                    if self._isChinese(name):
                        name = self._getRandName();

                    print(data["name"],"===>",name) 
                    creatpath = "{}\\{}".format(  header[0],name )
                    vsname = "{}\\{}\\{}.png".format(self._path,header[0],name)
                    
                    creatpath = self._replace(creatpath)
                    vsname = self._replace(vsname)

                    result = name.find("Particle")
                    if result != -1 : 
                        n =    self._find_last(creatpath,"\\")
                        creatpath = creatpath [:n]              
                        self._mkpath(creatpath)

                    self._done(  vsname, img, {"x":vd["x"],"y":vd["y"],"w":vd["width"],"h":vd["height"]} )  
                    index = index + 1


           

    def run(self):
        for key in self._files: 
            self._start(key,self._files[key])
             

      

if __name__ == "__main__":   
    start = time.time() 
    kv =  knift("D:\workspace\doc\knift")
    kv.run()
    tkinter.messagebox.showinfo("提示","人生苦短，何必那么劳累!\n用时:{} s".format(time.time() - start))
    


#318 Lines
from PyQt4 import QtGui,QtCore
import subprocess,commands,runshell,threading,os,re

class Thread(threading.Thread):

    def __init__(self,command,call_back,args=[]):
        
        self._command = command
        self._call_back = call_back
        self.args = args
        super(Thread,self).__init__()
        
    def run(self):
        
        self._command(*self.args)
        self._call_back(*self.args)

class compilerclass(QtGui.QDialog):

    def __init__(self,parent = None):
        
        global g
        QtGui.QMainWindow.__init__(self,parent)
        self.setGeometry(50,50,600,465)
        self.setWindowTitle("Compile")
        self.listerroutput = QtGui.QListWidget(self)
        self.listerroutput.itemDoubleClicked.connect(self.lstitem_doubleclicked)
        self.lbl1 = QtGui.QLabel('Compiler',self)
        self.lbl2 = QtGui.QLabel('Source File',self)
        self.lbl3 = QtGui.QLabel('Compiled File',self)
        self.lblcompiler = QtGui.QLabel('',self)
        self.lblsource = QtGui.QLabel('',self)
        self.lblcompiled = QtGui.QLabel('',self)
        self.lbl1.setGeometry(10,20,101,17)
        self.lbl2.setGeometry(10,50,81,17)
        self.lbl3.setGeometry(10,80,91,17)
        self.lblcompiler.setGeometry(120,20,600,17)
        self.lblsource.setGeometry(120,50,600,17)
        self.lblcompiled.setGeometry(120,80,600,17)
        self.cmdClose = QtGui.QPushButton('Close',self)
        self.cmdClose.setGeometry(500,433,90,30)
        self.cmdRun = QtGui.QPushButton('Run',self)
        self.cmdRun.setGeometry(410,433,90,30)
        self.cmdRun.show()
        self.connect(self.cmdRun, QtCore.SIGNAL('clicked()'),self.run)
        self.connect(self.cmdClose, QtCore.SIGNAL('clicked()'),self.cancel)              
        self.listerroutput.setGeometry(2,110,590,320)
        self.listerroutput.show()
        self.lbl1.show()
        self.lbl2.show()
        self.lbl3.show()        
        self.lblcompiler.show()
        self.lblsource.show()
        self.lblcompiled.show()
        self.gcccommand = ''
        self.gppcommand = ''
        self.compilerused =''
        self.olddir = ''
        self.previous_run = 0
        self.parent = parent
        self.projtimes=[]
        self.mode = ""
        
    def cancel(self):
        
        self.close()
        
    def getdir(self,filename):

        a = filename.split('/')
        s = ''
        for i in range(0,len(a)-1):
            s = "%s%s%s" % (s ,a[i],'/')
        return s

    def closeEvent(self,event):

        os.chdir(self.olddir)
        
    def run(self):
        
        if self.compilefilename != '':
                if self.previous_run == 0:
                    self.olddir = os.getcwd()
                os.chdir(self.getdir(str(self.compilefilename)))
                runshell.runccppprocess(self.compilefilename,self.olddir)
        self.previous_run +=1

    def lstitem_doubleclicked(self,item):

        text = unicode(item.text(),'utf-8')
        try:
            line_number = int(re.findall(":[0-9]*:",text)[0][1:len(re.findall(":[0-9]*:",text)[0])-1])-1
        except IndexError:
            line_number = 1
        filename = text[0:text.find(":")]
        
        for i in range(len(self.filepatharray)):            
                if self.filepatharray[i] == filename:
                    break
            
        if i != len(self.filepatharray):            
            if self.tabstrackarray == []:
                self.tabs.setCurrentIndex(i)
                cc = self.txtinputarray[i].txtInput.textCursor()
                cc.setLine(line_number)
                self.txtinputarray[i].txtInput.setTextCursor(cc)
                self.txtinputarray[i].txtInput.highlightcurrentline()
            else:                
                for j in range(len(self.tabstrackarray)+1):
                    try:
                        if self.tabstrackarray[j]==i:
                            break
                    except:
                        pass
                if j != len(self.tabstrackarray):                    
                    tabindex = j
                    self.tabs.setCurrentIndex(tabindex)
                    cc = self.txtinputarray[tabindex].txtInput.textCursor()
                    cc.setLine(line_number)
                    self.txtinputarray[tabindex].txtInput.setTextCursor(cc)
                    self.txtinputarray[tabindex].txtInput.highlightcurrentline()
            
    def showerroutput(self,s):

        self.listerroutput.clear()
        err_array = s.split('\n')
        self.listerroutput.addItems(err_array)
        
    def gcccompiler(self,filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray):
        
        self.compilerused ='GCC'
        cmd = ''
        self.getcommand()
        self.mode = mode
        if self.gcccommand != '':            
            commandsplit = self.gcccommand.split(' ')
            self.compilefilename = ''
            self.txtinputarray = txtinputarray
            self.tabs = tabs
            self.filepatharray = filepatharray
            self.tabstrackarray = tabstrackarray
            
            if mode == 'Project':
                for d in commandsplit:
                    if d == '<input>':
                        for s in filename:
                            if '.h' not in s:
                                cmd = cmd + ' ' + str(s)
                    if d == '<output>':
                        cmd = cmd + ' ' + str(compilefilename)
                    if d != '<input>' and d != '<output>':
                        cmd = cmd + ' ' + d
            #print commandsplit
            #print self.gcccommand
            if mode == 'File':
                for d in commandsplit:
                    if d == '<input>':
                        cmd = cmd + ' ' + str(filename)
                    if d == '<output>':
                        cmd = cmd + ' ' + str(compilefilename)
                    if d != '<input>' and d != '<output>':
                        cmd = cmd + ' ' + d
                self.lblsource.setText(filename)
            if cmd !='':            
                self.compilefilename = compilefilename
                thread = Thread(self.runcompiler,self.callback,[cmd,compilefilename])
                thread.start()
                self.lblcompiler.setText('GNU C Compiler(GCC)')
                self.lblcompiled.setText(self.compilefilename)
                self.listerroutput.clear()
                self.listerroutput.addItem('Compiling, Please Wait...')
                self.show()
        else:        
            msg_box = QtGui.QMessageBox.information(self,'GNU C Compiler','Please set command for GNU C Compiler',QtGui.QMessageBox.Ok)

    def callback(self,cmd,compilefilename):

        if cmd.find('-o')!=-1:
            if self.output == '':                                                       
                self.showerroutput('Compilation Successful')
                self.compilefilename = compilefilename            
                self.cmdRun.setEnabled(True)
            else:
                if 'warning' in self.output and 'error' not in self.output:
                    self.cmdRun.setEnabled(True)
                    self.compilefilename = compilefilename
                    self.showerroutput(self.output)        
                else:                
                    self.parent.compilefile = ''
                    self.cmdRun.setDisabled(True)
                    self.showerroutput(self.output)
        else:
            if cmd.find('-c')!=-1:
                if self.output == '':                                 
                    for i,x in enumerate(self.txtinputarray):
                        x.txtInput.setisDirty(False)
                    directory = compilefilename[:compilefilename.rindex('/')]
                    list_dir = os.listdir(directory)
                    commandsplit = self.gppcommand.split(' ')
                    cmd=''
                    for d in commandsplit:
                        if d == '<input>':
                            for s in list_dir:
                                if s.find('.o')!=-1:
                                    cmd = cmd + ' ' + directory+'/'+str(s)                                    
                        if d == '<output>':
                            cmd = cmd + ' ' + str(compilefilename)                        
                        if d != '<input>' and d != '<output>':
                            cmd = cmd + ' ' + d
                    thread = Thread(self.runcompiler,self.callback,[cmd,compilefilename])
                    thread.start()
                    self.compilefilename = compilefilename            
                    self.cmdRun.setEnabled(False)
                else:
                    if 'warning' in self.output and 'error' not in self.output:
                        self.cmdRun.setEnabled(True)
                        self.compilefilename = compilefilename
                        self.showerroutput(self.output)        
                    else:                        
                        self.parent.compilefile = ''
                        self.cmdRun.setDisabled(True)
                        self.showerroutput(self.output)
            
        
    def runcompiler(self,cmd,compilefilename):

        #print "running compiler with command " + cmd
        self.olddir = os.getcwd()
        os.chdir(compilefilename[:compilefilename.rindex('/')+1])
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.output = unicode(p.stderr.read(),'utf-8')
        if self.olddir !='':
            os.chdir(self.olddir)
        
    def gppcompiler(self,filename,compilefilename,mode,txtinputarray,tabs,filepatharray,tabstrackarray,projtimes=[]):
        
        self.compilerused ='G++' 
        cmd = ''
        cmd_lib='' 
        self.getcommand()
        self.mode = mode
        if self.gppcommand !='':            
            commandsplit = self.gppcommand.split(' ')
            self.compilefilename = ''
            self.txtinputarray = txtinputarray
            self.tabs = tabs
            self.filepatharray = filepatharray
            self.tabstrackarray = tabstrackarray
            
            if mode == 'Project':
                for d in commandsplit:
                    if d == '<input>':
                        cmd_lib_old=cmd_lib
                        for s in filename:
                            cmd = cmd + ' ' + str(s)
                            cmd_lib = cmd_lib + ' ' + str(s)
                        if projtimes[0]==0:
                            directory = filename[0][:filename[0].rindex('/')]
                            list_dir = os.listdir(directory)
                            for i,x in enumerate(list_dir):
                                if x.find(".h.gch")!=-1 or x.find(".o")!=-1:
                                    os.remove( os.path.join(directory,list_dir[i]))
                                    
                        if projtimes[0]>0:
                            cmd_lib=cmd_lib_old
                            for i,x in enumerate(txtinputarray):
                                if x.txtInput.getisDirty() == True:                        
                                    cmd_lib = cmd_lib + ' ' +str(filepatharray[tabstrackarray[i]])
                            
                    if d == '<output>':
                        cmd = cmd + ' ' + str(compilefilename)                        
                    if d != '<input>' and d != '<output>':
                        cmd = cmd + ' ' + d
                        cmd_lib = cmd_lib + ' ' +d
                cmd_lib = cmd_lib.replace('-o','-c')                

            if mode == 'File':
                for d in commandsplit:
                    if d == '<input>':
                        cmd = cmd + ' ' + str(filename)
                    if d == '<output>':
                        cmd = cmd + ' ' + str(compilefilename)
                    if d != '<input>' and d != '<output>':
                        cmd = cmd + ' ' + d
                self.lblsource.setText(filename)
            self.compilefilename = compilefilename
            if cmd != '':
                
                if mode== 'File':
                    thread = Thread(self.runcompiler,self.callback,[cmd,compilefilename])
                    thread.start()                    
                else:                                     
                    thread = Thread(self.runcompiler,self.callback,[cmd_lib,compilefilename])
                    thread.start()                   
                        
                self.lblcompiler.setText('GNU C++ Compiler(G++)')
                self.listerroutput.clear()
                self.lblcompiled.setText(self.compilefilename)
                self.listerroutput.addItem('Compiling, Please Wait...')
                self.show()
        else:
            msg_box = QtGui.QMessageBox.information(self,'GNU C++ Compiler','Please set command for GNU C++ Compiler',QtGui.QMessageBox.Ok)
        
    def getcommand(self):

        self.gcccommand = ''
        self.gppcommand = ''
                        
        try:
            
            settings = ''
            settingsfile = open('./settings.ini','r')
            for line in settingsfile:
                settings = settings + line
            settingsarray = settings.split(' ')
            settingsfile.close()
            
            for i in range(settings.index('<gcc>') + len('<gcc>'),settings.index('</gcc>')):
                self.gcccommand = self.gcccommand + settings[i]

            for i in range(settings.index('<g++>') + len('<g++>'),settings.index('</g++>')):
                self.gppcommand = self.gppcommand + settings[i]

        except:
            pass

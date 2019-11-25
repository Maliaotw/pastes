import wx
import time
import subprocess
import os
# import wx.richtext as rt
from pathlib import Path


# 自定義窗口類MyFrame
class MyFrame(wx.Frame):
    temp = ""
    def __init__(self):
        super().__init__(parent=None, title="Pastes", size=(500, 400), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.Center()
        swindow = wx.SplitterWindow(parent=self, id=-1)
        left = wx.Panel(parent=swindow)
        right = wx.Panel(parent=swindow)

        # 設置左右布局的分割窗口left和right
        swindow.SplitVertically(left, right, 200)

        # 設置最小窗格大小，左右布局指左邊窗口大小
        swindow.SetMinimumPaneSize(80)

        # 創建一棵樹
        self.tree = self.CreateTreeCtrl(left)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_click, self.tree)

        # 為left面板設置一個布局管理器
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        left.SetSizer(vbox1)
        vbox1.Add(self.tree, 1, flag=wx.EXPAND | wx.ALL, border=5)

        # 為right面板設置一個布局管理器
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        right.SetSizer((vbox2))
        self.st = wx.TextCtrl(right, 2, style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_RICH2)
        # self.st = wx.TextCtrl(right,2)
        vbox2.Add(self.st, 1, flag=wx.EXPAND | wx.ALL, border=5)

        self.createTimer()

    @property
    def path(self):
        files_path = os.path.join(Path.home(), ".pastes")
        if not os.path.isdir(files_path):
            os.mkdir(files_path)
        return files_path

    def on_click(self, event):
        item = event.GetItem()
        self.st.Clear()
        dirname = self.tree.GetItemText(self.tree.GetItemParent(item))
        name = self.tree.GetItemText(item)
        if dirname in self.notes:
            file = os.path.join(self.path, dirname, name)
            with open(file, 'r') as f:
                self.st.AppendText(f.read())

    def CreateTreeCtrl(self, parent):
        self.tree = wx.TreeCtrl(parent)
        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, size=wx.Size(16, 16)))
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, size=(16, 16)))
        self.tree.AssignImageList(imglist)

        root = self.tree.AddRoot('歷史剪貼簿', image=0)

        today = time.strftime("%Y%m%d")
        if not os.path.isdir(os.path.join(self.path, today)):
            os.mkdir(os.path.join(self.path, today))

        self.data = {}

        notes = os.listdir(self.path)
        self.notes = sorted(notes, reverse=True)
        for name in self.notes:
            item = self.tree.AppendItem(root, name, 0)
            self.data[name] = item
            for i in os.listdir(os.path.join(self.path,name)):
                self.tree.PrependItem(item, i, 1)

        self.tree.Expand(root)
        self.tree.SelectItem(root)

        # 返回樹對象
        return self.tree

    def createTimer(self):
        self.timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._OnReTime, self.timer1)
        self.timer1.Start(1000)

    def load_paste(self):
        return subprocess.check_output('pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')

    def _OnReTime(self, event):
        # 系統時間
        NowTime = time.strftime("%H%M%S")
        # print(NowTime)
        # print(self.load_paste())
        paste = self.load_paste()
        # print(paste)

        today = time.strftime("%Y%m%d")
        if paste != self.temp:
            with open(os.path.join(self.path, today, NowTime), 'w') as f:
                f.write(paste)
            # self.tree.AppendItem()
            # self.tree.PrependItem()
            # 每一筆新增都是倒序
            item = self.tree.PrependItem(self.data[today], NowTime, 1)
            self.tree.SelectItem(item)

            self.temp = paste


class App(wx.App):
    def OnInit(self):
        # 創建窗口對象
        frame = MyFrame()
        frame.Show()
        return True

    def OnExit(self):
        print("應用程序退出")
        return 0


if __name__ == '__main__':
    app = App()
    app.MainLoop()

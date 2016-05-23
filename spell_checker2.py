import wx
from enchant.checker import SpellChecker
from enchant.checker.wxSpellCheckerDialog import wxSpellCheckerDialog

app = wx.PySimpleApp()
text = "This is sme text with a fw speling errors in it. Here are a fw more to tst it ut."
dlg = wxSpellCheckerDialog(None,-1,"")
chkr = SpellChecker("en_US",text)
dlg.SetSpellChecker(chkr)
dlg.Show()
app.MainLoop()
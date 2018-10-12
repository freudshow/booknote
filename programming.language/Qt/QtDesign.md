# <center>**qt widget 相关**</center>

## qtcreator添加widget

语境: 我的项目名称为 *qtserver*

- **正确流程**
	1. 在项目*qtserver*上点击右键->Add New...->Files and Classes->Qt->Qt Designer Form Class->Choose.
	1. 接下来按照提示一步步完成部件的ui和相关.h .cpp文件的创建.
- **遇到的问题**: 刚开始我只选择"Qt Designer Form", qtCreator只帮我创建了一个.ui文件, 并没有创建相关的.h .cpp文件. 我是手动添加的此窗体相关的.h和.cpp文件, 导致在mainwindow模块中找不到此ui的class定义或者实现, 郁闷了很久, 具体原因不明.
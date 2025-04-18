#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyperclip
import keyboard
import threading
import time
import sys


class QuickText:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickText - 快速文本工具")
        # 窗口大小已在main函数中通过center_window设置
        self.root.resizable(True, True)

        # 设置窗口最小尺寸
        self.root.minsize(864, 500)

        # 数据存储路径
        self.data_dir = self.get_data_dir()
        self.data_file = os.path.join(self.data_dir, "presets.json")

        # 预设文本数据
        self.presets = self.load_presets()

        # 创建UI
        self.create_ui()

        # 设置热键监听线程
        self.hotkey_thread = threading.Thread(
            target=self.listen_for_hotkeys, daemon=True)
        self.hotkey_thread.start()

    def get_data_dir(self):
        """获取数据目录，优先使用当前目录"""
        # 首先检查当前工作目录
        current_dir = os.getcwd()
        if os.path.exists(os.path.join(current_dir, "presets.json")):
            return current_dir

        # 如果当前目录下不存在配置文件，则检查exe所在目录
        if getattr(sys, 'frozen', False):
            # 在PyInstaller打包环境中
            exe_dir = os.path.dirname(sys.executable)
            if os.path.exists(os.path.join(exe_dir, "presets.json")):
                return exe_dir

        # 最后使用脚本所在目录或用户数据目录
        if getattr(sys, 'frozen', False):
            # 使用exe所在目录
            app_data = os.path.dirname(sys.executable)
        else:
            # 在开发环境中使用脚本所在目录
            app_data = os.path.dirname(os.path.abspath(__file__))

        return app_data

    def load_presets(self):
        """从JSON文件加载预设文本"""
        default_presets = {"常用": {
            "欢迎使用": "欢迎使用QuickText!\n\n这是您的第一个预设文本。\n您可以在设置中添加更多预设。",
            "网络诊断": "ipconfig /all & ping www.google.com",
            "系统信息": "systeminfo",
            "查看进程": "tasklist | findstr \"chrome\""
        }}

        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # 检查是否为新的分组格式，如果不是则转换
                    if data and not isinstance(next(iter(data.values())), dict):
                        # 转换旧格式到新格式
                        return {"常用": data}
                    return data
            except Exception as e:
                messagebox.showerror("加载错误", f"无法加载预设文件: {str(e)}")
                # 创建默认预设文件
                self.presets = default_presets
                self.save_presets()
                return default_presets
        else:
            # 创建默认预设文件
            self.presets = default_presets
            self.save_presets()
            return default_presets

    def save_presets(self):
        """保存预设文本到JSON文件"""
        try:
            # 确保目录存在
            dir_path = os.path.dirname(self.data_file)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, ensure_ascii=False, indent=2)

            print(f"预设数据已保存到: {self.data_file}")
            return True
        except Exception as e:
            error_msg = f"无法保存预设文件: {str(e)}"
            messagebox.showerror("保存错误", error_msg)
            print(f"保存错误: {str(e)}, 路径: {self.data_file}")

            # 尝试保存到当前工作目录
            try:
                current_dir = os.getcwd()
                fallback_file = os.path.join(current_dir, "presets.json")
                with open(fallback_file, 'w', encoding='utf-8') as f:
                    json.dump(self.presets, f, ensure_ascii=False, indent=2)

                # 更新数据文件路径
                self.data_dir = current_dir
                self.data_file = fallback_file

                print(f"已成功保存到备用位置: {fallback_file}")
                return True
            except Exception as e2:
                print(f"备用保存也失败: {str(e2)}")
                return False

    def create_ui(self):
        """创建用户界面"""
        # 创建一个笔记本小部件（选项卡）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 快速访问选项卡 - 作为默认第一个选项卡
        self.quick_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.quick_frame, text="快速访问")

        # 设置选项卡
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="设置")

        # 创建自定义样式
        self.create_custom_styles()

        # 设置快速访问选项卡
        self.setup_quick_tab()

        # 设置设置选项卡（包含预设管理功能）
        self.setup_settings_tab()

    def create_custom_styles(self):
        """创建自定义样式"""
        style = ttk.Style()

        # 创建没有焦点边框的按钮样式
        style.configure("NoBorder.TButton",
                        focuscolor=style.configure(".")["background"],
                        highlightthickness=0,
                        borderwidth=0)
        style.map("NoBorder.TButton",
                  relief=[('active', 'flat'),
                          ('pressed', 'flat'),
                          ('!disabled', 'flat')],
                  focuscolor=[('active', style.configure(".")["background"]),
                              ('!disabled', style.configure(".")["background"])])

    def setup_quick_tab(self):
        """设置快速访问选项卡"""
        # 创建左右分割的面板
        quick_paned = ttk.PanedWindow(self.quick_frame, orient=tk.HORIZONTAL)
        quick_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧框架
        left_frame = ttk.Frame(quick_paned)
        quick_paned.add(left_frame, weight=1)

        # 添加搜索框
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_frame, text="搜索预设:").pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)

        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        clear_button = ttk.Button(
            search_frame, text="清除", command=self.clear_search)
        clear_button.pack(side=tk.LEFT)

        # 说明标签
        ttk.Label(left_frame, text="点击文本按钮复制内容到剪贴板:").pack(
            anchor=tk.W, pady=(0, 5))

        # 创建一个包含选项卡的笔记本控件，用于分组
        self.groups_notebook = ttk.Notebook(left_frame)
        self.groups_notebook.pack(fill=tk.BOTH, expand=True)

        # 右侧预览框架
        right_frame = ttk.Frame(quick_paned)
        quick_paned.add(right_frame, weight=2)

        # 预览标签
        ttk.Label(right_frame, text="内容预览:").pack(anchor=tk.W, pady=(0, 5))

        # 预览文本区域
        self.preview_text = scrolledtext.ScrolledText(
            right_frame, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)  # 设为只读

        # 设置分组和刷新按钮
        self.setup_group_tabs()

    def setup_group_tabs(self):
        """设置分组选项卡"""
        # 清除现有选项卡
        for tab in self.groups_notebook.tabs():
            self.groups_notebook.forget(tab)

        # 为每个分组创建一个选项卡
        self.group_frames = {}
        self.group_canvases = {}
        self.group_button_frames = {}

        for group_name in self.presets.keys():
            # 创建分组框架
            group_frame = ttk.Frame(self.groups_notebook)
            self.groups_notebook.add(group_frame, text=group_name)
            self.group_frames[group_name] = group_frame

            # 创建滚动区域
            canvas = tk.Canvas(group_frame, width=300, height=200)
            scrollbar = ttk.Scrollbar(
                group_frame, orient=tk.VERTICAL, command=canvas.yview)

            button_frame = ttk.Frame(canvas)

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind_all("<MouseWheel>", lambda event, c=canvas: c.yview_scroll(
                int(-1*(event.delta/120)), "units"))
            canvas.bind_all("<Button-4>", lambda event,
                            c=canvas: c.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda event,
                            c=canvas: c.yview_scroll(1, "units"))

            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 创建按钮框架
            canvas.create_window((0, 0), window=button_frame,
                                 anchor=tk.NW, width=canvas.winfo_width())

            # 更新Canvas的scrollregion
            def update_scrollregion(event, c=canvas):
                c.configure(scrollregion=c.bbox("all"))
                # 调整按钮框架宽度与Canvas宽度一致
                c.itemconfig(c.find_withtag("all")[0], width=c.winfo_width())

            button_frame.bind("<Configure>", update_scrollregion)

            # 存储引用
            self.group_canvases[group_name] = canvas
            self.group_button_frames[group_name] = button_frame

            # 初始化分组的最后宽度记录
            setattr(self, f'last_width_{group_name}', canvas.winfo_width())

        # 刷新所有分组的按钮
        self.refresh_all_group_buttons()

    def refresh_all_group_buttons(self):
        """刷新所有分组的按钮"""
        for group_name, items in self.presets.items():
            self.refresh_group_buttons(group_name, items)

    def refresh_group_buttons(self, group_name, items):
        """刷新指定分组的按钮"""
        self.create_buttons_for_items(group_name, items)

    def on_canvas_resize(self, event, group_name, items):
        """当画布大小变化时重新布局按钮"""
        # 获取新的画布宽度
        new_width = event.width

        # 如果宽度变化超过一定阈值，重新排列按钮
        if abs(new_width - getattr(self, f'last_width_{group_name}', 0)) > 50:
            setattr(self, f'last_width_{group_name}', new_width)
            self.refresh_group_buttons(group_name, items)

    def show_and_copy_preset(self, group_name, name, content):
        """显示预设内容并复制到剪贴板"""
        # 显示预设内容
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, content)
        self.preview_text.config(state=tk.DISABLED)

        # 复制到剪贴板
        self.copy_to_clipboard(content)

    def setup_settings_tab(self):
        """设置选项卡（包含预设管理功能）"""
        # 创建一个笔记本小部件，用于在设置中切换不同功能
        settings_notebook = ttk.Notebook(self.settings_frame)
        settings_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 常规设置选项卡
        general_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(general_frame, text="常规设置")

        # 预设管理选项卡
        self.manage_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(self.manage_frame, text="预设管理")

        # 关于选项卡
        about_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(about_frame, text="关于")

        # 设置常规设置选项卡
        self.setup_general_tab(general_frame)

        # 设置预设管理选项卡
        self.setup_manage_tab()

        # 设置关于选项卡
        self.setup_about_tab(about_frame)

    def setup_general_tab(self, parent_frame):
        """设置常规设置选项卡"""
        # 设置标签
        ttk.Label(parent_frame, text="全局热键设置").pack(
            anchor=tk.W, padx=10, pady=10)

        # 热键说明
        ttk.Label(
            parent_frame, text="按Ctrl+Alt+Q 打开/隐藏应用").pack(anchor=tk.W, padx=10, pady=5)

        # 添加更多设置选项（如果需要）

    def setup_about_tab(self, parent_frame):
        """设置关于选项卡"""
        # 关于信息
        about_inner_frame = ttk.LabelFrame(parent_frame, text="应用信息")
        about_inner_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(about_inner_frame,
                  text="QuickText - 快速文本工具").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Label(about_inner_frame, text="用于快速访问预设文本和命令。").pack(
            anchor=tk.W, padx=5, pady=5)

        # 版本信息
        ttk.Label(about_inner_frame, text="版本: 1.0.0").pack(
            anchor=tk.W, padx=5, pady=5)

    def setup_manage_tab(self):
        """设置预设管理选项卡"""
        # 创建分组管理选项卡
        manage_notebook = ttk.Notebook(self.manage_frame)
        manage_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建预设编辑框架
        edit_frame = ttk.Frame(manage_notebook)
        manage_notebook.add(edit_frame, text="编辑预设")

        # 创建分组管理框架
        group_manage_frame = ttk.Frame(manage_notebook)
        manage_notebook.add(group_manage_frame, text="管理分组")

        # 设置预设编辑界面
        self.setup_preset_edit_tab(edit_frame)

        # 设置分组管理界面
        self.setup_group_manage_tab(group_manage_frame)

    def setup_preset_edit_tab(self, parent_frame):
        """设置预设编辑选项卡"""
        # 创建左右分割面板
        edit_paned = ttk.PanedWindow(parent_frame, orient=tk.HORIZONTAL)
        edit_paned.pack(fill=tk.BOTH, expand=True)

        # 左侧框架
        left_frame = ttk.Frame(edit_paned)
        edit_paned.add(left_frame, weight=1)

        # 分组选择下拉框
        group_frame = ttk.Frame(left_frame)
        group_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(group_frame, text="分组:").pack(side=tk.LEFT)

        self.group_var = tk.StringVar()
        self.group_combo = ttk.Combobox(
            group_frame, textvariable=self.group_var, state="readonly")
        self.group_combo.pack(side=tk.LEFT, fill=tk.X,
                              expand=True, padx=(5, 0))
        self.group_combo.bind("<<ComboboxSelected>>", self.on_group_selected)

        # 更新分组下拉框
        self.update_group_combo()

        # 预设列表标签
        ttk.Label(left_frame, text="预设列表:").pack(anchor=tk.W)

        # 预设列表及滚动条
        self.presets_listbox_frame = ttk.Frame(left_frame)
        self.presets_listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.presets_listbox = tk.Listbox(self.presets_listbox_frame)
        self.presets_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            self.presets_listbox_frame, orient=tk.VERTICAL, command=self.presets_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.presets_listbox.config(yscrollcommand=scrollbar.set)

        # 绑定列表选择事件
        self.presets_listbox.bind('<<ListboxSelect>>', self.on_preset_selected)

        # 按钮框架
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        # 添加、删除、重命名按钮
        ttk.Button(btn_frame, text="添加", command=self.add_preset).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除", command=self.delete_preset).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="重命名", command=self.rename_preset).pack(
            side=tk.LEFT, padx=5)

        # 右侧编辑框架
        right_frame = ttk.Frame(edit_paned)
        edit_paned.add(right_frame, weight=2)

        # 预设内容标签
        ttk.Label(right_frame, text="预设内容:").pack(anchor=tk.W, pady=(0, 5))

        # 编辑区域
        self.content_text = scrolledtext.ScrolledText(
            right_frame, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # 记录当前编辑的预设信息
        self.current_editing = {"group": None, "name": None}

        # 为编辑区域添加焦点事件，防止选择文本时丢失当前编辑的预设信息
        self.content_text.bind("<FocusIn>", self.on_content_focus)

        # 保存按钮
        ttk.Button(right_frame, text="保存内容",
                   command=self.save_content).pack(anchor=tk.E)

        # 初始化
        if len(self.presets) > 0:
            first_group = next(iter(self.presets.keys()))
            self.group_var.set(first_group)
            self.refresh_preset_list()

    def on_content_focus(self, event):
        """当内容区域获得焦点时，确保当前编辑信息不丢失"""
        # 内容区域获得焦点时，不做任何处理
        # 这个方法存在是为了在后续版本中可能需要的扩展
        pass

    def on_preset_selected(self, event):
        """当预设被选中时更新编辑区域"""
        # 如果正在拖动，不处理选择事件
        if getattr(self, 'is_dragging', False):
            return

        try:
            # 获取选中的分组和预设名称
            group = self.group_var.get()
            idx = self.presets_listbox.curselection()[0]
            name = self.presets_listbox.get(idx)

            # 获取内容
            if group in self.presets and name in self.presets[group]:
                content = self.presets[group][name]

                # 清除并设置内容文本
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, content)

                # 记录当前正在编辑的预设信息
                self.current_editing = {"group": group, "name": name}
        except (IndexError, KeyError):
            pass

    def save_content(self):
        """保存编辑区域的内容到选中的预设"""
        # 优先使用记录的当前编辑预设信息
        if self.current_editing["group"] and self.current_editing["name"]:
            group = self.current_editing["group"]
            name = self.current_editing["name"]

            # 确认分组和预设仍然存在
            if group in self.presets and name in self.presets[group]:
                content = self.content_text.get(1.0, tk.END).rstrip()
                self.presets[group][name] = content
                self.save_presets()
                self.refresh_group_buttons(group, self.presets[group])
                messagebox.showinfo("成功", "内容已保存")
                return

        # 如果没有记录的编辑信息，则尝试从列表选择中获取
        try:
            group = self.group_var.get()
            idx = self.presets_listbox.curselection()[0]
            name = self.presets_listbox.get(idx)
            content = self.content_text.get(1.0, tk.END).rstrip()

            self.presets[group][name] = content
            self.save_presets()
            self.refresh_group_buttons(group, self.presets[group])

            # 更新当前编辑信息
            self.current_editing = {"group": group, "name": name}

            messagebox.showinfo("成功", "内容已保存")
        except (IndexError, KeyError):
            messagebox.showerror("错误", "请先选择一个预设")

    def copy_to_clipboard(self, content):
        """复制内容到剪贴板"""
        try:
            pyperclip.copy(content)
            # 缩短消息内容，保留前20个字符
            display_content = content[:20] + \
                "..." if len(content) > 20 else content
            self.show_toast("已复制到剪贴板", display_content)
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")

    def show_toast(self, title, message):
        """显示一个简单的提示框，几秒后自动消失"""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)  # 无边框窗口

        # 计算位置（右下角）
        w, h = 300, 60
        ws = toast.winfo_screenwidth()
        hs = toast.winfo_screenheight()
        x = ws - w - 10
        y = hs - h - 50
        toast.geometry(f"{w}x{h}+{x}+{y}")

        toast.configure(bg="#333333")

        # 标题
        ttk.Label(
            toast,
            text=title,
            background="#333333",
            foreground="white",
            font=("Arial", 10, "bold")
        ).pack(anchor=tk.W, padx=10, pady=(5, 0))

        # 消息
        ttk.Label(
            toast,
            text=message,
            background="#333333",
            foreground="white"
        ).pack(anchor=tk.W, padx=10)

        # 3秒后自动关闭
        toast.after(3000, toast.destroy)

    def listen_for_hotkeys(self):
        """监听全局热键"""
        # 注册Ctrl+Alt+Q打开/隐藏应用
        keyboard.add_hotkey('ctrl+alt+q', self.toggle_visibility)

        # 保持线程运行
        while True:
            time.sleep(0.1)

    def toggle_visibility(self):
        """切换应用窗口的可见性"""
        if self.root.state() == 'normal':
            self.root.withdraw()  # 隐藏窗口
        else:
            self.root.deiconify()  # 显示窗口
            self.root.lift()  # 提升窗口到顶层

    def center_dialog(self, dialog):
        """使对话框居中显示在主窗口上"""
        # 更新主窗口几何信息
        self.root.update_idletasks()

        # 获取主窗口和对话框的尺寸和位置
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()

        # 对话框尺寸
        dialog_width = 300
        dialog_height = 150

        # 计算居中位置
        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2

        # 确保对话框不会超出屏幕边界
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = max(0, min(x, screen_width - dialog_width))
        y = max(0, min(y, screen_height - dialog_height))

        # 设置对话框位置
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def update_group_combo(self):
        """更新分组下拉框"""
        groups = list(self.presets.keys())
        self.group_combo['values'] = groups
        if groups and not self.group_var.get():
            self.group_var.set(groups[0])

    def on_group_selected(self, event):
        """当分组选择改变时刷新预设列表"""
        self.refresh_preset_list()

    def refresh_preset_list(self):
        """刷新预设列表"""
        self.presets_listbox.delete(0, tk.END)

        # 创建已排序的预设列表
        group = self.group_var.get()
        if group and group in self.presets:
            # 使用有序字典保存顺序
            self.current_presets = list(self.presets[group].keys())
            for name in self.current_presets:
                self.presets_listbox.insert(tk.END, name)

        # 绑定拖放事件
        self.presets_listbox.bind('<Button-1>', self.on_list_click)
        self.presets_listbox.bind('<B1-Motion>', self.on_list_drag)
        self.presets_listbox.bind('<ButtonRelease-1>', self.on_list_drop)

    def on_list_click(self, event):
        """处理列表点击事件"""
        # 记录点击的项索引
        self.drag_start_index = self.presets_listbox.nearest(event.y)

        # 高亮选中的项
        if self.drag_start_index >= 0:
            self.presets_listbox.selection_clear(0, tk.END)
            self.presets_listbox.selection_set(self.drag_start_index)
            self.presets_listbox.activate(self.drag_start_index)

        # 标记开始拖动的位置
        self.is_dragging = False
        self.drag_start_y = event.y

    def on_list_drag(self, event):
        """处理列表拖动事件"""
        # 计算拖动距离，只有超过阈值才认为是拖动操作
        drag_distance = abs(event.y - self.drag_start_y)
        if drag_distance < 5:  # 5像素的拖动阈值
            return

        # 标记正在拖动
        self.is_dragging = True

        # 获取当前鼠标位置下的项索引
        drag_current_index = self.presets_listbox.nearest(event.y)

        # 确保有效的索引范围
        if drag_current_index < 0:
            return

        # 显示拖放指示器
        self.presets_listbox.selection_clear(0, tk.END)
        self.presets_listbox.selection_set(drag_current_index)
        self.presets_listbox.activate(drag_current_index)
        self.presets_listbox.see(drag_current_index)  # 确保拖动项可见

    def on_list_drop(self, event):
        """处理列表放下事件"""
        # 如果没有拖动，处理为普通点击
        if not getattr(self, 'is_dragging', False):
            return

        self.is_dragging = False

        # 获取拖放的目标索引
        drop_index = self.presets_listbox.nearest(event.y)

        # 确保有效的索引范围和确实发生了移动
        if drop_index < 0 or self.drag_start_index == drop_index:
            return

        # 获取拖动的项
        group = self.group_var.get()
        if not group or group not in self.presets:
            return

        # 获取预设名称
        try:
            dragged_item = self.current_presets[self.drag_start_index]
        except (IndexError, AttributeError):
            return

        # 从列表中移除
        self.current_presets.pop(self.drag_start_index)

        # 插入到新位置
        if drop_index >= len(self.current_presets):
            self.current_presets.append(dragged_item)
        else:
            self.current_presets.insert(drop_index, dragged_item)

        # 重新排序预设字典
        self.reorder_presets(group, self.current_presets)

        # 刷新列表显示
        self.refresh_preset_list()

        # 选中移动后的项
        self.presets_listbox.selection_set(drop_index)
        self.presets_listbox.activate(drop_index)

        # 刷新快速访问按钮
        self.refresh_group_buttons(group, self.presets[group])

        # 更新内容显示
        name = self.current_presets[drop_index]
        content = self.presets[group][name]
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, content)

    def reorder_presets(self, group, new_order):
        """根据新顺序重新排列预设"""
        if not group or group not in self.presets:
            return

        # 创建一个新的有序字典
        new_presets = {}

        # 按新顺序重建字典
        for name in new_order:
            if name in self.presets[group]:
                new_presets[name] = self.presets[group][name]

        # 确保没有丢失任何预设
        for name, content in self.presets[group].items():
            if name not in new_presets:
                new_presets[name] = content

        # 更新预设字典
        self.presets[group] = new_presets

        # 保存更改
        self.save_presets()

    def setup_group_manage_tab(self, parent_frame):
        """设置分组管理选项卡"""
        # 分组列表标签
        ttk.Label(parent_frame, text="分组列表:").pack(
            anchor=tk.W, padx=10, pady=(10, 5))

        # 分组列表框架
        groups_frame = ttk.Frame(parent_frame)
        groups_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 分组列表
        self.groups_listbox = tk.Listbox(groups_frame)
        self.groups_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            groups_frame, orient=tk.VERTICAL, command=self.groups_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.groups_listbox.config(yscrollcommand=scrollbar.set)

        # 按钮框架
        group_btn_frame = ttk.Frame(parent_frame)
        group_btn_frame.pack(fill=tk.X, padx=10, pady=10)

        # 添加、删除、重命名按钮
        ttk.Button(group_btn_frame, text="添加分组",
                   command=self.add_group).pack(side=tk.LEFT, padx=5)
        ttk.Button(group_btn_frame, text="删除分组",
                   command=self.delete_group).pack(side=tk.LEFT, padx=5)
        ttk.Button(group_btn_frame, text="重命名分组",
                   command=self.rename_group).pack(side=tk.LEFT, padx=5)

        # 刷新分组列表
        self.refresh_groups_list()

        # 绑定拖放事件
        self.groups_listbox.bind('<Button-1>', self.on_group_list_click)
        self.groups_listbox.bind('<B1-Motion>', self.on_group_list_drag)
        self.groups_listbox.bind('<ButtonRelease-1>', self.on_group_list_drop)

    def refresh_groups_list(self):
        """刷新分组列表"""
        self.groups_listbox.delete(0, tk.END)

        # 保存当前分组列表
        self.current_groups = list(self.presets.keys())
        for group in self.current_groups:
            self.groups_listbox.insert(tk.END, group)

    def on_group_list_click(self, event):
        """处理分组列表点击事件"""
        # 记录点击的项索引
        self.group_drag_start_index = self.groups_listbox.nearest(event.y)

        # 高亮选中的项
        if self.group_drag_start_index >= 0:
            self.groups_listbox.selection_clear(0, tk.END)
            self.groups_listbox.selection_set(self.group_drag_start_index)
            self.groups_listbox.activate(self.group_drag_start_index)

        # 标记开始拖动的位置
        self.group_is_dragging = False
        self.group_drag_start_y = event.y

    def on_group_list_drag(self, event):
        """处理分组列表拖动事件"""
        # 计算拖动距离，只有超过阈值才认为是拖动操作
        drag_distance = abs(event.y - self.group_drag_start_y)
        if drag_distance < 5:  # 5像素的拖动阈值
            return

        # 标记正在拖动
        self.group_is_dragging = True

        # 获取当前鼠标位置下的项索引
        drag_current_index = self.groups_listbox.nearest(event.y)

        # 确保有效的索引范围
        if drag_current_index < 0:
            return

        # 显示拖放指示器
        self.groups_listbox.selection_clear(0, tk.END)
        self.groups_listbox.selection_set(drag_current_index)
        self.groups_listbox.activate(drag_current_index)
        self.groups_listbox.see(drag_current_index)  # 确保拖动项可见

    def on_group_list_drop(self, event):
        """处理分组列表放下事件"""
        # 如果没有拖动，不做处理
        if not getattr(self, 'group_is_dragging', False):
            return

        self.group_is_dragging = False

        # 获取拖放的目标索引
        drop_index = self.groups_listbox.nearest(event.y)

        # 确保有效的索引范围和确实发生了移动
        if drop_index < 0 or self.group_drag_start_index == drop_index:
            return

        # 获取拖动的项
        try:
            dragged_group = self.current_groups[self.group_drag_start_index]
        except (IndexError, AttributeError):
            return

        # 从列表中移除
        self.current_groups.pop(self.group_drag_start_index)

        # 插入到新位置
        if drop_index >= len(self.current_groups):
            self.current_groups.append(dragged_group)
        else:
            self.current_groups.insert(drop_index, dragged_group)

        # 重新排序分组字典
        self.reorder_groups(self.current_groups)

        # 刷新列表显示
        self.refresh_groups_list()

        # 选中移动后的项
        self.groups_listbox.selection_set(drop_index)
        self.groups_listbox.activate(drop_index)

        # 刷新选项卡
        self.setup_group_tabs()

    def reorder_groups(self, new_order):
        """根据新顺序重新排列分组"""
        # 创建一个新的有序字典
        new_presets = {}

        # 按新顺序重建字典
        for name in new_order:
            if name in self.presets:
                new_presets[name] = self.presets[name]

        # 确保没有丢失任何分组
        for name, content in self.presets.items():
            if name not in new_presets:
                new_presets[name] = content

        # 更新预设字典
        self.presets = new_presets

        # 保存更改
        self.save_presets()

    def add_group(self):
        """添加新分组"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加分组")
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示对话框
        self.center_dialog(dialog)

        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="分组名称:").pack(pady=(10, 5))

        name_entry = ttk.Entry(frame, width=40)
        name_entry.pack(pady=5)
        name_entry.focus_set()

        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)

        # 确定按钮
        ok_btn = ttk.Button(btn_frame, text="确定", command=lambda: on_ok())
        ok_btn.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_btn = ttk.Button(btn_frame, text="取消", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        def on_ok():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("错误", "请输入分组名称")
                return

            if name in self.presets:
                messagebox.showerror("错误", "分组名称已存在")
                return

            self.presets[name] = {}
            self.save_presets()
            self.refresh_groups_list()
            self.update_group_combo()
            self.setup_group_tabs()
            dialog.destroy()

    def rename_group(self):
        """重命名分组"""
        try:
            idx = self.groups_listbox.curselection()[0]
            old_name = self.groups_listbox.get(idx)

            # 创建对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("重命名分组")
            dialog.transient(self.root)
            dialog.grab_set()

            # 居中显示对话框
            self.center_dialog(dialog)

            frame = ttk.Frame(dialog, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(frame, text="新名称:").pack(pady=(10, 5))

            name_entry = ttk.Entry(frame, width=40)
            name_entry.pack(pady=5)
            name_entry.insert(0, old_name)
            name_entry.focus_set()

            # 按钮框架
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill=tk.X, pady=10)

            # 确定按钮
            ok_btn = ttk.Button(btn_frame, text="确定", command=lambda: on_ok())
            ok_btn.pack(side=tk.LEFT, padx=5)

            # 取消按钮
            cancel_btn = ttk.Button(
                btn_frame, text="取消", command=dialog.destroy)
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            def on_ok():
                new_name = name_entry.get().strip()
                if not new_name:
                    messagebox.showerror("错误", "请输入分组名称")
                    return

                if new_name == old_name:
                    dialog.destroy()
                    return

                if new_name in self.presets:
                    messagebox.showerror("错误", "分组名称已存在")
                    return

                # 重命名分组
                self.presets[new_name] = self.presets[old_name]
                del self.presets[old_name]
                self.save_presets()
                self.refresh_groups_list()
                self.update_group_combo()
                self.setup_group_tabs()
                dialog.destroy()

        except (IndexError, KeyError):
            messagebox.showerror("错误", "请先选择一个分组")

    def delete_group(self):
        """删除所选分组"""
        try:
            idx = self.groups_listbox.curselection()[0]
            name = self.groups_listbox.get(idx)

            if len(self.presets) <= 1:
                messagebox.showerror("错误", "至少需要保留一个分组")
                return

            if messagebox.askyesno("确认", f"确定要删除分组 '{name}'? 这将删除该分组下的所有预设。"):
                del self.presets[name]
                self.save_presets()
                self.refresh_groups_list()
                self.update_group_combo()
                self.setup_group_tabs()
        except (IndexError, KeyError):
            messagebox.showerror("错误", "请先选择一个分组")

    def add_preset(self):
        """添加新预设"""
        group = self.group_var.get()
        if not group:
            messagebox.showerror("错误", "请先选择或创建一个分组")
            return

        # 先清空内容编辑框
        self.content_text.delete(1.0, tk.END)

        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加预设")
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示对话框
        self.center_dialog(dialog)

        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="预设名称:").pack(pady=(10, 5))

        name_entry = ttk.Entry(frame, width=40)
        name_entry.pack(pady=5)
        name_entry.focus_set()

        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)

        # 确定按钮
        ok_btn = ttk.Button(btn_frame, text="确定", command=lambda: on_ok())
        ok_btn.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_btn = ttk.Button(btn_frame, text="取消", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        def on_ok():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("错误", "请输入预设名称")
                return

            if name in self.presets[group]:
                messagebox.showerror("错误", "预设名称已存在")
                return

            # 获取当前编辑区域的内容作为新预设的内容
            # 因为我们已经清空了编辑框，内容将为空
            content = self.content_text.get(1.0, tk.END).rstrip()

            # 添加新预设，内容为空
            self.presets[group][name] = content
            self.save_presets()
            self.refresh_preset_list()
            self.refresh_group_buttons(group, self.presets[group])

            # 选中新添加的预设
            idx = self.current_presets.index(name)
            self.presets_listbox.selection_set(idx)
            self.presets_listbox.activate(idx)

            # 更新当前编辑信息
            self.current_editing = {"group": group, "name": name}

            dialog.destroy()

    def delete_preset(self):
        """删除所选预设"""
        try:
            group = self.group_var.get()
            idx = self.presets_listbox.curselection()[0]
            name = self.presets_listbox.get(idx)

            if messagebox.askyesno("确认", f"确定要删除预设 '{name}'?"):
                del self.presets[group][name]
                self.save_presets()
                self.refresh_preset_list()
                self.refresh_group_buttons(group, self.presets[group])
                self.content_text.delete(1.0, tk.END)

                # 清除当前编辑信息
                self.current_editing = {"group": None, "name": None}
        except (IndexError, KeyError):
            messagebox.showerror("错误", "请先选择一个预设")

    def rename_preset(self):
        """重命名预设"""
        try:
            group = self.group_var.get()
            idx = self.presets_listbox.curselection()[0]
            old_name = self.presets_listbox.get(idx)

            # 创建对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("重命名预设")
            dialog.transient(self.root)
            dialog.grab_set()

            # 居中显示对话框
            self.center_dialog(dialog)

            frame = ttk.Frame(dialog, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(frame, text="新名称:").pack(pady=(10, 5))

            name_entry = ttk.Entry(frame, width=40)
            name_entry.pack(pady=5)
            name_entry.insert(0, old_name)
            name_entry.focus_set()

            # 按钮框架
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill=tk.X, pady=10)

            # 确定按钮
            ok_btn = ttk.Button(btn_frame, text="确定", command=lambda: on_ok())
            ok_btn.pack(side=tk.LEFT, padx=5)

            # 取消按钮
            cancel_btn = ttk.Button(
                btn_frame, text="取消", command=dialog.destroy)
            cancel_btn.pack(side=tk.RIGHT, padx=5)

            def on_ok():
                new_name = name_entry.get().strip()
                if not new_name:
                    messagebox.showerror("错误", "请输入预设名称")
                    return

                if new_name == old_name:
                    dialog.destroy()
                    return

                if new_name in self.presets[group]:
                    messagebox.showerror("错误", "预设名称已存在")
                    return

                # 重命名预设
                self.presets[group][new_name] = self.presets[group][old_name]
                del self.presets[group][old_name]
                self.save_presets()
                self.refresh_preset_list()
                self.refresh_group_buttons(group, self.presets[group])

                # 更新当前编辑信息
                if self.current_editing["group"] == group and self.current_editing["name"] == old_name:
                    self.current_editing["name"] = new_name

                dialog.destroy()

        except (IndexError, KeyError):
            messagebox.showerror("错误", "请先选择一个预设")

    def on_search_change(self, *args):
        """当搜索框内容变化时调用此函数"""
        search_text = self.search_var.get().lower()

        # 如果搜索框为空，恢复所有按钮
        if not search_text:
            self.refresh_all_group_buttons()
            return

        # 保存所有匹配的预设
        matched_presets = {}

        # 创建特殊的搜索结果分组，将所有匹配项合并显示
        search_results = {}

        # 遍历所有分组和预设
        for group_name, items in self.presets.items():
            group_matches = {}

            for name, content in items.items():
                # 搜索名称和内容
                if (search_text in name.lower() or
                        search_text in content.lower()):
                    # 添加到原分组的匹配结果
                    group_matches[name] = content

                    # 添加到搜索结果，使用"分组名:预设名"作为键
                    display_name = f"[{group_name}] {name}"
                    search_results[display_name] = content

            # 如果有匹配项，保存该分组的匹配结果
            if group_matches:
                matched_presets[group_name] = group_matches

        # 首先清除所有分组的按钮
        for group_name in self.presets.keys():
            if group_name in self.group_button_frames:
                button_frame = self.group_button_frames[group_name]
                for widget in button_frame.winfo_children():
                    widget.destroy()

        # 检查是否已有"搜索结果"分组，如果没有则创建
        search_tab_name = "搜索结果"
        if search_tab_name not in self.group_frames:
            # 创建搜索结果选项卡
            search_frame = ttk.Frame(self.groups_notebook)
            self.groups_notebook.add(search_frame, text=search_tab_name)
            self.group_frames[search_tab_name] = search_frame

            # 创建滚动区域
            canvas = tk.Canvas(search_frame, width=300, height=200)
            scrollbar = ttk.Scrollbar(
                search_frame, orient=tk.VERTICAL, command=canvas.yview)

            button_frame = ttk.Frame(canvas)

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind_all("<MouseWheel>", lambda event, c=canvas: c.yview_scroll(
                int(-1*(event.delta/120)), "units"))
            canvas.bind_all("<Button-4>", lambda event,
                            c=canvas: c.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda event,
                            c=canvas: c.yview_scroll(1, "units"))

            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 创建按钮框架
            canvas.create_window((0, 0), window=button_frame,
                                 anchor=tk.NW, width=canvas.winfo_width())

            # 更新Canvas的scrollregion
            def update_scrollregion(event, c=canvas):
                c.configure(scrollregion=c.bbox("all"))
                # 调整按钮框架宽度与Canvas宽度一致
                c.itemconfig(c.find_withtag("all")[0], width=c.winfo_width())

            button_frame.bind("<Configure>", update_scrollregion)

            # 存储引用
            self.group_canvases[search_tab_name] = canvas
            self.group_button_frames[search_tab_name] = button_frame

            # 初始化分组的最后宽度记录
            setattr(
                self, f'last_width_{search_tab_name}', canvas.winfo_width())

        # 显示搜索结果
        if search_results:
            # 选中搜索结果选项卡
            for i, tab_id in enumerate(self.groups_notebook.tabs()):
                if self.groups_notebook.tab(tab_id, "text") == search_tab_name:
                    self.groups_notebook.select(i)
                    break

            # 创建一个特殊的show_and_copy_preset函数，用于搜索结果项
            def create_search_result_handler(display_name, content):
                # 从显示名称提取原始分组和名称
                parts = display_name.split('] ', 1)
                if len(parts) == 2:
                    group = parts[0][1:]  # 去掉开头的'['
                    name = parts[1]
                    return lambda: self.show_and_copy_preset(group, name, content)
                else:
                    return lambda: self.copy_to_clipboard(content)

            # 显示搜索结果
            self.create_buttons_for_items(
                search_tab_name, search_results, create_search_result_handler)

    def create_buttons_for_items(self, group_name, items, command_func=None):
        """为指定的项目创建按钮"""
        if group_name not in self.group_button_frames:
            return

        button_frame = self.group_button_frames[group_name]
        canvas = self.group_canvases[group_name]

        # 清除现有按钮
        for widget in button_frame.winfo_children():
            widget.destroy()

        # 创建按钮流布局
        button_frame.grid_columnconfigure(0, weight=1)

        # 获取canvas的当前宽度
        canvas_width = canvas.winfo_width()
        if canvas_width <= 1:  # 初始时可能还没有宽度
            canvas_width = canvas.winfo_reqwidth()
            if canvas_width <= 1:
                canvas_width = 300  # 默认初始宽度

        # 按钮配置
        min_btn_width = 150  # 按钮最小宽度
        btn_padding = 10  # 按钮间距

        # 创建临时标签计算文本宽度
        temp_label = tk.Label(button_frame, font=("Arial", 9))

        # 创建按钮
        x, y = 0, 0
        max_width = 0

        for name, content in items.items():
            # 计算文本宽度
            temp_label.config(text=name)
            temp_label.update_idletasks()
            text_width = temp_label.winfo_width() + 30  # 添加一些额外空间
            btn_width = max(min_btn_width, text_width)

            # 创建按钮框架以容纳按钮
            btn_frame = ttk.Frame(button_frame, width=btn_width)

            # 检查是否需要换行
            if x > 0 and (x * btn_width + x * btn_padding) > canvas_width:
                x = 0
                y += 1

            # 创建按钮并放置
            if command_func is not None:
                command = command_func(name, content)
            else:
                def command(g=group_name, n=name,
                            c=content): return self.show_and_copy_preset(g, n, c)

            btn = tk.Button(
                btn_frame,
                text=name,
                command=command,
                highlightthickness=0,
                bd=0,
                relief="flat",
                takefocus=0,
                bg="#e8e8e8",  # 浅灰背景
                fg="#333333",  # 深色文字
                activebackground="#d0d0d0",  # 点击时的背景色
                activeforeground="#000000",  # 点击时的文字颜色
                padx=10,
                pady=5,
                font=("Arial", 9),
                wraplength=0  # 设置为0禁止文本自动换行
            )
            btn.pack(fill=tk.BOTH, expand=True)

            # 放置按钮框架
            btn_frame.grid(row=y, column=x, padx=5, pady=3, sticky="nsew")

            # 配置网格权重
            button_frame.grid_rowconfigure(y, weight=1)
            button_frame.grid_columnconfigure(x, weight=1)

            # 更新位置
            x += 1
            max_width = max(max_width, x)

        # 销毁临时标签
        temp_label.destroy()

        # 添加窗口大小变化事件处理
        canvas.bind("<Configure>", lambda e, g=group_name,
                    i=items: self.on_canvas_resize(e, g, i))

    def clear_search(self):
        """清除搜索框内容"""
        self.search_var.set("")
        # 刷新所有按钮
        self.refresh_all_group_buttons()

        # 移除搜索结果选项卡
        search_tab_name = "搜索结果"
        for i, tab_id in enumerate(self.groups_notebook.tabs()):
            if self.groups_notebook.tab(tab_id, "text") == search_tab_name:
                self.groups_notebook.forget(tab_id)
                if search_tab_name in self.group_frames:
                    del self.group_frames[search_tab_name]
                if search_tab_name in self.group_canvases:
                    del self.group_canvases[search_tab_name]
                if search_tab_name in self.group_button_frames:
                    del self.group_button_frames[search_tab_name]
                break


def center_window(window, width=864, height=500):
    """使窗口居中显示在屏幕上"""
    # 获取屏幕宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 计算居中位置
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # 设置窗口位置和大小
    window.geometry(f"{width}x{height}+{x}+{y}")


def main():
    """程序主入口"""
    root = tk.Tk()
    root.title("QuickText - 快速文本工具")

    # 设置窗口居中显示
    center_window(root)

    # 设置图标
    try:
        # 尝试直接加载图标文件
        icon_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "tool.png")
        if os.path.exists(icon_path):
            icon_img = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon_img)
        # 对于打包后的环境，可能需要特殊处理
        elif getattr(sys, 'frozen', False):
            # 在PyInstaller打包环境中
            base_path = sys._MEIPASS if hasattr(
                sys, '_MEIPASS') else os.path.dirname(sys.executable)
            icon_path = os.path.join(base_path, "tool.png")
            if os.path.exists(icon_path):
                icon_img = tk.PhotoImage(file=icon_path)
                root.iconphoto(True, icon_img)
    except Exception as e:
        print(f"加载图标出错: {e}")

    app = QuickText(root)
    root.mainloop()


if __name__ == "__main__":
    main()

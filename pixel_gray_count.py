import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class PixelGrayReader:
    def __init__(self, root):
        self.root = root
        self.root.title("图片灰度值读取器")
        self.root.geometry("800x600")
        
        # 图片相关变量
        self.original_image = None
        self.gray_image = None
        self.display_image = None
        self.photo = None
        self.scale_factor = 1.0
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 顶部按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # 打开图片按钮
        open_btn = tk.Button(button_frame, text="打开图片", command=self.open_image)
        open_btn.pack(side=tk.LEFT, padx=5)
        
        # 缩放按钮
        zoom_in_btn = tk.Button(button_frame, text="放大", command=self.zoom_in)
        zoom_in_btn.pack(side=tk.LEFT, padx=5)
        
        zoom_out_btn = tk.Button(button_frame, text="缩小", command=self.zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(button_frame, text="重置", command=self.reset_zoom)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # 信息显示框架
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        
        self.info_label = tk.Label(info_frame, text="请打开一张图片", font=("Arial", 12))
        self.info_label.pack()
        
        # 图片显示画布
        self.canvas = tk.Canvas(self.root, bg="white", width=750, height=500)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # 绑定鼠标点击事件
        self.canvas.bind("<Button-1>", self.on_click)
        
        # 滚动条
        scrollbar_v = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_h = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif")]
        )
        
        if file_path:
            try:
                # 读取原始图片
                self.original_image = cv2.imread(file_path)
                if self.original_image is None:
                    messagebox.showerror("错误", "无法读取图片文件")
                    return
                
                # 转换为灰度图
                self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
                
                # 重置缩放
                self.scale_factor = 1.0
                
                # 显示图片
                self.update_display()
                
                # 更新信息
                height, width = self.gray_image.shape
                self.info_label.config(text=f"图片已加载 - 尺寸: {width}x{height} - 点击图片获取灰度值")
                
            except Exception as e:
                messagebox.showerror("错误", f"打开图片时发生错误: {str(e)}")
    
    def update_display(self):
        if self.gray_image is None:
            return
        
        # 根据缩放因子调整图片大小
        height, width = self.gray_image.shape
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)
        
        # 调整图片大小
        if self.scale_factor != 1.0:
            self.display_image = cv2.resize(self.gray_image, (new_width, new_height))
        else:
            self.display_image = self.gray_image.copy()
        
        # 转换为PIL图片格式用于显示
        pil_image = Image.fromarray(self.display_image)
        self.photo = ImageTk.PhotoImage(pil_image)
        
        # 清除画布并显示新图片
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # 更新画布滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def zoom_in(self):
        if self.gray_image is not None:
            self.scale_factor *= 1.2
            self.update_display()
            self.update_info_label()
    
    def zoom_out(self):
        if self.gray_image is not None:
            self.scale_factor /= 1.2
            self.update_display()
            self.update_info_label()
    
    def reset_zoom(self):
        if self.gray_image is not None:
            self.scale_factor = 1.0
            self.update_display()
            self.update_info_label()
    
    def update_info_label(self):
        if self.gray_image is not None:
            height, width = self.gray_image.shape
            self.info_label.config(
                text=f"图片尺寸: {width}x{height} - 缩放: {self.scale_factor:.1f}x - 点击图片获取灰度值"
            )
    
    def on_click(self, event):
        if self.display_image is None:
            return
        
        # 获取点击位置在画布上的坐标
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 转换为原始图片坐标
        original_x = int(canvas_x / self.scale_factor)
        original_y = int(canvas_y / self.scale_factor)
        
        # 检查坐标是否在图片范围内
        height, width = self.gray_image.shape
        if 0 <= original_x < width and 0 <= original_y < height:
            # 获取灰度值
            gray_value = self.gray_image[original_y, original_x]
            
            # 更新信息显示
            self.info_label.config(
                text=f"位置: ({original_x}, {original_y}) - 灰度值: {gray_value} - 缩放: {self.scale_factor:.1f}x"
            )
            
            # 在图片上标记点击位置
            self.mark_clicked_position(canvas_x, canvas_y)
        else:
            self.info_label.config(text="点击位置超出图片范围")
    
    def mark_clicked_position(self, x, y):
        # 删除之前的标记
        self.canvas.delete("click_marker")
        
        # 在点击位置画一个红色圆圈
        self.canvas.create_oval(
            x-3, y-3, x+3, y+3,
            outline="red", width=2,
            tags="click_marker"
        )

def main():
    root = tk.Tk()
    app = PixelGrayReader(root)
    root.mainloop()

if __name__ == "__main__":
    main()

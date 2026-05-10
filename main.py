import tkinter as tk
from tkinter import messagebox
import math
import winsound
import json
import os
import threading
import time
from datetime import datetime
from ctypes import windll
from PIL import Image, ImageDraw

try:
    import pystray
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

class PomodoroApp:
    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser('~'), '.pomodoro_settings.json')
        self.default_settings = {
            'work_time': 25,
            'short_break': 5,
            'long_break': 15,
            'pomodoros_before_long': 4,
            'auto_start_breaks': True,
            'sound_enabled': True,
            'window_geometry': '480x650'
        }
        self.settings = self.load_settings()
        
        self.tray_icon = None
        
        self.state = {
            'mode': 'work',
            'time_left': self.settings['work_time'] * 60,
            'total_time': self.settings['work_time'] * 60,
            'is_running': False,
            'completed_pomodoros': 0,
            'timer_thread': None,
            'stop_event': threading.Event()
        }
        
        self.colors = {
            'bg': '#1E1E24',
            'card_bg': '#1E1E24',
            'work_primary': '#F25F78',
            'break_primary': '#4ECDC4',
            'text': '#FFFFFF',
            'text_secondary': '#A0A0B0',
            'progress_bg': '#2A2A35',
            'btn_secondary': '#2A2A35'
        }
        
        self.setup_window()
        self.create_ui()
        self.update_display()
        
        if HAS_PYSTRAY:
            self.create_system_tray()
    
    def create_tray_icon_image(self):
        size = (64, 64)
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        primary = self.get_primary_color()
        r, g, b = int(primary[1:3], 16), int(primary[3:5], 16), int(primary[5:7], 16)
        draw.ellipse([2, 2, 62, 62], fill=(r, g, b, 255))
        draw.ellipse([8, 8, 56, 56], fill=(255, 255, 255, 200))
        return image
    
    def create_system_tray(self):
        icon_image = self.create_tray_icon_image()
        
        self.tray_icon = pystray.Icon('pomodoro')
        self.tray_icon.title = '番茄钟'
        self.tray_icon.icon = icon_image
        self.tray_icon.visible = True
        
        self.tray_icon.menu = pystray.Menu(
            pystray.MenuItem('显示主窗口', self.show_from_tray, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('开始/暂停', lambda: self.root.after(0, self.toggle_timer)),
            pystray.MenuItem('重置', lambda: self.root.after(0, self.reset_timer)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('退出', self.quit_from_tray)
        )
        
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()
        
        print("托盘图标已创建，请在任务栏右下角 ^ 箭头处查找")
    
    def update_tray_tooltip(self):
        if self.tray_icon:
            minutes = self.state['time_left'] // 60
            seconds = self.state['time_left'] % 60
            time_str = f'{minutes:02d}:{seconds:02d}'
            mode_str = '专注' if self.state['mode'] == 'work' else '休息'
            status_str = '运行中' if self.state['is_running'] else '暂停'
            self.tray_icon.title = f'{mode_str} {time_str} - {status_str}'
    
    def show_from_tray(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def quit_from_tray(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.pause_timer()
        self.settings['window_geometry'] = self.root.geometry()
        self.save_settings()
        self.root.destroy()
        
    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    return {**self.default_settings, **saved}
        except Exception as e:
            print(f"加载设置失败: {e}")
        return self.default_settings.copy()
    
    def save_settings(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def setup_window(self):
        self.root = tk.Tk()
        self.root.title('番茄钟')
        self.root.geometry(self.settings.get('window_geometry', '480x650'))
        self.root.minsize(400, 600)
        self.root.maxsize(600, 800)
        self.root.configure(bg=self.colors['bg'])
        self.root.resizable(True, True)
        
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
    
    def get_primary_color(self):
        if self.state['mode'] == 'work':
            return self.colors['work_primary']
        return self.colors['break_primary']
    
    def darken_color(self, color, factor):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def create_ui(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors['card_bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        self.create_header()
        self.create_mode_selector()
        self.create_mode_label()
        self.create_timer_display()
        self.create_controls()
        self.create_pomodoro_counter()
        self.create_settings_button()
    
    def create_header(self):
        self.header_label = tk.Label(
            self.main_frame,
            text='番茄钟',
            bg=self.colors['card_bg'],
            fg=self.get_primary_color(),
            font=('Microsoft YaHei UI', 20, 'bold')
        )
        self.header_label.pack(pady=(0, 10))
    
    def create_mode_selector(self):
        self.mode_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'])
        self.mode_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.mode_buttons = {}
        modes = [('专注', 'work'), ('短休息', 'short_break'), ('长休息', 'long_break')]
        
        for text, mode in modes:
            btn = tk.Button(
                self.mode_frame,
                text=text,
                bg=self.colors['card_bg'],
                fg=self.get_primary_color(),
                font=('Microsoft YaHei UI', 10, 'bold'),
                bd=0,
                cursor='hand2',
                highlightthickness=0,
                command=lambda m=mode: self.switch_mode(m)
            )
            self.mode_buttons[mode] = btn
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.update_mode_buttons()
    
    def create_mode_label(self):
        self.mode_label = tk.Label(
            self.main_frame,
            text='工作时间',
            bg=self.colors['card_bg'],
            fg=self.get_primary_color(),
            font=('Microsoft YaHei UI', 10)
        )
        self.mode_label.pack(pady=(0, 15))
    
    def create_timer_display(self):
        self.timer_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'])
        self.timer_frame.pack(fill=tk.X, pady=20)
        
        self.canvas_size = 250
        self.center = self.canvas_size // 2
        self.radius = 90
        
        self.canvas = tk.Canvas(
            self.timer_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=self.colors['card_bg'],
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(pady=10)
        
        self.time_label = tk.Label(
            self.timer_frame,
            text='25:00',
            bg=self.colors['card_bg'],
            fg=self.get_primary_color(),
            font=('Microsoft YaHei UI', 36, 'bold')
        )
        self.time_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def draw_progress_ring(self):
        self.canvas.delete('all')
        
        self.canvas.create_oval(
            self.center - self.radius - 8, self.center - self.radius - 8,
            self.center + self.radius + 8, self.center + self.radius + 8,
            outline=self.colors['progress_bg'],
            width=12,
            fill=''
        )
        
        if self.state['total_time'] > 0:
            progress = self.state['time_left'] / self.state['total_time']
            extent = 360 * progress
            
            start_angle = 90
            
            if extent > 0:
                self.canvas.create_arc(
                    self.center - self.radius - 8, self.center - self.radius - 8,
                    self.center + self.radius + 8, self.center + self.radius + 8,
                    start=start_angle,
                    extent=extent,
                    outline=self.get_primary_color(),
                    width=12,
                    style=tk.ARC
                )
    
    def create_controls(self):
        self.controls_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'])
        self.controls_frame.pack(fill=tk.X, pady=20)
        
        self.start_pause_btn = tk.Button(
            self.controls_frame,
            text='开始',
            bg=self.get_primary_color(),
            fg='white',
            font=('Microsoft YaHei UI', 12, 'bold'),
            bd=0,
            cursor='hand2',
            highlightthickness=0,
            command=self.toggle_timer,
            width=15
        )
        self.start_pause_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.reset_btn = tk.Button(
            self.controls_frame,
            text='重置',
            bg=self.colors['btn_secondary'],
            fg=self.colors['text_secondary'],
            font=('Microsoft YaHei UI', 11),
            bd=0,
            cursor='hand2',
            highlightthickness=0,
            command=self.reset_timer,
            width=10
        )
        self.reset_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.skip_btn = tk.Button(
            self.controls_frame,
            text='跳过',
            bg=self.colors['btn_secondary'],
            fg=self.colors['text_secondary'],
            font=('Microsoft YaHei UI', 11),
            bd=0,
            cursor='hand2',
            highlightthickness=0,
            command=self.skip_to_next,
            width=10
        )
        self.skip_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    def create_pomodoro_counter(self):
        self.counter_frame = tk.Frame(self.main_frame, bg=self.colors['card_bg'])
        self.counter_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.counter_label = tk.Label(
            self.counter_frame,
            text='已完成: 0 个番茄',
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            font=('Microsoft YaHei UI', 10)
        )
        self.counter_label.pack(pady=10)
    
    def create_settings_button(self):
        self.settings_btn = tk.Button(
            self.main_frame,
            text='⚙️ 设置',
            bg=self.colors['btn_secondary'],
            fg=self.colors['text_secondary'],
            font=('Microsoft YaHei UI', 10),
            bd=0,
            cursor='hand2',
            highlightthickness=0,
            command=self.open_settings
        )
        self.settings_btn.pack(side=tk.BOTTOM, pady=10)
    
    def update_mode_buttons(self):
        primary = self.get_primary_color()
        for mode, btn in self.mode_buttons.items():
            if mode == self.state['mode']:
                btn.configure(bg=primary, fg='white')
            else:
                btn.configure(bg=self.colors['card_bg'], fg=primary)
    
    def update_display(self):
        minutes = self.state['time_left'] // 60
        seconds = self.state['time_left'] % 60
        time_str = f'{minutes:02d}:{seconds:02d}'
        
        mode_labels = {'work': '工作时间', 'short_break': '短休息', 'long_break': '长休息'}
        mode_label = mode_labels.get(self.state['mode'], '工作时间')
        
        self.time_label.configure(text=time_str, fg=self.get_primary_color())
        self.header_label.configure(fg=self.get_primary_color())
        self.mode_label.configure(fg=self.get_primary_color())
        self.root.title(f'{time_str} - {mode_label}')
        
        self.draw_progress_ring()
        self.update_start_pause_button()
        self.update_mode_buttons()
        
        if HAS_PYSTRAY:
            self.update_tray_tooltip()
    
    def update_start_pause_button(self):
        if self.state['is_running']:
            self.start_pause_btn.configure(text='暂停', bg=self.get_primary_color())
        else:
            if self.state['time_left'] < self.state['total_time']:
                self.start_pause_btn.configure(text='继续', bg=self.get_primary_color())
            else:
                self.start_pause_btn.configure(text='开始', bg=self.get_primary_color())
    
    def toggle_timer(self):
        if self.state['is_running']:
            self.pause_timer()
        else:
            self.start_timer()
    
    def start_timer(self):
        self.state['is_running'] = True
        self.state['stop_event'].clear()
        self.update_display()
        
        self.state['timer_thread'] = threading.Thread(target=self._timer_loop, daemon=True)
        self.state['timer_thread'].start()
    
    def _timer_loop(self):
        while self.state['time_left'] > 0 and not self.state['stop_event'].is_set():
            time.sleep(1)
            if self.state['stop_event'].is_set():
                break
            self.state['time_left'] -= 1
            self.root.after(0, self.update_display)
        
        if self.state['time_left'] <= 0 and not self.state['stop_event'].is_set():
            self.root.after(0, self.complete)
    
    def pause_timer(self):
        self.state['is_running'] = False
        self.state['stop_event'].set()
        self.update_display()
    
    def reset_timer(self):
        self.pause_timer()
        
        if self.state['mode'] == 'work':
            self.state['time_left'] = self.settings['work_time'] * 60
        elif self.state['mode'] == 'short_break':
            self.state['time_left'] = self.settings['short_break'] * 60
        else:
            self.state['time_left'] = self.settings['long_break'] * 60
        
        self.state['total_time'] = self.state['time_left']
        self.update_display()
    
    def complete(self):
        self.pause_timer()
        self.play_sound()
        
        if self.state['mode'] == 'work':
            self.state['completed_pomodoros'] += 1
            self.counter_label.configure(text=f'已完成: {self.state["completed_pomodoros"]} 个番茄')
            
            self.show_notification('番茄钟', '专注时间完成！休息一下吧 🎉')
            
            if self.state['completed_pomodoros'] % self.settings['pomodoros_before_long'] == 0:
                self.switch_mode('long_break', self.settings['auto_start_breaks'])
            else:
                self.switch_mode('short_break', self.settings['auto_start_breaks'])
        else:
            self.show_notification('番茄钟', '休息结束！开始新的专注吧 💪')
            self.switch_mode('work', False)
    
    def skip_to_next(self):
        self.pause_timer()
        if self.state['mode'] == 'work':
            self.switch_mode('short_break', False)
        else:
            self.switch_mode('work', False)
    
    def switch_mode(self, mode, auto_start=False):
        self.pause_timer()
        self.state['mode'] = mode
        
        if mode == 'work':
            self.state['time_left'] = self.settings['work_time'] * 60
        elif mode == 'short_break':
            self.state['time_left'] = self.settings['short_break'] * 60
        else:
            self.state['time_left'] = self.settings['long_break'] * 60
        
        self.state['total_time'] = self.state['time_left']
        self.update_display()
        
        if auto_start:
            self.root.after(500, self.start_timer)
    
    def play_sound(self):
        if not self.settings['sound_enabled']:
            return
        
        try:
            frequency = 880
            duration = 500
            winsound.Beep(frequency, duration)
            self.root.after(600, lambda: winsound.Beep(frequency, 300))
        except:
            pass
    
    def show_notification(self, title, message):
        try:
            self.root.wm_attributes('-topmost', True)
            self.root.after(0, lambda: messagebox.showinfo(title, message))
            self.root.wm_attributes('-topmost', False)
        except:
            pass
    
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title('设置')
        settings_window.geometry('350x400')
        settings_window.resizable(False, False)
        settings_window.configure(bg=self.colors['card_bg'])
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        center_x = self.root.winfo_x() + (self.root.winfo_width() - 350) // 2
        center_y = self.root.winfo_y() + (self.root.winfo_height() - 400) // 2
        settings_window.geometry(f'+{center_x}+{center_y}')
        
        fields = [
            ('专注时长 (分钟)', 'work_time', 1, 60),
            ('短休息 (分钟)', 'short_break', 1, 30),
            ('长休息 (分钟)', 'long_break', 1, 60),
            ('长休息前的番茄数', 'pomodoros_before_long', 1, 10)
        ]
        
        entries = {}
        for i, (label, key, min_val, max_val) in enumerate(fields):
            row_frame = tk.Frame(settings_window, bg=self.colors['card_bg'])
            row_frame.pack(fill=tk.X, padx=20, pady=8)
            
            tk.Label(row_frame, text=label, bg=self.colors['card_bg'], fg=self.colors['text_secondary'], font=('Microsoft YaHei UI', 10)).pack(side=tk.LEFT)
            
            entry = tk.Entry(row_frame, width=10, justify=tk.CENTER, bg=self.colors['btn_secondary'], fg=self.colors['text'], font=('Microsoft YaHei UI', 10), bd=0, highlightthickness=1, highlightcolor=self.get_primary_color())
            entry.insert(0, str(self.settings[key]))
            entry.pack(side=tk.RIGHT)
            entries[key] = (entry, min_val, max_val)
        
        checkbox_vars = {}
        for i, (label, key) in enumerate([('自动开始休息', 'auto_start_breaks'), ('启用提示音', 'sound_enabled')]):
            row_frame = tk.Frame(settings_window, bg=self.colors['card_bg'])
            row_frame.pack(fill=tk.X, padx=20, pady=8)
            
            var = tk.BooleanVar(value=self.settings[key])
            checkbox_vars[key] = var
            tk.Checkbutton(row_frame, text=label, variable=var, bg=self.colors['card_bg'], fg=self.colors['text_secondary'], font=('Microsoft YaHei UI', 10), selectcolor=self.colors['card_bg']).pack(anchor=tk.W)
        
        def save():
            valid = True
            new_settings = {}
            
            for key, (entry, min_val, max_val) in entries.items():
                try:
                    value = int(entry.get())
                    if value < min_val or value > max_val:
                        messagebox.showwarning('验证失败', f'{key} 必须在 {min_val}-{max_val} 之间')
                        valid = False
                        break
                    new_settings[key] = value
                except ValueError:
                    messagebox.showwarning('验证失败', f'请输入有效的数字')
                    valid = False
                    break
            
            if valid:
                for key, var in checkbox_vars.items():
                    new_settings[key] = var.get()
                
                self.settings.update(new_settings)
                self.save_settings()
                
                self.reset_timer()
                
                settings_window.destroy()
        
        tk.Button(settings_window, text='保存', bg=self.get_primary_color(), fg='white', font=('Microsoft YaHei UI', 11, 'bold'), bd=0, cursor='hand2', highlightthickness=0, command=save, width=20).pack(pady=20)
    
    def on_close(self):
        if HAS_PYSTRAY and self.tray_icon:
            self.root.withdraw()
            self.root.after(0, lambda: messagebox.showinfo('番茄钟', '番茄钟已最小化到系统托盘，点击托盘图标可重新打开'))
        else:
            self.pause_timer()
            self.settings['window_geometry'] = self.root.geometry()
            self.save_settings()
            self.root.destroy()
    
    def run(self):
        self.root.bind('<space>', lambda e: self.toggle_timer())
        self.root.bind('<Control-r>', lambda e: self.reset_timer())
        self.root.mainloop()

if __name__ == '__main__':
    app = PomodoroApp()
    app.run()

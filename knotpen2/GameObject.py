import pygame
from i18n import _

# handle_mouse_down(button, x, y): 鼠标按下回调函数
#   button: 1=左键, 2=中键, 3=右键, 4=滚轮上滚, 5=滚轮下滚
# handle_mouse_up(button, x, y): 鼠标抬起回调函数
# handle_key_down(key, mod, unicode): 键盘按键按下回调函数
# handle_key_up(key, mod): 键盘按键释放回调函数
# handle_quit(): 页面关闭回调函数，返回页面是否要继续运行
# draw_screen(screen): 用于绘制屏幕内容
# die_check(): 检测游戏当前是否应该被关闭, True: 是, False: 否

class GameObject:
    def __init__(self) -> None:
        self.quit_cnt = 0
        self.mouse_x = 0
        self.mouse_y = 0

    def get_window_caption(self) -> str:
        return "GameObject::get_window_caption"

    def draw_screen(self, screen):
        screen.fill((255, 255, 255)) # 填充白色背景

    def handle_mouse_down(self, button, x, y):
        self.mouse_x, self.mouse_y = x, y
        button_names = {1: _("左键"), 2: _("中键"), 3: _("右键"), 4: _("滚轮上滚"), 5: _("滚轮下滚")}
        button_name = button_names.get(button, _("未知按钮") + f"({button})")
        print(_("鼠标按下: ") + f"{button_name} @ ({x}, {y})")

        # 示例：处理键盘事件的回调函数
    def handle_key_down(self, key, mod, unicode):
        key_name = pygame.key.name(key)
        modifiers = []
        if mod & pygame.KMOD_SHIFT:
            modifiers.append("Shift")
        if mod & pygame.KMOD_CTRL:
            modifiers.append("Ctrl")
        if mod & pygame.KMOD_ALT:
            modifiers.append("Alt")
        
        mod_str = "+".join(modifiers) if modifiers else _("无修饰键")
        print(_("按键按下: ") + f"{key_name} (Unicode: {unicode}, " + _("修饰键: ") + f"{mod_str})")
    
    def handle_key_up(self, key, mod):
        key_name = pygame.key.name(key)
        print(_("按键释放: ") + f"{key_name}")
    
    def handle_mouse_up(self, button, x, y):
        self.mouse_x, self.mouse_y = x, y
        button_names = {1: _("左键"), 2: _("中键"), 3: _("右键")}
        if button in button_names:  # 只处理真正的按键抬起事件
            print(_("鼠标抬起：") + f"{button_names[button]} @ ({x}, {y})")
    
    def handle_quit(self):
        self.quit_cnt += 1
        print(_("尝试关闭窗口（第 %d 次）") % self.quit_cnt)
    
    def get_mouse_pos(self): # 获得鼠标的位置
        return self.mouse_x, self.mouse_y

    def die_check(self):
        if self.quit_cnt >= 3:
            print(_("尝试关闭窗口（第 %d 次），游戏退出") % self.quit_cnt)
            return True # 窗口已经死了
        else:
            return False # 窗口还没死
        
    def handle_mouse_move(self, x, y, show_log=False): # 鼠标移动事件
        self.mouse_x, self.mouse_y = x, y
        
        if show_log:
            print(_("鼠标移动：") + f"({x}, {y})")

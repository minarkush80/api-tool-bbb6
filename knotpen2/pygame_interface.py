import pygame

# handle_mouse_down(button, x, y): 鼠标按下回调函数
#   button: 1=左键, 2=中键, 3=右键, 4=滚轮上滚, 5=滚轮下滚
# handle_mouse_up(button, x, y): 鼠标抬起回调函数
# handle_key_down(key, mod, unicode): 键盘按键按下回调函数
# handle_key_up(key, mod): 键盘按键释放回调函数
# handle_quit(): 页面关闭回调函数，返回页面是否要继续运行
# draw_screen(screen): 用于绘制屏幕内容
# die_check(): 检测游戏当前是否应该被关闭, True: 是, False: 否
def pygame_interface(handle_mouse_down=None, handle_mouse_up=None, 
                     handle_key_down=None, handle_key_up=None, 
                     handle_quit=None, draw_screen=None,
                     die_check=None, handle_mouse_move=None, width=None, height=None, caption=""):
    pygame.init() # 初始化 Pygame

    pygame.key.stop_text_input()  # 禁用输入法
    pygame.event.set_blocked(pygame.TEXTINPUT) # 禁用文本输入模式
    
    # 获取屏幕分辨率
    desktop_sizes = pygame.display.get_desktop_sizes()
    primary_width, primary_height = desktop_sizes[0] # 获取主屏幕分辨率

    if width is None:
        width = primary_width - 100

    if height is None:
        height = primary_height - 100

    # 设置窗口尺寸
    screen = pygame.display.set_mode((width, height))
    
    # 设置窗口标题
    pygame.display.set_caption(caption)
    
    # 主循环控制变量
    running = True
    
    # 主游戏循环
    while running:
        if die_check is not None:
            running = not die_check()

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # 检测退出事件
                if handle_quit is not None:
                    handle_quit()# 调用退出回调函数

            elif event.type == pygame.MOUSEMOTION: # 鼠标移动事件
                x, y = event.pos
                if handle_mouse_move is not None:
                    handle_mouse_move(x, y)

            elif event.type == pygame.MOUSEBUTTONDOWN: # 检测鼠标按下
                x, y = event.pos
                button = event.button
                
                if handle_mouse_down is not None:
                    handle_mouse_down(button, x, y)
            
            elif event.type == pygame.MOUSEBUTTONUP: # 检测鼠标抬起
                x, y = event.pos
                button = event.button
                
                if handle_mouse_up is not None:
                    handle_mouse_up(button, x, y)

            elif event.type == pygame.KEYDOWN: # 检测键盘按键按下
                key = event.key
                mod = event.mod    # 按键修饰符（如 Shift、Ctrl 等）
                unicode = event.unicode  # 按键对应的 Unicode 字符
                
                if handle_key_down is not None:
                    handle_key_down(key, mod, unicode)
            
            elif event.type == pygame.KEYUP: # 检测键盘按键释放
                key = event.key
                mod = event.mod    # 按键修饰符（如 Shift、Ctrl 等）
                
                if handle_key_up is not None:
                    handle_key_up(key, mod)
        
        if draw_screen is None:
            screen.fill((255, 255, 255)) # 填充白色背景
        else:
            draw_screen(screen) # 绘制屏幕内容
        pygame.display.flip() # 更新显示

    pygame.quit() # 退出 Pygame

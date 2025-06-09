import os
import sys

def add_parent_dir_to_sys_path():
    """
    将当前文件的父目录和目录 添加到 sys.path 的开头。
    只能放在我的运行py文件的文件夹里面，不能放在最外层
    甚至不能放单独py文件，因为导入这个文件又需要索引。。。。我服了
    """
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)

    # 获取当前文件所在的目录
    current_dir = os.path.dirname(current_file_path)

    # 获取当前目录的父目录
    parent_dir = os.path.dirname(current_dir)

    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

if __name__ == '__main__':
    add_parent_dir_to_sys_path()
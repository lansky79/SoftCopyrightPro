import sys
import os
import datetime
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from PyQt5.QtWidgets import QGroupBox, QSpinBox, QProgressBar, QStatusBar, QMessageBox, QHeaderView
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QVariant

from sofcrtpro.file_scanner import scan_directory
from sofcrtpro.code_processor import process_code_files
from sofcrtpro.document_generator import generate_document

# 添加调试开关
DEBUG = True

def debug_print(*args, **kwargs):
    """调试打印函数"""
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

def generate_filename(software_name, software_version):
    """生成唯一的文件名：项目名+版本号(V大写)_月日时分"""
    # 格式化版本号（确保v变为V）
    version = software_version.strip()
    if version.startswith('v'):
        version = 'V' + version[1:]
    elif not version.startswith('V'):
        version = 'V' + version
    
    # 获取当前日期时间 - 只使用月日时分
    now = datetime.datetime.now()
    date_str = now.strftime("%m%d%H%M")
    
    # 组合文件名 - 项目名+版本号_日期时间
    filename = f"{software_name}{version}_{date_str}"
    
    # 替换文件名中的非法字符
    filename = filename.replace(" ", "").replace(":", "-").replace("/", "-").replace("\\", "-")
    
    return filename

def ensure_directory_exists(directory_path):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            debug_print(f"创建目录: {directory_path}")
            return True
        except Exception as e:
            debug_print(f"创建目录失败: {directory_path}, 错误: {str(e)}")
            return False
    return True

def check_file_writable(file_path):
    """检查文件是否可写入"""
    # 如果文件不存在，检查目录是否可写
    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            return ensure_directory_exists(directory)
        return os.access(directory, os.W_OK)
    
    # 如果文件存在，检查是否可写
    return os.access(file_path, os.W_OK)

class DocumentGeneratorThread(QThread):
    """文档生成线程，避免生成过程阻塞GUI"""
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
    
    def run(self):
        try:
            # 获取参数
            classified_files = self.params['classified_files']
            output_path = self.params['output_path']
            software_name = self.params['software_name']
            software_version = self.params['software_version']
            font_name_en = self.params['font_name_en']
            font_name_cn = self.params['font_name_cn']
            lines_per_page = self.params['lines_per_page']
            
            # 设置进度
            self.progress_signal.emit(10)
            
            # 检查输出路径是否可写
            if not check_file_writable(output_path + '.docx'):
                raise PermissionError(f"无法写入文件: {output_path}.docx，可能是文件被占用或没有写入权限")
            
            # 调试打印文件列表
            debug_print("DocumentGeneratorThread文件列表:")
            for file_type, files in classified_files.items():
                if file_type != 'exact_order':  # 跳过exact_order键
                    debug_print(f"{file_type}: {len(files)}个文件")
                    for f in files:
                        debug_print(f"  - {f}")
            
            # 检查是否提供了精确的文件顺序
            has_exact_order = 'exact_order' in classified_files and classified_files['exact_order']
            
            # 提取用于处理的文件列表
            process_files = {}
            exact_file_order = []  # 添加一个明确的文件顺序列表
            
            if has_exact_order:
                debug_print(f"使用自定义文件顺序处理 ({len(classified_files['exact_order'])}个文件)")
                exact_file_order = classified_files['exact_order']
                
                # 输出精确的文件顺序，便于调试
                debug_print("精确文件顺序:")
                for idx, f in enumerate(exact_file_order):
                    debug_print(f"  {idx+1}. {f}")
                
                # 创建一个只包含backend和frontend的字典，但保持exact_order中的顺序
                process_files = {
                    'backend': [f for f in exact_file_order 
                                if f in classified_files['backend']],
                    'frontend': [f for f in exact_file_order 
                                if f in classified_files['frontend']]
                }
            else:
                debug_print("使用默认分类顺序处理文件")
                process_files = {
                    'backend': classified_files['backend'],
                    'frontend': classified_files['frontend']
                }
                # 创建一个默认顺序列表
                exact_file_order = process_files['backend'] + process_files['frontend']
            
            # 添加顺序信息到process_files中
            process_files['file_order'] = exact_file_order
            
            # 处理代码文件 - 不使用额外参数
            merged_content, pages, processed_files = process_code_files(process_files, lines_per_page)
            
            # 检查处理后的文件是否与预期顺序一致
            debug_print("处理前的文件顺序:")
            for idx, f in enumerate(exact_file_order):
                debug_print(f"  {idx+1}. {f}")
                
            debug_print("处理后的文件顺序:")
            for idx, f in enumerate(processed_files):
                debug_print(f"  {idx+1}. {f}")
            
            # 确保processed_files按照exact_file_order中的顺序排列
            # 创建一个新的有序文件列表
            ordered_processed_files = []
            for file_path in exact_file_order:
                if file_path in processed_files:
                    ordered_processed_files.append(file_path)
            
            # 添加任何在processed_files中但不在exact_file_order中的文件（极少情况）
            for file_path in processed_files:
                if file_path not in ordered_processed_files:
                    ordered_processed_files.append(file_path)
            
            self.progress_signal.emit(50)
            
            # 使用重新排序后的文件列表
            debug_print(f"最终处理的文件顺序 ({len(ordered_processed_files)}个):")
            for idx, f in enumerate(ordered_processed_files):
                debug_print(f"  {idx+1}. {f}")
            
            # 生成文档 - 使用排序后的文件列表
            output_file, stats = generate_document(
                content=merged_content,
                output_path=output_path,  # 这里不添加扩展名，让generate_document函数添加
                file_list=ordered_processed_files,
                output_format='docx',
                software_name=software_name,
                software_version=software_version,
                font_name_en=font_name_en,
                font_name_cn=font_name_cn,
                font_size=10.5
            )
            
            debug_print(f"生成的文档路径: {output_file}")
            
            self.progress_signal.emit(100)
            self.finished_signal.emit(output_file)
            
        except Exception as e:
            debug_print(f"文档生成错误: {str(e)}")
            self.error_signal.emit(str(e))

# 定义一个自定义的TreeWidgetItem类，以便实现自定义排序
class SortableTreeWidgetItem(QTreeWidgetItem):
    """自定义的树节点项，支持数值排序"""
    
    def __lt__(self, other):
        """重写小于操作符，以便支持自定义排序规则"""
        column = self.treeWidget().sortColumn()
        
        if column == 2:  # 代码行数列
            # 获取代码行数
            try:
                return int(self.text(column)) < int(other.text(column))
            except ValueError:
                return super().__lt__(other)
        elif column == 4:  # 日期列
            # 获取UserRole中的时间戳进行比较
            try:
                my_timestamp = self.data(column, Qt.UserRole)
                other_timestamp = other.data(column, Qt.UserRole)
                return float(my_timestamp) < float(other_timestamp)
            except (ValueError, TypeError):
                return super().__lt__(other)
        else:
            # 其他列按默认方式排序
            return super().__lt__(other)

class SoftCopyrightApp(QMainWindow):
    """软著源代码管理器应用程序主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("软著源代码管理器")
        self.setGeometry(100, 100, 1900, 1000)  # 进一步增大初始窗口大小
        self.setup_ui()
        self.file_data = {}  # 存储文件信息的字典
        
    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        super().resizeEvent(event)
        
        # 窗口大小变化时调整列宽以填满整个区域
        if hasattr(self, 'file_tree') and hasattr(self, 'output_file_list'):
            # 获取文件树的总宽度
            file_tree_width = self.file_tree.width()
            
            # 计算文件树的列宽总和(除最后一列)
            file_tree_columns_width = sum(self.file_tree.header().sectionSize(i) for i in range(1, self.file_tree.header().count()))
            
            # 调整第一列宽度以填满剩余空间
            first_column_width = max(500, file_tree_width - file_tree_columns_width - 25)  # 减去25像素作为滚动条和边框的空间
            self.file_tree.header().resizeSection(0, first_column_width)
            
            # 对输出文件列表做类似处理
            output_list_width = self.output_file_list.width()
            output_list_second_column_width = self.output_file_list.header().sectionSize(1)
            
            # 调整第一列宽度以填满剩余空间
            output_first_column_width = max(500, output_list_width - output_list_second_column_width - 25)
            self.output_file_list.header().resizeSection(0, output_first_column_width)
    
    def setup_ui(self):
        """设置用户界面"""
        # 设置应用程序全局字体
        app_font = self.font()
        app_font.setPointSize(10)  # 设置基础字体大小
        self.setFont(app_font)
        
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧面板 - 文件列表和顺序控制按钮
        left_panel = QVBoxLayout()
        
        # 文件列表
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["文件路径", "类型", "代码行数", "后缀", "创建日期"])  # 修改列标题使其更明确
        
        # 设置列宽可调整
        self.file_tree.header().setSectionResizeMode(0, QHeaderView.Interactive)  # 文件列可调整大小
        self.file_tree.header().setSectionResizeMode(1, QHeaderView.Interactive)  # 类型列可调整大小
        self.file_tree.header().setSectionResizeMode(2, QHeaderView.Interactive)  # 代码行数列可调整大小
        self.file_tree.header().setSectionResizeMode(3, QHeaderView.Interactive)  # 后缀列可调整大小
        self.file_tree.header().setSectionResizeMode(4, QHeaderView.Interactive)  # 创建日期列可调整大小
        
        # 设置合理的初始列宽
        self.file_tree.header().resizeSection(0, 500)  # 文件列初始宽度增加
        self.file_tree.header().resizeSection(1, 80)   # 类型列初始宽度增加
        self.file_tree.header().resizeSection(2, 100)  # 代码行数列初始宽度增加
        self.file_tree.header().resizeSection(3, 80)   # 后缀列初始宽度增加
        self.file_tree.header().resizeSection(4, 150)  # 创建日期列初始宽度增加
        
        # 确保最后一列拉伸填满剩余空间
        self.file_tree.header().setStretchLastSection(True)
        
        self.file_tree.itemChanged.connect(self.on_item_changed)
        
        # 启用排序
        self.file_tree.setSortingEnabled(True)
        self.file_tree.setRootIsDecorated(False)  # 不显示展开/折叠箭头，因为没有子项
        self.file_tree.header().setSectionsClickable(True)  # 确保列标题可点击

        # 文件顺序控制按钮
        order_buttons_layout = QHBoxLayout()
        
        self.move_up_button = QPushButton("上移文件")
        self.move_up_button.setMinimumHeight(40)  # 增大按钮高度
        self.move_up_button.setMinimumWidth(120)  # 设置最小宽度
        self.move_up_button.clicked.connect(self.move_item_up)
        
        self.move_down_button = QPushButton("下移文件")
        self.move_down_button.setMinimumHeight(40)  # 增大按钮高度
        self.move_down_button.setMinimumWidth(120)  # 设置最小宽度
        self.move_down_button.clicked.connect(self.move_item_down)
        
        order_buttons_layout.addWidget(self.move_up_button)
        order_buttons_layout.addWidget(self.move_down_button)
        
        # 添加到左侧面板
        left_panel.addWidget(self.file_tree)
        left_panel.addLayout(order_buttons_layout)
        
        # 创建左侧面板容器
        left_container = QWidget()
        left_container.setLayout(left_panel)
        
        # 右侧面板
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)  # 增加右侧各组件间距
        
        # 右侧字体样式
        right_label_style = "QLabel { font-size: 11pt; }"
        right_input_style = "QLineEdit { font-size: 11pt; height: 30px; }"
        right_spinbox_style = "QSpinBox { font-size: 11pt; height: 30px; width: 60px; }"  # 减小数字输入框宽度
        right_button_style = "QPushButton { font-size: 11pt; height: 45px; }"
        group_title_style = "QGroupBox { font-size: 12pt; font-weight: bold; }"
        
        # 统计信息区域 - 更紧凑排列
        stats_group = QGroupBox("统计信息")
        stats_group.setStyleSheet(group_title_style)
        stats_group.setMaximumHeight(170)  # 稍微增加高度
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(8)  # 增加间距
        stats_layout.setContentsMargins(15, 15, 15, 15)  # 调整边距
        
        # 水平布局的统计信息 - 第一行
        stats_row1 = QHBoxLayout()
        self.total_files_label = QLabel("总文件数: 0")
        self.total_files_label.setStyleSheet(right_label_style)
        self.selected_files_label = QLabel("已选文件数: 0")
        self.selected_files_label.setStyleSheet(right_label_style)
        stats_row1.addWidget(self.total_files_label)
        stats_row1.addWidget(self.selected_files_label)
        
        # 水平布局的统计信息 - 第二行
        stats_row2 = QHBoxLayout()
        self.total_lines_label = QLabel("总代码行数: 0")
        self.total_lines_label.setStyleSheet(right_label_style)
        self.estimated_pages_label = QLabel("预计生成页数: 0")
        self.estimated_pages_label.setStyleSheet(right_label_style)
        stats_row2.addWidget(self.total_lines_label)
        stats_row2.addWidget(self.estimated_pages_label)
        
        # 添加到主统计布局
        stats_layout.addLayout(stats_row1)
        stats_layout.addLayout(stats_row2)
        stats_group.setLayout(stats_layout)
        
        # 文件筛选选项
        filter_group = QGroupBox("文件筛选选项")
        filter_group.setStyleSheet(group_title_style)
        filter_group.setMaximumHeight(140)  # 增加高度
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(10)  # 增加间距
        filter_layout.setContentsMargins(15, 15, 15, 15)  # 调整边距
        
        # 最小代码行数筛选器
        min_lines_layout = QHBoxLayout()
        
        # 取消选择按钮直接替代"取消选择少于"文字
        self.apply_filter_button = QPushButton("取消选择")
        self.apply_filter_button.setStyleSheet(right_button_style)
        self.apply_filter_button.setMinimumHeight(30)  # 设置高度与数字输入框一致
        self.apply_filter_button.setMinimumWidth(120)  # 设置最小宽度，与其他按钮保持一致
        self.apply_filter_button.clicked.connect(self.apply_min_lines_filter)
        min_lines_layout.addWidget(self.apply_filter_button)
        
        # 数字选择框
        self.min_lines_spinner = QSpinBox()
        self.min_lines_spinner.setStyleSheet(right_spinbox_style)
        self.min_lines_spinner.setFixedHeight(30)  # 强制固定高度
        self.min_lines_spinner.setRange(1, 1000)
        self.min_lines_spinner.setValue(10)  # 默认值为10行
        self.min_lines_spinner.setSingleStep(5)
        min_lines_layout.addWidget(self.min_lines_spinner)
        
        # 只保留"行的代码文件"文字
        min_lines_suffix = QLabel("行的代码文件")
        min_lines_suffix.setStyleSheet(right_label_style)
        min_lines_layout.addWidget(min_lines_suffix)
        
        filter_layout.addLayout(min_lines_layout)
        
        # 选择全部/取消全部按钮
        select_buttons_layout = QHBoxLayout()
        self.select_all_button = QPushButton("全部选择")
        self.select_all_button.setStyleSheet(right_button_style)
        self.select_all_button.setMinimumHeight(40)  # 增大按钮高度
        self.select_all_button.setMinimumWidth(120)  # 设置最小宽度，与其他按钮保持一致
        self.select_all_button.clicked.connect(lambda: self.toggle_all_selection(True))
        
        self.deselect_all_button = QPushButton("全部取消")
        self.deselect_all_button.setStyleSheet(right_button_style)
        self.deselect_all_button.setMinimumHeight(40)  # 增大按钮高度
        self.deselect_all_button.setMinimumWidth(120)  # 设置最小宽度，与其他按钮保持一致
        self.deselect_all_button.clicked.connect(lambda: self.toggle_all_selection(False))
        
        select_buttons_layout.addWidget(self.select_all_button)
        select_buttons_layout.addWidget(self.deselect_all_button)
        
        filter_layout.addLayout(select_buttons_layout)
        
        filter_group.setLayout(filter_layout)
        
        # 参数设置区域
        params_group = QGroupBox("文档参数设置")
        params_group.setStyleSheet(group_title_style)
        params_layout = QVBoxLayout()
        params_layout.setSpacing(10)  # 增加间距
        params_layout.setContentsMargins(15, 15, 15, 15)  # 调整边距
        
        # 软件名称
        name_layout = QHBoxLayout()
        name_label = QLabel("软件名称:")
        name_label.setStyleSheet(right_label_style)
        name_layout.addWidget(name_label)
        self.name_input = QLineEdit("系统")
        self.name_input.setStyleSheet(right_input_style)
        name_layout.addWidget(self.name_input)
        params_layout.addLayout(name_layout)
        
        # 版本号
        version_layout = QHBoxLayout()
        version_label = QLabel("版本号:")
        version_label.setStyleSheet(right_label_style)
        version_layout.addWidget(version_label)
        self.version_input = QLineEdit("V1.0")
        self.version_input.setStyleSheet(right_input_style)
        version_layout.addWidget(self.version_input)
        params_layout.addLayout(version_layout)
        
        # 输出路径
        output_path_layout = QHBoxLayout()
        output_path_label = QLabel("输出路径:")
        output_path_label.setStyleSheet(right_label_style)
        output_path_layout.addWidget(output_path_label)
        self.output_path_input = QLineEdit("./output")
        self.output_path_input.setStyleSheet(right_input_style)
        self.output_path_button = QPushButton("浏览...")
        self.output_path_button.setMinimumHeight(35)  # 调整浏览按钮高度
        self.output_path_button.clicked.connect(self.select_output_path)
        output_path_layout.addWidget(self.output_path_input)
        output_path_layout.addWidget(self.output_path_button)
        params_layout.addLayout(output_path_layout)
        
        # 字体设置
        font_layout = QHBoxLayout()
        en_font_label = QLabel("英文字体:")
        en_font_label.setStyleSheet(right_label_style)
        font_layout.addWidget(en_font_label)
        self.en_font_input = QLineEdit("Courier New")
        self.en_font_input.setStyleSheet(right_input_style)
        font_layout.addWidget(self.en_font_input)
        cn_font_label = QLabel("中文字体:")
        cn_font_label.setStyleSheet(right_label_style)
        font_layout.addWidget(cn_font_label)
        self.cn_font_input = QLineEdit("SimSun")
        self.cn_font_input.setStyleSheet(right_input_style)
        font_layout.addWidget(self.cn_font_input)
        params_layout.addLayout(font_layout)
        
        # 每页最少行数
        lines_layout = QHBoxLayout()
        lines_label = QLabel("每页最少行数:")
        lines_label.setStyleSheet(right_label_style)
        lines_layout.addWidget(lines_label)
        self.lines_per_page = QSpinBox()
        self.lines_per_page.setStyleSheet(right_spinbox_style)
        self.lines_per_page.setFixedHeight(30)  # 强制固定高度
        self.lines_per_page.setRange(30, 100)
        self.lines_per_page.setValue(50)
        lines_layout.addWidget(self.lines_per_page)
        params_layout.addLayout(lines_layout)
        
        params_group.setLayout(params_layout)
        
        # 输出文件列表（新增）
        output_list_group = QGroupBox("输出文件列表（按合并顺序）")
        output_list_group.setStyleSheet(group_title_style)
        output_list_layout = QVBoxLayout()
        output_list_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建文件列表展示
        self.output_file_list = QTreeWidget()
        self.output_file_list.setHeaderLabels(["文件路径", "类型"])  # 修改列标题使其更明确
        self.output_file_list.setMinimumHeight(180)  # 设置最小高度
        self.output_file_list.setRootIsDecorated(False)  # 不显示展开/折叠箭头
        
        # 设置列宽可调整
        self.output_file_list.header().setSectionResizeMode(0, QHeaderView.Interactive)  # 文件列可调整大小
        self.output_file_list.header().setSectionResizeMode(1, QHeaderView.Interactive)  # 类型列可调整大小
        
        # 设置合理的初始列宽
        self.output_file_list.header().resizeSection(0, 500)  # 文件列初始宽度
        self.output_file_list.header().resizeSection(1, 80)   # 类型列初始宽度
        
        # 确保最后一列拉伸填满剩余空间
        self.output_file_list.header().setStretchLastSection(True)
        
        # 启用排序
        self.output_file_list.setSortingEnabled(True)
        self.output_file_list.header().setSectionsClickable(True)  # 确保列标题可点击
        
        # 启用工具提示
        self.output_file_list.setToolTip("显示按当前顺序将合并的文件列表")
        self.output_file_list.setMouseTracking(True)  # 启用鼠标跟踪以便显示提示气泡
        # 修改文本省略模式
        self.output_file_list.header().setTextElideMode(Qt.ElideMiddle)  # 对所有列使用省略号表示中间部分
        
        output_list_layout.addWidget(self.output_file_list)
        
        # 添加刷新文件列表按钮
        self.refresh_list_button = QPushButton("刷新文件列表")
        self.refresh_list_button.setStyleSheet(right_button_style)
        self.refresh_list_button.setMinimumHeight(40)
        self.refresh_list_button.setMinimumWidth(120)  # 设置最小宽度，与其他按钮保持一致
        self.refresh_list_button.clicked.connect(self.refresh_output_file_list)
        output_list_layout.addWidget(self.refresh_list_button)
        
        output_list_group.setLayout(output_list_layout)
        
        # 功能按钮区
        buttons_layout = QHBoxLayout()
        self.select_folder_button = QPushButton("选择项目文件夹")
        self.select_folder_button.setStyleSheet(right_button_style)
        self.select_folder_button.setMinimumHeight(45)  # 增大按钮高度
        self.select_folder_button.setMinimumWidth(120)  # 设置最小宽度，与其他按钮保持一致
        self.select_folder_button.clicked.connect(self.select_project_folder)
        
        self.stat_button = QPushButton("统计文件")
        self.stat_button.setStyleSheet(right_button_style)
        self.stat_button.setMinimumHeight(45)  # 增大按钮高度
        self.stat_button.setMinimumWidth(120)  # 设置最小宽度，与其他按钮保持一致
        self.stat_button.clicked.connect(self.stat_files)
        
        self.generate_button = QPushButton("生成文档")
        self.generate_button.setStyleSheet(right_button_style)  # 移除黑体样式，与其他按钮保持一致
        self.generate_button.setMinimumHeight(45)  # 增大按钮高度
        self.generate_button.setMinimumWidth(120)  # 设置最小宽度，与其他按钮保持一致
        self.generate_button.clicked.connect(self.generate_document)
        
        self.about_button = QPushButton("关于")
        self.about_button.setStyleSheet(right_button_style)
        self.about_button.setMinimumHeight(45)  # 增大按钮高度
        self.about_button.setMinimumWidth(120)  # 设置最小宽度，与其他按钮保持一致
        self.about_button.clicked.connect(self.show_about_dialog)
        
        buttons_layout.addWidget(self.select_folder_button)
        buttons_layout.addWidget(self.stat_button)
        buttons_layout.addWidget(self.generate_button)
        buttons_layout.addWidget(self.about_button)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(30)  # 调整进度条高度
        
        # 组合右侧面板
        right_panel.addWidget(stats_group)
        right_panel.addWidget(filter_group)
        right_panel.addWidget(params_group)
        right_panel.addWidget(output_list_group)  # 添加输出文件列表
        right_panel.addLayout(buttons_layout)
        right_panel.addWidget(self.progress_bar)
        
        # 组合主布局
        main_layout.addWidget(left_container, 2)
        main_layout.addLayout(right_panel, 1)
        
        # 设置中央窗口部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("准备就绪")
        
        # 添加开发者信息到状态栏右侧
        developer_label = QLabel("由 SourceStride 源踔科技 开发")
        developer_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.status_bar.addPermanentWidget(developer_label)
        
        # 更新输出文件列表
        self.refresh_output_file_list()
    
    def select_project_folder(self):
        """选择项目文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择项目文件夹")
        if folder:
            self.current_folder = folder
            self.status_bar.showMessage(f"已选择文件夹: {folder}")
            self.scan_files(folder)
    
    def select_output_path(self):
        """选择输出路径"""
        folder = QFileDialog.getExistingDirectory(self, "选择输出路径")
        if folder:
            self.output_path_input.setText(folder)
    
    def on_item_changed(self, item, column):
        """处理文件树项目状态变化"""
        if column == 0:  # 只处理第一列的勾选状态变化
            file_path = item.text(0)
            is_checked = item.checkState(0) == Qt.Checked
            
            if file_path in self.file_data:
                # 更新文件的选中状态
                self.file_data[file_path]['selected'] = is_checked
                debug_print(f"文件选择状态更新: {file_path} -> {'选中' if is_checked else '未选中'}")
                self.update_stats()  # 更新统计信息
                self.status_bar.showMessage(f"{'选中' if is_checked else '取消选中'}: {file_path}")
                
                # 刷新输出文件列表
                self.refresh_output_file_list()
    
    def get_file_creation_date(self, file_path):
        """获取文件的创建日期"""
        try:
            # 获取文件的创建时间（Windows）或修改时间（Unix）
            if os.name == 'nt':  # Windows
                ctime = os.path.getctime(file_path)
            else:  # Unix
                ctime = os.path.getmtime(file_path)  # Unix没有直接的创建时间，使用修改时间代替
            
            # 转换为格式化的日期字符串
            return datetime.datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M')
        except Exception as e:
            debug_print(f"获取文件创建日期失败 {file_path}: {e}")
            return "未知"

    def scan_files(self, folder):
        """扫描文件夹中的源代码文件"""
        self.status_bar.showMessage("正在扫描文件...")
        self.file_tree.clear()
        self.file_data = {}
        
        # 暂时禁用排序
        self.file_tree.setSortingEnabled(False)
        
        # 使用现有的文件扫描功能
        all_files = scan_directory(folder)
        debug_print(f"扫描到的所有文件数: {len(all_files)}")
        
        # 过滤源代码文件
        backend_identifiers = {'.py', '.java', '.c', '.cpp', '.cs', '.go', '.rb', '.php', '.swift'}
        frontend_identifiers = {'.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.vue', '.scss', '.less'}
        
        # GUI前端相关的标识符（文件名或路径中包含这些字符串的可能是UI/前端文件）
        gui_frontend_indicators = ['ui', 'gui', 'view', 'window', 'dialog', 'form', 'widget', 'screen', 'page']
        
        code_files = []
        for file_path in all_files:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in backend_identifiers or file_ext in frontend_identifiers:
                code_files.append(file_path)
        
        debug_print(f"过滤后的源代码文件数: {len(code_files)}")
        
        # 暂时阻止信号，以避免每次添加项目时触发状态更新
        self.file_tree.blockSignals(True)
        
        # 统计每个文件的行数
        for file_path in code_files:
            file_ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path).lower()
            
            # 智能判断文件类型（前端/后端）
            if file_ext in frontend_identifiers:
                file_type = "前端"  # 基于扩展名判断为前端
            elif file_ext in backend_identifiers:
                # 对于Python等后端语言，还需进一步判断是否为GUI前端代码
                is_gui_frontend = False
                
                # 检查文件名和路径中是否包含UI/前端相关的关键词
                path_lower = file_path.lower()
                for indicator in gui_frontend_indicators:
                    if indicator in file_name or f"/{indicator}/" in path_lower.replace("\\", "/"):
                        is_gui_frontend = True
                        break
                
                # 如果文件名判断不足够，可以尝试通过文件内容判断
                if not is_gui_frontend and file_ext == '.py':
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(4000)  # 只读取前4000个字符进行判断
                            # 检查是否包含常见UI框架的导入或使用
                            gui_imports = ['import tkinter', 'from tkinter', 'import qt', 'from qt', 
                                          'import wx', 'from wx', 'import gtk', 'from gtk',
                                          'import PyQt', 'from PyQt', 'import PySide', 'from PySide',
                                          'QMainWindow', 'QWidget', 'QDialog', 'QApplication',
                                          'Frame', 'Window', 'App']
                            for gui_import in gui_imports:
                                if gui_import.lower() in content.lower():
                                    is_gui_frontend = True
                                    break
                    except Exception as e:
                        debug_print(f"读取文件内容判断类型时出错 {file_path}: {e}")
                
                file_type = "前端" if is_gui_frontend else "后端"
            else:
                file_type = "后端"  # 默认归类为后端
            
            line_count = self.count_file_lines(file_path)
            creation_date = self.get_file_creation_date(file_path)
            
            # 存储文件信息
            self.file_data[file_path] = {
                'type': file_type,
                'lines': line_count,
                'selected': True,  # 默认选中
                'ext': file_ext,    # 存储文件后缀
                'creation_date': creation_date  # 存储创建日期
            }
            
            # 使用自定义TreeWidgetItem添加到树控件
            item = SortableTreeWidgetItem(self.file_tree)
            item.setText(0, file_path)
            item.setText(1, file_type)
            item.setText(2, str(line_count))
            item.setText(3, file_ext)  # 显示文件后缀
            item.setText(4, creation_date)  # 显示创建日期
            
            # 为创建日期设置排序数据
            try:
                date_obj = datetime.datetime.strptime(creation_date, '%Y-%m-%d %H:%M')
                # 用时间戳作为排序依据
                item.setData(4, Qt.UserRole, float(time.mktime(date_obj.timetuple())))
            except:
                item.setData(4, Qt.UserRole, float(0))  # 解析失败时使用0作为排序值
                
            item.setCheckState(0, Qt.Checked)
        
        # 重新启用信号
        self.file_tree.blockSignals(False)
        
        # 启用排序
        self.file_tree.setSortingEnabled(True)
        
        # 默认按代码行数倒序排序
        self.file_tree.sortByColumn(2, Qt.DescendingOrder)
        
        self.update_stats()
        self.status_bar.showMessage(f"扫描完成，找到 {len(code_files)} 个源代码文件")
        
        # 刷新输出文件列表
        self.refresh_output_file_list()
    
    def count_file_lines(self, file_path):
        """计算文件的代码行数"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # 移除空行和纯注释行
                code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
                return len(code_lines)
        except Exception as e:
            debug_print(f"计算文件行数时出错 {file_path}: {e}")
            return 0
    
    def update_stats(self):
        """更新统计信息"""
        total_files = len(self.file_data)
        selected_files = sum(1 for info in self.file_data.values() if info['selected'])
        total_lines = sum(info['lines'] for file_path, info in self.file_data.items() if info['selected'])
        
        # 估算页数 (每页约50行)
        estimated_pages = total_lines // self.lines_per_page.value() + 1
        
        self.total_files_label.setText(f"总文件数: {total_files}")
        self.selected_files_label.setText(f"已选文件数: {selected_files}")
        self.total_lines_label.setText(f"总代码行数: {total_lines}")
        self.estimated_pages_label.setText(f"预计生成页数: {estimated_pages}")
        
        debug_print(f"统计信息更新: 总文件数={total_files}, 已选文件数={selected_files}, 总代码行数={total_lines}")
    
    def stat_files(self):
        """统计文件信息"""
        if not hasattr(self, 'current_folder'):
            QMessageBox.warning(self, "警告", "请先选择项目文件夹")
            return
        
        self.scan_files(self.current_folder)
    
    def move_item_up(self):
        """将选中的项目上移"""
        current_item = self.file_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个文件")
            return
            
        current_index = self.file_tree.indexOfTopLevelItem(current_item)
        if current_index <= 0:
            return  # 已经是第一项，无法上移
            
        # 暂时禁用排序
        self.file_tree.setSortingEnabled(False)
        
        # 从树中移除当前项
        self.file_tree.takeTopLevelItem(current_index)
        
        # 在新位置插入
        self.file_tree.insertTopLevelItem(current_index - 1, current_item)
        
        # 重新选中该项
        self.file_tree.setCurrentItem(current_item)
        
        # 更新状态栏消息
        self.status_bar.showMessage("文件已上移")
        
        # 刷新输出文件列表
        self.refresh_output_file_list()
    
    def move_item_down(self):
        """将选中的项目下移"""
        current_item = self.file_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个文件")
            return
            
        current_index = self.file_tree.indexOfTopLevelItem(current_item)
        if current_index >= self.file_tree.topLevelItemCount() - 1:
            return  # 已经是最后一项，无法下移
            
        # 暂时禁用排序
        self.file_tree.setSortingEnabled(False)
        
        # 从树中移除当前项
        self.file_tree.takeTopLevelItem(current_index)
        
        # 在新位置插入
        self.file_tree.insertTopLevelItem(current_index + 1, current_item)
        
        # 重新选中该项
        self.file_tree.setCurrentItem(current_item)
        
        # 更新状态栏消息
        self.status_bar.showMessage("文件已下移")
        
        # 刷新输出文件列表
        self.refresh_output_file_list()
    
    def generate_document(self):
        """生成文档"""
        if not hasattr(self, 'current_folder') or not self.file_data:
            QMessageBox.warning(self, "警告", "请先选择项目文件夹并扫描文件")
            return
        
        # 获取参数
        software_name = self.name_input.text()
        software_version = self.version_input.text()
        
        # 生成文件名
        output_filename = generate_filename(software_name, software_version)
        output_dir = self.output_path_input.text()
        
        # 确保输出目录存在
        if not ensure_directory_exists(output_dir):
            QMessageBox.critical(self, "错误", f"无法创建输出目录: {output_dir}")
            return
        
        # 构建完整输出路径
        output_path = os.path.join(output_dir, output_filename)
        
        # 检查文件是否可写
        if os.path.exists(output_path + '.docx') and not check_file_writable(output_path + '.docx'):
            # 如果文件已存在且不可写，尝试生成新文件名
            now = datetime.datetime.now()
            date_str = now.strftime("%m%d%H%M%S")  # 添加秒数以确保唯一
            
            # 确保版本号格式正确
            version = software_version.strip()
            if version.startswith('v'):
                version = 'V' + version[1:]
            elif not version.startswith('V'):
                version = 'V' + version
                
            output_filename = f"{software_name}{version}_{date_str}"
            output_path = os.path.join(output_dir, output_filename)
            
            QMessageBox.warning(
                self, "警告", 
                f"原文件可能被占用，将使用新文件名: {output_filename}.docx"
            )
        
        font_name_en = self.en_font_input.text()
        font_name_cn = self.cn_font_input.text()
        lines_per_page = self.lines_per_page.value()
        
        # 获取选中的文件，按当前树控件中的显示顺序
        current_file_order = []
        backend_files = []
        frontend_files = []
        
        # 遍历树控件中的所有项目，保持当前显示顺序
        root = self.file_tree.invisibleRootItem()
        item_count = root.childCount()
        
        for i in range(item_count):
            item = root.child(i)
            file_path = item.text(0)
            is_checked = item.checkState(0) == Qt.Checked
            
            if is_checked and file_path in self.file_data:
                current_file_order.append(file_path)
                # 根据文件类型分类
                if self.file_data[file_path]['type'] == "后端":
                    backend_files.append(file_path)
                else:
                    frontend_files.append(file_path)
        
        # 为了确保文件按树控件显示顺序处理，使用 classified_files 参数
        selected_files = {
            'backend': backend_files,
            'frontend': frontend_files,
            # 添加一个特殊键来存储完整的文件顺序
            'exact_order': current_file_order
        }
        
        # 调试打印
        debug_print(f"生成文档 - 选中的文件数量: 后端={len(backend_files)}, 前端={len(frontend_files)}")
        debug_print(f"文件顺序: {current_file_order}")
        
        self.status_bar.showMessage(f"正在生成文档，包含后端文件: {len(backend_files)}个, 前端文件: {len(frontend_files)}个")
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 创建并启动文档生成线程
        self.doc_thread = DocumentGeneratorThread({
            'classified_files': selected_files,
            'output_path': output_path,
            'software_name': software_name,
            'software_version': software_version,
            'font_name_en': font_name_en,
            'font_name_cn': font_name_cn,
            'lines_per_page': lines_per_page
        })
        
        self.doc_thread.progress_signal.connect(self.update_progress)
        self.doc_thread.finished_signal.connect(self.document_generated)
        self.doc_thread.error_signal.connect(self.document_error)
        
        self.doc_thread.start()
        self.status_bar.showMessage("正在生成文档...")
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def document_generated(self, output_file):
        """文档生成完成"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"文档生成完成: {output_file}")
        
        # 获取文件名部分，不含路径
        file_name = os.path.basename(output_file)
        
        result = QMessageBox.question(
            self, "生成完成", 
            f"文档已成功生成到: {output_file}\n\n"
            f"文件名: {file_name}\n\n"
            f"是否打开文档?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            os.startfile(output_file)
    
    def document_error(self, error_msg):
        """文档生成错误"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("生成文档时出错")
        
        # 检查是否是权限错误
        if "Permission denied" in error_msg or "拒绝访问" in error_msg:
            QMessageBox.critical(
                self, "权限错误", 
                f"生成文档时出错: 文件访问被拒绝\n\n可能的原因:\n"
                f"1. 文件被其他程序占用\n"
                f"2. 没有写入权限\n"
                f"3. 输出目录不存在或无法访问\n\n"
                f"建议:\n"
                f"- 关闭可能打开该文件的程序\n"
                f"- 选择不同的输出路径\n"
                f"- 以管理员身份运行程序\n\n"
                f"详细错误: {error_msg}"
            )
        else:
            QMessageBox.critical(self, "错误", f"生成文档时出错:\n{error_msg}")

    def apply_min_lines_filter(self):
        """应用最小行数筛选，取消选择少于指定行数的文件"""
        if not self.file_data:
            QMessageBox.warning(self, "警告", "请先扫描文件")
            return
        
        min_lines = self.min_lines_spinner.value()
        deselected_count = 0
        
        # 暂时阻止信号，以避免每次勾选状态变化时都触发更新
        self.file_tree.blockSignals(True)
        
        # 遍历文件树中的所有项目
        root = self.file_tree.invisibleRootItem()
        item_count = root.childCount()
        
        for i in range(item_count):
            item = root.child(i)
            file_path = item.text(0)
            
            if file_path in self.file_data:
                # 获取文件的代码行数
                line_count = self.file_data[file_path]['lines']
                
                # 如果代码行数少于指定的最小值，取消选择该文件
                if line_count < min_lines:
                    item.setCheckState(0, Qt.Unchecked)
                    self.file_data[file_path]['selected'] = False
                    deselected_count += 1
        
        # 重新启用信号
        self.file_tree.blockSignals(False)
        
        # 更新统计信息
        self.update_stats()
        
        # 显示筛选结果
        self.status_bar.showMessage(f"已取消选择 {deselected_count} 个代码行数少于 {min_lines} 行的文件")
        
        # 刷新输出文件列表
        self.refresh_output_file_list()
    
    def toggle_all_selection(self, select_all):
        """选择或取消选择所有文件"""
        if not self.file_data:
            QMessageBox.warning(self, "警告", "请先扫描文件")
            return
        
        # 暂时阻止信号，以避免每次勾选状态变化时都触发更新
        self.file_tree.blockSignals(True)
        
        # 遍历文件树中的所有项目
        root = self.file_tree.invisibleRootItem()
        item_count = root.childCount()
        
        for i in range(item_count):
            item = root.child(i)
            file_path = item.text(0)
            
            if file_path in self.file_data:
                item.setCheckState(0, Qt.Checked if select_all else Qt.Unchecked)
                self.file_data[file_path]['selected'] = select_all
        
        # 重新启用信号
        self.file_tree.blockSignals(False)
        
        # 更新统计信息
        self.update_stats()
        
        # 显示操作结果
        action = "选择" if select_all else "取消选择"
        self.status_bar.showMessage(f"已{action}所有文件")
        
        # 刷新输出文件列表
        self.refresh_output_file_list()

    def refresh_output_file_list(self):
        """刷新输出文件列表"""
        self.output_file_list.clear()
        
        # 获取选中的文件，根据当前树中的顺序
        current_file_order = []
        
        # 遍历树控件中的所有项目，按当前显示顺序获取文件
        root = self.file_tree.invisibleRootItem()
        item_count = root.childCount()
        
        # 收集文件，保持树控件的显示顺序
        for i in range(item_count):
            item = root.child(i)
            file_path = item.text(0)
            is_checked = item.checkState(0) == Qt.Checked
            
            if is_checked and file_path in self.file_data:
                current_file_order.append(file_path)
        
        # 调试打印
        debug_print(f"选中的文件数量: {len(current_file_order)}")
        debug_print(f"文件顺序: {current_file_order}")
        
        # 填充输出文件列表
        for file_path in current_file_order:
            item = QTreeWidgetItem(self.output_file_list)
            item.setText(0, file_path)
            item.setText(1, self.file_data[file_path]['type'])
            # 设置工具提示，显示完整路径
            item.setToolTip(0, file_path)
            item.setToolTip(1, f"类型: {self.file_data[file_path]['type']}, 行数: {self.file_data[file_path]['lines']}")

    def show_about_dialog(self):
        """显示关于对话框"""
        about_text = (
            "软著源代码管理器\n\n"
            "版本: V1.0\n\n"
            "开发者: SourceStride 源踔科技\n\n"
            "功能描述: 用于软件著作权申请的源代码整理工具，"
            "可以自动扫描项目文件夹，统计代码行数，按自定义顺序合并源代码，"
            "并生成符合软著申请要求的Word文档。"
        )
        
        QMessageBox.about(self, "关于软著源代码管理器", about_text)

def main():
    app = QApplication(sys.argv)
    window = SoftCopyrightApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

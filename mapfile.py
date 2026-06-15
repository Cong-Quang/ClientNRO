import os
import ast
import json
from pathlib import Path

class AdvancedRAGSourceAnalyzer:
    def __init__(self, root_dir, ignore_dirs=None, ignore_extensions=None):
        self.root_dir = Path(root_dir).resolve()
        # Bỏ qua các thư mục hệ thống/ẩn, nhưng QUÉT HẾT các thư mục chức năng của bạn
        self.ignore_dirs = ignore_dirs or {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.idea', '.vscode'}
        self.ignore_extensions = ignore_extensions or {'.pyc', '.pyo', '.pyd', '.png', '.jpg', '.jpeg', '.exe'}

    def _should_ignore(self, path: Path) -> bool:
        """Kiểm tra file hoặc thư mục có thuộc danh sách bỏ qua không."""
        return any(part in self.ignore_dirs for part in path.parts) or path.suffix in self.ignore_extensions

    def get_function_args(self, node) -> str:
        """Trích xuất danh sách tham số của hàm kèm theo type hinting (nếu có)."""
        args_list = []
        
        # Xử lý tham số thường
        for arg in node.args.args:
            # Bỏ qua 'self' hoặc 'cls' trong class để Agent dễ đọc
            if arg.arg in ('self', 'cls'):
                continue
            annotation = f": {ast.unparse(arg.annotation)}" if arg.annotation else ""
            args_list.append(f"{arg.arg}{annotation}")
            
        # Xử lý *args và **kwargs
        if node.args.vararg:
            args_list.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args_list.append(f"**{node.args.kwarg.arg}")
            
        return ", ".join(args_list)

    def parse_python_file(self, file_path: Path):
        """Phân tích cú pháp file Python bằng AST để trích xuất Class, Hàm và Tham số."""
        functions = []
        classes = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                node = ast.parse(f.read(), filename=file_path.name)

            for item in node.body:
                # 1. Trích xuất Hàm Toàn cục (Global Functions)
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    docstring = ast.get_docstring(item) or ""
                    args = self.get_function_args(item)
                    functions.append({
                        "name": item.name,
                        "args": args,
                        "type": "async_function" if isinstance(item, ast.AsyncFunctionDef) else "function",
                        "lineno": item.lineno,
                        "docstring": docstring.strip()
                    })
                
                # 2. Trích xuất Lớp (Classes) và các hàm bên trong nó
                elif isinstance(item, ast.ClassDef):
                    class_methods = []
                    class_docstring = ast.get_docstring(item) or ""
                    
                    for sub_item in item.body:
                        if isinstance(sub_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_docstring = ast.get_docstring(sub_item) or ""
                            m_args = self.get_function_args(sub_item)
                            class_methods.append({
                                "name": sub_item.name,
                                "args": m_args,
                                "type": "async_method" if isinstance(sub_item, ast.AsyncFunctionDef) else "method",
                                "lineno": sub_item.lineno,
                                "docstring": method_docstring.strip()
                            })
                    
                    classes.append({
                        "name": item.name,
                        "docstring": class_docstring.strip(),
                        "lineno": item.lineno,
                        "methods": class_methods
                    })

        except Exception as e:
            return {"error": f"Lỗi đọc file: {str(e)}"}

        return {"functions": functions, "classes": classes}

    def generate_text_tree(self) -> str:
        """Tạo sơ đồ cây thư mục trực quan trực tiếp theo cấu trúc thư mục."""
        tree_lines = ["."]
        
        def _build_tree(dir_path: Path, prefix: str = ""):
            try:
                entries = sorted(list(dir_path.iterdir()), key=lambda x: (x.is_file(), x.name.lower()))
            except PermissionError:
                return
                
            entries = [e for e in entries if e.name not in self.ignore_dirs and e.suffix not in self.ignore_extensions and not e.name.startswith('.')]
            
            for i, entry in enumerate(entries):
                is_last = (i == len(entries) - 1)
                connector = "└── " if is_last else "├── "
                tree_lines.append(f"{prefix}{connector}{entry.name}")
                
                if entry.is_dir():
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    _build_tree(entry, new_prefix)

        _build_tree(self.root_dir)
        return "\n".join(tree_lines)

    def scan_project(self):
        """Quét đệ quy toàn bộ thư mục và lưu thông tin chi tiết."""
        project_structure = {}

        for root, dirs, files in os.walk(self.root_dir):
            # Lọc bỏ thư mục ẩn/hệ thống ngay lập tức để tối ưu tốc độ walk
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                if self._should_ignore(file_path):
                    continue

                # Lấy đường dẫn tương đối chuẩn hóa (ví dụ: logs/logger_config.py hoặc main.py)
                relative_path = str(file_path.relative_to(self.root_dir)).replace("\\", "/")
                
                file_info = {
                    "file_name": file,
                    "extension": file_path.suffix,
                    "abs_path": relative_path,  # Đổi abs_path thành đường dẫn gọn dạng tương đối
                    "functions": [],
                    "classes": []
                }

                # Phân tích sâu nếu là file code Python
                if file_path.suffix == '.py':
                    parsed_data = self.parse_python_file(file_path)
                    file_info.update(parsed_data)

                project_structure[relative_path] = file_info

        return project_structure

    def generate_markdown_summary(self, structure_data, tree_str):
        """Tạo file Markdown chi tiết để nhét vào Context Prompt của Agent."""
        md = ["# 🗺️ BẢN ĐỒ CẤU TRÚC HỆ THỐNG SOURCE CODE\n"]
        
        md.append("## 🌳 Cây thư mục tổng quan")
        md.append("```text")
        md.append(tree_str)
        md.append("```\n" + "="*50 + "\n")
        
        md.append("## 🔍 Chi tiết các file và hàm xử lý")
        
        for rel_path, info in sorted(structure_data.items()):
            md.append(f"### 📄 File: `{rel_path}`")
            
            if "error" in info:
                md.append(f"- *⚠️ {info['error']}*\n")
                continue

            # 1. Liệt kê Class
            if info.get("classes"):
                for cls in info["classes"]:
                    md.append(f"- **Class `{cls['name']}`** (Dòng {cls['lineno']})")
                    if cls['docstring']:
                        md.append(f"  > *Mô tả:* {cls['docstring']}")
                    for method in cls["methods"]:
                        md.append(f"  - `{method['type']}`: **`{method['name']}({method['args']})`** (Dòng {method['lineno']})")
                        if method['docstring']:
                            md.append(f"    > *Chi tiết:* {method['docstring']}")
            
            # 2. Liệt kê Hàm tự do bên ngoài
            if info.get("functions"):
                for fn in info["functions"]:
                    md.append(f"- `{fn['type']}`: **`{fn['name']}({fn['args']})`** (Dòng {fn['lineno']})")
                    if fn['docstring']:
                        md.append(f"  > *Mô tả:* {fn['docstring']}")
            
            if not info.get("classes") and not info.get("functions"):
                md.append("- *(File cấu hình hoặc file rỗng, không chứa hàm)*")
                
            md.append("\n" + "-"*30 + "\n")
            
        return "\n".join(md)


if __name__ == "__main__":
    SOURCE_DIRECTORY = "." 
    
    analyzer = AdvancedRAGSourceAnalyzer(root_dir=SOURCE_DIRECTORY)
    
    print("🔄 1. Đang vẽ cây thư mục dự án...")
    tree_structure = analyzer.generate_text_tree()
    
    print("🔄 2. Đang phân tích sâu mã nguồn Python...")
    result = analyzer.scan_project()

    # Lưu file JSON
    with open("project_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print("✅ Đã cập nhật và xuất 'project_summary.json' với đường dẫn tinh gọn.")

    # Lưu file Markdown
    markdown_content = analyzer.generate_markdown_summary(result, tree_structure)
    with open("project_summary.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print("✅ Đã cập nhật và xuất 'project_summary.md'")
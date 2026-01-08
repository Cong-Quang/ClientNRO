import os
import ast
import json

def analyze_file(filepath):
    """Phân tích một file Python và trích xuất cấu trúc"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Lấy docstring nếu có
                        docstring = ast.get_docstring(item) or ""
                        methods.append({
                            'name': item.name,
                            'docstring': docstring[:100] if docstring else ""
                        })
                
                class_docstring = ast.get_docstring(node) or ""
                classes.append({
                    'name': node.name,
                    'docstring': class_docstring[:100] if class_docstring else "",
                    'methods': methods
                })
            
            elif isinstance(node, ast.FunctionDef):
                # Chỉ lấy functions ở top-level (không trong class)
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                    docstring = ast.get_docstring(node) or ""
                    functions.append({
                        'name': node.name,
                        'docstring': docstring[:100] if docstring else ""
                    })
        
        return {
            'classes': classes,
            'functions': functions
        }
    except Exception as e:
        return {
            'error': str(e),
            'classes': [],
            'functions': []
        }

def main():
    project_root = '.'
    result = {}
    
    for root, dirs, files in os.walk(project_root):
        # Bỏ qua các thư mục không cần thiết
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'GameGoc', '.venv', 'venv']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, project_root)
                
                analysis = analyze_file(filepath)
                result[rel_path] = analysis
    
    # Lưu kết quả ra file JSON
    with open('project_structure.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("Analysis complete! Results saved to project_structure.json")

if __name__ == "__main__":
    main()

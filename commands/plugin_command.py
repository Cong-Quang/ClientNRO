"""
Plugin Command - Quản lý plugins qua command line
"""
from commands.base_command import Command


class PluginCommand(Command):
    """Command để quản lý plugins"""
    
    def __init__(self, manager):
        """Initialize with account manager"""
        self.manager = manager
    
    async def execute(self, parts):
        """
        Execute plugin command
        
        Usage:
            plugin list              - Liệt kê tất cả plugins
            plugin enable <name>     - Enable plugin
            plugin disable <name>    - Disable plugin
            plugin reload <name>     - Reload plugin
            plugin info <name>       - Xem thông tin plugin
        """
        if len(parts) < 2:
            self._show_help()
            return
        
        subcommand = parts[1].lower()
        
        # Get plugin manager from manager
        plugin_manager = getattr(self.manager, '_plugin_manager', None)
        if not plugin_manager:
            print("❌ Plugin system chưa được khởi tạo!")
            return
        
        if subcommand == "list":
            self._list_plugins(plugin_manager)
        elif subcommand == "enable":
            if len(parts) < 3:
                print("❌ Usage: plugin enable <name>")
                return
            self._enable_plugin(plugin_manager, parts[2])
        elif subcommand == "disable":
            if len(parts) < 3:
                print("❌ Usage: plugin disable <name>")
                return
            self._disable_plugin(plugin_manager, parts[2])
        elif subcommand == "reload":
            if len(parts) < 3:
                print("❌ Usage: plugin reload <name>")
                return
            self._reload_plugin(plugin_manager, parts[2])
        elif subcommand == "info":
            if len(parts) < 3:
                print("❌ Usage: plugin info <name>")
                return
            self._show_info(plugin_manager, parts[2])
        else:
            print(f"❌ Unknown subcommand: {subcommand}")
            self._show_help()
    
    def _list_plugins(self, plugin_manager):
        """Liệt kê tất cả plugins"""
        plugins = plugin_manager.get_all_plugins()
        
        if not plugins:
            print("📦 Không có plugin nào được load")
            return
        
        print("=" * 70)
        print("📦 DANH SÁCH PLUGINS")
        print("=" * 70)
        
        for name, plugin in plugins.items():
            status = "✅ Enabled" if plugin.enabled else "❌ Disabled"
            print(f"{status} | {plugin.name} v{plugin.version}")
            print(f"         Author: {plugin.author}")
            print(f"         {plugin.description}")
            print("-" * 70)
        
        enabled_count = len(plugin_manager.get_enabled_plugins())
        print(f"\nTổng: {len(plugins)} plugins ({enabled_count} enabled)")
        print("=" * 70)
    
    def _enable_plugin(self, plugin_manager, name):
        """Enable plugin"""
        plugin = plugin_manager.get_plugin(name)
        
        if not plugin:
            print(f"❌ Plugin không tồn tại: {name}")
            print(f"   Dùng 'plugin list' để xem danh sách")
            return

        if plugin.enabled:
            print(f"⚠️ Plugin '{name}' đã được bật từ trước.")
            return

        if plugin_manager.enable_plugin(name):
            print(f"✅ Đã enable plugin: {name}")
        else:
            print(f"❌ Không thể enable plugin: {name}")
            print(f"   Vui lòng kiểm tra logs để biết thêm chi tiết.")
    
    def _disable_plugin(self, plugin_manager, name):
        """Disable plugin"""
        plugin = plugin_manager.get_plugin(name)
        
        if not plugin:
            print(f"❌ Plugin không tồn tại: {name}")
            return

        if not plugin.enabled:
            print(f"⚠️ Plugin '{name}' đã tắt từ trước.")
            return

        if plugin_manager.disable_plugin(name):
            print(f"✅ Đã disable plugin: {name}")
        else:
            print(f"❌ Không thể disable plugin: {name}")
    
    def _reload_plugin(self, plugin_manager, name):
        """Reload plugin"""
        print(f"🔄 Đang reload plugin: {name}...")
        if plugin_manager.reload_plugin(name):
            print(f"✅ Đã reload plugin: {name}")
        else:
            print(f"❌ Không thể reload plugin: {name}")
    
    def _show_info(self, plugin_manager, name):
        """Hiển thị thông tin chi tiết plugin"""
        plugin = plugin_manager.get_plugin(name)
        
        if not plugin:
            print(f"❌ Plugin không tồn tại: {name}")
            print(f"   Dùng 'plugin list' để xem danh sách")
            return
        
        print("=" * 70)
        print(f"📦 THÔNG TIN PLUGIN: {plugin.name}")
        print("=" * 70)
        print(f"Name:        {plugin.name}")
        print(f"Version:     {plugin.version}")
        print(f"Author:      {plugin.author}")
        print(f"Description: {plugin.description}")
        print(f"Status:      {'✅ Enabled' if plugin.enabled else '❌ Disabled'}")
        print("=" * 70)
    
    def _show_help(self):
        """Hiển thị help"""
        print("=" * 70)
        print("📦 PLUGIN COMMANDS")
        print("=" * 70)
        print("plugin list              - Liệt kê tất cả plugins")
        print("plugin enable <name>     - Enable plugin")
        print("plugin disable <name>    - Disable plugin")
        print("plugin reload <name>     - Reload plugin (restart required)")
        print("plugin info <name>       - Xem thông tin plugin")
        print("=" * 70)
        print("\nVí dụ:")
        print("  plugin list")
        print("  plugin enable AutoChatPlugin")
        print("  plugin disable HelloPlugin")
        print("  plugin info AutoChatPlugin")
        print("=" * 70)

# tests/test_scheduler.py

import unittest
from unittest.mock import patch

# 假设可以从 gateway 模块导入
from core.scheduler import get_best_node
from config import Settings

class TestScheduler(unittest.TestCase):
    """
    对动态调度器 `get_best_node` 函数的模拟单元测试。
    """

    def setUp(self):
        """设置模拟的节点配置和状态。"""
        print(f"\n--- Setting up for {self.id()} ---")
        
        # 模拟来自 config.py 的节点配置
        self.mock_nodes_config = [
            {"id": 1, "name": "Node 1 (Fast)", "static_weight": 10.0, "monitor_base_url": "...", "llm_url": "..."},
            {"id": 2, "name": "Node 2 (Medium)", "static_weight": 5.0, "monitor_base_url": "...", "llm_url": "..."},
            {"id": 3, "name": "Node 3 (Slow)", "static_weight": 2.0, "monitor_base_url": "...", "llm_url": "..."},
            {"id": 4, "name": "Node 4 (Offline)", "static_weight": 10.0, "monitor_base_url": "...", "llm_url": "..."},
            {"id": 5, "name": "Node 5 (Locked)", "static_weight": 10.0, "monitor_base_url": "...", "llm_url": "..."},
        ]

        # 模拟来自 core/state.py 的实时节点状态缓存
        self.mock_node_status_cache = {
            1: {"id": 1, "online": True, "metrics": {"locked": False, "gpu": {"utilization_percent": 10, "temperature_celsius": 60}, "memory": {"percent": 20}}},
            2: {"id": 2, "online": True, "metrics": {"locked": False, "gpu": {"utilization_percent": 5, "temperature_celsius": 50}, "memory": {"percent": 10}}},
            3: {"id": 3, "online": True, "metrics": {"locked": False, "gpu": {"utilization_percent": 80, "temperature_celsius": 85}, "memory": {"percent": 90}}},
            4: {"id": 4, "online": False, "metrics": None},
            5: {"id": 5, "online": True, "metrics": {"locked": True, "gpu": {"utilization_percent": 5, "temperature_celsius": 50}, "memory": {"percent": 10}}},
        }

    def tearDown(self):
        """清理测试环境。"""
        print(f"--- Tearing down {self.id()} ---")

    @patch('gateway.core.scheduler.settings')
    @patch('gateway.core.scheduler.state')
    async def test_select_least_loaded_node(self, mock_state, mock_settings):
        """
        测试: 调度器是否选择了负载最低的节点。
        
        在这个场景中:
        - Node 1 负载较低。
        - Node 2 负载最低。
        - Node 3 负载极高。
        - Node 4 离线。
        - Node 5 被锁定。
        
        预期结果: 应该选择 Node 2，因为它在线、未锁定且综合负载最低。
        """
        print("    - 验证调度器是否选择负载最低的节点...")
        
        # 配置 mock 对象
        mock_settings.NODES = self.mock_nodes_config
        mock_state.NODE_STATUS_CACHE = self.mock_node_status_cache
        
        # 使用 async/await 来运行异步函数
        best_node = await get_best_node()
        
        self.assertIsNotNone(best_node)
        self.assertEqual(best_node['id'], 2)
        
        print(f"    - 调度器选择了 Node {best_node['id']}，测试通过。")

    @patch('gateway.core.scheduler.settings')
    @patch('gateway.core.scheduler.state')
    async def test_scheduler_avoids_offline_and_locked_nodes(self, mock_state, mock_settings):
        """
        测试: 调度器是否会避开离线和锁定的节点。
        
        在这个场景中，我们让 Node 1 和 Node 2 也处于不可用状态。
        
        预期结果: 应该返回 None，因为没有可用的节点。
        """
        print("    - 验证调度器是否忽略不可用的节点...")
        
        # 修改状态，使所有可用节点都不可调度
        self.mock_node_status_cache[1]['online'] = False
        self.mock_node_status_cache[2]['metrics']['locked'] = True
        
        mock_settings.NODES = self.mock_nodes_config
        mock_state.NODE_STATUS_CACHE = self.mock_node_status_cache
        
        best_node = await get_best_node()
        
        self.assertIsNone(best_node, "当所有节点都不可用时，调度器应返回 None")
        
        print("    - 调度器正确地忽略了所有不可用节点，测试通过。")

# 使得可以直接运行此文件
if __name__ == '__main__':
    import asyncio
    # unittest 不直接支持异步测试的 setUp/tearDown，但支持异步测试方法
    # 为了简单起见，我们手动运行异步测试
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestScheduler))
    runner = unittest.TextTestRunner(verbosity=2)
    
    # 为了运行 async def test_* 方法，我们需要一个事件循环
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.run(suite))


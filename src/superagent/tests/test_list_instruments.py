import unittest
import json
import os
from datetime import datetime
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.algogene_client import AlgogeneClient

class TestListInstruments(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        self.client = AlgogeneClient()
        # 确保存在data目录
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)

    def test_list_all_instruments(self):
        """测试获取所有金融工具列表并保存到JSON文件"""
        try:
            # 调用API获取所有工具列表
            result = self.client.list_all_instruments()
            
            # 验证返回的数据结构
            self.assertIn('count', result)
            self.assertIn('res', result)
            self.assertIsInstance(result['count'], int)
            self.assertIsInstance(result['res'], list)
            
            # 为结果添加时间戳
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'data': result
            }
            
            # 生成输出文件名（包含时间戳）
            filename = f'instruments_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            output_path = os.path.join(self.data_dir, filename)
            
            # 保存到JSON文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # 验证文件是否成功创建
            self.assertTrue(os.path.exists(output_path))
            
            # 打印结果摘要
            print(f"\n成功获取金融工具列表:")
            print(f"总数量: {result['count']}")
            print(f"已保存到文件: {output_path}")
            
            # 打印前5个工具作为示例
            if result['res']:
                print("\n前5个金融工具示例:")
                for instrument in result['res'][:5]:
                    print(f"- {instrument}")
                    
        except Exception as e:
            self.fail(f"测试失败: {str(e)}")

if __name__ == '__main__':
    unittest.main() 
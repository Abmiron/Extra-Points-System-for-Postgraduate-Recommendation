from models import Rule, RuleCalculation
from extensions import db
import json


class RuleEngine:
    """
    规则引擎核心类，用于处理推免综合成绩计算的规则匹配与分值计算
    """

    def __init__(self):
        # 计算类型映射表
        self.calculation_types = {
            "tree": "树结构计算",
        }

    def match_and_calculate(self, rules, student_data):
        """
        匹配规则并计算分数

        参数:
        - rules: 规则列表
        - student_data: 学生数据字典

        返回:
        - 包含匹配规则和总得分的结果字典
        """
        matched_rules = []
        total_score = 0.0
        matched_details = []

        # 调试信息
        print(f"[DEBUG] match_and_calculate调用: rules={rules}, type(rules)={type(rules)}")
        print(f"[DEBUG] student_data={student_data}, type(student_data)={type(student_data)}")
        print(f"[DEBUG] 学生数据tree_path: {student_data.get('tree_path')}")

        # 遍历所有规则
        for rule in rules:
            # 创建临时对象用于条件评估
            class TempApplication:
                def __init__(self, data):
                    self.__dict__ = data

            application = TempApplication(student_data)
            student = TempApplication(student_data)

            # 调试信息
            print(f"[DEBUG] 处理规则: rule.id={rule.id}, rule.name={rule.name}, rule.type={rule.type}")
            
            # 直接匹配规则并计算分数
            score = self.calculate_score(rule, student_data)
            matched_rules.append(rule)
            total_score += score
            matched_details.append(
                {
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "rule_type": rule.type,
                    "score": score,
                }
            )

        return {
            "matched_rules_count": len(matched_rules),
            "total_score": total_score,
            "matched_rules": matched_details,
        }

    def calculate_score(self, rule, student_data):
        """
        计算单个规则的分数
        :param rule: Rule对象或规则ID
        :param student_data: 学生数据（字典或对象）
        :return: 计算得到的分数
        """
        try:
            # 调试信息
            print(f"[DEBUG] calculate_score调用: rule={rule}, type(rule)={type(rule)}")
            print(f"[DEBUG] student_data={student_data}, type(student_data)={type(student_data)}")
            print(f"[DEBUG] 学生数据tree_path: {student_data.get('tree_path')}")
            
            # 如果传入的是规则ID，获取Rule对象
            if isinstance(rule, int):
                from models import Rule
                rule = Rule.query.get(rule)
                if not rule:
                    print(f"规则ID {rule} 不存在")
                    return 0.0
            
            # 调试信息
            print(f"[DEBUG] Rule对象: id={rule.id}, name={rule.name}, type={rule.type}")
            
            if not rule:
                print("[DEBUG] Rule对象为空")
                return 0.0

            # 获取规则的计算配置（通过relationship访问）
            calculation = rule.calculation
            if not calculation:
                print(f"[DEBUG] 规则 {rule.id} 没有计算配置")
                return 0.0

            # 调试规则配置信息
            print(f"[DEBUG] 规则计算配置: id={calculation.id}, calculation_type={calculation.calculation_type}, parameters={calculation.parameters}")
            print(f"[DEBUG] 规则最大分数限制: {calculation.max_score}")

            # 仅支持树结构计算类型
            if calculation.calculation_type == "tree":
                # 对于树结构计算，我们将student_data作为application参数传递
                score = self._calculate_tree_score(calculation, student_data)
                print(f"[DEBUG] 树结构计算分数: {score}")
                return score
            else:
                # 不支持的计算类型
                print(f"[DEBUG] 不支持的计算类型: {calculation.calculation_type}")
                return 0.0
        except Exception as e:
            print(f"[DEBUG] 计算分数时发生错误: {e}")
            import traceback
            print(f"[DEBUG] 异常堆栈: {traceback.format_exc()}")
            return 0.0

    def _calculate_tree_score(self, calculation, student_data):
        """
        树结构计算得分
        """
        if not calculation.parameters:
            return 0.0

        try:
            # 处理参数：如果已经是字典则直接使用，否则解析JSON字符串
            if isinstance(calculation.parameters, dict):
                params = calculation.parameters
            else:
                params = json.loads(calculation.parameters)
                if not isinstance(params, dict):
                    print("[DEBUG] 参数不是有效的JSON字典")
                    return 0.0

            # 获取树结构配置（从tree.structure路径获取）
            tree_config = params.get("tree", {}).get("structure", {})
            if not tree_config:
                print("[DEBUG] tree.structure字段不存在或为空")
                return 0.0
            
            # 调试信息
            print(f"[DEBUG] 树结构配置: {tree_config}")

            # 转换student_data为字典格式
            student_dict = {}
            if hasattr(student_data, '__dict__'):
                student_dict = {k: v for k, v in student_data.__dict__.items() if not k.startswith('_')}
            elif isinstance(student_data, dict):
                student_dict = student_data
            else:
                print("[DEBUG] student_data不是字典或对象")
                return 0.0

            # 提取树路径
            tree_path = student_dict.get("tree_path", [])
            
            # 调试信息
            print(f"[DEBUG] 学生数据: {student_dict}")
            print(f"[DEBUG] 树路径: {tree_path}")
            
            if not tree_path or not isinstance(tree_path, list):
                print("[DEBUG] 未找到有效的树路径")
                return 0.0
            
            # 查找匹配路径的分数
            def find_node_score(node, path_index=0):
                if not node:
                    print(f"[DEBUG] 节点为空，path_index: {path_index}")
                    return 0.0
                if path_index >= len(tree_path):
                    print(f"[DEBUG] path_index超出范围，path_index: {path_index}, 路径长度: {len(tree_path)}")
                    return 0.0
                
                # 获取节点名称（从dimension.name中获取）
                node_name = node.get("dimension", {}).get("name", "")
                expected_name = tree_path[path_index]
                # 忽略空格进行比较
                node_name_stripped = node_name.replace(" ", "")
                expected_name_stripped = expected_name.replace(" ", "")
                print(f"[DEBUG] 检查节点: {node_name}, 期望名称: {expected_name}, path_index: {path_index}")
                print(f"[DEBUG] 忽略空格比较: {node_name_stripped} == {expected_name_stripped}")
                
                # 检查当前节点是否匹配路径中的当前项（忽略空格）
                if node_name_stripped == expected_name_stripped:
                    print(f"[DEBUG] 节点匹配!")
                    # 如果是最后一个路径项，返回该节点的分数
                    if path_index == len(tree_path) - 1:
                        node_score = float(node.get("score", 0.0))
                        print(f"[DEBUG] 找到匹配的叶子节点，分数: {node_score}")
                        return node_score
                    # 否则继续向下查找所有子节点，找到最深层的匹配节点
                    print(f"[DEBUG] 继续向下查找子节点，path_index增加到: {path_index + 1}")
                    max_score = 0.0
                    for child in node.get("children", []):
                        child_name = child.get("dimension", {}).get("name", "")
                        print(f"[DEBUG] 遍历子节点: {child_name}")
                        score = find_node_score(child, path_index + 1)
                        if score > max_score:
                            max_score = score
                            print(f"[DEBUG] 从子节点 {child_name} 找到更高分数: {score}")
                    if max_score > 0:
                        return max_score
                    print(f"[DEBUG] 没有找到匹配的子节点")
                else:
                    print(f"[DEBUG] 节点不匹配")
                
                # 没有找到匹配的路径
                print(f"[DEBUG] 没有找到匹配的路径")
                return 0.0
            
            # 查找匹配路径的分数
            print(f"[DEBUG] 开始查找路径: {tree_path}")
            
            # 从根节点的子节点开始匹配路径
            found = False
            result = 0.0
            
            # 获取根节点
            root_node = tree_config.get("root", {})
            
            # 遍历根节点的所有子节点
            for child in root_node.get("children", []):
                # 调试信息
                print(f"[DEBUG] 检查根节点子节点: {child.get('dimension', {}).get('name')}")
                
                # 从根节点的子节点开始匹配路径
                score = find_node_score(child, 0)
                if score > 0:
                    result = score
                    found = True
                    break
            
            if not found:
                print(f"[DEBUG] 未找到匹配的路径")
                result = 0.0
                
            print(f"[DEBUG] 最终获取分数: {result}")

            # 应用最大值限制
            if calculation.max_score is not None:
                result = min(result, float(calculation.max_score))

            return round(result, 4)
        except Exception as e:
            print(f"[DEBUG] 树结构计算错误: {e}")
            import traceback
            traceback.print_exc()
            return 0.0


# 创建规则引擎实例
rule_engine = RuleEngine()

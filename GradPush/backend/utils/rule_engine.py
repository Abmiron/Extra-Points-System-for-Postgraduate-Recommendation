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

        # 遍历所有规则
        for rule in rules:
            # 创建临时对象用于条件评估
            class TempApplication:
                def __init__(self, data):
                    self.__dict__ = data

            application = TempApplication(student_data)
            student = TempApplication(student_data)

            # 直接匹配规则并计算分数
            score = self.calculate_score(rule, application, student)
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

    def calculate_score(self, rule, application, student=None):
        """
        根据规则计算实际得分
        
        参数:
        - rule: 规则对象
        - application: 可以是应用数据对象或字典
        - student: 学生数据对象或字典（可选）
        """
        if not rule:
            return 0.0

        # 获取规则的计算配置
        calculation = RuleCalculation.query.filter_by(rule_id=rule.id).first()
        if not calculation:
            return 0.0

        # 仅支持树结构计算类型
        if calculation.calculation_type == "tree":
            return self._calculate_tree_score(calculation, application, student)
        else:
            # 不支持的计算类型
            return 0.0

    def _calculate_tree_score(self, calculation, application, student=None):
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
                    return 0.0

            # 获取树结构配置
            tree_config = params.get("tree", {})
            if not tree_config:
                return 0.0

            scores = tree_config.get("scores", {})
            if not scores:
                return 0.0

            # 获取树结构数据
            tree = tree_config.get("structure", {})
            if not tree or not tree.get("root"):
                return 0.0

            # 从应用数据中提取相关字段值
            student_data = {}  # 存储学生数据字段
            if isinstance(application, dict):
                student_data = application
            else:
                # 如果是对象，将所有属性转换为字典
                student_data = application.__dict__

            # 遍历树结构，找到匹配的叶子节点路径
            def find_matching_path(node, current_path):
                # 如果是叶子节点，返回当前路径
                if not node.get("children") or len(node.get("children")) == 0:
                    return current_path

                # 遍历子节点
                for child in node.get("children", []):
                    child_dimension = child.get("dimension", {})
                    child_key = child_dimension.get("key")
                    child_name = child_dimension.get("name")
                    
                    # 检查当前子节点是否匹配
                    is_matched = False
                    
                    # 灵活匹配方式：检查是否有任何字段的值等于当前节点名
                    for key, value in student_data.items():
                        if str(value) == child_name:
                            is_matched = True
                            break
                    
                    # 传统匹配方式：使用节点自己的dimension.key来匹配student_data
                    if not is_matched and child_key and child_key in student_data:
                        child_value = str(student_data.get(child_key))
                        if child_value == child_name:
                            is_matched = True
                    
                    # 如果当前子节点匹配，继续向下遍历
                    if is_matched:
                        result = find_matching_path(child, current_path + [child_name])
                        if result:
                            return result
                    
                    # 如果当前子节点不匹配，但有子节点，也尝试向下遍历（处理特殊情况）
                    elif child.get("children") and len(child.get("children")) > 0:
                        result = find_matching_path(child, current_path + [child_name])
                        if result:
                            return result

                # 没有找到匹配的路径
                return None

            # 从根节点开始查找匹配路径
            matching_path = find_matching_path(tree.get("root"), [])
            if not matching_path:
                return 0.0

            # 组合成键，格式如 "国家级_一等奖及以上_A+类"
            tree_key = "_".join(matching_path)

            # 获取对应的分数
            result = float(scores.get(tree_key, 0.0))

            # 应用最大值限制
            if calculation.max_score is not None:
                result = min(result, float(calculation.max_score))

            return round(result, 4)
        except Exception as e:
            print(f"树结构计算错误: {e}")
            import traceback

            traceback.print_exc()
            return 0.0


# 创建规则引擎实例
rule_engine = RuleEngine()

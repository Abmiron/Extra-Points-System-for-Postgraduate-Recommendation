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
            "multiplicative": "乘积计算",
            "cumulative": "累积计算",
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
        支持乘积式、累积式和json_formula计算
        """
        if not rule:
            return 0.0

        # 获取规则的计算配置
        calculation = RuleCalculation.query.filter_by(rule_id=rule.id).first()
        if not calculation:
            return 0.0

        # 支持json_formula计算类型，实际内部使用乘积计算
        if calculation.calculation_type in ["multiplicative", "json_formula"]:
            return self._calculate_multiplicative_score(
                calculation, application, student
            )
        elif calculation.calculation_type == "cumulative":
            return self._calculate_cumulative_score(calculation, application, student)
        else:
            # 不支持的计算类型
            return 0.0

    def _calculate_multiplicative_score(self, calculation, application, student=None):
        """
        乘积计算得分
        基于多个因素的乘积计算最终得分
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

            # 支持两种参数名称：factors（后端命名）和coefficients（前端命名）
            factors = params.get("factors", params.get("coefficients", []))
            if not factors:
                return 0.0

            # 基础分值
            base_score = float(params.get("base_score", 1.0))
            result = base_score

            # 计算所有因素的乘积
            for factor in factors:
                if isinstance(factor, str):
                    # 支持字典和对象两种类型的application参数
                    if isinstance(application, dict):
                        factor_value = application.get(factor)
                    else:
                        factor_value = getattr(application, factor, None)
                    
                    if isinstance(factor_value, (int, float)):
                        result *= factor_value
                    elif isinstance(factor_value, str):
                        # 尝试将字符串转换为数字
                        try:
                            result *= float(factor_value)
                        except ValueError:
                            pass
                elif isinstance(factor, (int, float)):
                    result *= factor
                elif isinstance(factor, dict) and "key" in factor:
                    # 处理前端发送的系数对象格式
                    key = factor["key"]
                    # 从应用数据中获取对应的值
                    if isinstance(application, dict):
                        factor_value = application.get(key)
                    else:
                        factor_value = getattr(application, key, None)
                    
                    if isinstance(factor_value, (int, float)):
                        result *= factor_value
                    elif isinstance(factor_value, str):
                        # 尝试将字符串转换为数字
                        try:
                            result *= float(factor_value)
                        except ValueError:
                            pass

            # 应用最大值限制
            if calculation.max_score is not None:
                result = min(result, float(calculation.max_score))

            return round(result, 4)
        except Exception as e:
            print(f"乘积计算错误: {e}")
            import traceback
            traceback.print_exc()
            return float(calculation.base_score or 0.0)

    def _calculate_cumulative_score(self, calculation, application, student=None):
        """
        累积计算得分
        基于多个项目的累积值计算最终得分
        """
        if not calculation.parameters:
            return 0.0

        try:
            params = json.loads(calculation.parameters)
            if not isinstance(params, dict):
                return 0.0

            cumulative_field = params.get("cumulative_field")
            multiplier = float(params.get("multiplier", 1.0))

            if not cumulative_field:
                return float(calculation.base_score or 0.0)

            # 获取累积字段值（支持字典和对象两种类型的application参数）
            if isinstance(application, dict):
                cumulative_value = application.get(cumulative_field)
            else:
                cumulative_value = getattr(application, cumulative_field, None)

            if not cumulative_value:
                return float(calculation.base_score or 0.0)

            if not isinstance(cumulative_value, (int, float)):
                try:
                    cumulative_value = float(cumulative_value)
                except (ValueError, TypeError):
                    return float(calculation.base_score or 0.0)

            # 计算累积得分
            result = cumulative_value * multiplier

            # 应用最小值限制
            if params.get("min_score") is not None:
                result = max(result, float(params.get("min_score")))

            return round(result, 4)
        except Exception as e:
            print(f"累积计算错误: {e}")
            return float(calculation.base_score or 0.0)


# 创建规则引擎实例
rule_engine = RuleEngine()

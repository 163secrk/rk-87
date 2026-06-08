from typing import List, Dict, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.risk_rule import RiskRule, RuleConditionOperator, RuleAction
from app.models.customer import Customer
from app.models.loan_application import LoanApplication
from app.models.blacklist import Blacklist
from app.schemas.loan_application import RiskAssessmentResult
import json
import re


class RiskAssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_score = 600
        self.max_score = 1000
        self.min_score = 0

    async def _get_enabled_rules(self) -> List[RiskRule]:
        result = await self.db.execute(
            select(RiskRule).where(RiskRule.is_enabled == True).order_by(RiskRule.priority)
        )
        return result.scalars().all()

    async def _check_blacklist(self, id_card: str) -> bool:
        result = await self.db.execute(
            select(Blacklist).where(
                Blacklist.id_card == id_card,
                Blacklist.is_active == True
            )
        )
        return result.scalar_one_or_none() is not None

    def _get_field_value(self, obj: Any, field_path: str) -> Any:
        fields = field_path.split(".")
        value = obj
        for field in fields:
            if hasattr(value, field):
                value = getattr(value, field)
            elif isinstance(value, dict) and field in value:
                value = value[field]
            else:
                return None
        return value

    def _evaluate_condition(self, field_value: Any, operator: RuleConditionOperator, condition_value: str) -> bool:
        if field_value is None:
            return False

        try:
            if operator in [RuleConditionOperator.GT, RuleConditionOperator.LT,
                           RuleConditionOperator.GTE, RuleConditionOperator.LTE]:
                num_value = float(field_value)
                cond_num = float(condition_value)
                if operator == RuleConditionOperator.GT:
                    return num_value > cond_num
                elif operator == RuleConditionOperator.LT:
                    return num_value < cond_num
                elif operator == RuleConditionOperator.GTE:
                    return num_value >= cond_num
                elif operator == RuleConditionOperator.LTE:
                    return num_value <= cond_num

            elif operator == RuleConditionOperator.EQ:
                return str(field_value) == condition_value

            elif operator == RuleConditionOperator.NEQ:
                return str(field_value) != condition_value

            elif operator == RuleConditionOperator.CONTAINS:
                return condition_value in str(field_value)

            elif operator == RuleConditionOperator.NOT_CONTAINS:
                return condition_value not in str(field_value)

            elif operator == RuleConditionOperator.IN:
                values = [v.strip() for v in condition_value.split(",")]
                return str(field_value) in values

            elif operator == RuleConditionOperator.NOT_IN:
                values = [v.strip() for v in condition_value.split(",")]
                return str(field_value) not in values

        except (ValueError, TypeError):
            return False

        return False

    def _calculate_age(self, birth_date) -> int:
        if not birth_date:
            return 0
        from datetime import date
        today = date.today()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        return age

    def _calculate_debt_ratio(self, customer: Customer, loan_amount: float, loan_term: int) -> float:
        if customer.monthly_income <= 0:
            return 1.0
        monthly_payment = loan_amount / loan_term if loan_term > 0 else loan_amount
        return monthly_payment / customer.monthly_income

    async def _calculate_base_score(self, customer: Customer, application: LoanApplication) -> Tuple[int, List[str]]:
        score = self.base_score
        reasons = []

        age = self._calculate_age(customer.birth_date)
        if 25 <= age <= 45:
            score += 50
            reasons.append(f"年龄{age}岁，处于最佳年龄段，+50分")
        elif 20 <= age < 25 or 45 < age <= 55:
            score += 25
            reasons.append(f"年龄{age}岁，+25分")
        elif age < 20 or age > 60:
            score -= 50
            reasons.append(f"年龄{age}岁，风险较高，-50分")

        if customer.education in ["博士", "硕士", "研究生"]:
            score += 40
            reasons.append(f"学历{customer.education}，+40分")
        elif customer.education == "本科":
            score += 30
            reasons.append(f"学历{customer.education}，+30分")
        elif customer.education == "大专":
            score += 15
            reasons.append(f"学历{customer.education}，+15分")
        elif customer.education in ["高中", "中专", "初中及以下"]:
            score -= 10
            reasons.append(f"学历{customer.education}，-10分")

        if customer.work_years >= 5:
            score += 30
            reasons.append(f"工作年限{customer.work_years}年，+30分")
        elif customer.work_years >= 3:
            score += 20
            reasons.append(f"工作年限{customer.work_years}年，+20分")
        elif customer.work_years >= 1:
            score += 10
            reasons.append(f"工作年限{customer.work_years}年，+10分")
        elif customer.work_years < 1:
            score -= 20
            reasons.append(f"工作年限{customer.work_years}年，-20分")

        if customer.monthly_income >= 50000:
            score += 50
            reasons.append(f"月收入{customer.monthly_income}元，+50分")
        elif customer.monthly_income >= 20000:
            score += 35
            reasons.append(f"月收入{customer.monthly_income}元，+35分")
        elif customer.monthly_income >= 10000:
            score += 20
            reasons.append(f"月收入{customer.monthly_income}元，+20分")
        elif customer.monthly_income >= 5000:
            score += 10
            reasons.append(f"月收入{customer.monthly_income}元，+10分")
        elif customer.monthly_income < 3000:
            score -= 20
            reasons.append(f"月收入{customer.monthly_income}元，-20分")

        if customer.has_house:
            score += 40
            reasons.append("有房产，+40分")
        if customer.has_car:
            score += 20
            reasons.append("有车产，+20分")

        if customer.total_assets > 0 and customer.total_liabilities >= 0:
            if customer.total_liabilities == 0:
                score += 20
                reasons.append("无负债，+20分")
            elif customer.total_liabilities / customer.total_assets < 0.3:
                score += 15
                reasons.append("资产负债率低于30%，+15分")
            elif customer.total_liabilities / customer.total_assets > 0.7:
                score -= 30
                reasons.append("资产负债率高于70%，-30分")

        debt_ratio = self._calculate_debt_ratio(customer, application.loan_amount, application.loan_term)
        if debt_ratio <= 0.3:
            score += 20
            reasons.append(f"月供收入比{debt_ratio:.0%}，+20分")
        elif debt_ratio <= 0.5:
            score += 10
            reasons.append(f"月供收入比{debt_ratio:.0%}，+10分")
        elif debt_ratio > 0.7:
            score -= 40
            reasons.append(f"月供收入比{debt_ratio:.0%}，超过70%，-40分")

        if application.loan_term <= 12:
            score += 10
            reasons.append("贷款期限1年以内，+10分")
        elif application.loan_term <= 36:
            score += 5
            reasons.append("贷款期限1-3年，+5分")
        elif application.loan_term > 60:
            score -= 15
            reasons.append("贷款期限超过5年，-15分")

        return score, reasons

    async def assess_risk(self, customer: Customer, application: LoanApplication) -> RiskAssessmentResult:
        is_blacklisted = await self._check_blacklist(customer.id_card)
        if is_blacklisted:
            return RiskAssessmentResult(
                risk_score=0,
                risk_level="extreme_high",
                auto_decision="reject",
                auto_decision_reason="客户在黑名单中，自动拒绝",
                matched_rules=["黑名单检查"],
                triggered_rules=[{"rule": "黑名单检查", "action": "auto_reject"}]
            )

        base_score, base_reasons = await self._calculate_base_score(customer, application)
        score = base_score
        matched_rules = base_reasons.copy()
        triggered_rules = []
        auto_decision = None
        decision_reasons = []

        rules = await self._get_enabled_rules()

        for rule in rules:
            field_value = self._get_field_value(customer, rule.condition_field)
            if field_value is None:
                field_value = self._get_field_value(application, rule.condition_field)

            if self._evaluate_condition(field_value, rule.condition_operator, rule.condition_value):
                matched_rules.append(f"规则[{rule.rule_name}]触发")
                triggered_rules.append({
                    "rule_code": rule.rule_code,
                    "rule_name": rule.rule_name,
                    "action": rule.action,
                    "action_value": rule.action_value
                })

                if rule.action == RuleAction.SCORE_PLUS:
                    score += int(rule.action_value or 0)
                elif rule.action == RuleAction.SCORE_MINUS:
                    score -= int(rule.action_value or 0)
                elif rule.action == RuleAction.SET_SCORE:
                    score = int(rule.action_value or 0)
                elif rule.action == RuleAction.AUTO_REJECT:
                    auto_decision = "reject"
                    decision_reasons.append(f"规则[{rule.rule_name}]触发，自动拒绝")
                elif rule.action == RuleAction.AUTO_APPROVE:
                    if auto_decision != "reject":
                        auto_decision = "approve"
                    decision_reasons.append(f"规则[{rule.rule_name}]触发，建议自动通过")
                elif rule.action == RuleAction.MANUAL_REVIEW:
                    if auto_decision is None:
                        auto_decision = "manual"
                    decision_reasons.append(f"规则[{rule.rule_name}]触发，需要人工审核")

        score = max(self.min_score, min(self.max_score, score))

        if score >= 800:
            risk_level = "low"
            if auto_decision is None:
                auto_decision = "approve"
                decision_reasons.append("综合评分>=800，建议自动通过")
        elif score >= 700:
            risk_level = "medium_low"
            if auto_decision is None:
                auto_decision = "approve"
                decision_reasons.append("综合评分700-799，建议自动通过")
        elif score >= 600:
            risk_level = "medium"
            if auto_decision is None:
                auto_decision = "manual"
                decision_reasons.append("综合评分600-699，需要人工审核")
        elif score >= 500:
            risk_level = "medium_high"
            if auto_decision is None:
                auto_decision = "manual"
                decision_reasons.append("综合评分500-599，需要人工审核")
        else:
            risk_level = "high"
            if auto_decision is None:
                auto_decision = "reject"
                decision_reasons.append("综合评分<500，自动拒绝")

        return RiskAssessmentResult(
            risk_score=score,
            risk_level=risk_level,
            auto_decision=auto_decision,
            auto_decision_reason="; ".join(decision_reasons) if decision_reasons else "根据评分模型自动决策",
            matched_rules=matched_rules,
            triggered_rules=triggered_rules
        )

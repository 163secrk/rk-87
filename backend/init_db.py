import asyncio
import sys
from datetime import date

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.risk_rule import RiskRule, RuleConditionOperator, RuleAction
from app.models.customer import Customer
from app.models.blacklist import Blacklist


SYNC_DB_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/?charset=utf8mb4"


async def create_database():
    sync_engine = create_engine(SYNC_DB_URL)
    with sync_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        conn.commit()
    sync_engine.dispose()
    print(f"数据库 {settings.DB_NAME} 创建成功")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("数据表创建成功")


async def init_data():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        users = [
            User(
                username="admin",
                email="admin@jindun.com",
                password_hash=get_password_hash("123456"),
                full_name="系统管理员",
                phone="13800000001",
                role=UserRole.ADMIN,
                department="信息技术部",
                is_active=True
            ),
            User(
                username="manager",
                email="manager@jindun.com",
                password_hash=get_password_hash("123456"),
                full_name="张经理",
                phone="13800000002",
                role=UserRole.MANAGER,
                department="风控部",
                is_active=True
            ),
            User(
                username="reviewer1",
                email="reviewer1@jindun.com",
                password_hash=get_password_hash("123456"),
                full_name="李审核",
                phone="13800000003",
                role=UserRole.REVIEWER,
                department="风控部",
                is_active=True
            ),
            User(
                username="reviewer2",
                email="reviewer2@jindun.com",
                password_hash=get_password_hash("123456"),
                full_name="王审核",
                phone="13800000004",
                role=UserRole.REVIEWER,
                department="风控部",
                is_active=True
            ),
            User(
                username="operator1",
                email="operator1@jindun.com",
                password_hash=get_password_hash("123456"),
                full_name="赵专员",
                phone="13800000005",
                role=UserRole.OPERATOR,
                department="运营部",
                is_active=True
            ),
        ]
        db.add_all(users)
        await db.flush()
        print("用户数据初始化完成")

        risk_rules = [
            RiskRule(
                rule_code="RULE_001",
                rule_name="月收入低于3000元",
                description="客户月收入低于3000元，风险较高",
                category="income",
                priority=1,
                condition_field="monthly_income",
                condition_operator=RuleConditionOperator.LT,
                condition_value="3000",
                action=RuleAction.SCORE_MINUS,
                action_value="30",
                is_enabled=True
            ),
            RiskRule(
                rule_code="RULE_002",
                rule_name="月收入高于50000元",
                description="客户月收入高于50000元，风险较低",
                category="income",
                priority=2,
                condition_field="monthly_income",
                condition_operator=RuleConditionOperator.GT,
                condition_value="50000",
                action=RuleAction.SCORE_PLUS,
                action_value="30",
                is_enabled=True
            ),
            RiskRule(
                rule_code="RULE_003",
                rule_name="工作年限不足1年",
                description="客户工作年限不足1年，稳定性较差",
                category="employment",
                priority=3,
                condition_field="work_years",
                condition_operator=RuleConditionOperator.LT,
                condition_value="1",
                action=RuleAction.SCORE_MINUS,
                action_value="20",
                is_enabled=True
            ),
            RiskRule(
                rule_code="RULE_004",
                rule_name="工作年限超过10年",
                description="客户工作年限超过10年，稳定性好",
                category="employment",
                priority=4,
                condition_field="work_years",
                condition_operator=RuleConditionOperator.GT,
                condition_value="10",
                action=RuleAction.SCORE_PLUS,
                action_value="20",
                is_enabled=True
            ),
            RiskRule(
                rule_code="RULE_005",
                rule_name="贷款金额超过50万",
                description="单笔贷款金额超过50万，需要人工审核",
                category="loan",
                priority=5,
                condition_field="loan_amount",
                condition_operator=RuleConditionOperator.GT,
                condition_value="500000",
                action=RuleAction.MANUAL_REVIEW,
                action_value="",
                is_enabled=True
            ),
            RiskRule(
                rule_code="RULE_006",
                rule_name="贷款期限超过10年",
                description="贷款期限超过10年，风险较高",
                category="loan",
                priority=6,
                condition_field="loan_term",
                condition_operator=RuleConditionOperator.GT,
                condition_value="120",
                action=RuleAction.SCORE_MINUS,
                action_value="25",
                is_enabled=True
            ),
            RiskRule(
                rule_code="RULE_007",
                rule_name="高负债",
                description="资产负债率超过70%，风险较高",
                category="liability",
                priority=7,
                condition_field="total_liabilities",
                condition_operator=RuleConditionOperator.GT,
                condition_value="0",
                action=RuleAction.MANUAL_REVIEW,
                action_value="",
                is_enabled=False
            ),
            RiskRule(
                rule_code="RULE_008",
                rule_name="无房无车且低收入",
                description="无房无车且月收入低于5000，需要人工审核",
                category="asset",
                priority=8,
                condition_field="has_house",
                condition_operator=RuleConditionOperator.EQ,
                condition_value="False",
                action=RuleAction.MANUAL_REVIEW,
                action_value="",
                is_enabled=False
            ),
            RiskRule(
                rule_code="RULE_009",
                rule_name="学历初中及以下",
                description="学历较低，减分处理",
                category="education",
                priority=9,
                condition_field="education",
                condition_operator=RuleConditionOperator.IN,
                condition_value="初中,初中及以下,小学",
                action=RuleAction.SCORE_MINUS,
                action_value="15",
                is_enabled=True
            ),
            RiskRule(
                rule_code="RULE_010",
                rule_name="博士/硕士学历",
                description="高学历，加分处理",
                category="education",
                priority=10,
                condition_field="education",
                condition_operator=RuleConditionOperator.IN,
                condition_value="博士,硕士,研究生",
                action=RuleAction.SCORE_PLUS,
                action_value="25",
                is_enabled=True
            ),
        ]
        db.add_all(risk_rules)
        await db.flush()
        print("风控规则数据初始化完成")

        customers = [
            Customer(
                name="张三",
                id_card="110101199001011234",
                phone="13900000001",
                email="zhangsan@example.com",
                gender="男",
                birth_date=date(1990, 1, 1),
                marital_status="已婚",
                education="本科",
                address="北京市朝阳区建国路88号",
                work_unit="北京某科技有限公司",
                position="高级工程师",
                monthly_income=25000,
                total_assets=1500000,
                total_liabilities=300000,
                work_years=8,
                has_house=True,
                has_car=True,
                credit_score=750,
                risk_level="medium_low",
                remark="优质客户"
            ),
            Customer(
                name="李四",
                id_card="110101199505155678",
                phone="13900000002",
                email="lisi@example.com",
                gender="女",
                birth_date=date(1995, 5, 15),
                marital_status="未婚",
                education="硕士",
                address="北京市海淀区中关村大街1号",
                work_unit="某互联网公司",
                position="产品经理",
                monthly_income=35000,
                total_assets=800000,
                total_liabilities=100000,
                work_years=5,
                has_house=False,
                has_car=True,
                credit_score=780,
                risk_level="low",
                remark=""
            ),
            Customer(
                name="王五",
                id_card="310101198808209012",
                phone="13900000003",
                email="wangwu@example.com",
                gender="男",
                birth_date=date(1988, 8, 20),
                marital_status="已婚",
                education="大专",
                address="上海市浦东新区陆家嘴",
                work_unit="某贸易公司",
                position="销售主管",
                monthly_income=15000,
                total_assets=500000,
                total_liabilities=200000,
                work_years=12,
                has_house=True,
                has_car=True,
                credit_score=680,
                risk_level="medium",
                remark=""
            ),
            Customer(
                name="赵六",
                id_card="440101199212123456",
                phone="13900000004",
                email="zhaoliu@example.com",
                gender="男",
                birth_date=date(1992, 12, 12),
                marital_status="未婚",
                education="高中",
                address="广州市天河区天河路",
                work_unit="某餐饮公司",
                position="服务员",
                monthly_income=4500,
                total_assets=50000,
                total_liabilities=0,
                work_years=3,
                has_house=False,
                has_car=False,
                credit_score=580,
                risk_level="medium_high",
                remark="收入较低，无资产"
            ),
            Customer(
                name="孙七",
                id_card="510101198503057890",
                phone="13900000005",
                email="sunqi@example.com",
                gender="女",
                birth_date=date(1985, 3, 5),
                marital_status="已婚",
                education="博士",
                address="成都市武侯区天府大道",
                work_unit="某研究院",
                position="研究员",
                monthly_income=60000,
                total_assets=3000000,
                total_liabilities=500000,
                work_years=15,
                has_house=True,
                has_car=True,
                credit_score=850,
                risk_level="low",
                remark="高端客户"
            ),
        ]
        db.add_all(customers)
        await db.flush()
        print("客户数据初始化完成")

        blacklists = [
            Blacklist(
                name="黑名单用户1",
                id_card="110101197001010001",
                phone="13000000001",
                blacklist_type="fraud",
                reason="涉嫌贷款诈骗，有多次逾期记录",
                source="内部数据",
                added_by=1,
                is_active=True
            ),
            Blacklist(
                name="黑名单用户2",
                id_card="110101197505050002",
                phone="13000000002",
                blacklist_type="overdue",
                reason="多次严重逾期，欠款未还",
                source="人行征信",
                added_by=1,
                is_active=True
            ),
        ]
        db.add_all(blacklists)

        await db.commit()
        print("所有数据初始化完成")
        print("\n默认登录账号：")
        print("  管理员: admin / 123456")
        print("  经理: manager / 123456")
        print("  审核员: reviewer1 / 123456, reviewer2 / 123456")
        print("  操作员: operator1 / 123456")


async def main():
    try:
        print("开始初始化数据库...")
        await create_database()
        await create_tables()
        await init_data()
        print("\n数据库初始化完成！")
        print(f"数据库地址: {settings.DB_HOST}:{settings.DB_PORT}")
        print(f"数据库名: {settings.DB_NAME}")
    except Exception as e:
        print(f"初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

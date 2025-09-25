import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Tuple
from loguru import logger
from sqlalchemy import Column, DateTime, text, func, delete, and_, UniqueConstraint, desc
from sqlmodel import Field, select, update, SQLModel

from bisheng.database.base import session_getter
from bisheng.database.constants import AdminRole
from bisheng.database.models.base import SQLModelSerializable


class FlowStatus(Enum):
    LIKE = 1
    CANCEL = 2

class UpvoteBase(SQLModelSerializable):
    """
    技能收藏表
    """
    user_id: int = Field(default=0, description='创建用户ID')
    flow_id: str = Field(index=True, max_length=32, description="所属的技能ID")
    flow_type: Optional[int] = Field(index=False, default=1)
    status: Optional[int] = Field(index=False, default=1)
    create_time: Optional[datetime] = Field(default=None, sa_column=Column(
        DateTime, nullable=False, index=True, server_default=text('CURRENT_TIMESTAMP')))
    update_time: Optional[datetime] = Field(default=None, sa_column=Column(
        DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP')))


class Upvote(UpvoteBase, table=True):
    __tablename__ = "upvote"
    __table_args__ = (UniqueConstraint('user_id', 'flow_id', 'flow_type', name='user_upvote_flow_unique'), {"comment": "技能收藏表"})
    id: Optional[int] = Field(default=None, index=True, primary_key=True, description="标签唯一ID")


# 定义结果模型（不会建表，只用于返回）
class UpvoteCount(SQLModel):
    flow_id: str
    count: int

class UpvoteDao(Upvote):
    @classmethod
    def get_upvote_by_user_id(cls, user_id: int, status: Optional[int] = None) -> List[Upvote]:
        """ 根据用户查询收藏的工作流记录 """
        with session_getter() as session:
            query = select(Upvote).where(Upvote.user_id == user_id)
            if status is not None:
                query = query.where(Upvote.status == status)
            return list(session.exec(query).all())

    @classmethod
    def get_upvote_by_flow_id(cls, flow_id: str, flow_type: int, status: Optional[int] = None) -> int:
        logger.info(f"flow_id: {flow_id}, flow_type: {flow_type}, status: {status}")
        with session_getter() as session:
            query = select(Upvote).where(
                and_(Upvote.flow_id == flow_id), Upvote.flow_type == flow_type
            )
            if status is not None:
                query = query.where(Upvote.status == status)
            count_query = select(func.count()).select_from(query.subquery())
            total = session.exec(count_query).one()
            return total

    @classmethod
    def get_upvote_by_user_flow_id(cls, user_id: int, flow_id: str) -> Upvote | None:
        with session_getter() as session:
            query = select(Upvote).where(and_(Upvote.user_id == user_id, Upvote.flow_id == flow_id))
            return session.exec(query).first()

    @classmethod
    def get_count_by_ids(cls, flow_ids: List[str]) -> List[UpvoteCount] | None:
        """ 根据技能ID列表查询技能收藏数量 """
        with (session_getter() as session):
            statement = select(Upvote.flow_id, func.count().label('count')) \
                .where(and_(Upvote.flow_id.in_(flow_ids), Upvote.status == 1)) \
                .group_by(Upvote.flow_id).order_by(desc(func.count()))
            result = session.exec(statement).all()
            return [UpvoteCount(flow_id=row[0], count=row[1]) for row in result] if result is not None else None

    @classmethod
    def insert_upvote(cls, upvote: Upvote) -> Upvote:
        """ 插入点赞收藏关联数据 """
        with session_getter() as session:
            session.add(upvote)
            session.commit()
            session.refresh(upvote)
            return upvote

    @classmethod
    def update_upvote(cls, flow_id: str, user_id: int, status: int) -> int:
        """ 更新点赞收藏关联数据 """
        with session_getter() as session:
            statement = update(Upvote).where(and_(Upvote.flow_id == flow_id, Upvote.user_id == user_id)).values(
                status=status, update_time=datetime.now())
            result = session.exec(statement)
            session.commit()
            return result

import json
from typing import List

from fastapi import Request, HTTPException
from loguru import logger

from bisheng.api.errcode.base import UnAuthorizedError
from bisheng.api.services.user_service import UserPayload
from bisheng.database.models.upvote import Upvote, UpvoteDao


class UpvoteService:
    @classmethod
    def get_upvote_by_flow_id(cls,
                 request: Request,
                 login_user: UserPayload,
                 flow_id: str,
                 flow_type: int,
                 status: int) -> int:
        """
        获取技能收藏
        """
        count = UpvoteDao.get_upvote_by_flow_id(flow_id=flow_id, flow_type=flow_type, status=1)
        return count

    @classmethod
    def get_upvote_by_user_flow_id(cls,
                 request: Request,
                 login_user: UserPayload,
                 flow_id: str,
                 flow_type: int,
                 status: int) -> List[Upvote]:
        """
        获取技能收藏
        """
        upvote = UpvoteDao.get_upvote_by_user_flow_id(user_id=login_user.user_id, flow_id=flow_id)
        return upvote

    @classmethod
    def create_upvote(cls,
                     request: Request,
                     login_user: UserPayload,
                     flow_id: str,
                     flow_type: int,
                     status: int) -> Upvote:
        """
        登记技能收藏
        """
        new_upvote = Upvote(flow_id=flow_id, flow_type=flow_type, status=status, user_id=login_user.user_id)
        new_upvote = UpvoteDao.insert_upvote(new_upvote)
        return new_upvote

    @classmethod
    def update_upvote(cls,
                    request: Request,
                    login_user: UserPayload,
                    flow_id: str,
                    flow_type: int,
                    status: int) -> Upvote:
        """
        更新技能收藏
        """
        upvote = UpvoteDao.get_upvote_by_user_flow_id(login_user.user_id, flow_id)
        if not upvote:
            upvote = Upvote(user_id=login_user.user_id, flow_id=flow_id, flow_type=flow_type, status=status)
        else:
            upvote.status = status
        result = UpvoteDao.insert_upvote(upvote)
        return result

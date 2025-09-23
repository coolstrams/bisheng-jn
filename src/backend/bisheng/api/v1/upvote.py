from typing import List

from fastapi import APIRouter, Request, Depends, Query, Body

from bisheng.api.services.upvote import UpvoteService
from bisheng.api.services.user_service import UserPayload, get_login_user, get_admin_user
from bisheng.api.v1.schemas import UnifiedResponseModel, resp_200
from bisheng.database.models.upvote import Upvote

router = APIRouter(prefix='/upvote', tags=['Upvote'])


@router.get('')
def get_upvote(
        request: Request,
        login_user: UserPayload = Depends(get_login_user),
        flow_id: str = Query(None, description='技能ID'),
        flow_type: int = Query(None, description='技能类型'),
        status: int = Query(None, description='技能状态'),
):
    count = UpvoteService.get_upvote_by_flow_id(request, login_user, flow_id, flow_type, status == 1)
    return resp_200(count)


@router.post('')
def create_upvote(
        request: Request,
        login_user: UserPayload = Depends(get_login_user),
        flow_id: str = Body(..., embed=True, description='技能ID'),
        flow_type: int = Body(..., embed=True, description='技能类型'),
        status: int = Body(..., embed=True, description='技能状态'),
):
    result = UpvoteService.create_upvote(request, login_user, flow_id, flow_type, status)
    return resp_200(result)


@router.put('')
def update_upvote(
        request: Request,
        login_user: UserPayload = Depends(get_login_user),
        flow_id: str = Body(..., embed=True, description='技能ID'),
        flow_type: int = Body(..., embed=True, description='技能类型'),
        status: int = Body(..., embed=True, description='技能状态'),
):
    result = UpvoteService.update_upvote(request, login_user, flow_id, flow_type, status)
    return resp_200(result)

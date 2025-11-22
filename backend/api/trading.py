# # ===================================
# # api/trading.py (Proxy endpoints)
# # ===================================
# from fastapi import APIRouter, HTTPException, status, Depends
# from backend.models.common import APIResponse
# from backend.services.trading_service import trading_service
# from backend.core.security import get_current_user

# router = APIRouter()

# @router.get("/metrics", response_model=APIResponse)
# async def get_trading_metrics(current_user_id: str = Depends(get_current_user)):
#     """Get live trading metrics for dashboard"""
    
#     user_result = await user_service.get_user_by_id(current_user_id)
#     if not user_result["status"]:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
#     user = user_result["data"]
#     result = await trading_service.get_live_trading_metrics(current_user_id, user["role"])
    
#     if result["status"]:
#         return APIResponse(
#             success=True,
#             message="Trading metrics retrieved successfully",
#             data=result["data"]
#         )
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to fetch trading metrics"
#         )

# @router.get("/positions", response_model=APIResponse)
# async def get_live_positions(
#     group_id: str = None,
#     current_user_id: str = Depends(get_current_user)
# ):
#     """Get current open positions"""
    
#     result = await trading_service.get_live_positions(group_id)
    
#     if result["status"]:
#         return APIResponse(
#             success=True,
#             message="Live positions retrieved successfully",
#             data=result["data"]
#         )
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to fetch positions"
#         )

# @router.get("/member-performance/{member_id}", response_model=APIResponse)
# async def get_member_performance(
#     member_id: str,
#     current_user_id: str = Depends(get_current_user)
# ):
#     """Get detailed member performance"""
    
#     result = await trading_service.get_member_performance(member_id)
    
#     if result["status"]:
#         return APIResponse(
#             success=True,
#             message="Member performance retrieved successfully",
#             data=result["data"]
#         )
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to fetch member performance"
#         )
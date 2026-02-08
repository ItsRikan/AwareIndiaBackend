from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
import asyncio

from src.scan.model import (
    scan_image_async,
    response_model_async,
    compare_model_async
)
from src.schema import (
    VisionModelSchema,
    ResponseModelSchema,
    ScanImageResponseSchema,
    ScanRequestSchema,
    CompareRequestSchema,
    CompareModelOutputSchema,
    CompareOutputSchema,
)
from src.routers.history import insert_into_history
from src.routers.auth import get_current_user
router = APIRouter()


@router.post("/scan")
async def scan(req:ScanRequestSchema,user=Depends(get_current_user)):
    vision_response:VisionModelSchema = await scan_image_async(url=req.url)
    if not vision_response.status:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,detail="Vision model failed to scan the image")
    final_response:ResponseModelSchema = await response_model_async(
        ingredients=vision_response.ingredients,
        category=req.category,
        allergy=req.allergy
    )
    if not final_response.status:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,detail="Response model failed to generate response")

    await insert_into_history(
        user_id=user.id,
        name=final_response.product_name,
        image_url=req.url,
        health_score=final_response.health_score,
        calory=vision_response.nutrition_estimate.get("calory"),
        energy=vision_response.nutrition_estimate.get("energy"),
        protein=vision_response.nutrition_estimate.get("protein"),
        sugar=vision_response.nutrition_estimate.get("sugar"),
        fat=vision_response.nutrition_estimate.get("fat"),
        fiber=vision_response.nutrition_estimate.get("fiber")
    )
    return ScanImageResponseSchema(
        is_safe=final_response.is_safe,
        url=req.url,
        health_score=final_response.health_score,
        product_name=vision_response.name or final_response.product_name,
        description=final_response.description,
        ingredients=final_response.ingredients,
        nutrition_estimate=vision_response.nutrition_estimate
    )

@router.post("/compare")
async def compare(req:CompareRequestSchema,user=Depends(get_current_user)):
    scan_1,scan_2 = await asyncio.gather(
        scan_image_async(req.url1),
        scan_image_async(req.url2)
    )
    if not scan_1.status or not scan_2.status:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,detail="Vision model failed to scan the image")
    
    final_response:CompareModelOutputSchema = await compare_model_async(
        product1=scan_1,
        product2=scan_2,
        use_case=req.usecase,
        allergy=req.allergy,
        category=req.category
    )
    if not final_response.status:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,detail="Compare model failed to generate the response")
    return CompareOutputSchema(
        url1=req.url1,
        url2=req.url2,
        best_product=final_response.best_product,
        is_safe1=final_response.is_safe1,
        is_safe2=final_response.is_safe2,
        health_score1=final_response.health_score1,
        health_score2=final_response.health_score2,
        description1=final_response.description1,
        description2=final_response.description2,
        preferred_for_you=final_response.preferred_for_you
    )
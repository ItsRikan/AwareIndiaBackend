


from fastapi import APIRouter,Depends


from src.routers.auth import get_current_user, supabase

router = APIRouter()
async def insert_into_history(
        user_id:str,
        name:str,
        image_url:str,
        health_score:int,
        calory:int,
        energy:int,
        protein:int,
        sugar:int,
        fat:int,
        fiber:int
        ):
    try:
        supabase.table('history').insert({
            "user":user_id,
            "name":name,
            "image_url":image_url,
            "health_score":health_score,
            "calory":calory,
            "energy":energy,
            "protein":protein,
            "sugar":sugar,
            "fat":fat,
            "fiber":fiber
            
            }).execute()
    except Exception as e:
        print(f"Error inserting history: {e}")
        raise
@router.get("/history")
async def get_recent_history(user=Depends(get_current_user)):
    try:
        history = supabase.table('history').select("*").eq("user",user.id).order("created_at").execute()
        return history.data[:10]
    except:
        return []
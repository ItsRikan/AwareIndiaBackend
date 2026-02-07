import os
import re,json
from google.genai import Client, types, errors
import aiohttp
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import mimetypes


from src.scan.utils import http_options
from src.scan.instruction import VISION_MODEL_INSTRUCTION,RESPONSE_MODEL_INSTRUCTION, COMPARE_MODEL_INSTRUCTION
from src.schema import VisionModelSchema,ResponseModelSchema,Ingredients,CompareModelOutputSchema
from src.scan.config import MODEL1,MODEL2
load_dotenv()
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
model = Client(api_key=GOOGLE_API_KEY,http_options=http_options)

def extract_structured_text(markdown_string):
    match = re.search(r"```[a-zA-Z]*\n([\s\S]*?)\n```", markdown_string)
    if match:
        return match.group(1).strip()
    else:
        return None
    

async def load_and_validate_image(url:str)->bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            content = await resp.read()
            img = Image.open(BytesIO(content))
            img.verify()
            return content


async def scan_image_async(url:str)->VisionModelSchema:
    mime_type=None
    try:
        mime_type, _ = mimetypes.guess_type(url)
        mime_type = mime_type or "image/jpeg"
        image_bytes = await load_and_validate_image(url) 
        response = await model.aio.models.generate_content(
            model=MODEL1,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                ),
                VISION_MODEL_INSTRUCTION
            ]
        )
        response = extract_structured_text(response.text)
        response = VisionModelSchema.model_validate_json(response)
        return response
    except errors.APIError as e:
        return VisionModelSchema(status=False,ingredients=[""],nutrition_estimate={"":0})

async def response_model_async(ingredients:list,category:str,allergy:str)->ResponseModelSchema:
    try:
        ingredients = ", ".join(str(i).lower() for i in ingredients)
        additional_info = f"Ingredients : {ingredients}; Category : {category}; Allergies or Diseases : {allergy}"

        prompt = RESPONSE_MODEL_INSTRUCTION + "\n" + additional_info
        response = await model.aio.models.generate_content(
            model=MODEL2,
            contents=[prompt,]
        )
        response = extract_structured_text(response.text)
        return ResponseModelSchema.model_validate_json(response)
    except Exception as e:
        return ResponseModelSchema(
            is_safe=False,
            product_name="",
            description="",
            ingredients=[Ingredients(name="",Itype="",description="",health_score=0)],
            health_score=0,
            status=False
            )
    
async def compare_model_async(product1:dict,product2:dict,use_case:str,allergy:str,category:str):
    try:
        additional_info = f"\n Input : \n Product1 Details : {product1} \n Product2 Details : {product2} \n Use case : {use_case}\n Allergy : {allergy}\n Category : {category}"
        prompt = COMPARE_MODEL_INSTRUCTION + additional_info
        response = await model.aio.models.generate_content(
            model=MODEL2,
            contents=[prompt,]
        )
        response = extract_structured_text(response.text)
        return CompareModelOutputSchema.model_validate_json(response)
    except:
        return CompareModelOutputSchema(
            status=False,
            best_product="",
            is_safe1=False,
            is_safe2=False,
            health_score1=0,
            health_score2=0,
            description1="",
            description2="",
            preferred_for_you=""
        )

from fastapi import FastAPI, UploadFile, File, HTTPException
import easyocr
from PIL import Image
import io
import re
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


try:
    reader = easyocr.Reader(['de'], gpu=False)
    logger.info("EasyOCR Reader initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing EasyOCR Reader: {e}")
    raise RuntimeError(f"Could not initialize EasyOCR: {e}")



FULL_PLATE_PATTERN = re.compile(r'^([A-Z]{1,3})([A-Z]{1,2})([0-9]{1,4})$')

CITY_CODE_PATTERN = re.compile(r'^[A-Z]{1,3}$')

REST_OF_PLATE_PATTERN = re.compile(r'^[A-Z]{1,2}[0-9]{1,4}$')

FORMATTED_PLATE_PATTERN = re.compile(r'^[A-Z]{1,3}-[A-Z]{1,2}[0-9]{1,4}$')

def find_plates_from_texts(texts):

    potential_plates = set() 

    if not texts:
        return []

    
    cleaned_texts = [re.sub(r'[^A-Z0-9]', '', text.upper()) for text in texts]
    
    cleaned_texts = [t for t in cleaned_texts if t]

    num_texts = len(cleaned_texts)

  
    for i, cleaned_text in enumerate(cleaned_texts):
        match = FULL_PLATE_PATTERN.match(cleaned_text)
        if match:
            city_code, letters, numbers = match.groups()
            formatted_plate = f"{city_code}-{letters}{numbers}"
            potential_plates.add(formatted_plate)
            logger.info(f"Plate number found (Einzelblock): original='{texts[i]}', cleaned='{cleaned_text}', formatted='{formatted_plate}'")

   
    if num_texts >= 2:
        for i in range(num_texts):
          
            text_i = cleaned_texts[i]
            if CITY_CODE_PATTERN.match(text_i):
                
                for j in range(num_texts):
                    if i == j: 
                        continue

                    text_j = cleaned_texts[j]
                    
                    if REST_OF_PLATE_PATTERN.match(text_j):
                       
                        formatted_plate = f"{text_i}-{text_j}" 

                     
                        if FORMATTED_PLATE_PATTERN.match(formatted_plate):
                            potential_plates.add(formatted_plate)
                        
                            logger.info(f"Plate found (Kombiniert): parts='{text_i}' + '{text_j}', formatted='{formatted_plate}'")
                    

    return list(potential_plates)

@app.post("/scan")
async def scan_plate(file: UploadFile = File(...)):
   
    logger.info(f"Received file: {file.filename}, Content-Type: {file.content_type}")
    if not file.content_type or not file.content_type.startswith('image/'):
        logger.warning(f"Received file with invalid Content-Type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        image_bytes = await file.read()
        if len(image_bytes) > 10 * 1024 * 1024:
             logger.warning("Image file size too large.")
             raise HTTPException(status_code=413, detail="Image file too large (max 10MB).")

       
        result_texts = reader.readtext(image_bytes, detail=0, paragraph=False)
        logger.info(f"OCR Results (raw texts): {result_texts}")

        
        plates = find_plates_from_texts(result_texts)
        logger.info(f"Detected plates (final): {plates}")

        return {"plates": plates}

    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during image processing.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
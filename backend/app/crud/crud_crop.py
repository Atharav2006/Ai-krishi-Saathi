from app.crud.base import CRUDBase
from app.models.crop import Crop
from app.schemas.crop import CropBase

class CRUDCrop(CRUDBase[Crop, CropBase, CropBase]):
    pass

crop = CRUDCrop(Crop)

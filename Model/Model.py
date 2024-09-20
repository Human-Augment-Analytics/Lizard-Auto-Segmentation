from transformers import Mask2FormerForUniversalSegmentation


category_info = {0: 'Background', 1: 'Lower Jaw', 2: 'Tooth', 3: 'Other Bone'}


class Model:
    def __init__():
        self.model = Mask2FormerForUniversalSegmentation.from_pretrained('facebook/mask2former-swin-base-coco-panoptic', id2label=category_info, ignore_mismatched_sizes=True)


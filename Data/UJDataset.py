from torch.utils.data import Dataset
import numpy as np
import torch

class UJDataset(Dataset):
    """Pytorch Dataset for preprocessed lizard scans with upper jaw and skull also segmented"""

    def __init__(self, dataset, processor, transform=None):
        self.dataset = dataset
        self.processor = processor
        self.transform = transform
    
    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        image = np.array(self.dataset[idx]['image'], dtype=np.float32)
        panoptic_seg_gt = np.array(self.dataset[idx]['label'], dtype=np.float32)

        if self.transform is not None:
            transformed = self.transform(image= image, mask= panoptic_seg_gt)
            image, panoptic_seg_gt = transformed['image'], transformed['mask']
            image = image.transpose(2,0,1)
        
        inst2class = {segment['id']: segment['category_id'] for segment in self.dataset[idx]['segments_info']}

        inputs = self.processor([image], [panoptic_seg_gt], instance_id_to_semantic_id=inst2class, return_tensors='pt')
        inputs = {k: v.squeeze() if isinstance(v, torch.Tensor) else v[0] for k, v in inputs.items()}
        return inputs

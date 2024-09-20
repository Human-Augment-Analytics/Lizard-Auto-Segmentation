from torch.utils.data import DataLoader
from Data.UJDataset import UJDataset
import albumentations as A
from datasets import Dataset, load_from_disk
from transformers import Mask2FormerImageProcessor
from Model.Model import Model


train = load_from_disk("OneScanDataset.hf")
processor = Mask2FormerImageProcessor(ignore_index=0, do_resize=False, do_rescale=False, do_normalize=False)
print(train[0]['image'])

transform = A.Compose([
    A.Resize(width=512, height=512),
    A.ToRGB()
])

train_ds = UJDataset(train, processor, transform)

def collate_fn(batch):
    pixel_values = torch.stack([example["pixel_values"] for example in batch])
    pixel_mask = torch.stack([example["pixel_mask"] for example in batch])
    class_labels = [example["class_labels"] for example in batch]
    mask_labels = [example["mask_labels"] for example in batch]
    return {"pixel_values": pixel_values, "pixel_mask": pixel_mask, "class_labels": class_labels, "mask_labels": mask_labels}

train_dataloader = DataLoader(train_ds, batch_size=2, shuffle=True, collate_fn=collate_fn)
print(train[0]['image'].size)
print(train_ds[1])

batch = next(iter(train_dataloader))
print(batch)
m = Model()
o = m.model(
    pixel_values=batch["pixel_values"],
    mask_labels=batch["mask_labels"],
    class_labels=batch["class_labels"]
)
print(o.loss)
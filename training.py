from torch.utils.data import DataLoader
from Data.UJDataset import UJDataset
import albumentations as A
from datasets import Dataset, load_from_disk
from transformers import Mask2FormerImageProcessor
from Model.Model import Model
import torch


data = load_from_disk("TwoScanDataset.hf")
processor = Mask2FormerImageProcessor(ignore_index=0, do_resize=False, do_rescale=False, do_normalize=False)

train = data['Train']
val = data['Test']


transform = A.Compose([
    A.Resize(width=512, height=512),
    A.ToRGB(),
    A.HorizontalFlip(p=0.5)
])

train_ds = UJDataset(train, processor, transform)
val_ds = UJDataset(val, processor, transform)

def collate_fn(batch):
    pixel_values = torch.stack([example["pixel_values"] for example in batch])
    pixel_mask = torch.stack([example["pixel_mask"] for example in batch])
    class_labels = [example["class_labels"] for example in batch]
    mask_labels = [example["mask_labels"] for example in batch]
    return {"pixel_values": pixel_values, "pixel_mask": pixel_mask, "class_labels": class_labels, "mask_labels": mask_labels}

train_dataloader = DataLoader(train_ds, batch_size=2, shuffle=True, collate_fn=collate_fn)
val_dataloader = DataLoader(val_ds, batch_size=2, shuffle=True, collate_fn=collate_fn)
#print(train[0]['image'].size)
#print(train_ds[1])

#batch = next(iter(train_dataloader))
#print(batch)
m = Model()
#o = m.model(
#    pixel_values=batch["pixel_values"],
#    mask_labels=batch["mask_labels"],
#    class_labels=batch["class_labels"]
#)
#print(o.loss)



from tqdm.auto import tqdm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
m.model.to(device)

optimizer = torch.optim.Adam(m.model.parameters(), lr=5e-5)

running_loss = 0.0
num_samples = 0
for epoch in range(10):
  print("Epoch:", epoch)
  m.model.train()
  for idx, batch in enumerate(tqdm(train_dataloader)):
      # Reset the parameter gradients
      optimizer.zero_grad()

      # Forward pass
      outputs = m.model(
              pixel_values=batch["pixel_values"].to(device),
              mask_labels=[labels.to(device) for labels in batch["mask_labels"]],
              class_labels=[labels.to(device) for labels in batch["class_labels"]],
      )

      # Backward propagation
      loss = outputs.loss
      loss.backward()

      batch_size = batch["pixel_values"].size(0)
      running_loss += loss.item()
      num_samples += batch_size

      if idx % 100 == 0:
        print("Loss:", running_loss/num_samples)

      # Optimization
      optimizer.step()
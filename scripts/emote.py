# import os
# import random
# import argparse
# import numpy as np
# import pandas as pd
# from sklearn.metrics import classification_report

# import torch
# from torch.utils.data import Dataset
# from torch.utils.data import DataLoader
# import torch.nn as nn
# from torch.nn import BCEWithLogitsLoss
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# from transformers import AdamW
# from emote_config import Emote_Config

# from unsupervised import UnsupervisedEval
# from finetune import EmoteTrainer


# def set_seed(seed):
#     random.seed(seed)
#     np.random.seed(seed)
#     torch.manual_seed(seed)
#     torch.cuda.manual_seed_all(seed)
#     torch.backends.cudnn.deterministic = True
#     torch.backends.cudnn.benchmark = False


# def encode_data(tokenizer, sentences_1, sentences_2, labels, strategies):
#     """Encode the sentences and labels into a format that the model can understand."""
#     inputs = tokenizer(list(sentences_1), list(sentences_2), truncation=True, padding=True, return_tensors="pt")
#     labels = torch.tensor(labels)
#     strategies = torch.tensor(strategies)
    
#     return inputs, labels, strategies
        

# class CustomizedDataset(Dataset):
#     def __init__(self, encodings, labels, strategies):
#         self.encodings = encodings
#         self.labels = labels
#         self.strategies = strategies

#     def __getitem__(self, idx):
#         item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
#         item['labels'] = self.labels[idx].clone().detach()
#         item['strategies'] = self.strategies[idx].clone().detach()
#         return item

#     def __len__(self):
#         return len(self.labels)



# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--finetune', type=int, default=0, help='0 means unsupervised, 1 means fine-tuning.')
#     parser.add_argument('--model_name', type=str, default='bert-base', help='Options include bert-base, roberta-base, roberta-large, or bart-large')
#     parser.add_argument('--portion', type=float, default=1, help='A float indicating the portion of training data used, default is 1.')
#     parser.add_argument('--seed', type=int, default=43)
#     parser.add_argument('--hfpath', type=str, default='YOUR_PATH', help='directory for huggingface cache')
#     args = parser.parse_args()

#     new_emote_config = Emote_Config(args.finetune, args.model_name, args.portion, args.seed, args.hfpath)

#     seed = args.seed
#     set_seed(seed)

#     os.environ["HF_HOME"] = new_emote_config.hfpath

#     print('model_name: ', new_emote_config.model_name)
#     print('model_path: ', new_emote_config.model_path)

#     tokenizer = AutoTokenizer.from_pretrained(new_emote_config.model_path)
#     tokenizer.add_tokens(['[EM]'])

#     # Load the data
#     if args.portion == 1.0:
#         train_data = pd.read_csv(new_emote_config.train_csv_fp, escapechar='\\', engine='python')
#     else:
#         train_data = pd.read_csv(new_emote_config.train_csv_fp, escapechar='\\', engine='python')
#         train_data = train_data.sample(frac=new_emote_config.portion, random_state=1)
#         train_data = train_data.reset_index(drop=True)
#         print('train_data.shape: ', train_data.shape)
#         print(train_data.head(10))

#     val_data = pd.read_csv(new_emote_config.val_csv_fp, escapechar='\\', engine='python')
#     test_data = pd.read_csv(new_emote_config.test_csv_fp, escapechar='\\', engine='python')

#     # merge train_data and val_data and test_data into all_data
#     all_data = pd.concat([train_data, val_data, test_data], ignore_index=True)


#     # Encode the data
#     train_inputs, train_labels, train_strategies = encode_data(tokenizer, train_data['sent1'], train_data['sent2'], train_data['label'], train_data['strategy'])
#     val_inputs, val_labels, val_strategies = encode_data(tokenizer, val_data['sent1'], val_data['sent2'], val_data['label'], val_data['strategy'])
#     test_inputs, test_labels, test_strategies = encode_data(tokenizer, test_data['sent1'], test_data['sent2'], test_data['label'], test_data['strategy'])
#     all_inputs, all_labels, all_strategies = encode_data(tokenizer, all_data['sent1'], all_data['sent2'], all_data['label'], all_data['strategy'])

#     # Create the datasets
#     train_dataset = CustomizedDataset(train_inputs, train_labels, train_strategies)
#     val_dataset = CustomizedDataset(val_inputs, val_labels, val_strategies)
#     test_dataset = CustomizedDataset(test_inputs, test_labels, test_strategies)
#     all_dataset = CustomizedDataset(all_inputs, all_labels, all_strategies)

#     # Define the batch size
#     batch_size = new_emote_config.bs

#     # Create the DataLoaders
#     train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
#     val_loader = DataLoader(val_dataset, batch_size=batch_size)
#     test_loader = DataLoader(test_dataset, batch_size=batch_size)
#     all_loader = DataLoader(all_dataset, batch_size=batch_size)

#     # Define the device
#     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#     if args.finetune == 0:
#         # Which means unsupervised evaluation
#         model = AutoModelForSequenceClassification.from_pretrained(new_emote_config.model_path)
#         # Resize the token embeddings of the model
#         model.resize_token_embeddings(len(tokenizer))
#         new_token_id = tokenizer.convert_tokens_to_ids('[EM]')
#         print('new_token_id: ', new_token_id)
#         embeddings = model.get_input_embeddings()
#         with torch.no_grad():
#             # Since our special [EM] token is a new token, we need to initialize its embedding
#             # In our paper, we didn't set the initialization, and the Transformer version at that time will produce a random initialization, so there will be some different results w.r.t. the different initializations.
#             embeddings.weight[new_token_id] = torch.normal(0, 0.01, (embeddings.embedding_dim,))
#         print('Unsupervised evaluation')
#         model.to(device)
#         unsupervised_eval = UnsupervisedEval(model, test_loader, device, 'test', new_emote_config)
#         unsupervised_eval.unsupervised_evaluation()
#         exit()

#     # Load the pretrained model and changed the output space into 2 labels;
#     # We make this decision baded on the rationaled that even though the output space is changed, the model is still pretrained on the MNLI dataset and have the parametric knowledge of the entailment task.
    
#     # An updated PyTorch or Transformers version may produce slightly different results for the fine-tuning experiments. 
#     model = AutoModelForSequenceClassification.from_pretrained(new_emote_config.model_path, num_labels=2, output_hidden_states=True, ignore_mismatched_sizes=True)
    
#     model.resize_token_embeddings(len(tokenizer)) 
#     model.to(device)

#     # Initialize the trainer
#     trainer = EmoteTrainer(model, train_loader, val_loader, test_loader, device, new_emote_config=new_emote_config, tokenizer=tokenizer)

#     # Train the model
#     trainer.train(epochs=new_emote_config.max_epoch)
import os
import random
import argparse
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report

import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
from torch.nn import BCEWithLogitsLoss
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW
from emote_config import Emote_Config

from unsupervised import UnsupervisedEval
from finetune import EmoteTrainer


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def encode_data(tokenizer, sentences_1, sentences_2, labels, strategies):
    """将文本和标签转换为模型可接受的格式。"""
    # 将文本数据转换为字符串，并填充缺失值为空字符串
    sents1 = [str(s) for s in sentences_1.fillna("").tolist()]
    sents2 = [str(s) for s in sentences_2.fillna("").tolist()]
    inputs = tokenizer(sents1, sents2, truncation=True, padding=True, return_tensors="pt")
    
    # 将标签和策略转成列表后再转换为 tensor
    labels = torch.tensor(labels.tolist())
    strategies = torch.tensor(strategies.tolist())
    
    return inputs, labels, strategies
        

class CustomizedDataset(Dataset):
    def __init__(self, encodings, labels, strategies):
        self.encodings = encodings
        self.labels = labels
        self.strategies = strategies

    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        item['labels'] = self.labels[idx].clone().detach()
        item['strategies'] = self.strategies[idx].clone().detach()
        return item

    def __len__(self):
        return len(self.labels)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--finetune', type=int, default=0, help='0 表示无监督评估，1 表示微调。')
    parser.add_argument('--model_name', type=str, default='bert-base', help='可选：bert-base, roberta-base, roberta-large, 或 bart-large')
    parser.add_argument('--portion', type=float, default=1, help='训练数据的比例，默认是 1。')
    parser.add_argument('--seed', type=int, default=43)
    parser.add_argument('--hfpath', type=str, default='YOUR_PATH', help='HuggingFace 缓存目录')
    args = parser.parse_args()

    new_emote_config = Emote_Config(args.finetune, args.model_name, args.portion, args.seed, args.hfpath)

    seed = args.seed
    set_seed(seed)

    os.environ["HF_HOME"] = new_emote_config.hfpath

    print('model_name: ', new_emote_config.model_name)
    print('model_path: ', new_emote_config.model_path)

    tokenizer = AutoTokenizer.from_pretrained(new_emote_config.model_path)
    tokenizer.add_tokens(['[EM]'])

    # 读取数据，同时指定 escapechar 和 engine
    if args.portion == 1.0:
        train_data = pd.read_csv(new_emote_config.train_csv_fp, escapechar='\\', engine='python')
    else:
        train_data = pd.read_csv(new_emote_config.train_csv_fp, escapechar='\\', engine='python')
        train_data = train_data.sample(frac=new_emote_config.portion, random_state=1)
        train_data = train_data.reset_index(drop=True)
        print('train_data.shape: ', train_data.shape)
        print(train_data.head(10))

    if args.portion == 1.0:
        train2_data = pd.read_csv(new_emote_config.train2_csv_fp, escapechar='\\', engine='python')
    else:
        train2_data = pd.read_csv(new_emote_config.train2_csv_fp, escapechar='\\', engine='python')
        train2_data = train2_data.sample(frac=new_emote_config.portion, random_state=1)
        train2_data = train2_data.reset_index(drop=True)
        print('train2_data.shape: ', train2_data.shape)
        print(train2_data.head(10))

    val_data = pd.read_csv(new_emote_config.val_csv_fp, escapechar='\\', engine='python')
    test_data = pd.read_csv(new_emote_config.test_csv_fp, escapechar='\\', engine='python')

    # 合并数据（可选）
    all_data = pd.concat([train_data, val_data, test_data], ignore_index=True)

    # 对数据进行编码
    train_inputs, train_labels, train_strategies = encode_data(tokenizer, train_data['sent1'], train_data['sent2'], train_data['label'], train_data['strategy'])
    train2_inputs, train2_labels, train2_strategies = encode_data(tokenizer, train2_data['sent1'], train2_data['sent2'], train2_data['label'], train2_data['strategy'])
    val_inputs, val_labels, val_strategies = encode_data(tokenizer, val_data['sent1'], val_data['sent2'], val_data['label'], val_data['strategy'])
    test_inputs, test_labels, test_strategies = encode_data(tokenizer, test_data['sent1'], test_data['sent2'], test_data['label'], test_data['strategy'])
    all_inputs, all_labels, all_strategies = encode_data(tokenizer, all_data['sent1'], all_data['sent2'], all_data['label'], all_data['strategy'])

    # 创建数据集
    train_dataset = CustomizedDataset(train_inputs, train_labels, train_strategies)
    train2_dataset = CustomizedDataset(train2_inputs, train2_labels, train2_strategies)
    val_dataset = CustomizedDataset(val_inputs, val_labels, val_strategies)
    test_dataset = CustomizedDataset(test_inputs, test_labels, test_strategies)
    all_dataset = CustomizedDataset(all_inputs, all_labels, all_strategies)

    # 定义 batch size
    batch_size = new_emote_config.bs

    # 创建 DataLoader
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    train2_loader = DataLoader(train2_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    all_loader = DataLoader(all_dataset, batch_size=batch_size)

    # 定义设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if args.finetune == 0:
        # 无监督评估
        model = AutoModelForSequenceClassification.from_pretrained(new_emote_config.model_path)
        model.resize_token_embeddings(len(tokenizer))
        new_token_id = tokenizer.convert_tokens_to_ids('[EM]')
        print('new_token_id: ', new_token_id)
        embeddings = model.get_input_embeddings()
        with torch.no_grad():
            embeddings.weight[new_token_id] = torch.normal(0, 0.01, (embeddings.embedding_dim,))
        print('Unsupervised evaluation')
        model.to(device)
        unsupervised_eval = UnsupervisedEval(model, test_loader, device, 'test', new_emote_config)
        unsupervised_eval.unsupervised_evaluation()
        exit()

    # 微调分支：加载预训练模型并将输出类别设为2
    model = AutoModelForSequenceClassification.from_pretrained(new_emote_config.model_path, num_labels=2, output_hidden_states=True, ignore_mismatched_sizes=True)
    model.resize_token_embeddings(len(tokenizer)) 
    model.to(device)

        
    # 初始化训练器并开始训练 (visual json)
    print("Fine-tune #1: visual info")
    trainer = EmoteTrainer(model, train_loader, val_loader, test_loader, device, new_emote_config=new_emote_config, tokenizer=tokenizer, name='visual')
    trainer.train(epochs=new_emote_config.max_epoch)
    
    # 初始化训练器并开始训练 (elco)
    print("Fine-tune #2: ELCo")
    trainer2 = EmoteTrainer(model, train2_loader, val_loader, test_loader, device, new_emote_config=new_emote_config, tokenizer=tokenizer, name='visual+elco')
    trainer2.train(epochs=new_emote_config.max_epoch)



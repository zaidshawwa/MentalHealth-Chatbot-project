from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import Trainer, TrainingArguments
from datasets import load_dataset



class FineTuningTrainer:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        """إعداد النموذج والمحولات (Tokenizer)"""
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token




    def load_and_split_data(self):
        """تحميل مجموعة البيانات وتقسيمها إلى تدريب واختبار"""
        dataset = load_dataset("Amod/mental_health_counseling_conversations")
        dataset = dataset["train"].train_test_split(test_size=0.25, seed=42)
        train_dataset = dataset["train"]
        eval_dataset = dataset["test"]
        return train_dataset, eval_dataset




    def tokenize_conversation(self, example):
        """دالة لتحويل النصوص إلى توكنز (Tokens) قابلة للمعالجة بواسطة النموذج"""
        text = example["Context"] + self.tokenizer.eos_token + example["Response"] + self.tokenizer.eos_token
        tokenized = self.tokenizer(text, truncation=True, max_length=250, padding='max_length', return_tensors='pt')
        return {"input_ids": tokenized["input_ids"].squeeze(), "labels": tokenized["input_ids"].squeeze()}




    def train_model(self, train_dataset, eval_dataset):
        """إعدادات التدريب وبدء عملية fine-tuning"""
        training_args = TrainingArguments(
            output_dir="./dialogpt-finetuned",
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=8,
            learning_rate=5e-5,
            logging_steps=50,
            eval_strategy="epoch",
            save_strategy="epoch",
            save_total_limit=2,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=None
        )

        trainer.train()
        trainer.save_model("./dialogpt-finetuned")
        self.tokenizer.save_pretrained("./dialogpt-finetuned")
        return trainer

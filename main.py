

from fine_tuning_trainer import FineTuningTrainer  # استيراد فئة FineTuningTrainer

# إنشاء كائن من فئة FineTuningTrainer
trainer = FineTuningTrainer(model_name="microsoft/DialoGPT-medium")

# تحميل البيانات وتقسيمها
train_dataset, eval_dataset = trainer.load_and_split_data()

# تدريب النموذج
trainer.train_model(train_dataset, eval_dataset)

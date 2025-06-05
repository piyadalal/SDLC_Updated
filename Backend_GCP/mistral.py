from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import get_peft_model, LoraConfig, TaskType
from transformers import TrainingArguments, Trainer, DataCollatorForSeq2Seq
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
from peft import get_peft_model

model = get_peft_model(model, peft_config)


model_id = "mistralai/Mistral-7B-v0.1"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype="bfloat16",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token


peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none"
)

model = get_peft_model(model, peft_config)

def format_example(example):
    return tokenizer(
        f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Output:\n{example['output']}",
        truncation=True, padding="max_length", max_length=512
    )

tokenized = dataset.map(format_example, batched=True)


training_args = TrainingArguments(
    output_dir="mistral-testcase-ft",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    num_train_epochs=3,
    logging_steps=10,
    save_strategy="epoch",
    evaluation_strategy="no",
    learning_rate=2e-4,
    bf16=True,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, padding=True, return_tensors="pt")
)

trainer.train()

model.save_pretrained("mistral-testcase-gen")
tokenizer.save_pretrained("mistral-testcase-gen")


pipe = pipeline("text-generation", model="mistral-testcase-gen", tokenizer="mistral-testcase-gen", device_map="auto")
output = pipe("### Instruction:\nGenerate a test case for:\n\n### Input:\nWhen the user presses Pause during playback, playback should stop.\n\n### Output:\n", max_new_tokens=200)
print(output[0]["generated_text"])



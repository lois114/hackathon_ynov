# -*- coding: utf-8 -*-
import os

import numpy as np
import triton_python_backend_utils as pb_utils


class TritonPythonModel:
    def initialize(self, args):
        self.model_name = os.getenv("TRITON_HF_MODEL", "microsoft/Phi-3.5-mini-instruct")
        self.max_new_tokens = int(os.getenv("TRITON_MAX_NEW_TOKENS", "256"))
        self.load_error = None
        self.tokenizer = None
        self.model = None

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.torch = torch
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
            )
            self.model.eval()
        except Exception as exc:
            self.load_error = str(exc)

    def execute(self, requests):
        responses = []
        for request in requests:
            prompt_tensor = pb_utils.get_input_tensor_by_name(request, "PROMPT")
            prompt = self._decode_prompt(prompt_tensor.as_numpy())
            if self.load_error:
                answer = f"ERREUR_CHARGEMENT_MODELE: {self.load_error}"
            else:
                answer = self._generate(prompt)
            output = pb_utils.Tensor("RESPONSE", np.array([answer.encode("utf-8")], dtype=object))
            responses.append(pb_utils.InferenceResponse(output_tensors=[output]))
        return responses

    def _decode_prompt(self, array):
        value = array.reshape(-1)[0]
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return str(value)

    def _generate(self, prompt):
        system = (
            "You are a financial assistant specialized in finance, investments, "
            "budgeting and economic concepts. Answer clearly and cautiously."
        )
        formatted = f"<|system|>\n{system}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
        inputs = self.tokenizer(formatted, return_tensors="pt", truncation=True, max_length=4096)
        if self.torch.cuda.is_available():
            inputs = {key: value.to(self.model.device) for key, value in inputs.items()}
        with self.torch.no_grad():
            generated = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=0.4,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        new_tokens = generated[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    def finalize(self):
        self.model = None
        self.tokenizer = None

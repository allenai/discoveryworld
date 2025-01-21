{
    "type": "openai_chat",
    "model": std.extVar("MODEL"),
    "max_tokens": 10000,
    "temperature": 0.0,
    "use_cache": true,
    "seed": std.parseInt(std.extVar("SEED")),
    "stop": ["\n"],
}